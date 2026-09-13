# Phase A Production Release

## Scope And Result

Cristian authorized exact commit `6b62c618321c8dd53b6513851c1a1911833b3cb4`
for an app-only release with private Redis and inspected proxy trust.
Cutover completed **2026-09-13T20:04:36Z** at <https://linkyoh.com/>.
`specs/REVAMP.md` remains **HOLD: awaiting Cristian's separate sign-off**.
No redesign, finder activation, shared-edge change or DNS change was performed.

- Account `944327601374`, region `us-east-1`, running instance
  `i-0df5dfaabc889f576`, `t3a.large`, Elastic IP `34.232.192.13` verified live.
- Project `/opt/linkyoh`, Compose project `linkyoh`, alias `linkyoh-web` retained.
- New web image:
  `sha256:e252a3ce5593b3f43da9f84b445e43afbcd1b589fa225272ca839d8f7995d9c0`.
- Existing Python 3.9.25 / Django 3.2.20 / redis-py 4.5.5 / psycopg2 2.8.5
  runtime layers retained from
  `sha256:811a1128956bfddcdd227427e64fb807c06d180c6fdc9b9b36dd68a985e90202`.
  Only exact committed source was overlaid; no dependency upgrade or env file
  entered the new build context. All 306 packaged files match the commit in the
  image and deployed tree. Older remote test files were preserved in backup.
- All 24 tests passed in this actual amd64 runtime against synthetic SQLite and
  a separate disposable Redis. No production env/database was used for tests.
- Production migration plan was empty; release startup had no migrations to
  apply. Collectstatic copied 161 files and post-processed 191; public new CSS/JS
  byte-match source. Existing duplicate admin-static and Gunicorn buffering
  warnings remain, with no startup failure.

## Proxy And Limiter

Inspected `edge` has CIDR `172.20.0.0/16`; the only ingress Caddy container has
address `172.20.0.2`. **LYTRUSTED_PROXY_NETWORKS=172.20.0.2/32** pins the actual
proxy rather than trusting every other app on that bridge. No all-address range,
private-network blanket or client-supplied address was used. Re-inspect this value
if the edge container is recreated or its address changes; do not widen it as a
shortcut. `/opt/edge/Caddyfile` and the running Caddy container were unchanged.

`linkyoh-directory_limits-1` uses the already-present Redis image pinned at
`redis@sha256:6ab0b6e7381779332f97b8ca76193e45b0756f38d4c0dcda72dbb3c32061ab99`.
It joins only `linkyoh_linkyoh_network`, publishes no ports, has a 64 MiB / 0.25 CPU
cap, a 16 MiB key budget, expiring counters and disabled RDB/AOF persistence.
Health is `healthy`, restart count zero; observed memory about 5.6 MiB.
The existing env bytes are unchanged except the new trusted-proxy setting.

Live HTTPS proof: 32 HEAD requests across apex/www with changing forged XFF
headers and alternating user agents completed in 4.78 seconds: **30 HTTP 200,
2 HTTP 429**. A further forged header remained 429 with `Retry-After: 6`,
`Cache-Control: no-store` and noindex. An independent source IP returned 200 while
the first was limited; login, robots, llms, sitemap and CSS remained 200. The
limited IP recovered to 200 after the window. Runtime confirms 30/10s and
120/60s; sustained-window and bounded Redis-failure 503 behavior passed in the
isolated image tests, not through a deliberate production outage.

This is app-layer limiting. Shared-edge limiter-module work remains separately
gated. Real carrier/shared-NAT traffic and sustained capacity remain operational
observation items, not claims established by this bounded QA burst.

## Public And Neighbor Evidence

Evidence directory: `evidence/release-20260913/`; `manifest.json` hashes 26 files.
Includes source manifests, actual image proof, before/after container snapshots,
runtime/trust/backup proofs, HTTPS and limiter reports, discovery assertions, six
browser-page records and twelve screenshots.

- Nine public routes returned 200 before and after: Linkyoh apex/www, WOP health,
  n8n, Payments, National Perspective, Rybbit health, MarketDay and Yardsale.
- All **22 neighbors** retained container ID, image, start time and restart count
  during Linkyoh's switch, including Linkyoh Celery/Beat/RabbitMQ and shared Caddy.
  Payments had completed its independent switch before this cutover baseline.
  MarketDay was told our switch finished before its own authorized release.
- Caddy configuration SHA-256 stayed
  `e513d8cf3545ba9cbf36663841e6926b670e5e1f433d1d7d57d1ab72fd52784b`.
- Home, AI-admin provider profile and GraceKennedy gig loaded at 390/944px with
  zero JavaScript errors or broken images. Strip order, seven links/two inactive
  labels, UTM/data-track, 44px targets, keyboard focus, banner and social image
  200s passed. Rybbit was blocked/stubbed; no live analytics-ingestion claim.
- Live Organization sister links and LocalBusiness/Service schema passed;
  robots AI/private rules, llms, sitemap and category page passed. Legacy gig,
  profile and category URLs still return 301 to their canonical routes.
- Existing provider layout overflow is still visible (399px body at 390px for
  this live profile); the new strip fits. Prior baseline proof and the revamp
  issue remain in `verification.md` and `REVAMP.md`. No redesign was attempted.
- Host reserve gates passed. After verification: about 2.3 GiB RAM available,
  1.8 GiB swap free and 13 GiB disk free; web about 171 MiB. Preflight CloudWatch
  five-minute average CPU ranged 25.5-34.2%, maximum sample 52.6%.

No listing, provider or account mutation was submitted, no external messages or
orders were sent, and no other property's code was changed. Public reads may
exercise pre-existing visit/statistics behavior.

## Operations And Rollback

Active Compose source is the exact commit plus the app-local image-pinning file
`/opt/linkyoh/docker-compose.release.yml`. Subsequent operations should use both
`-f docker-compose.aws.yml -f docker-compose.release.yml`, the existing `.env`,
and explicit service names; never recreate the edge or unrelated dependencies.

Immediate rollback image is retained as `linkyoh-web:rollback-pre-6b62c61` with the
full old digest above. Root-only source/config and static-volume archives are at
`/opt/linkyoh/releases/6b62c61-20260913/`. Matching mode-0600 off-host copies are
outside this Git repository in
`/Users/cristiansilva/WorkSpace/Linkyoh/.release-backups/6b62c61-20260913/`.
Their checksums are in `backup-checksums.json`. Review retention on 2026-09-27.
No RDS/S3 restore or new cloud snapshot was needed for this no-schema app update.

If rollback is needed, first inspect for subsequent releases and env rotation.
Restore the old app files/Compose and pin the old image; preserve current secrets
and revert only this release's proxy-trust addition if appropriate. Recreate only
web with `up -d --no-deps --no-build web`, recollect the prior image's static files
or restore the retained static archive, and verify public/neighbor health. The
unused private limiter may stay running until a reviewed cleanup. Do not roll
back the database, run Compose down, or blindly restore an old env after rotation.
The deployment controller's automatic rollback was prepared but not exercised:
this successful release required no rollback.
