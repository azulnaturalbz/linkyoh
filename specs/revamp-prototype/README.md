# Linkyoh revamp prototype

**HOLD for Cristian's prototype review. No Django template implementation yet.**
Spec decision: APPROVED WITH AMENDMENTS, 2026-09-13. See [REVAMP.md](../REVAMP.md).

## Open

Open [Home](index.html), [Results](results.html) or [Provider](provider.html).
The EN/ES control switches language and preserves supported search parameters.
Spanish entry points: [Inicio](es/index.html), [Resultados](es/results.html),
[Proveedor](es/provider.html). Each card opens its own fixture provider; the maker
variant is [Pine & Plane](provider-pine.html), with two-photo gallery and MarketDay
banner. The unknown-check example is [Westside](provider-west.html).

These are static documents; no application or server is required. For a browser
that blocks local file URLs, `node specs/revamp-prototype/serve.mjs` starts a
temporary, read-only loopback preview restricted to this directory. It exposes no
API or production data, and rejects writes and paths outside the prototype.

## Review journeys

1. Ask for `plumber in Cayo` / `plomero en Cayo`: two sample matches. Try
   `carpenter in Belmopan` / `carpintero en Belmopán`: one maker. Unknown service
   returns an honest empty state. `tonight` / `esta noche` never implies availability.
2. Expand filters, choose district/town/service, apply, change language, use Back
   and clear. URLs use GET `q`, `category`, `district`, `town`. Mobile results keep
   filters collapsed until requested. Desktop uses the same controls inline.
3. Inspect Checked scopes/dates, partial and missing checks. Open a provider's
   explanation, photo viewer, WhatsApp preview and quote form. Consent is required
   and unchecked; review/edit/local lead status are usable. Closing clears contact
   input. Nothing is sent or stored.
4. Open Linkyoh for Pros: Claim, Verify, Manage. Inspect pending review, profile
   editor preview, leads inbox/detail and the future WhatsApp opt-in control.
   Keyboard arrows move through tabs. No account, claim, verification or lead is
   created. A sample inbox is not a WOP integration.

## Truth and activation boundaries

- All three business identities and check records are **fictional fixtures**,
  visibly labelled on every page. Dates demonstrate scoped evidence rendering;
  they do not verify real people or businesses. No ratings, contact numbers,
  licensing, availability or nationwide coverage are invented for live records.
- The plumbing illustration is AI-generated. Workshop photos are illustrative
  Unsplash images, not work by the named sample businesses. Real implementation
  must use sourced provider media and actual verification evidence only.
- Search parsing/filtering here runs over fixtures in JavaScript. The planned
  production implementation is **server-side Django GET parsing**, retaining
  existing `param`/`location` route compatibility while introducing reviewed
  aliases. This prototype does not claim SQL, API, i18n middleware or no-JS dynamic
  filtering is implemented. Static page content and ordinary links are readable
  without JavaScript; preview dialogs/filter simulation need JavaScript.
- No WOP script, endpoint key, API credential, telemetry, storage, service worker,
  or outbound form endpoint. CSP forbids connect requests. Ecosystem links are
  ordinary deliberate navigation, with the canonical UTM/data-track attributes.
- WOP `linkyoh` endpoint/origin/binding and real lead acceptance remain gates.
  The first UI release must use search/direct-contact fallback until reviewed
  quote transport is available. Claims stay slice 4; campaigns/deploys separate.

## Sources and reproduction

- Published hub CSS downloaded 2026-09-13 from
  [silvatech-ui.css](https://silvatech.bz/brand/silvatech-ui.css), SHA-256
  `1371df9a867ed7461a4021ae9b35535510792d051a7c7e1ccccca5c4d910de5f`.
  Byte-identical to the hub's local published source. `prototype.css` adds light
  surfaces without changing the six core Lab variables or shared strip rules.
- Inter/Sora WOFF2 and OFL licenses copied from MarketDay's released
  `static/fonts/ecosystem/`. No external font request.
- Lucide 1.8.0 bundled UMD, ISC license included; copied from the configured Codex
  runtime package, not a new app/package-manager dependency.
- `assets/plumbing.png` and `assets/pipe-repair.png`: original generated
  illustrative images, 2026-09-13; not evidence of real provider work.
- `assets/workshop.jpg`: [Unsplash wood workshop collection](https://unsplash.com/s/photos/wood-workshop),
  source image `photo-1582571881821-380713f48b29`.
- `assets/workbench.jpg`: [Yasamine June on Unsplash](https://unsplash.com/photos/a-workbench-filled-with-lots-of-tools-2PMdixMFvvU),
  source image `photo-1633419946251-6d8b5dd33170`.

Run `node specs/revamp-prototype/build.mjs` after changing page copy/fixtures.
It deterministically generates static EN/ES documents and local fixture JS.
Edit `prototype.css` / `prototype.js` directly for layout/behavior. Build/preview
use only Node's standard library. Python dependencies, Docker and Django files
remain unchanged on `codex/005-linkyoh-revamp-ui`.

## Verification: 2026-09-13

**PASS:** 41 rendered page/state checks and 19 interaction journeys. Zero browser
errors, failed images, horizontal overflows, external requests or tested WCAG AA
text-contrast failures (2,947 rendered text samples, including large-text thresholds).
This is contrast and targeted interaction evidence, not a full WCAG certification.
Primary action/focus colors were checked; normal placeholder contrast is 4.67:1,
white/violet button contrast 6.29:1, dark/WhatsApp green 9.80:1.

Required matrix: Home, Results and Provider x EN/ES x 390/1440px. Extra widths:
320/768/944px with Spanish's longer copy. Pros/quote/modal, claimed versus unclaimed
ownership, filter parsing/GET/back/locale, no-match, urgency, gallery, keyboard tabs,
menu collapse, consent-before-review and clearing contact data on close all pass.
No-JS proof is limited to static content and provider navigation; production
server-side filtering is still future work. No Django or database test is claimed.

- [Screenshot review gallery](evidence/index.html): 12 full-page captures with
  viewport counterparts, plus quote/Pros/empty states (40 PNGs total).
- [Machine-readable report](evidence/qa-report.json).
- Reproduce with the temporary loopback server above, then
  `PROTOTYPE_URL=http://127.0.0.1:PORT node specs/revamp-prototype/qa.mjs`.
  `PLAYWRIGHT_MODULE` can override the configured bundled Playwright path. This
  is development-only QA, not a new app dependency.

The in-app browser verified mobile EN/ES layouts and parsing against the restricted
loopback preview; file-URL navigation is blocked by that browser. Artifact capture
uses the same loopback-only static files. No production page or API was exercised.
