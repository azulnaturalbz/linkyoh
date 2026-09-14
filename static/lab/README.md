# Lab assets

The approved prototype at `3988d72` supplies the baseline layout and licensed
fonts/icons. No prototype fixture images or businesses are production assets.

- Hub stylesheet: byte-for-byte copy of Silvatech
  `public/brand/silvatech-ui.css`, SHA-256
  `1371df9a867ed7461a4021ae9b35535510792d051a7c7e1ccccca5c4d910de5f`.
- Inter and Sora: local Latin WOFF2, licenses in `assets/fonts/`.
- Lucide 1.8.0: local browser build and ISC license in `assets/`.
- htmx 1.9.6 and Alpine 3.13.0: pinned local copies of the versions already used
  by the legacy base, with licenses. No Python runtime packages are added.
- `discovery.css` and `discovery.js`: scoped public-page layout and progressive
  interaction; native GET/details controls remain the no-JavaScript path.

Do not update the shared stylesheet silently from a remote URL. Review a new hub
revision and rerun the UI evidence when refreshing these assets.
