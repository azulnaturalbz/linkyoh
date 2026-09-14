# Sitewide Lab app-only release

## Authorization and scope

Cristian approved the latest UI and deployment on 2026-09-13 Belize time, recorded
2026-09-14 UTC. This supersedes the local UI/logo and deployment HOLD. Deploy the
committed UI branch, including Kev's unchanged marketing reference asset and brief.
The dependency modernization branch, claim slice 4, WOP endpoint, campaigns and
other properties remain outside scope.

## Plan and gates

- [x] Freeze exact committed runtime files; preserve the existing dependency image.
- [x] Re-run tests in that runtime with disposable PostgreSQL/Redis only.
- [x] Verify live source baseline, empty migration plan, actual proxy trust,
  private limiter, capacity and all neighbors before mutation.
- [x] Hold existing shared release locks and the Linkyoh app-release lock; retain
  source/config/static backups on host and verified private off-host copies.
- [x] Pin new image and recreate only `web`, using both existing Compose files.
- [x] Check public EN/ES pages, assets, canonical/legacy/schema/crawl contracts,
  responsive and no-JS/keyboard behavior; compare neighbors/config/firewall.
- [x] Record source/image identity, evidence and final ledger handoff.

No schema or dependency change is expected. No production fixture import or
reference-data rewrite is allowed. Existing read-only source/reference evidence
remains in the parent spec; public reads can exercise existing view counters.
The previously verified 64 PostgreSQL/Redis tests and 370-view local QA matrix
remain the wider regression evidence. Live checks must be bounded below limiter
thresholds and must not submit contact/claim/account forms.

Candidate source: `34196aad3d0a50ac02c2b75981fb411645bffef5` (UI `b985245`
plus Kev reference). Image: `sha256:ff3ce873f0c0546f0b3dee0d1338fd682c909e914020689eff90fb06eefdf66c`.
All 356 runtime files, including compiled EN/ES catalogs, are selected from Git;
no private fixture, local database or environment enters the build context.
Existing Python 3.9.25/Django 3.2.20 layers remain unchanged. All 64 tests pass
inside this exact amd64 image with isolated local PostgreSQL/Redis; containers
and their disposable volumes are removed. Nine offline controller tests cover
neighbor/config preservation, exact proxy trust, private Redis and rollback.

Read-only candidate production checks pass: no planned migrations, no migration
drift, system check clean and WOP disabled. Pre-cutover tooling corrections:
timer inventory uses loaded instances instead of trying to inspect an uninstanced
systemd template; Compose JSON's numeric-string memory limit is parsed as an
integer. Both checks stopped before source or container mutation. An initial
build command ran before its upload finished and failed before building; the
completed upload was rebuilt and verified. A first local test-helper mount was
too shallow for its path lookup; corrected to its canonical path before 64 tests.

No Linkyoh secret-refresh timer exists on this host. Do not claim one was locked:
the controller holds the existing shared MarketDay release lock, existing WOP
release lock and a Linkyoh app-release lock, preserves `.env` bytes and checks
all timer states. No timer is stopped or enabled by this release.

## Initial attempt and recovery

The first cutover started at `2026-09-14T03:59:12Z`. The candidate served the
new UI, but a post-switch guard incorrectly treated Docker's ephemeral short
container-ID DNS alias as a stable routing alias. It restored the previous image
and source/static files. Old public HTTP 200 was independently confirmed; all 24
neighbors, protected settings, timers and firewall rules remained unchanged.
The guard also rejected its rollback snapshot for the same false difference,
so independent recovery evidence is retained in `evidence/initial-attempt/`.
This caused two short web-container restart windows, not an application test
failure; no database rollback or neighbor restart occurred.

The corrected guard excludes only the exact current container ID and requires
the complete stable allowlist `linkyoh-web`, `linkyoh-web-1`, `web`. An added
offline test proves it still rejects unexpected aliases. Original evidence and
backups remain intact; the same tested image is retried under a new directory
`/opt/linkyoh/releases/34196aa-20260914-retry1/` with fresh checks and backups.

