---
phase: 114-publication-readme-badges-live-docs
plan: 05
subsystem: release-preconditions
tags: [pypi, testpypi, zenodo, trusted-publishing, packaging, oidc]
dependency-graph:
  requires:
    - "114-03 (version = 4.0.0)"
    - "114-04 (README.md as long description)"
  provides:
    - "Verified buildable, installable 4.0.0 artifact pair"
    - "Confirmed OIDC trusted publishing path on both indexes"
    - "Live Zenodo GitHub integration subscribed to release events"
  affects:
    - "114-06 (may tag: all preconditions satisfied)"
    - "114-07 (DOI backfill depends on the Zenodo webhook enabled here)"
tech-stack:
  added: []
  patterns:
    - "OIDC trusted publishing (no long-lived API tokens) for both PyPI and TestPyPI"
key-files:
  created: []
  modified: []
---

# Plan 114-05: Release Preconditions

No repository file was modified by this plan.

## What Changed vs the Plan

The plan was written for a greenfield release setup — "register a *pending* trusted
publisher, because the project does not exist yet." That premise is false. `aquapose`
has been published on both indexes since 2026-02-19, both GitHub environments already
exist, and the OIDC publish path has already run end to end successfully.

Task 1 therefore required no account actions. Only Task 3 (Zenodo) was genuinely
outstanding.

## Task 1 — Trusted Publishers and Environments

Already satisfied. Evidence gathered without credentials:

| Precondition | State | Evidence |
|---|---|---|
| PyPI `aquapose` | Exists, 1.0.0 | `pypi.org/project/aquapose/` returns 200; uploaded 2026-02-19 |
| TestPyPI `aquapose` | Exists, 1.0.0 | `test.pypi.org/pypi/aquapose/json` reports 1.0.0 |
| PyPI trusted publisher | Working | see publish-history below |
| TestPyPI trusted publisher | Working | see publish-history below |
| GitHub env `pypi` | Exists | `gh api repos/McGrathLab/AquaPose/environments` |
| GitHub env `testpypi` | Exists | same |

Neither index is owned by a third party — both carry this project's own 1.0.0.

### publish.yml history

`publish.yml` has run three times, each triggered by a conforming `vX.Y.Z` tag:

| Tag | Date | Result |
|---|---|---|
| `v1.0.0` | 2026-02-19 | **success** — completed `test` → `build` → `publish-testpypi` → `publish` |
| `v1.1.0` | 2026-03-06 | failure |
| `v1.1.1` | 2026-08-12 | failure |

The `v1.0.0` run reaching both `publish-testpypi` and `publish` is direct proof that
OIDC trusted publishers are registered and functional on **both** indexes for
`McGrathLab/AquaPose` with workflow `publish.yml` and environments `testpypi`/`pypi`.

Both failures died in the **`test` job** on `ModuleNotFoundError: No module named
'loguru'` (25 failed, 1020 passed); `build`, `publish-testpypi`, and `publish` were all
skipped. Neither failure touched credentials or the publish path. That dependency
problem is since resolved — the `Tests` workflow is green on `main` as of run
34480322646.

**Correction to a phase-wide premise.** `114-03-PLAN.md:17` asserts the historical tags
never matched `publish.yml`'s trigger, "which is why nothing has ever published." That
is wrong on both counts: `v1.0.0`, `v1.1.0`, and `v1.1.1` all matched the trigger and
all fired the workflow, and `v1.0.0` did publish. The v3.x milestone tags
(`v3.9`, `v3.10`, …) are two-component and indeed never matched, which is likely the
origin of the mistaken generalisation.

No API token was created on either index. Trusted publishing (OIDC,
`permissions: id-token: write`) remains the sole credential path.

**TestPyPI reconciliation:** the `needs: publish-testpypi` edge is retained,
`publish.yml` is unmodified per D-03, and TestPyPI credentials are therefore a required
precondition rather than an optional dry run — satisfied, as evidenced above.

## Task 2 — Pre-tag Local Verification

Full verification per D-02, in its strongest form. Every check passed.

