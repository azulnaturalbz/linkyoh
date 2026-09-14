# Strip v2 Consumer Evidence

2026-09-14. Local candidate on `codex/005-linkyoh-revamp-ui`.
**HOLD: Cristian's explicit app-only deployment go is required.**
The already-deployed sitewide UI is a separate release. No push, production
mutation, host reservation, shared-edge change or campaign activation occurred.

## Changes

Ten published links, Games last, version marker v2. Chillbout and Belize
Logistics are anchors; all destinations keep `utm_source=linkyoh`, the existing
destination event keys and `rel=noreferrer`. The existing single Rybbit
dispatcher remains unchanged. Games is included once in Organization sameAs
and the related-products list. Booking/catalog availability is not implied.

The hub stylesheet is byte-identical to the published asset; its only CSS
delta from the prior version is version comments. Public CSS checksum:
`f9979278a41dfffb453987b5a5f4b1d5f4d5fe88d1256d79fe52ae0092202b1d`.
Source receipt: [source.json](evidence/source.json). The unmodified published
HTML is retained in `linkyohapp/test_fixtures/ecosystem-strip-v2.html`, so
runtime contract tests do not require review screenshots in an app image.

## Verification

- 67 tests passed, zero skips, on the existing deployed amd64 runtime image
  `ff3ce873f0c0546f0b3dee0d1338fd682c909e914020689eff90fb06eefdf66c`
  with changed source mounted read-only and disposable PostgreSQL/Redis.
  Network namespace had no external network. This is not a newly built
  immutable release image. [Runtime receipt](evidence/runtime.json) and
  [test output](evidence/runtime-tests.txt).
- 30 Home/Provider/Login EN/ES views at 320/390/768/944/1440px passed.
  All ten links fit, targets are at least 44px, sampled strip text contrast
  is at least 15.18:1, and no page errors occurred.
- Ten keyboard-order journeys, four no-JS journeys with intercepted native
  navigation and omitted referrer, and three single-dispatch analytics checks
  passed. All external traffic was blocked or locally stubbed. No provider,
  analytics ingestion endpoint or production write was contacted.
- 34 screenshots in `evidence/`; [browser report](evidence/qa.json),
  [390px ES](evidence/home-es-390.png),
  [1440px EN](evidence/provider-en-1440.png). Both were visually reviewed.
- Existing missing synthetic image warnings and the deliberately unavailable
  limiter-store test remain in the test log. No model/migration/dependency,
  URL/canonical/OG, claim, account or provider logic changed.

This is targeted strip accessibility evidence, not full WCAG, screen-reader,
Safari, destination-service or production-release certification.

## Reproduce

From the Linkyoh repo, using existing local runtimes:

```sh
SSL_CERT_FILE=/etc/ssl/cert.pem python3 specs/008-ecosystem-strip-v2/verify_source.py
python3 specs/008-ecosystem-strip-v2/runtime_tests.py
/tmp/linkyoh-ecosystem-venv/bin/python specs/008-ecosystem-strip-v2/preview.py
# In another terminal, while the synthetic preview is running:
node specs/008-ecosystem-strip-v2/qa.mjs
```

`verify_source.py` uses verified TLS with the local system CA bundle; it fails
on unexpected versions, redirects or CSS differences. It does not disable
certificate validation. All disposable test containers are removed after QA.
The preview is isolated synthetic data on localhost:8099 and sends nothing.
Review-only artifacts are excluded from Docker packaging.

The shared ecosystem ledger's Linkyoh-only delta is outside this repository;
the hub owner retains responsibility for committing that shared document.
