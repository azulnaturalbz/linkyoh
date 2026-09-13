# Implementation Plan

1. Extend existing templates with isolated includes and a byte-identical copy of
   hub ecosystem-strip.css. Keep existing Bootstrap/color/font defaults intact.
2. Reuse seo.py; add ecosystem constants, crawler text endpoints and a delegated
   Rybbit event handler that sends only destination/placement (no search/PII).
3. Add middleware using existing redis dependency and atomic Lua counters with
   expiries: 30 requests/10 seconds and 120/60 seconds per IP across all protected
   routes. Hash addresses with HMAC, normalize IPv6, discard spoofed proxy prefixes.
   Reject over-budget requests with 429/Retry-After; Redis failure gives a bounded
   503/Retry-After on protected reads only. No local-memory fallback or silent bypass.
4. Add a private 64 MiB-capped Redis Compose service (16 MiB key budget, expiring
   counters, no persistence or host ports). App alias linkyoh-web stays unchanged.
   Production Compose requires explicit trusted edge CIDRs before activation.
5. Test in disposable local databases/Redis. Verify canonical redirects, source
   privacy, HTML escaping, multi-worker atomic limits, IP separation, reset,
   method exclusions and cache failure. Render home/profile/gig at 390/944px.
6. Spec the Lab/discovery/verification/finder/funnel/upgrade work, reconcile hub
   artifacts and ledger, commit, and record HOLD. No redesign implementation.

Spec Kit scripts/skills are absent from this checkout; use the existing numbered
spec.md/plan.md/tasks.md convention manually, preserving the same pre-code gates.

Shared-edge rate limiting is not shipped by editing Caddy here: stock Caddy's
rate-limit module is non-standard. The edge owner must validate any module or
equivalent perimeter solution separately; app protection does not stop network DDoS.

References: https://caddyserver.com/docs/modules/http.ratelimit,
https://developers.openai.com/api/docs/bots,
https://schema.org/Service, https://schema.org/LocalBusiness.
