# Linkyoh Revamp

Status: **HOLD - awaiting Cristian's sign-off on specs/REVAMP.md**.
Prepared: 2026-09-13 UTC. This document proposes work; it does not authorize it.
Canonical contracts: [Silvatech Ecosystem Ledger](../../../Silvatech/silvatech/SILVATECH-ECOSYSTEM.md),
especially sections 3 rule 6, 5.1 door 4, 7 and the Linkyoh property record.
Deployment remains a separate gate under the shared-host ledger, even after design sign-off.

## Outcome and differentiation

Linkyoh becomes Belize's useful service-finding network: discover a relevant
provider, understand what has been checked, contact them, and let an owner claim
and maintain the business. The competitor copied functionality and a look-alike
UI. A new color scheme alone does not address that problem.

The differentiators to deliver and measure are:

1. Reciprocal estate links: the shared strip and maker-to-MarketDay handoff connect
   discovery to stores, WhatsApp, payments and advice across Silvatech properties.
2. A grounded finder powered by the one WOP runtime: conversational matching to
   actual public records, with consented leads and relevant product handoffs.
3. Verified ownership with auditable human decisions: a badge states what was
   checked and when; imported, claimed and verified are separate states.
4. Maintained Belize coverage: normalized district/town and explicit multi-area
   service records, provenance, corrections, duplicate resolution and freshness.
5. Owner relationships and permitted lead outcomes: internal verification and
   consent records stay private and are not part of a public directory export.

Public pages and photos can still be copied. The advantage is the maintained
data, consented relationships, verified domains and working integrations. Do not
promise that robots, trademarks or rate limits make scraping impossible.

## Grounded baseline

- Source currently pins Django 3.2.20; Docker uses Python 3.9 Alpine.
- Despite the older ledger/guide's Bootstrap 4 label, base.html loads Bootstrap
  5.3.2, Font Awesome, htmx 1.9.6, Alpine 3.13 and Select2's Bootstrap 5 theme.
  django-bootstrap4 remains installed. Audit this mixed stack before removal.
- Profile already has individual/business types, company_name, public contact
  fields, is_verified and verified_date. Preserve display-name fallback:
  business company name, otherwise full name, otherwise username.
- Gig owns the service title/category/subcategory, image, price/call-for-pricing,
  primary location and owner; GigServiceArea supports multiple coverage areas.
  A location is not evidence of availability, licensing or nationwide coverage.
- GigClaimRequest tracks evidence, pending/approved/rejected and admin notes;
  approve() currently transfers gig ownership and emits a notification. It is not
  a complete provider-verification workflow or a concurrency-safe claim contract.
- ImportedGigSource stores internal source URL/notes/raw payload and importer.
  The existing staff/API-key ingestion endpoint supports media and deduplication.
  Preserve it as an operator surface; never expose the import key to a finder.
- Existing canonical provider/category/gig routes, legacy 301s, sitemap, Facebook
  metadata, QR paths, messaging and existing account behavior must remain valid.
- Phase A is additive and does not alter these records or account workflows.
- Local Phase A browser QA found a pre-existing provider action overflowing at
  390px (body 408px); removing all Phase A components leaves it unchanged. Include
  this in the mobile profile acceptance slice, not a silent Phase A redesign.

## Lab brand and discovery layout

Adopt the full Lab register only after this spec is approved. Consume the hub's
`public/brand/silvatech-ui.css` at a recorded version; use a local pinned copy or
reviewed asset release so a remote stylesheet cannot change production silently.
Do not create a competing brand token library.

| Token or convention | Required value |
| --- | --- |
| Body / headings / code | Inter / Sora / JetBrains Mono |
| Brand dark | --brand-900: #192d40 |
| Brand primary | --brand-500: #2b8ec8 |
| Brand light | --brand-300: #8ac5ea |
| Accent | --violet-500: #4f46e5 |
| Success / dark surface | --success: #2bd4a6 / --surface: #0f1c2b |
| Repeated card radius | 16px, per estate contract |
| Icons | Lucide; accessible names for icon-only controls |
| Shared marks | Ecosystem Strip, legal line, Powered by Silvatech trademark |

