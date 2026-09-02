# API Coverage — Phase 113 (Concepts & Tutorial)

No external API integration: this phase writes documentation, corrects two
factual errors in the Zenodo deposit and its generating templates, fixes a
numerically ill-conditioned angular-error metric, and removes a wheel-index pin
from `pyproject.toml`. It builds no client, wrapper, or adapter against any
external service.

The `api-coverage` detector fired on the phrase "Zenodo API file-count" in
`113-07-PLAN.md`. That reference is a single read-only `GET` against
`https://zenodo.org/api/records/<record_id>`, used once as an acceptance check to
confirm that the published record contains exactly the 22 files named in
`checksums.sha256`. It is a verification probe, not a capability surface: no
Zenodo capability is wrapped, no credential is stored, and no code in `src/`
gains a Zenodo dependency. The publication itself is a blocking
`checkpoint:human-action` performed by the maintainer in their own authenticated
browser session (D-04, and Phase 111's D-11 before it), precisely because it is
not an SDK integration.

A capability matrix would therefore have no rows to decide. Enumerating the
Zenodo REST surface and opting out of all of it would be noise, not a decision
record.
