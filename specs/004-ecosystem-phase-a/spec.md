# Linkyoh Phase A

Status: implementation authorized; deployment requires Cristian's go.

The canonical specification is `SILVATECH-ECOSYSTEM.md`, sections 2-7 and the
Linkyoh property record, at
`/Users/cristiansilva/WorkSpace/Silvatech/silvatech/SILVATECH-ECOSYSTEM.md`.
This checklist records Linkyoh implementation details, not a second ecosystem plan.

## Acceptance

- Consume the hub strip and MarketDay Django snippet, changing only utm_source.
- Inactive properties remain text; all ecosystem links have UTM and data-track.
- Legal marks, powered-by link, and approved MarketDay banner appear in existing
  layouts on home, provider profiles, and service detail pages without redesign.
- Public llms.txt and robots preserve private-route exclusions. Allow the ledger's
  AI agents; block CCBot, Bytespider, HTTrack, WebCopier and WebZIP. Explain that
  robots is voluntary and cannot technically enforce citation-only use.
- Organization sameAs covers the estate; business/service metadata uses actual
  service areas, never implies provider ownership by Silvatech or verification.
- Directory GET/HEAD requests share per-IP burst and minute limits across workers.
  API, account, POST, assets and health paths are outside this middleware.
  Proxy headers are trusted only from configured edge peers; never UA exemptions.
- No listing, provider, account, payment or ingestion behavior/schema changes.
- Write specs/REVAMP.md and stop at HOLD for Cristian's sign-off.

## Delivery boundary

Commit locally only. No push, cloud mutation, deployment or other property code.
The shared edge is owned by /opt/edge; its independent rate-limit rollout must be
coordinated under SHARED-HOST-MIGRATION.md after authorization.