Use neutral light page surfaces with restrained brand accents. Validate actual
text/background contrast; brand-500 or success color alone does not guarantee
accessible white text. Self-host fonts where practical, with stable fallbacks.
Remove competing inline green/orange overrides in reviewed slices. Keep Select2
only where needed until native controls or htmx equivalents pass feature parity.

Model discovery on MarketDay's root page, inspected in
`main/templates/restaurant/home.html`, `main/discovery.py`, `static/css/discovery.css`
and `docs/modernization/community-discovery.md`; adapt behavior, not merchant data.

- First viewport: clear Linkyoh identity, search, district/town/category filters,
  result count and the start of real provider/service cards. No oversized hero.
- Keep ordinary GET forms and meaningful labels. htmx progressively refreshes
  results; Alpine handles only local filter drawer/widget state. No second SPA.
- On mobile, show search and compact active filters, with a reachable filter
  drawer and clear/apply controls; keyboard, focus return, collapse and back work.
- District changes constrain town choices. Category changes constrain subcategory.
  Invalid combinations return an honest empty state and reset action.
- Apply filters before pagination; preserve them in shareable URLs and back/forward
  navigation. Normalize accepted parameters; do not carry arbitrary query strings.
- Cards show real image, service/business name, coverage, category, verification
  state and contact action. Reserve image aspect ratio and wrap pills. Never let
  long prices, names or categories stretch a card or hide another control.
- Provider pages use readable cover overlays and visible claim/correction actions.
  Display business name with the existing fallback, never the importing bot as
  though it were the advertised business.
- Map is optional and deferred. No required geolocation, inferred coordinates or
  publishing home-address pins. List-only discovery must remain complete.
- Preserve SEO canonical rules, legacy URLs, Open Graph images and sitemap entries.
  Filter/pagination pages use a reviewed canonical/noindex policy rather than
  generating an unbounded index of duplicate combinations.

## Verified-provider claim flow

Entry points: an unclaimed listing, provider page, or "Free verified provider
profile" recruiting destination. An imported listing remains explicitly curated
and unclaimed until ownership is approved; an import never creates verification.

Proposed journey: choose existing business (or request a missing one), sign in or
create account, confirm contact, submit ownership evidence, see pending review,
receive decision and manage the approved profile. Verification is a separate
review step with scope/date, expiry/recheck and revocation support.

- Extend existing Profile/GigClaimRequest rather than building parallel accounts.
  First specify the provider-to-many-gigs boundary and how shared importer accounts
  split into businesses; do not backfill importer profiles as verified businesses.
- Distinguish unclaimed, claim pending, claimed, verification pending, verified,
  rejected and revoked. Map current records conservatively; unknown stays unknown.
- Store who reviewed, what was checked, outcome/reason and timestamps. Only
  authorized reviewers set verification. Do not equate verification with licensing.
- Resolve competing claims in an atomic transaction with row locks and one active
  ownership decision; ensure retries cannot reassign twice or duplicate notices.
- Claim files require private storage and authorized short-lived access. Current
  supporting_document uses the default storage: audit actual S3 privacy before any
  new claim experience ships. A robots exclusion is not access control.
- Define retention/deletion, disputes, appeals and redaction; keep documents,
  personal identifiers and internal notes out of HTML, JSON-LD, llms and tools.
- Show verification scope/date and last owner confirmation, with correction/report
  action. Do not publish fake reviews, availability or verified counts to fill UI.

## Finder door: one WOP runtime

Example: "I need a plumber in Cayo tonight" leads to clarification of town and
urgency, matched public providers with sources, and an explicitly consented lead.
"Tonight" is a requirement to confirm, not permission to invent open hours.

