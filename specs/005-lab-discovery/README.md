# Slice 3 evidence

Decision date: 2026-09-13. Local verification completed 2026-09-14 UTC.
Branch: `codex/005-linkyoh-revamp-ui`. **Not deployed.**

## Delivery

Approved Lab Home, Results, Provider, Gig, Category and Subcategory pages, Django
EN/ES catalogs, deterministic GET smart search, conservative Checked evidence,
wrapped provider actions and progressive native controls. Family-design additions:
real-category shortcuts, safe-area mobile dock and compact provider facts.
The old owner editor remains at the existing profile URL with `?edit=1`.

Modernization stays on `codex/006-linkyoh-modernization`, established at `c8c8126`.
No requirements, Docker runtime, models, migrations, URL patterns or SEO helper
changes. No WOP activation, claim transition changes, campaigns or deployment.

## Verification

- 54 tests passed on PostgreSQL 18.4 and private disposable Redis, using existing
  local image `linkyoh-web:latest` (`58a4ed1119f6`, Python 3.9.25 / Django 3.2.20).
  Source was bind-mounted read-only. This is runtime compatibility evidence,
  not a new immutable release image or production-data proof.
- `manage.py check`: no issues. `makemigrations --dry-run --check`: no changes.
- Browser report: [qa-report.json](evidence/qa-report.json), 66 views, 8 journeys,
  6,064 rendered text-contrast samples, no tested AA failures, overflow, broken
  images, unexpected external requests or browser errors.
- Six page types x EN/ES x 320/390/768/944/1440 = 60 matrix views; six extra
  JS/no-JS/empty states. Keyboard covers skip link, menu open/close/focus return,
  filters, canonical category shortcuts and mobile navigation.
- GET EN/ES needs parse to actual synthetic records, persist locale, open detail
  and work without JavaScript. Model-level tests cover invalid/ambiguous filters,
  paired coverage, hidden records, bounded queries, pagination, scope/owner/date,
  legacy routes/canonicals, owner editor permissions and plain/HTMX likes.

Test logs include expected image-processing warnings from older tests' missing
fixture defaults and the deliberate Redis-unavailable test. The browser fixture
seeds its defaults, so these are not broken-image browser findings.

## Screenshot index

Full-page and viewport pairs use
`evidence/{page}-{language}-{width}.png` and `*-viewport.png`.
Pages: home, results, provider, gig, category, subcategory; languages: en, es.
Use viewport captures to inspect the fixed mobile dock: full-page captures keep
fixed elements at their viewport position, not the bottom of the expanded image.

| Surface | EN mobile | ES mobile | Desktop |
| --- | --- | --- | --- |
| Home | [390px](evidence/home-en-390-viewport.png) | [320px](evidence/home-es-320-viewport.png) | [1440px](evidence/home-en-1440.png) |
| Results | [390px](evidence/results-en-390-viewport.png) | [390px](evidence/results-es-390-viewport.png) | [1440px](evidence/results-en-1440.png) |
| Provider | [390px](evidence/provider-en-390-viewport.png) | [944px](evidence/provider-es-944-viewport.png) | [1440px](evidence/provider-en-1440.png) |
| Service | [390px](evidence/gig-en-390-viewport.png) | [390px](evidence/gig-es-390-viewport.png) | [1440px](evidence/gig-en-1440.png) |

## Reproduce locally

Use the existing project-compatible Python environment; no UI runtime packages
are added. The preview always selects `linkyoh.ecosystem_test_settings`, creates
a fresh temporary SQLite database and uses synthetic records/prototype artwork.
Never point this script at production data.

```sh
/tmp/linkyoh-ecosystem-venv/bin/python specs/005-lab-discovery/preview.py
node specs/005-lab-discovery/qa.mjs
```

Preview: `http://127.0.0.1:8097`. The QA module defaults to the installed Codex
Playwright runtime; set `PLAYWRIGHT_MODULE` to another installed module path.
For PostgreSQL, `postgres_check.py` is exclusively for a disposable container
network with local PostgreSQL 5432 and Redis 6379. It does not read production
credentials. Existing Docker image test command:

```sh
docker run --rm --network container:linkyoh-lab-qa-redis \
  --mount type=bind,source="$PWD",target=/linkyoh,readonly \
  --workdir /linkyoh --entrypoint python linkyoh-web:latest \
  specs/005-lab-discovery/postgres_check.py
```

## Limits and release gate

This is targeted Chromium contrast/interaction QA, not full WCAG certification,
screen-reader testing, Safari testing, production-volume load testing or hosted
acceptance. Analytics is stubbed, QR service returns a test pixel, and all other
external browser requests are blocked; no provider was contacted. QR decoding,
real S3 media and analytics ingestion require separately authorized release QA.
Synthetic contacts are non-delivery examples, not real business details.

The WOP gate remains closed. Unsupported phone verification, approval timestamps,
exclusions and availability remain unknown. Quote CTA opens WhatsApp with editable
text and sends nothing automatically. Claims/leads require later slices.

Cristian's next go is required before shared-host app-only deployment. Recheck
ledger ownership, neighbor health, immutable image/source, recovery and public
routes then; these local checks do not replace the release procedure.
