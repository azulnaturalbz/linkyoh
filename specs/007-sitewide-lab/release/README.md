# Sitewide Lab app-only release

## Authorization and scope

Cristian approved the latest UI and deployment on 2026-09-13 Belize time, recorded
2026-09-14 UTC. This supersedes the local UI/logo and deployment HOLD. Deploy the
committed UI branch, including Kev's unchanged marketing reference asset and brief.
The dependency modernization branch, claim slice 4, WOP endpoint, campaigns and
other properties remain outside scope.

## Plan and gates

- [ ] Freeze exact committed runtime files; preserve the existing dependency image.
- [ ] Re-run tests in that runtime with disposable PostgreSQL/Redis only.
- [ ] Verify live source baseline, empty migration plan, actual proxy trust,
  private limiter, capacity and all neighbors before mutation.
- [ ] Hold existing shared release and Linkyoh secret-refresh locks; retain
  source/config/static backups on host and verified private off-host copies.
- [ ] Pin new image and recreate only `web`, using both existing Compose files.
- [ ] Check public EN/ES pages, assets, canonical/legacy/schema/crawl contracts,
  responsive and no-JS/keyboard behavior; compare neighbors/config/firewall.
- [ ] Record source/image identity, evidence and final ledger handoff.

No schema or dependency change is expected. No production fixture import or
reference-data rewrite is allowed. Existing read-only source/reference evidence
remains in the parent spec; public reads can exercise existing view counters.
The previously verified 64 PostgreSQL/Redis tests and 370-view local QA matrix
remain the wider regression evidence. Live checks must be bounded below limiter
thresholds and must not submit contact/claim/account forms.

## Rollback contract

Retain current live image `sha256:e252a3ce5593b3f43da9f84b445e43afbcd1b589fa225272ca839d8f7995d9c0`.
Under the same locks, restore only owned source/static changes and the prior
image-pinning file; recreate only web. Do not restore an old secret file over
rotation, restore RDS, run Compose down, restart Redis/workers, change the shared
edge or alter firewall rules. Verify restored public health and unchanged
neighbors. On uncertainty, preserve the journal and stop further mutations.
