# Implementation Plan: Profile URL And UI Cleanup

## Scope

- Add profile URL helpers and SEO context in the existing SEO helper layer.
- Add `Profile.get_absolute_url()` and update profile routes to support canonical and legacy paths.
- Update templates to use canonical profile links.
- Refine profile header styling and gig-card badge wrapping.
- Include public provider profiles with active gigs in the sitemap.
- Add focused tests and browser verification.

## Files

- `linkyohapp/seo.py`
- `linkyohapp/models.py`
- `linkyohapp/urls.py`
- `linkyohapp/views.py`
- `linkyohapp/sitemaps.py`
- `linkyohapp/templates/profile.html`
- `linkyohapp/templates/includes/_gig_card.html`
- profile link templates in `base.html`, `home.html`, `gig_detail.html`, and `help_profile.html`
- `static/css/linkyoh-design-system.css`
- `linkyohapp/tests.py`

## Validation

- Compile Python modules.
- Run Django checks.
- Run all Linkyoh tests.
- Verify local canonical profile URL, legacy redirect, metadata, sitemap profile entry, and responsive profile-card layout.
