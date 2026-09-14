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
- [ ] Wait for Chillbout and queued WOP releases; coordinate own window.
- [ ] Fresh AWS/host capacity, source, actual proxy, configuration and neighbors.
- [ ] Backup image/source/static; hash-verify protected off-host copies.
- [ ] Read-only production check/migration plan, app-only switch and rollback guard.
- [ ] Public v2, CSS, llms/schema, SEO/legacy and responsive evidence.
- [ ] Neighbor/runtime preservation, commit/push, ledger closure and owner notices.

## Immutable Candidate

Image `sha256:778630b95827f791a3bc0c69eaf3326a99b400d6187b4bad2d3c859d75ce50fa`
is amd64, labelled with exact approved commit `60d5af7`. All 357 packaged
files match Git. The 67-test PostgreSQL/Redis suite passed inside the image
without an application-source mount; only the external test-runner helper
was mounted. Python 3.9.25 and Django 3.2.20 are unchanged. Receipt:
`evidence/image.json`; test log: `evidence/image-tests.txt`.
