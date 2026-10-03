# Locale-Preserving Ecosystem Navigation

Authority: Cristian's one-batch strip/navigation release approval, recorded in
the ecosystem ledger at 2026-10-03T11:37:13Z. This is not a new UI, Kev,
dependency, claim, campaign or WOP activation release.

The pre-fix live baseline is retained in `../recheck-20261003/`. Spanish strip
self-navigation returned English; the hub and Powered by links also discarded
the selected language. A fixed-destination template tag now preserves supported
language routes and merges attribution without duplicate parameters. Canonical
schema identities, CSS, tracking events/dispatcher and forward banners are unchanged.

## Local Evidence

- `evidence/runtime.json`: 70 tests pass on existing Python 3.9/Django 3.2
  with isolated PostgreSQL/Redis; source mounted read-only. Not image proof.
- `evidence/local/report.json`: Home/provider EN/ES at 320, 390, 768, 944 and
  1440px, 20 views/60 screenshots, 28 keyboard single-event checks and two
  no-JavaScript journeys pass. No page errors or horizontal overflow detected.
- All 20 actual rendered EN/ES strip hrefs reach meaningful public pages with
  attribution retained and a return-to-hub link. All ten roots and attributed
  baseline links also return HTTP 200. Real analytics and POSTs are blocked.
- Spanish destinations: hub `/es/`; Visit Belize, Linkyoh, WOP, Consulta and
  Belize Logistics `?lang=es`. Other products retain their existing root;
  translations are not invented. WOP visibly translates but its inherited
  document language remains `en`; that is an owner follow-up, not edited here.
- Synthetic local preview uses a disposable SQLite database, not production
  credentials/data. Public verification only performs GET/HEAD requests.

## Release Gate

Local changes are ready; immutable packaging, image tests, fresh serialized
shared-host admission, protected rollback custody, web-only release and live
verification remain pending. Payments owns the first October 3 host window.
No database migration, dependency installation or shared-edge change is needed.
