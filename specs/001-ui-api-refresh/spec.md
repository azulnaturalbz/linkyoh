# Feature Spec: Linkyoh UI Refresh And AI Listing Ingestion

## User Goals

- Make Linkyoh feel like a current, trustworthy Belize service and business aggregator rather than a dated gig-only marketplace.
- Fix the global navigation so it is coherent across desktop, tablet, and mobile, including reliable collapse behavior.
- Make buttons, search controls, dropdowns, footer social icons, and registration CTAs visible without hover and visually consistent.
- Preserve the existing HTMX/Alpine dynamic category, subcategory, district, and location behavior.
- Add a secure API path for AI/admin agents to create claimable business listings with images.
- Keep SEO/social sharing work intact: canonical URLs, Open Graph images, sitemap, and robots behavior must not regress.

## Scope

### In Scope

- Global CSS/design-system cleanup for color tokens, buttons, forms, Select2, navbar, category bar, footer, and mobile behavior.
- Base template markup updates for the top navigation, search, auth actions, category navigation, and footer copy.
- Homepage/search/register/about/gig/claim copy updates to align with the AI-assisted business aggregation strategy.
- Search filter markup repair and visual consistency.
- DRF API endpoint for authenticated staff/API-key imports at `/api/v1/imports/gigs/`.
- Multipart image upload support through Django storage.
- Import metadata model to track source URL, notes, raw payload, and created listing.
- Tests for API auth, relationship validation, image upload, duplicate handling, canonical response, and claimability.
- Relevant commit after verification.

### Out Of Scope

- Full redesign of every internal dashboard, messaging screen, or admin page.
- Direct-to-S3 presigned upload flow. Multipart upload through Django storage is sufficient for this iteration.
- Production deployment unless explicitly requested after local verification.
- Automated scraping of Facebook pages. This feature accepts data supplied by an agent/client.

## Requirements

### UI/UX

- The main header and category bar must sit together without a visible gap.
- Mobile nav and category menus must expand/collapse reliably.
- Header search input, search submit, login, register, and service/create actions must have stable sizes and visible colors.
- All primary CTAs must be visible in resting state, including register and Create My Account.
- Form controls and HTMX-loaded dropdowns must share the same visual treatment.
- Footer social icons must be centered in their circular buttons.
- Layout must avoid overlapping text and buttons on common mobile and desktop widths.

### Business Positioning

- Public copy should describe Linkyoh as an AI-assisted service and business discovery platform for Belize.
- Businesses should understand that listings can be curated/imported and later claimed.
- Claim wording should be clear, professional, and not imply the business personally created the listing.

### API

- Unauthenticated write requests must be rejected.
- Staff users may import listings through normal authenticated DRF access.
- A server-side API key may authorize an import agent when `LYIMPORT_API_KEY` is configured.
- Imported listings must be assigned to a staff/system import user so the existing claim flow works.
- The endpoint must validate category/subcategory and district/location relationships.
- The endpoint must support an uploaded main image and optional contacts/service areas.
- The endpoint must return the created/existing gig id, canonical URL, claim URL, image URL, active state, and warnings.
- Duplicate likely matches must not create duplicate active listings.

## Compatibility

- Existing user-created gig flow must continue working.
- Existing canonical/legacy SEO URLs must continue working.
- Existing production envs must continue to run if `LYIMPORT_API_KEY` is unset; in that case staff auth remains available.
- Existing S3 media behavior must be respected by using Django storage APIs.

## Security

- Do not expose secrets in code, specs, tests, logs, or commits.
- Do not add unauthenticated write endpoints.
- API-key authentication must use constant-time comparison.
- Imported raw payloads are admin/internal metadata and must not be rendered publicly.

## Verification

- Django system check.
- Django tests for the new API.
- Template/static compile checks.
- Browser QA at desktop and mobile widths for home, search, register, and a gig page.
- Confirm SEO tags still render on home/gig pages after UI changes.
