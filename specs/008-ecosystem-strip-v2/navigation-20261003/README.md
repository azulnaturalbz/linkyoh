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

Source `b5d8d4a45f4db7727a6185fe970196bd8915f306` is pushed on
`codex/005-linkyoh-revamp-ui` using the existing azulnaturalbz credential without
changing the active global account. Image
`sha256:089c44e44f6d80c2f9a1857131394c2b7121fa04774d60a27fa69765167c2861`
passes all 70 tests without an application-source mount; 358 files match Git,
Python remains 3.9.25 and Django 3.2.20. Fourteen release/rollback/window tests
pass. Exactly four application files differ from the live60d5af7 package,
including tests. The old immutable image remains available for rollback.

Fresh serialized shared-host admission, protected rollback custody, web-only
release and live verification remain pending. Payments owns the first October3
host window; MarketDay is also queued. No database migration, dependency
installation or shared-edge change is needed. The local GitHub/AWS executables
were incompatible with this Mac's architecture; isolated current CLI binaries
were used, without replacing global tools or adding application dependencies.
GitHub's push reports 71 existing default-branch dependency advisories, including
two critical; this is not a fresh candidate vulnerability audit. The separately
gated dependency modernization remains necessary and is not bundled here.