WOP Gate 0 is reported PASS in the 2026-09-13T03:39:00Z Handoff Log: specs 108-110
are merged and the Visit Belize endpoint is live. This is ledger evidence, not a
Linkyoh endpoint test. Only visit-belize is provisioned there. No widget is embedded
in Phase A. Before implementation, re-read the log and use WOP's published snippet
verbatim; require a reviewed Linkyoh WebsiteChatEndpoint, exact allowed origins
for apex/www, deployment binding and actual public smoke evidence.

- Proposed endpoint key: `linkyoh` (must be confirmed by WOP owner). Runtime,
  model access, memory, tools, retries and channel handoffs belong to WOP.
- Opening the widget must not create a conversation/lead; first send creates the
  conversation. Anonymous web identity is not verified WhatsApp identity.
- Display "AI assistant by Silvatech - a real person is always reachable" and the
  estate WhatsApp escape hatch, using a confirmed destination, never a dummy number.
- Add a bounded read-only Linkyoh search/detail tool over published records.
  Existing import API is not this search API. Define request filters, page limits,
  canonical result IDs/URLs, explicit coverage, verification scope/date and freshness.
- Match only actual records; prefer relevant area and service, disclose ranking,
  identify unknown hours and request provider confirmation for urgency. Distinguish
  sponsored placement. No providers: say so, offer filter expansion and human contact.
- Before capture, ask which contact method/details the user permits and which
  provider receives the enquiry. Minimize address/PII; confirm the lead summary.
- WOP owns idempotent lead capture with source_property=linkyoh and consent/source
  records. Deduplicate retries and do not silently send messages to providers.
- ProductHandoff carries only permitted context: makers -> MarketDay; business
  automation needs -> WOP. WOP publishes the A2A card under its federation contract;
  do not invent a Linkyoh-local runtime or disclose staff tools/brain internals.
- Failure/timeouts leave manual search/contact fully usable. Events distinguish
  match shown, contact requested, consent and accepted lead; no transcript/PII in Rybbit.

## Recruiting funnel

Offer: **Free verified provider profile**. Clarify that verification requires review
and does not imply paid placement, guaranteed leads or instant approval.

Meta Instant Form -> WOP leads with a dedicated Linkyoh LeadSource -> consented
WhatsApp follow-up -> find/claim existing listing or request a new profile -> review
-> owner confirmation -> useful traffic/contact reporting. Use the estate funnel
mechanics (manual placements, Audience Network off, one-tap WhatsApp); coordinate
audience sequencing so two properties do not recruit the same audience concurrently.
Campaign activation, spend, exact channel/destination and follow-up copy require
Cristian's approval; this spec launches no campaign or automation.

Measure accepted leads, duplicate claims avoided, completed profiles, verified
owners, time to decision, match-to-contact conversion and cross-product referrals.
Record the actual baseline before setting targets; do not invent performance figures.

## Django 3.2 to 5.2 checkpoints

Target: latest security-patched Django 5.2 LTS with a supported Python runtime.
Django 4.2 and Python 3.9 are already past their support windows as of this spec;
intermediate releases are isolated test checkpoints, not new production destinations.
Follow the official incremental upgrade guide, checking every intervening feature
release's deprecations. Do not mix the dependency upgrade with a visual rollout.

