# Linkyoh Lab design QA

2026-09-13 decision; evidence refreshed 2026-09-14 UTC. UI branch only.

## References and translation

Primary approved source: `specs/revamp-prototype/` at `3988d72`.
Additional owner-supplied reference: Stitch project `15344324354844864865`, Home,
Results and Provider screens inspected in Chrome. Captures and reconciliation:
`specs/005-lab-discovery/stitch/`.

Preserved the approved unframed ask-first light layout, pinned hub Lab stylesheet,
Inter/Sora, Lucide, 16px listing cards, violet Checked region and WhatsApp-first
contact. Adopted the source's category shortcuts, bottom mobile navigation and
compact provider facts. Original source remains unchanged; its generic trust/
opening claims, placeholder links, fake map and broken media were not imported.

## Visual and interaction evidence

- Inspected final mobile Home/Results/Provider/Service, desktop Provider and the
  Spanish 320px Home / 944px Provider screenshots. Text and actions fit; mobile
  navigation reserves bottom space and respects the safe area. Category shortcut
  counts follow stored taxonomy, not decorative placeholders.
- Automated 320/390/768/944/1440 EN/ES matrix covers all six public page types.
  No detected horizontal overflow, broken images or browser errors. Provider
  name is separate from cover, check/date text wraps, action rows do not force
  cards wider and native filters collapse/expand without JavaScript.
- 6,064 visible text-contrast samples meet their applicable AA size threshold.
  White text is not used on brand-500 for primary controls. Focus indicators and
  skip/menu/filter/category/dock keyboard paths were exercised.
- Dynamic business facts remain original-language data; interface labels use
  Django gettext. Unknown evidence is explicit. Production templates contain no
  synthetic checks, photos or provider names from the design reference.

## Result and remaining gates

Targeted local QA passes. [Evidence and limitations](specs/005-lab-discovery/README.md).
This is not a full WCAG audit, screen-reader/Safari certification or production
release proof. WOP/claim transitions and dependency modernization are separate.
HOLD for Cristian's review and app-only deployment go.

## Sitewide extension, 2026-09-14 UTC

The owner's 2026-09-13 request extends the same styling to account, management,
inbox, help and informational pages. Shared Lab shell, correctly bounded original
Stitch wordmark, a new illustrative banner, local compatibility assets and core
EN/ES controls are implemented. No provider photos, SEO routes, claims or runtime
dependencies were changed. The black mark is the local review choice; the source's
blue alternative and unchanged social/favicon branding await final brand review.

Production taxonomy/geography was read under enforced PostgreSQL read-only access
and imported only into a fresh local preview: 5 categories, 439 subcategories,
6 districts, 244 Local/Location records and their Belize/type parents. Exact
field/ID/relationship parity passes; suspect existing classifications remain
unchanged and documented for editorial review.

Final evidence: 64 PostgreSQL/Redis tests, 370 EN/ES responsive route/state captures,
four keyboard/no-JS discovery/form journeys and eight message recovery/native POST
checks. No detected overflow, local-image failures, page errors or sampled contrast
failures. Manually inspected mobile auth/help/forms, narrow Spanish profile editor
and populated notifications, messaging, and desktop About/banner. This is targeted
Chromium QA, not full accessibility or production delivery certification.

[Review, reproduction, screenshots and limits](specs/007-sitewide-lab/README.md).
Long legacy help/legal prose is not fully translated. No external delivery,
production write, WOP activation, deployment or dependency upgrade was performed.
