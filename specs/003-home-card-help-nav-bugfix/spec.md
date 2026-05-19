# Bugfix Specification: Homepage Provider Names And Help Navigation

## Goal

Fix two regressions found after the profile URL/UI update.

## Requirements

- Homepage gig cards must show the provider profile display name, so business profiles render the business/company name instead of the account user name.
- Help-page sidebar scripts must only intercept clicks inside the help sidebar table of contents.
- Global navbar, dropdown, category, and page navigation links must continue working on help pages.

## Acceptance

- Homepage custom gig card blocks use `gig.user.profile.get_display_name`.
- Help pages scope sidebar nav JavaScript to `.help-sidebar-nav .nav-link`.
- Browser verification from `/help/search/` and `/help/faq/` can navigate to `/about-us/` through the main navbar.
