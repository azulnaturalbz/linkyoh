# Production reference-data audit

Captured `2026-09-14T01:39:03.406280+00:00` through the existing production Django
connection in `linkyoh-web-1`. The authenticated shared-host connection was used
only to stream the bounded exporter on stdin. No script/config was installed on
the host, and no production record was written.

PostgreSQL `REPEATABLE READ READ ONLY`, default read-only PGOPTIONS and a 15-second
statement timeout were enforced. `SHOW transaction_read_only` returned `on`.
Only the seven allowlisted reference models below were serialized. No users,
provider contacts, messages, claims, account records, secrets or media files were
exported. Category media path strings remain part of exact reference field parity;
the referenced images were not downloaded as part of this snapshot.

| Model | Production | Isolated local |
|---|---:|---:|
| Country (Belize only) | 1 | 1 |
| District | 6 | 6 |
| LocalType (City/Town/Village) | 3 | 3 |
| Local | 244 | 244 |
| Location | 244 | 244 |
| Category | 5 | 5 |
| SubCategory | 439 | 439 |

Every ID, field and foreign-key relationship matches the snapshot, not just row
counts. Canonically ordered reference SHA-256:
`2cd92674fbeb8e3920a02081745efa30d00bff651f58082ffa3131827bcf2b32`.
Machine-readable proof: [reference-parity.json](evidence/reference-parity.json).

| Category | Subcategories |
|---|---:|
| Housing & Construction | 161 |
| Autos | 27 |
| Health | 119 |
| Pets | 11 |
| Services | 121 |

| District | Localities |
|---|---:|
| Belize | 37 |
| Cayo | 46 |
| Orange Walk | 37 |
| Corozal | 31 |
| Stann Creek | 30 |
| Toledo | 63 |

## Findings and boundaries

Actual source labels differ from early synthetic fixtures: `Plumber` (431),
`Cabinet Making` (330), `Woodworking` (473), `Belmopan City` (Local 2), and
`San Ignacio and Santa Elena Town` (Local 6). Added reviewed parser aliases and
city/town/village suffix handling without renaming or reassigning records.

Two existing assignments are candidates for editorial review: `Auto Glass Repair`
(SubCategory 292) and `Cabinet Refacing` (331) currently belong to `Health` (3).
They were copied exactly, not corrected in production or local reference data.
This is not an exhaustive semantic audit of all 439 categories or a claim that
the 244 stored localities represent every settlement in Belize.

Private snapshot: `/Users/cristiansilva/WorkSpace/Linkyoh/.reference-snapshots/linkyoh-reference-20260914.json`,
mode 0600 inside a 0700 directory outside the repository. Keep it private and
refresh through the same authorization/read-only procedure when needed. The
guarded importer accepts only an empty disposable `linkyoh-sitewide-*` SQLite
database and rejects non-SQLite, existing users/reference data, unapproved models,
schema changes, duplicate identifiers, broken relationships and count mismatch.

The user's original local database was not overwritten. The production reference
copy powers the isolated preview and its dropdown/search QA. Provider records are
separate synthetic examples; no production listings were copied or published.
