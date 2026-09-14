# Strip v2 App-Only Release

Cristian's exact "Approve" for application `60d5af7` is recorded by the hub
in the canonical ecosystem Handoff Log at 2026-09-14T18:07:07Z. That timestamp
is the receipt time, not an inferred user-message time. Source authority is
the hub task `019e3c4b-db00-7603-b929-5b5bb0b7e031` and its quoted conversation.
`2579b34` changes local handoff documentation only.

Follow the canonical shared-host APP-LINKYOH procedure. This is an app-only
replacement, not another host/VM/data migration. Reuse the installed runtime,
verify immutable source/image parity, take current app/static backups on and
off host, and replace web only. Preserve the private Redis and exact actual
Caddy /32 trust, env, Compose service definitions, edge, firewall and all
neighbors. Only the existing app-local release image pin may change.

No schema/data, Python dependency, account/claim, WOP binding or campaign
changes are authorized. No new RDS snapshot or source retirement is required
for this no-schema release; never restore a database for a template rollback.

## Gates

- [x] Exact candidate and sender-owned owner-approval receipt verified.
- [x] Build/test immutable candidate with the existing dependency layers.
- [x] Wait for Chillbout and queued WOP releases; coordinate own window.
- [x] Fresh AWS/host capacity, source, actual proxy, configuration and neighbors.
- [x] Backup image/source/static; hash-verify protected off-host copies.
- [x] Read-only production check/migration plan, app-only switch and rollback guard.
- [x] Public v2, CSS, llms/schema, SEO/legacy and responsive evidence.
- [x] Neighbor/runtime preservation after browser QA.
- [x] Commit/push, ledger closure and owner notices.

## Immutable Candidate

Image `sha256:778630b95827f791a3bc0c69eaf3326a99b400d6187b4bad2d3c859d75ce50fa`
is amd64, labelled with exact approved commit `60d5af7`. All 357 packaged
files match Git. The 67-test PostgreSQL/Redis suite passed inside the image
without an application-source mount; only the external test-runner helper
was mounted. Python 3.9.25 and Django 3.2.20 are unchanged. Receipt:
`evidence/image.json`; test log: `evidence/image-tests.txt`.

## Cutover

The controller completed at `2026-09-14T18:28:16.749087Z`, replacing only
Linkyoh web. All 24 neighboring containers and protected edge/env/Compose,
timers, firewall, stable aliases and exact Caddy trust were preserved. The
public v2 marker and Games link passed readiness. No rollback was needed for
this release. Final server comparison at `2026-09-14T18:31:42.272569Z` still
matches all 357 source files, all 24 neighbors and every protected setting.
Available RAM was 2,246,934,528 bytes and free disk 10,536,927,232 bytes.
Private Redis remains healthy with 64 MiB cap, and trust pins the actual
Caddy peer `172.20.0.2/32`.

## Public Verification

- 52 live EN/ES views across 320/390/768/944/1440px; 108 screenshots in
  `evidence/`, including each strip and four empty-state journeys.
- Four keyboard/no-JavaScript journeys pass skip link, reversible native
  mobile menu, shareable GET search, real Cayo parsing and honest empty state.
- Zero tested overflow, broken visible images, page errors or sampled AA
  contrast failures across 5,422 text samples. This is not full WCAG,
  screen-reader or Safari certification.
- Ten correctly ordered/attributed strip links on every tested page, Games
  last, 44px targets, noreferrer and Organization sameAs verified.
- Thirteen HTTPS/crawl checks, seven byte-identical static assets (including
  Kev), three OG images and three exact legacy 301s passed. Existing URLs,
  canonicals and sitemap remain intact.
- Production reference data, provider media and existing user workflows were
  not edited. Public GETs may exercise existing view counters; no account,
  claim, ingestion, quote or provider-contact submission was made.
- Analytics was stubbed; this is not live event-ingestion proof. WOP stays
  disabled/unprovisioned, and no campaign was activated.

Machine-readable receipts: `evidence/public-qa.json`, `cutover-result.json`,
`final-after.json`, `trust.json` and `backup-checksums.json`. Manual visual
review also checked mobile Home, Spanish provider strip and desktop Home.

Source/static archives are retained under
`/opt/linkyoh/releases/60d5af7-20260914/`, with hash-verified mode0600 off-host
copies in `/Users/cristiansilva/WorkSpace/Linkyoh/.release-backups/60d5af7-20260914/`.
The previous image remains tagged `linkyoh-web:rollback-pre-60d5af7`.
Review retention on 2026-09-28; no cleanup is authorized by that date alone.
Rollback restores only owned app/static files and the prior image pin under
the same locks, preserves current secrets, and recreates web with no deps.
Never restore the database or run Compose down for this template release.

GitHub reported 71 existing default-branch dependency advisories during the
UI branch push (2 critical, 34 high, 29 moderate, 6 low). This is a provider
notification, not a fresh vulnerability audit. Dependencies are unchanged;
modernization remains on its separate branch and release gate.

## Handoff

Release evidence `8899985` was pushed to the UI branch with `azulnaturalbz`;
global GitHub authentication was unchanged. Both canonical ledgers record
the window released at `2026-09-14T18:32:36Z`, with only Linkyoh's row,
record/directory and one final handoff entry updated. Completion messages
were accepted by WOP, Payments, MarketDay, Chillbout and the hub. No further
host mutation is pending. Shared-ledger changes remain for their respective
repository owners to commit; no foreign application code was changed.
