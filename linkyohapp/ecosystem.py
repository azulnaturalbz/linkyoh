"""Canonical property identities; activation follows the ecosystem ledger."""

SISTER_URLS = (
    'https://silvatech.bz',
    'https://visitbelize.silvatech.bz',
    'https://chillbout.com',
    'https://linkyoh.com',
    'https://marketday.silvatech.bz',
    'https://wop.silvatech.bz',
    'https://payments.silvatech.bz',
    'https://consulta.silvatech.bz',
    'https://belizelogistics.com',
    'https://games.silvatech.bz',
)

PUBLIC_CRAWL_AGENTS = (
    'GPTBot', 'OAI-SearchBot', 'ClaudeBot', 'Claude-SearchBot',
    'PerplexityBot', 'Google-Extended',
)
BLOCKED_CRAWL_AGENTS = ('CCBot', 'Bytespider', 'HTTrack', 'WebCopier', 'WebZIP')
PRIVATE_CRAWL_PATHS = (
    '/admin/', '/api/', '/login/', '/logout/', '/register/', '/my-gigs/',
    '/create-gig/', '/messages/', '/messaging/', '/notifications/',
    '/password-reset/', '/password-change/', '/reset/', '/verify-phone/',
    '/resend-code/', '/ajax/', '/ads/', '/track-event/', '/like-gig/',
    '/toggle-qr-code/', '/gigs/*/claim/', '/media/claim_documents/',
)


def robots_text(sitemap_url):
    lines = [
        '# Public discovery and attributed answers are welcome; no bulk mirroring.',
        '# See /llms.txt. Robots rules are voluntary, not authentication.',
        '# Allowing GPTBot/ClaudeBot/Google-Extended does not enforce citation-only use.',
    ]
    # Named agent groups do not inherit wildcard exclusions.
    for agents in (('*',), PUBLIC_CRAWL_AGENTS):
        lines.extend(f'User-agent: {agent}' for agent in agents)
        lines.extend(f'Disallow: {path}' for path in PRIVATE_CRAWL_PATHS)
        lines.append('Allow: /')
        lines.append('')
    lines.extend(f'User-agent: {agent}' for agent in BLOCKED_CRAWL_AGENTS)
    lines.extend(('Disallow: /', '', f'Sitemap: {sitemap_url}', ''))
    return '\n'.join(lines)
