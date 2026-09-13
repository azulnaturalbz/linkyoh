"""Shared-worker limits for public directory reads, independent of account logic."""

import hashlib
import hmac
import ipaddress
import logging

import redis
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

DIRECTORY_VIEWS = frozenset({
    'home', 'search', 'category_listing', 'sub_category_listing',
    'category_listing_legacy', 'sub_category_listing_legacy',
    'gig_detail', 'gig_detail_legacy', 'profile', 'profile_legacy',
})

# Check both windows and increment as one Redis operation across all workers.
LIMIT_SCRIPT = """
local retry = 0
for i, key in ipairs(KEYS) do
    local limit = tonumber(ARGV[(i - 1) * 2 + 1])
    if tonumber(redis.call('GET', key) or '0') >= limit then
        retry = math.max(retry, redis.call('TTL', key), 1)
    end
end
if retry > 0 then return retry end
for i, key in ipairs(KEYS) do
    local count = redis.call('INCR', key)
    if count == 1 then redis.call('EXPIRE', key, ARGV[(i - 1) * 2 + 2]) end
end
return 0
"""


def normalize_ip(value):
    address = ipaddress.ip_address(value.strip())
    return address.ipv4_mapped if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped else address


def client_address(request, trusted_networks):
    try:
        peer = normalize_ip(request.META.get('REMOTE_ADDR', ''))
    except ValueError:
        return 'unknown'
    if any(peer in network for network in trusted_networks):
        # Direct shared Caddy ignores incoming spoofed XFF by default. The rightmost
        # value remains the immediate client even if a prior chain is preserved.
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '').rsplit(',', 1)[-1]
        try:
            return str(normalize_ip(forwarded))
        except ValueError:
            pass
    return str(peer)


def unavailable_response(status, retry):
    message = ('Too many requests. Please try again shortly.' if status == 429
               else 'Service temporarily unavailable. Please try again shortly.')
    response = HttpResponse(message + '\n', status=status, content_type='text/plain; charset=utf-8')
    response['Retry-After'] = str(retry)
    response['Cache-Control'] = 'no-store'
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response


class DirectoryRateLimitMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.enabled = settings.LINKYOH_DIRECTORY_RATE_LIMIT_ENABLED
        self.networks = tuple(ipaddress.ip_network(value) for value in settings.LINKYOH_TRUSTED_PROXY_NETWORKS)
        self.windows = settings.LINKYOH_DIRECTORY_RATE_WINDOWS
        if any(network.prefixlen == 0 for network in self.networks):
            raise ImproperlyConfigured('Trust only the verified edge network, not all IP addresses.')
        if not self.windows or any(limit < 1 or seconds < 1 for limit, seconds in self.windows):
            raise ImproperlyConfigured('Directory rate windows must be positive.')
        if self.enabled:
            if not settings.LINKYOH_RATE_LIMIT_REDIS_URL:
                raise ImproperlyConfigured('Directory rate limiting requires its private Redis URL.')
            self.redis = redis.Redis.from_url(
                settings.LINKYOH_RATE_LIMIT_REDIS_URL,
                socket_connect_timeout=0.2, socket_timeout=0.2,
                retry_on_timeout=False,
            )

    def process_view(self, request, view_func, view_args, view_kwargs):
        if (not self.enabled or request.method not in ('GET', 'HEAD')
                or request.resolver_match.url_name not in DIRECTORY_VIEWS):
            return None
        address = client_address(request, self.networks)
        identity = hmac.new(settings.SECRET_KEY.encode(), address.encode(), hashlib.sha256).hexdigest()
        keys = [f'linkyoh:directory:{identity}:{index}' for index in range(len(self.windows))]
        arguments = [value for window in self.windows for value in window]
        try:
            retry = self.redis.eval(LIMIT_SCRIPT, len(keys), *keys, *arguments)
        except redis.RedisError:
            # Do not log connection strings, addresses, request paths or query data.
            logger.warning('Directory rate-limit store unavailable')
            return unavailable_response(503, 5)
        if retry:
            return unavailable_response(429, retry)
        return None
