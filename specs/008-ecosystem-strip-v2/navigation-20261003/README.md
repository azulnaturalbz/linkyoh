# Locale-Preserving Ecosystem Navigation

**HOLD: capacity; window released 2026-10-03T14:19:12Z.** Source is committed
and pushed, candidate image is staged, but this navigation fix is not live.
Production remains source60d5af7/image778630b95827. No additional deployment
approval is missing; fresh safe admission and the remaining release gates are.

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
Python remains 3.9.25 and Django 3.2.20. Fifteen release/rollback/window tests
pass. Exactly four application files differ from the live60d5af7 package,
including tests. The old immutable image remains available for rollback.

The coordinated Linkyoh window began14:03:32Z after Payments/MarketDay DONE,
with WOP queued next. Initial101-sample admission passed at minimum RAM
2,547,802,112 bytes and disk8,215,732,224 bytes; maximum recent five-minute CPU
average33.39%, minimum credits664.66 and no new swap-out. Staged image/source
transport checksums match. This is staging, not deployment.

At14:13Z the immediate preflight guard refused available RAM below
2,415,919,104 bytes (2GiB reserve plus the temporary256MiB check-container
ceiling). No preflight container, backup or cutover started. A subsequent
read observed2,325,508,096 bytes. All25 existing container identities, images,
starts, restart counts and health match the initial admission. Original refusal
is preserved in `evidence/preflight-refused.txt`; the one bounded post-stage
101-sample observation is recorded separately rather than replacing admission.
No guard relaxation, cache drop, resize or neighboring restart is permitted.

The separate post-stage101-sample check also failed: minimum available RAM
2,200,977,408 bytes, minimum free disk7,740,551,168 bytes, no extra swap-out,
all25 container records unchanged. Final14:18:53Z locked read verifies all357
live source hashes against60d5af7, the old running image, healthy private64MiB
Redis and actual Caddy172.20.0.2/32 trust. All13 HTTPS/crawl checks, three legacy
301s, three static byte comparisons and three OG images pass after refusal.
No backup/cutover marker exists and no rollback was necessary. See
`evidence/{admission-post-stage,hold-proof,public-after}.json`.

The staged artifacts remain under `/opt/linkyoh/releases/b5d8d4a-20261003/` and
the owned transfer directory `/tmp/linkyoh-navigation-b5d8d4a/`. These are not
rollback backups. All locks held by completed commands are released; WOP is
next in the shared-host queue and must take its own fresh gates. Resume only
with a new bounded admission/evidence attempt, verified staged hashes, current
neighbor baseline and protected on/off-host backups. Do not blindly replay
the create-only staging operation or overwrite either capacity observation.

Protected rollback custody, web-only release and live verification remain
pending. No database migration, dependency installation or shared-edge change
is needed. The local GitHub/AWS executables
were incompatible with this Mac's architecture; isolated current CLI binaries
were used, without replacing global tools or adding application dependencies.
GitHub's push reports 71 existing default-branch dependency advisories, including
two critical; this is not a fresh candidate vulnerability audit. The separately
gated dependency modernization remains necessary and is not bundled here.
