# Slice 3: Lab discovery and profiles

Owner approval: Cristian, 2026-09-13. Subordinate to REVAMP.md and the canonical
ecosystem ledger. Approved visual reference: revamp-prototype at 3988d72.

## Contract

- Home, results, category/subcategory lists, public provider profiles and service
  details use the approved light Lab layout, pinned hub CSS, Inter/Sora/Lucide.
- Checked appears on every listing card and provider header. Profile review
  boolean/date is only a profile review, not a phone/license/quality guarantee.
  Approved claims must match the current listing owner. updated_at is not a
  dedicated approval timestamp, so claim date stays unknown. PhoneVerification
  has no durable owner binding or confirmed_at: phone scope stays unknown.
  Staff importer verification never verifies the advertised business.
- Smart GET search uses existing taxonomy/geography records, bounded EN/ES aliases,
  unmatched text, explicit-filter precedence and honest ambiguity/empty states.
  Multi-area district/town pairs must refer to the same coverage record. Tonight
  indicates urgency, never availability. Existing param/location queries work.
- Django i18n uses a lang=en/es selector without changing canonical URL shapes.
  Original provider facts/names are not automatically translated.
- One finder component defaults to GET. Reviewed configuration later selects
  WOP's verbatim v2 iframe instead, retaining search; no invented initial-message
  API or second iframe input. No endpoint is enabled in this slice.
- Real WhatsApp/public phone contact, share/QR, reviews, likes, messages, profile
  editing and existing claim entry points remain reachable. Quote capture and
  WOP leads inbox stay gated, with honest direct contact fallback.

## Exclusions and compatibility

No Python dependencies, schema, claim/account transitions, production data,
campaigns, runtime/edge configuration, other property code or deployment changes.
Modernization stays separate. Existing SEO helper, OG, canonicals, legacy 301s,
sitemap and private surfaces stay intact. Existing profile editor is retained.
No payment/idempotency behavior changes; no external lead/message submissions.

## Stitch reconciliation, 2026-09-13

Cristian supplied Stitch project 15344324354844864865 during implementation and
authorized taking its strongest choices into the approved UI, then sharing back.
Source review: full-page Home, high-contrast Results and Provider previews.
Adopt icon-led category shortcuts, mobile bottom navigation with safe-area space,
and compact labelled provider facts. These are presentation-only additions.
Keep the approved ask-first hero, light Lab tokens/fonts, real Checked evidence,
canonical links and WhatsApp-first contact. Do not copy generic Verified/Open Now
claims, placeholder links, a map with invented coordinates, broken source images,
or the source's competing navy/orange palette. Preserve the original Stitch work;
use a remix for the reviewed synthesis. Capture revised EN/ES matrix again.

## Acceptance

Tests cover parsing (EN/ES, Unicode, bounds, ambiguity, invalid/filter conflicts,
multi-area pairing, pagination), evidence privacy/scopes, routes/SEO, no endpoint
by default, locale switching and existing regressions. Capture Home/Results/
Provider/Gig/Category/Subcategory in EN/ES at 320/390/768/944/1440; no horizontal
overflow, broken images or browser errors. Test real GET without JS, keyboard
menus/filters/links, contrast, mobile actions and dependency-file parity.
