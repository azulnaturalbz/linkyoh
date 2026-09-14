# Brand provenance and review choice

Source: owner's Stitch project
https://stitch.withgoogle.com/projects/15344324354844864865, inspected in the
authenticated browser. Original project remains unchanged. Prior feedback/remix:
https://stitch.withgoogle.com/projects/16136778374827234844.

The source has two logo candidates. `stitch-title-2.png` is the black linked-chain
wordmark selected for this local preview. `stitch-redesigned-logo.png` is the blue
alternative, retained here for Cristian's choice. No explicit final selection
between these two was received during this pass.

`static/lab/assets/linkyoh-stitch-wordmark.png` is byte-identical to Title-2.
Its original 1000px square bitmap is not edited; `lab/brand.html` and `sitewide.css`
use a fixed-aspect CSS viewport around the artwork to remove blank padding from
layout. Desktop/390px container width is 136px, 320px width is 112px. The bitmap
remains proportional, with the trademark mark outside it. Header/footer use the
same include and sizing, not independent approximations.

`stitch-banner.png` is the original orange/green launch banner reference. It was
not copied into the application because it conflicts with the approved Lab
register and says "LAUNCHING NOW". The new
`static/lab/assets/linkyoh-belize-banner.png` was generated with the built-in image
tool using the actual wordmark as a reference: light surfaces, local trades and a
Belize timber-house model. It is brand illustration, not evidence of an actual
provider/project. Source output is preserved at
`/Users/cristiansilva/.codex/generated_images/019e419a-d141-7f12-9853-1711359a3900/exec-87043294-5a13-4ba0-be8d-2b5acb728677.png`.
Uploaded provider photos and cover images are never replaced by this artwork.

## Asset identity

| Asset | SHA-256 |
|---|---|
| linkyoh-stitch-wordmark.png | 083ed1434a6e619483d39fb1e6d33ec03e6a60d1073210c7a04316067803d174 |
| linkyoh-belize-banner.png | 5e034f9c083520e8367c5da8af778046763f9b6a8137578f62fb199f58e72b00 |
| silvatech-ui.css (unchanged hub source) | 1371df9a867ed7461a4021ae9b35535510792d051a7c7e1ccccca5c4d910de5f |

Existing frontend CDN versions were vendored locally to avoid network-dependent
forms during QA and normal navigation. No package upgrade or Python dependency
change is bundled. Bootstrap 5.3.2 (CSS + bundle), jQuery 3.6.0, Select2 4.1.0-rc.0
and select2-bootstrap-5-theme 1.3.0 retain their upstream license headers.

| Local asset | SHA-256 |
|---|---|
| bootstrap.min.css | 3017df4a76db5f01c2b99b603d88b03106df13bcfe18e67b7c13c2341d3a67df |
| bootstrap.bundle.min.js | 82f64f62bb03c1bc1824b0f9c9e05f70dba33e146818e63cdf5c306c8cf3dedd |
| jquery.min.js | ff1523fb7389539c84c65aba19260648793bb4f5e29329d2ee8804bc37a3fe6e |
| select2.min.js | f7244fff610595b944f76bf3080d74e3af42b5dd234f8f079e698cc39ac966b0 |
| select2.min.css | cda4a81c187015d95ed2c71f1841540b08203cdec5fa2a7d5d1825a3c2166f8c |
| select2-bootstrap-5-theme.min.css | 5cb35411fccf18705e4ad112d836cb514459ddeefddc169b970cc99588fa5b64 |

Upstream paths: `https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/`,
`https://code.jquery.com/jquery-3.6.0.min.js`,
`https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/`, and
`https://cdn.jsdelivr.net/npm/select2-bootstrap-5-theme@1.3.0/dist/`.
Licensed Inter/Sora, Lucide, Alpine and HTMX from slice 3 remain unchanged.
