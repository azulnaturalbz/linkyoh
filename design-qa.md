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
