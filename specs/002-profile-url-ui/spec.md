# Feature Specification: Profile URL And UI Cleanup

## Goal

Make public Linkyoh profile pages match the SEO-friendly URL and visual quality established for gig, category, and subcategory pages.

## Requirements

- Public profiles must have canonical, slugged provider URLs that include the display name and user id.
- Legacy numeric profile URLs must continue to work and redirect permanently to the canonical URL.
- Profile pages must render server-side SEO metadata, Open Graph tags, Twitter card tags, canonical URL, and JSON-LD.
- Provider profiles with active listings must be included in the sitemap.
- Header text and profile-type/verification badges must remain readable on cover images.
- Service listing cards on profile pages must keep price, category, and subcategory badges inside the card at desktop and mobile widths.
- Existing profile editing, QR code, messaging, and gig-card behavior must continue to work.

## Acceptance

- `/profile/<id>/` returns `301` to `/belize/providers/<profile-name>-<id>/`.
- The canonical profile page returns `200` and includes profile-specific canonical, Open Graph, and Twitter metadata.
- The sitemap includes canonical provider profile URLs for profiles with active listings.
- Browser checks show no horizontal overflow and no badge overflow in profile gig cards.