## Live result

Successful cutover: **2026-09-14T04:02:24.448827Z**, https://linkyoh.com/ and
https://www.linkyoh.com/. Source/image identity above is unchanged after testing.
The release is web-only: all 24 neighboring containers retained their IDs,
images, start times and restart counts, including Linkyoh workers/RabbitMQ/Redis.
Shared Caddy, stable aliases, `.env`, Compose source, timers and firewall rules
are unchanged. Trust remains the actual `172.20.0.2/32`; Redis remains private,
healthy and capped at 64 MiB. Final bounded capacity observation: about 2.66 GiB
available RAM, 1.66 GiB swap free, 10.43 GiB disk free; no web OOM/restart.

`evidence/public-qa.json`: **52 live views** in EN/ES at 320/390/768/944/1440px,
four native/keyboard journeys, 5,370 rendered text contrast samples, zero detected
overflow, broken visible images, page errors or sampled AA failures. Includes
Home/Results/Provider/Gig at every width and Category/Subcategory/Login/Register/
Help/About at 390px. Four journeys exercise skip links, menu open/close, smart
GET parsing to actual Cayo records, shareable URLs and honest empty results.
An initial QA-only route typo `/about/` returned 404; corrected to the existing
`/about-us/` route, with the first report preserved. No app route was changed.

Ten app/neighbor HTTPS endpoints and robots/llms/sitemap return 200. Three legacy
routes retain exact 301 destinations. Five CSS/brand/Kev assets byte-match Git;
three distinct OG images return 200, including actual S3 listing media. Canonicals,
Organization/LocalBusiness/Service JSON-LD and real-record Checked chips remain.
The original social-image/favicon contract is unchanged. Rybbit is suppressed
in automated QA; no analytics-delivery or social-cache-refresh claim is made.
External QR rendering is allowed, but QR decoding is not certified. This is
targeted Chromium QA, not full WCAG, screen-reader, Safari or load certification.

No provider/account/claim submission, fixture import, dependency upgrade, WOP
activation, campaign, other-app restart, DNS, edge or firewall mutation occurred.
Public GETs may exercise existing listing view counters. Long legacy help/legal
prose remains in its source language, as disclosed in the approved local review.

Kev's unchanged master is now served at
https://linkyoh.com/static/brand/kev/kev-plumbing-master.png and documented in
`docs/brand/KEV.md`. It is a fictional AI brand asset, not a seeded provider.
The owner's naming decision was also captured as Brain inbox claim
`2026-09-13-linkyoh-006`, pending human review, not promoted to accepted truth.

Private recovery copies remain under
`/opt/linkyoh/releases/34196aa-20260914{,-retry1}/` and the matching
`/Users/cristiansilva/WorkSpace/Linkyoh/.release-backups/` directories. Both source/
config and static archives have verified off-host hashes. Review retention on
2026-09-28; do not delete them automatically. Runtime is `34196aa`; subsequent
evidence commits do not change the deployed artifact.

Publication check: Gitleaks 8.30.1 scanned release evidence/controller text and
reported 18 source-manifest SHA-256 values whose filenames contain key/password
terms. Each is validated as a generated 64-character source checksum; zero
unresolved findings. Check transcripts normalize trailing spaces from Docker's
progress lines; original protected remote logs remain available.

## Rollback procedure

Retain current live image `sha256:e252a3ce5593b3f43da9f84b445e43afbcd1b589fa225272ca839d8f7995d9c0`.
Under the same locks, restore only owned source/static changes and the prior
image-pinning file; recreate only web. Do not restore an old secret file over
rotation, restore RDS, run Compose down, restart Redis/workers, change the shared
edge or alter firewall rules. Verify restored public health and unchanged
neighbors. On uncertainty, preserve the journal and stop further mutations.
