# Sitewide Lab review

Owner request: 2026-09-13 Belize time. Verified locally 2026-09-14 UTC on
`codex/005-linkyoh-revamp-ui`. **Approved for app-only deployment on 2026-09-13
Belize time; release verification is recorded separately in `release/README.md`.**
This extends approved slice 3; it does not start claim slice 4 or modernization.

## Review

Preview: http://127.0.0.1:8098/ with the actual production taxonomy/geography and
explicitly synthetic provider/account records. Local-only sign-in: `qa-provider`,
password `Local-review-only-2026`. These credentials have no production use.

- [Home, 390px](evidence/home-en-390.png)
- [Sign in, 390px](evidence/login-en-390.png)
- [Listing editor, Spanish/no-JS](evidence/form-es-nojs.png)
- [Profile editor, Spanish/320px](evidence/profile-edit-es-320.png)
- [Notifications, Spanish/320px](evidence/notification_list-es-320.png)
- [About and new banner, desktop](evidence/about-en-1440.png)
- [FAQ, Spanish/390px](evidence/help_faq-es-390.png)

Shared Lab navigation/footer now covers accounts/password lifecycle, profile and
listing management, claims, messages, notifications, help and information/legal
pages as well as discovery. Consistent fields, buttons, Lucide icons, focus states
and responsive layouts replace conflicting legacy defaults. Notifications now
render in the correct template block; conversation navigation and message POSTs
have native fallbacks, with failed AJAX sends retaining the draft and showing an
error. Successful sends clear the draft only after a successful response.

Main category/district and dependent options are rendered before JavaScript runs.
HTMX still narrows dependent choices; edit selections and invalid form input remain
visible. The smart parser recognizes production labels such as `Plumber`,
`Belmopan City` and `San Ignacio and Santa Elena Town`, including common EN/ES
short forms. No reference names or IDs were changed to fit the UI.

## Evidence

- **64 tests passed**, PostgreSQL 18.4 and isolated Redis, existing local
  Python 3.9.25/Django 3.2.20 application image with a local source bind mount.
  [Raw test log](evidence/postgres-tests.log).
- Django system check passes; migration dry-run reports no changes. Runtime
  dependencies, models/forms, migrations, URL patterns and SEO helper are unchanged.
- [370 responsive checks](evidence/qa-report.json): 37 route/states, EN/ES,
  320/390/768/944/1440px; no detected overflow, broken local images, page errors or
  sampled text-contrast failures. Some legacy routes redirect to the current view.
  Viewport captures are `{route}-{language}-{width}.png`, plus 390px full-page files.
- [Four keyboard/no-JS journeys](evidence/journeys.json): skip link, native mobile
  menu, smart GET/shareable URL/empty state, taxonomy dropdowns, listing steps,
  profile editor and FAQ navigation. [Eight message checks](evidence/messages.json)
  cover EN/ES, JS/native POST and draft recovery via intercepted responses.
- [Exact local reference parity](evidence/reference-parity.json) covers every
  exported field, ID and relationship; [data audit](reference-audit.md).

The large screenshot set is excluded from the application Docker build context.
All accounts, claims and provider photos in these captures are synthetic fixtures.
Rybbit and the external QR image service were stubbed; other external browser
requests were blocked. No provider, email, SMS, WhatsApp or WOP lead was contacted.
Tests do not certify QR decoding, S3/CDN delivery, production behavior, Safari,
screen readers, all WCAG criteria or every form submission combination.

## Brand and language

[Asset provenance](brand-review/README.md). The preview uses the actual black
linked-chain wordmark from Stitch `Title-2.png`, at a bounded responsive size;
the alternative blue mark is retained as design provenance. Cristian accepted
the current preview for this release on 2026-09-13 Belize time. The new banner is illustrative
brand artwork, not a photo proving anything about a real provider. User-uploaded
provider media is untouched. The favicon and existing OG/social-image contract
are deliberately unchanged pending the final brand/release review.

Discovery/provider pages retain Django EN/ES. Shared navigation, account forms and
core editor/help/notification controls gained reviewed translations. Long legacy
help articles, legal copy, some field help text and provider-authored facts remain
in their source language; this is not a claim of complete sitewide translation.

## Reproduce

Use the existing Python environment; do not add packages to the UI branch.
Create a fresh reference snapshot only with read-only production authorization and
the guards in [export_reference_data.py](export_reference_data.py). Keep it outside
Git, directory mode 0700/file 0600. The current private snapshot path is documented
in the data audit. `preview.py` migrates a new disposable SQLite database and
refuses to import over existing user/reference records.

```sh
/tmp/linkyoh-ecosystem-venv/bin/python specs/007-sitewide-lab/preview.py /Users/cristiansilva/WorkSpace/Linkyoh/.reference-snapshots/linkyoh-reference-20260914.json
node specs/007-sitewide-lab/qa.mjs
node specs/007-sitewide-lab/journeys.mjs
node specs/007-sitewide-lab/messages.mjs
```

The Node scripts accept `PLAYWRIGHT_MODULE` for an existing installation. Wait for
the preview to answer HTTP 200 before running them. Do not run QA against a public
host. PostgreSQL test reproduction uses the disposable network described in
`../005-lab-discovery/README.md` and `postgres_check.py`, never a production DSN.

The original local-review evidence above predates deployment authorization.
Cristian subsequently approved the current styling/wordmark and app-only release.
He named the generated plumbing character Kev for future Linkyoh marketing;
see `docs/brand/KEV.md`. Claim transitions, new Python dependencies, WOP embedding
and campaign activation remain outside this release.