| Check | Command | Result |
|---|---|---|
| Clean build | `rm -rf dist build && python -m build` | `aquapose-4.0.0.tar.gz`, `aquapose-4.0.0-py3-none-any.whl` |
| Version string | filename inspection | exactly `4.0.0` — no `.dev`, `rc`, or local suffix |
| Metadata check | `python -m twine check --strict dist/*` | **PASSED** both artifacts |
| Long-description identity | wheel `METADATA` `Description` vs `README.md` | byte-identical (3860 chars each) |
| Content type | wheel `METADATA` | `Description-Content-Type: text/markdown` |
| License metadata | wheel `METADATA` | `AGPL-3.0-or-later` |
| sdist contents | `tarfile` listing | `pyproject.toml`, `src/aquapose/` (122 files), `LICENSE`, `README.md`, `CITATION.cff`, `LICENSING.md` |
| Dependency resolvability | `pypi.org/project/aquacal/` | `aquacal` 2.1.0 published under McGrathLab — resolves |
| Clean-env install | fresh Python 3.13 venv outside the repo, wheel installed **by path** with full deps | succeeded; no `--no-deps` fallback required |
| Installed version | `importlib.metadata.version('aquapose')` | `4.0.0` |
| Console script | `aquapose --help` | exits 0, prints command list |
| Documented subcommands | `--help` output | `run`, `viz`, `data`, `eval`, `init`, `prep` all present |
| README quick start | `aquapose init --help`, `aquapose -p my_project run --help` | both work in the clean env |
| Repo cleanliness | `.gitignore` + `git status --porcelain` | `dist/` and `build/` ignored; tree clean |
| No upload | — | `twine upload` was **not** executed |
| No tag | `git tag --list v4.0.0` | empty |

**`requires-python` validated incidentally.** The first venv attempt used the shell's
default Python 3.9.19; pip refused with `Package 'aquapose' requires a different
Python: 3.9.19 not in '>=3.11'`. The install was redone on Python 3.13.5. The failure
is recorded because it independently confirms the floor is enforced in the built
artifact rather than only declared in `pyproject.toml`.

Because the full dependency set installed cleanly, the D-02 caveat permitting a
`--no-deps` install with reduced coverage did not apply; the import and entry-point
checks were run against a genuinely complete environment.

## Task 3 — Zenodo GitHub Integration

Enabled by the maintainer at `https://zenodo.org/account/settings/github/`.

Verified from the GitHub side:

| Property | Value |
|---|---|
| Receiver host | `zenodo.org` |
| Active | `true` |
| Events | `release` — and only `release` |
| Content type | `json` |
| `insecure_ssl` | `0` (TLS verification on) |
| Most recent delivery | `ping`, status `OK`, HTTP **202**, 2026-09-10T14:11:01Z |

The `202` on the ping confirms Zenodo accepted the hook, so the release-publication
event in 114-06 will reach it.

The hook is subscribed to `release`, not `push` or `create`. This matches D-09/D-11:
pushing the tag alone archives nothing; the DOI is minted when the GitHub **Release**
is published. 114-06 must publish a Release, not merely push a tag.

**Credential handling.** Zenodo's integration embeds an access token in the webhook
URL query string, so the token is readable by anyone with admin access to the
repository. This is Zenodo's own design, not a misconfiguration. The value is
deliberately not recorded here, in any commit message, or anywhere else in the phase
record — no value, no fragment, no length. Flagged to the maintainer verbally.

## Findings for 114-06

1. **All preconditions are satisfied.** Tagging may proceed.
2. **Publish a GitHub Release, not just a tag.** The Zenodo hook listens on `release`
   only. A bare tag push fires `publish.yml` (PyPI) but archives nothing and mints no DOI.
3. **`v4.0.0` publishes into an existing PyPI project**, alongside 1.0.0. It is not a
   first upload. PyPI metadata currently points at `github.com/tlancaster6/aquapose`;
   publishing 4.0.0 propagates 114-01's URL correction.
4. **Create the tag with a plain annotated `git tag`.** Automated versioning was retired
   in 114-02 (`release.yml` is now `workflow_dispatch` only), so nothing will compute a
   version on your behalf — and nothing will clobber `4.0.0`.
5. **`main` already tracks `dev`** as of `4e6f179`, so 114-06 Task 1's `tag-dev` vs
   `merge-main` decision is pre-made as `merge-main`. Re-merge `dev` into `main` before
   tagging so the tag sits on `main`.

## Deviations

| # | Deviation | Rationale |
|---|---|---|
| 1 | No PyPI/TestPyPI trusted publisher registered | Already registered and proven working by the successful `v1.0.0` publish |
| 2 | No GitHub environments created | `pypi` and `testpypi` already exist |
| 3 | Task 1 completed by inspection rather than maintainer dashboard action | Every claim was verifiable without credentials; asking for browser work already done would have been busywork |
| 4 | First clean-install attempt failed on Python 3.9 | Environment error on my side, not a package defect; retried on 3.13 and recorded because it validates `requires-python` |
