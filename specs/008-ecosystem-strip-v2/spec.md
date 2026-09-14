# Ecosystem Strip v2

Date: 2026-09-14. Branch: `codex/005-linkyoh-revamp-ui`.
Authority: canonical SILVATECH-ECOSYSTEM.md v1.1 sections 1.1, 1.2, 2.3a and 6;
hub publication `e014da98b2d8938247988edd92e5dbdc51c99518`, Amplify job 52.
This is a consumer integration, not a new ecosystem strategy.

## Contract

- Consume the published HTML and CSS at `https://silvatech.bz/brand/`.
- Preserve the exact ten-link order: Silvatech, Visit Belize, Chillbout,
  Linkyoh, MarketDay, WOP, Payments, Consulta, Belize Logistics, Games.
- Every strip destination is an anchor. Include `data-strip-version="v2"`;
  use `utm_source=linkyoh`, `utm_medium=ecosystem`, `utm_campaign=strip` and
  each destination's published `data-track` key.
- Retain `rel="noreferrer"` to avoid disclosing private page URLs and the
  existing single analytics dispatcher. No client-side availability probes.
- Copy hub shared CSS byte-for-byte. Preserve Linkyoh's layered Lab styling.
- Keep the related-products and Organization identities consistent with the
  new Games sister URL. No other metadata, canonical or routing changes.
- An active link does not assert that a destination's gated features are ready.
  This supersedes v1 inactive-strip instructions, not any product HOLD.

## Boundaries

No Python dependencies, migrations, listing/provider/account/claim logic,
production data, credentials, endpoint embedding, campaigns or host changes.
No payments or write APIs are involved; payment/idempotency behavior is unchanged.
Existing links, forward banner, legal copy, translations, SEO and privacy remain.
Historical v1 evidence is not rewritten.

The hub handoff is not deployment authorization. Prepare and commit locally,
then HOLD for Cristian's explicit app-only deployment go. The previous UI
release remains live independently of this candidate.

## Acceptance

1. Published artifacts and vendored CSS have matching SHA-256 checksums;
   rendered Django strip matches hub navigation after attribution/privacy changes.
2. Ten ordered anchors have correct destinations, source, campaign and events.
   Games, Chillbout and Logistics dispatch once through existing analytics.
3. Home and private/public template paths retain the strip. Related products
   and Organization include Games exactly once.
4. Tests pass on the existing Django runtime with isolated PostgreSQL/Redis.
5. EN/ES at 320, 390, 768, 944 and 1440 pixels: ten usable links, no strip
   overflow, 44px targets, visible keyboard focus, AA text contrast and no-JS links.
6. Record local evidence, commit, update only Linkyoh's ledger slots and send
   the hub a contract-completion notice. Do not deploy.