| Checkpoint | Work and exit evidence |
| --- | --- |
| 0: establish recovery | Capture current image/revision and dependency inventory; isolated DB restore and S3 media path proof; baseline tests, counts, canonical redirects, auth, claims, messaging, QR, imports, payments/ad hooks and worker schedules. No production dump in repo. |
| 1: clean 3.2 | Latest 3.2 patch in an isolated branch; enable deprecation warnings. Inventory URL helpers, deprecated JSONField imports, middleware, CSRF origins, storage and timezone assumptions. Preserve primary keys and URL slugs. |
| 2: 4.0 / 4.1 / 4.2 | Step through feature releases with tests, latest patch per checkpoint. Move contrib.postgres JSONField to models.JSONField with migration-state review; pin compatible DRF, forms, history, phonenumber, Celery and storage packages. Audit DEFAULT_AUTO_FIELD and pytz/zoneinfo; no surprise migrations. |
| 3: supported Python | On isolated 4.2 test checkpoint, move to Python 3.12 and rebuild native wheels. Refresh psycopg, Pillow/HEIF, Gunicorn, requests, certifi, boto3, Redis and Celery compatibility as a reviewed lock; verify Belize time and media processing. |
| 4: 5.0 / 5.1 / 5.2 | Complete deprecation removals; replace DEFAULT_FILE_STORAGE/STATICFILES_STORAGE with STORAGES; review USE_L10N, auth/logout POST/CSRF behavior, URL APIs and Django-compatible form renderers. Run each release's checks before advancing. |
| 5: release candidate | Full PostgreSQL suite, migration plan against restored data, secrets-free image scan, storage/claim privacy proof, worker/beat delivery, concurrency and browser QA. Verify compatible read/write period or schedule maintenance with tested restore. |
| 6: authorized deployment | Cristian's go, shared-host ledger claim, fresh backups/capacity and neighbor baseline, app-only immutable image rollout, collectstatic/migrations when approved, public and operator smoke tests, rollback observation and ledger handoff. Never restart shared edge as a side effect. |

## Acceptance and release slices

1. Approve this spec and record sign-off in the Handoff Log. Phase A deployment
   is independently authorized and verified; no production changes are implied.
2. Dependency modernization with recovery evidence; no cosmetic changes in that
   release. Keep existing URLs, data and integrations compatible.
3. Lab discovery/profiles with GET-first filters and responsive parity. No dead
   chat buttons before an endpoint is available.
4. Verified claim review with privacy, permissions, race/retry tests and a real
   owner/reviewer acceptance journey using approved data.
5. Provisioned WOP finder with synthetic grounding/consent/no-match/failure tests,
   then reviewed lead handoff; recruiting campaign is the last explicit gate.

For UI slices, verify 320/390/768/944/1440px widths, zoom, keyboard and no-JS use;
WCAG AA text/focus contrast, label/error relationships, touch targets, no horizontal
overflow or card-pill clipping, navigation collapse and resilient empty/loading/error
states. Verify filters persist through pagination/back; bounded SQL/materialization
with representative volumes; no hidden/unpublished records in results or schemas.

For the agent, require source-cited matches, unknown-availability honesty, no-result
behavior, repeated-send idempotency, consent before contact, prompt-injection
resistance to source text and proof that private/account data is inaccessible.

For operations, compare shared neighbors before/after each authorized rollout.
Rate-limit counters must work across workers, reject spoofed XFF and preserve
normal browse/API/account flows. Monitor Redis health, 429/503 and false positives
behind shared mobile/carrier NAT; thresholds need actual traffic validation.

## Owner sign-off

Pending: Cristian's acceptance of this scope and release ordering. Record exact
decision/date in the canonical Handoff Log. Until then: **no redesign code, claim
logic changes, endpoint embedding, dependency upgrades or campaign activation**.

## References

- [Django upgrade guide](https://docs.djangoproject.com/en/5.2/howto/upgrade-version/)
- [Django 5.2 release notes](https://docs.djangoproject.com/en/5.2/releases/5.2/)
- [Supported Python versions](https://docs.djangoproject.com/en/5.2/faq/install/)
- [OpenAI crawler distinctions](https://developers.openai.com/api/docs/bots)
- [Service schema](https://schema.org/Service)

The canonical ecosystem and shared-host ledgers remain the authority for cross-agent
contracts, state, deployment procedure and handoffs. This is the requested Linkyoh
product revamp spec, not a replacement ledger.
