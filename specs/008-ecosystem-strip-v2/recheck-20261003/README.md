# Live Strip v2 Verification

Verified 2026-10-03. Project **Linkyoh**, task **Linkyoh Agent 1**
(`019e419a-d141-7f12-9853-1711359a3900`). This is the current hub-requested
navigation verification, not a repeat of the September UI/Kev deployment.

Application source remains `60d5af730c9844261b2a661dadb9ee42d98ee7c9`.
At preflight the UI branch and its remote both pointed to documentation commit
`916e49f52ae6537e9c32fc036aa7e943a9edd0c7`; no application changes since
`60d5af7` and no tracked worktree changes were present. Existing untracked files
were preserved. No new application candidate was created.

## Current Evidence

- Public Home: <https://linkyoh.com/>.
- Public provider: <https://linkyoh.com/belize/providers/linkyoh-ai-admin-218/>.
- Published hub HTML validates all ten destinations in the specified order,
  Games last, with original destination events. HTML hash:
  `d8ee28f64288652a04cf06b245f69e7f2924a88bac842f78c3cc901e8dd8a22a`.
- Hub full Lab CSS and live Linkyoh copy match committed source; live scoped
  strip CSS and the existing analytics dispatcher also match source bytes.
- All ten canonical roots and all ten Linkyoh-attributed destination URLs
  return 200 on the expected hosts without redirects.
- Twelve Home/provider EN/ES views at 320, 390 and 1440px pass: v2 marker,
  order, canonical Visit Belize, `utm_source=linkyoh`,
  `utm_medium=ecosystem`, `utm_campaign=strip`, destination event names,
  minimum 44px strip targets, noreferrer and no horizontal overflow.
- Both pages retain the translated MarketDay forward banner, correct root,
  source/medium and separate `utm_campaign=forward` attribution.
- Twenty-four real keyboard activations (all ten Home strip links plus
  Home/provider banners in EN/ES) have visible focus, a native GET navigation
  request without Referer, and exactly one bounded Rybbit event through a
  stub. Navigation destinations were intercepted with inert receipt pages;
  the separate HTTPS checks establish actual destination reachability.
- Two no-JavaScript journeys verify opening/closing the mobile menu and
  actual native self-link navigation. No page errors or attempted writes.
- Thirty-six screenshots are retained here: `{home,provider}-{en,es}-
  {320,390,1440}.png`, plus `-strip.png` and `-forward.png`. Mobile and desktop
  strip and Spanish mobile banner screenshots were visually inspected.

Machine-readable evidence: [report.json](report.json). Reproduction:

```sh
/Users/cristiansilva/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node specs/008-ecosystem-strip-v2/recheck-20261003/verify.mjs
```

## Routing Findings

1. From Spanish Linkyoh, the strip's Linkyoh self-link drops `lang=es` and the
   actual destination renders English. Verified by native no-JS navigation.
2. From Spanish Linkyoh, the strip's Silvatech link targets the English root;
   the Spanish hub at <https://silvatech.bz/es/> is available and renders `es`.

These are locale-continuity limitations, not broken destination/UTM/event
contracts. The current canonical reference uses those root URLs. A follow-up
needs a reviewed locale-routing contract and a separately approved application
release; no links were silently changed during this verification-only pass.

## Scope And Gate

No app implementation, push, deployment, restart, host window, SSH/RDS query,
listing/claim update, WOP/A2A binding, campaign, modernization or other-property
code change. Real analytics was suppressed; dispatch proof is not ingestion
proof. Public GETs may exercise existing view counters. September immutable
image/test/neighbor evidence remains historical and was not rerun here.

During initial scope reconciliation an old local AWS CLI invocation failed
before execution with `bad CPU type in executable: aws`; no cloud or host
operation followed. It was not needed for this public navigation verification.
The older UI/Kev request and its completed release are not authority for new
production work.

This is non-behavioral evidence under existing Spec 008, so no new feature
specification is required. Only this directory is committed locally. Shared
ledger changes belong to the hub owner. This report describes the pre-fix
baseline only. The subsequent hub receipt at 2026-10-03T11:37:13Z records
Cristian's explicit one-batch authorization for scoped locale fixes and release;
Spec 008's dated amendment governs that follow-up. Existing claims, runtime
and campaign gates remain unchanged.
