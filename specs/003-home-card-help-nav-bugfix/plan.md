# Plan: Homepage Provider Names And Help Navigation

## Scope

- `linkyohapp/templates/home.html`
- `linkyohapp/templates/help_*.html`

## Approach

Update the remaining custom homepage card markup to use the already-canonical profile display name helper, then narrow help-page sidebar JavaScript selectors so the script does not bind to global navigation links.

## Validation

- Compile Python modules.
- Run Django checks.
- Run current test suite.
- Browser-check help/search and help/faq top-nav navigation.
