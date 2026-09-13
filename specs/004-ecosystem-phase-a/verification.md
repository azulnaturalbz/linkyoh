# Phase A Verification

Verified locally on 2026-09-13 UTC. No production release, live rate-limit claim,
cloud change, provider/account modification or external lead/message submission.

## Results

- 24 Django tests passed against isolated SQLite and real disposable Redis 7,
  including all pre-existing import/profile tests and the new ecosystem tests.
- Redis checks cover concurrent bursts, multiple middleware instances, IP
  separation, spoofed forwarded prefixes, GET/HEAD, independent window expiry,
  429/Retry-After, Redis failure 503, and excluded API/account/text routes.
- Real Django HTTP requests confirm trusted edge IP separation across home,
  provider and gig routes, without bypass through a forged XFF prefix.
- `manage.py check`: no issues. `makemigrations --dry-run --check`: no changes.
- AWS Compose validates without loading the real env, with a synthetic trusted
  CIDR. New Redis is private to Linkyoh, capped at 64 MiB/0.25 CPU, with a 16 MiB
  expiring-key budget and no persistence/host ports. Existing edge alias remains.
- Existing canonical profile/legacy redirect and ingestion/image tests pass.
- Initial robots test exposed Python robotparser's first-match behavior; put
  private Disallow paths before Allow / for compatibility. Named agents repeat
  private exclusions rather than incorrectly relying on wildcard inheritance.
- HTML/data checks cover strip links, legal/powered-by/banner marks, crawl rules,
  llms public surfaces, sameAs, service-area fidelity and script-safe JSON-LD.

## Browser evidence

`evidence/browser-report.json` records six actual Chromium page loads: home,
provider and gig at 390px and 944px. All returned HTTP 200 with no page JavaScript
errors or broken images. Synthetic Example Plumbing records and existing Linkyoh
artwork were used; no real provider or account was edited. Analytics requests were
blocked, and the event API was replaced by a local capture stub.

Each page has seven active strip links and two inactive spans, in estate order.
New strip bounds fit both viewports, links retain 44px targets and keyboard focus.
Banner clicks emitted one `marketday_clickout` with source/placement only. Plain
anchors retain normal navigation when analytics is absent or fails.

Screenshots: `evidence/{home,provider,gig}-{390,944}-{forward,footer}.png`.
The local preview used http://127.0.0.1:8096 and was stopped after verification.

Known inherited issue: provider page width is 408px at a 390px viewport. Browser
inspection identified an existing `.btn.btn-outline-primary` with right edge
407.953px. Removing the strip, banner, new stylesheet and nav trademark still
leaves a 408px body. Recorded for the approved revamp; Phase A adds no overflow.
Home/gig fit both widths; provider fits 944px. This is not full accessibility QA.

## Reconciliation

Adopted hub `public/brand/ecosystem-strip.css` byte-for-byte. Started from
MarketDay's then-current `main/templates/components/ecosystem_strip.html` and
reconciled against the hub's published `public/brand/ecosystem-strip.html` nav:
the final nav matches exactly with only utm_source=hub changed to linkyoh.
MarketDay later added a template source variable and noreferrer for its tenant
context; Linkyoh keeps the canonical hub nav and its fixed property source.
CSS SHA-256: `4ddf53b7d4459f9b53c72d169c782bc14c785aa0241d7c5c0e190ffeea542425`.
The strip reference became available after Linkyoh claimed its row. Full Lab
`silvatech-ui.css` adoption remains in REVAMP.md, not Phase A.

## Reproduction

Use a disposable environment with the repository requirements, Django 3.2.20
and an isolated Redis instance, never the production env. This macOS ARM run used
Python 3.10.19, psycopg2-binary 2.9.10 as a local wheel override, and setuptools
80.10.2 for the old widget_tweaks import. Production requirements were unchanged;
the production Python 3.9 Alpine image was not built or deployed in this pass.
Tests log expected absent fixture-image warnings and the exercised Redis outage.

```sh
LINKYOH_TEST_REDIS_URL=redis://127.0.0.1:16389/0 python manage.py test linkyohapp --settings=linkyoh.ecosystem_test_settings --noinput
python manage.py check --settings=linkyoh.ecosystem_test_settings
python manage.py makemigrations --dry-run --check --settings=linkyoh.ecosystem_test_settings
LYTRUSTED_PROXY_NETWORKS=172.30.0.0/24 docker compose --env-file /dev/null -f docker-compose.aws.yml config --no-env-resolution --quiet
```

The CIDR above is test-only. Runtime trust must use the inspected edge network,
not a copied example or all-address range. No production env contents were read.

## Deployment gates

Cristian's go is required. Follow the canonical shared-host ledger, claim only
APP-LINKYOH, record current image/backup/capacity and neighbor health, verify real
edge topology and XFF behavior, and admit the 64 MiB cache budget before rollout.
Set LYTRUSTED_PROXY_NETWORKS from inspected topology; Compose deliberately refuses
an absent value. Validate build/collectstatic and app-only rollout/rollback. Verify
public home, provider, gig, sitemap, robots, llms and other shared apps afterward.

Limiter failure intentionally returns a temporary 503 for protected reads;
monitor cache health and 429/503 rates. Production thresholds are 30 requests/10s
and 120/60s per IP across directory routes, including authenticated readers and
crawlers. Carrier/shared NAT false positives must be checked with real traffic.
Do not allow-list callers merely by spoofable user-agent strings.

This is app-layer protection. Shared-edge HTML rate limiting from ecosystem
section 4.2 remains an edge-owner integration gate. No stock Caddy directive or
custom module was installed here, and no other property's code was changed.

Final product gate: HOLD, awaiting Cristian's sign-off on specs/REVAMP.md.
