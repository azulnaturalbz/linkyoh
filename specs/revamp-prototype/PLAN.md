# Static prototype plan

Owner decision: REVAMP.md approved with amendments, 2026-09-13. This artifact is
subordinate to REVAMP.md and the canonical ecosystem ledger, not a second strategy.
Scope: Home, Results, Provider, EN/ES; Pros and quote previews within those pages.

The repository AGENTS.md requests Spec Kit, but neither `.specify/` nor its skills
is installed in this checkout. Do not bootstrap tooling or change project rules
for a static review. Use the owner-requested REVAMP.md as the specification and
this bounded plan/checklist as its implementation and acceptance artifacts.

## Implementation

1. Pin the published hub stylesheet; reuse licensed Inter/Sora and local Lucide.
2. Build static HTML from shared page functions and bilingual fixture data with
   Node's standard library only. No application/Python changes or dependencies.
3. Add responsive light-surface CSS; use 390px reading order at 1440px.
4. Add local-only GET query/filter simulation, locale links, provider photo viewer,
   quote preview with unchecked consent and Pros workflow previews. No API calls,
   local storage of contact details, real phone numbers or analytics.
5. Exercise twelve required page/language/width combinations, keyboard, filters,
   empty states, no-JS navigation, images/fonts, contrast and consent behavior.
6. Capture screenshots, document evidence, commit only owned prototype/spec files,
   update own ecosystem record/row and append handoff. HOLD for prototype review.

## Acceptance checklist

- [x] Amended approval recorded; separate UI-first/upgrade branches/releases.
- [x] Spec amended before prototype code.
- [x] Published CSS pinned with provenance and checksum.
- [x] Six primary localized documents, plus per-fixture provider variants.
- [x] Search/filter/back/locale/no-match behavior demonstrated.
- [x] Evidence-scoped Checked states and explicit fictional-data notice.
- [x] Provider photos/areas/do/don't, quote consent and Pros previews.
- [x] Twelve required full-page screenshots, viewport variants and state captures.
- [x] 41 rendered page/state checks and 19 journeys; zero tested AA text failures.
- [x] No Django/runtime, database, claims, endpoint or deployment modifications.
- [x] Canonical handoff recorded; prototype-only commit; HOLD for owner review.
