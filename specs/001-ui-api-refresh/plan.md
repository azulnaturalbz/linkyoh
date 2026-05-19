# Implementation Plan: Linkyoh UI Refresh And AI Listing Ingestion

## Technical Approach

- Keep Bootstrap 5, HTMX, Alpine.js, Font Awesome, and Select2 rather than introducing Tailwind or a new frontend build pipeline.
- Move the most important repeated UI fixes into `static/css/linkyoh-design-system.css`.
- Simplify `base.html` header structure so the main navbar and category bar share one sticky header and collapse naturally.
- Use the existing HTMX endpoints for dynamic dropdown population.
- Add a small DRF API package under `linkyohapp/api/`.
- Add a lightweight `ImportedGigSource` model for import attribution and duplicate checks.
- Add optional env settings for API-key imports without requiring a configured key locally.

## Files Expected To Change

- `specs/001-ui-api-refresh/*`
- `credentials.py`
- `linkyoh/settings.py`
- `linkyoh/urls.py`
- `linkyohapp/models.py`
- `linkyohapp/admin.py`
- `linkyohapp/api/*`
- `linkyohapp/migrations/*`
- `linkyohapp/tests.py`
- `linkyohapp/templates/base.html`
- `linkyohapp/templates/home.html`
- `linkyohapp/templates/search_results.html`
- `linkyohapp/templates/account/register.html`
- `linkyohapp/templates/about.html`
- `linkyohapp/templates/gig_detail.html`
- `linkyohapp/templates/claim_gig.html`
- `static/css/linkyoh-design-system.css`
- `.env.example`

## Risks

- Global button and form CSS can affect many pages. Mitigate with browser checks and avoiding overly broad destructive styling.
- API imports can create bad data if validation is weak. Mitigate with serializer validation and tests.
- New migration affects production deployment. Mitigate by making the new model additive only.
- Header changes can disturb SEO tags if `base.html` is edited carelessly. Mitigate by preserving the head metadata block.

## Rollback

- Revert the UI/API commit.
- If migration has run, leave the additive import metadata table in place or drop it in a follow-up rollback migration if required.
- API route is isolated under `/api/v1/imports/` and can be disabled by removing URL inclusion.

## Verification Commands

```bash
python3 -m compileall -q linkyoh linkyohapp
docker run --rm --env-file .env -e LYDEPLOYMENT_MODE=app -e LYSTATIC_ROOT=/tmp/staticfiles linkyoh-web python manage.py check
docker run --rm --env-file .env -e DJANGO_SETTINGS_MODULE=linkyoh.test_settings -e LYDEPLOYMENT_MODE=app -e LYSTATIC_ROOT=/tmp/staticfiles linkyoh-web python manage.py test linkyohapp.tests.GigImportApiTests
git diff --check
```

Browser QA should cover desktop and mobile widths:

- `/`
- `/search/`
- `/register/`
- one active gig URL

## Deployment Notes

- Build and run migrations before restarting production web.
- Configure `LYIMPORT_API_KEY` only in production secret/env storage if API-key import access is needed.
- Configure `LYIMPORT_USER_USERNAME` if the default `linkyoh-ai-admin` should differ.
