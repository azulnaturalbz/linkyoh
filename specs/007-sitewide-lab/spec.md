# Sitewide Lab completion

Owner request: 2026-09-13 Belize time. Continues slice 3 on the UI branch; it does
not authorize claim slice 4, WOP activation, dependency upgrades or deployment.

## Scope

Apply the approved Lab styling to all existing application surfaces: discovery,
accounts/password lifecycle, profile management, listing creation/editing/claims,
dashboard/my listings, messages, notifications, help, about/contact and policies.
Use shared navigation/footer, Inter/Sora, Lucide, accessible buttons/controls,
consistent spacing and mobile layouts. Preserve all forms, CSRF, permissions,
existing URLs/canonicals/OG, submissions and error states. No cosmetic admin
replacement or third-party payment-provider redesign; email branding is included
without changing delivery logic or message meaning.

Inspect and reuse the actual owner-supplied Stitch logo and suitable banner assets,
with explicit aspect ratios and mobile/desktop sizing. Do not infer a new logo
from a text label or overwrite real provider photos. System/default/promotional
banners can change; user-uploaded business media remains its owner's content.

Read production RDS through the existing app connection in a read-only transaction.
Export only allowlisted category/subcategory and Belize geography reference tables
(including dependent local/locality/district/country/type tables identified from
the model). No user, contact, message, claim or secret export. Snapshot outside
git, preserve IDs/relationships and report counts/integrity. Import only into an
isolated local preview database; never overwrite production or an existing local
database. Commit a safe importer/exporter and aggregate evidence, not a DB dump.

## Acceptance

Inventory all routed template surfaces and exercise representative public and
authenticated states in EN/ES at 320/390/768/944/1440px. Test form validation,
keyboard/no-JS navigation, dependent dropdowns, logo/banner fit, contrast,
overflow and existing regression suite. Production lookup counts must agree with
the isolated local copy. Unknown facts stay unknown. No provider/email/SMS send
during QA. Record data/asset provenance, commit and HOLD before deployment.
