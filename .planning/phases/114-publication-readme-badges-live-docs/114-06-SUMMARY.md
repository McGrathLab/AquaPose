---
phase: 114-publication-readme-badges-live-docs
plan: 06
subsystem: release
tags: [release, pypi, zenodo, doi, tagging, publishing]
dependency-graph:
  requires:
    - "114-03 (version 4.0.0, CITATION.cff Pass A)"
    - "114-04 (README as long description)"
    - "114-05 (trusted publishers, Zenodo webhook, verified artifact)"
  provides:
    - "aquapose 4.0.0 published on PyPI"
    - "GitHub Release v4.0.0 on main"
    - "Zenodo software archive with concept and version DOIs"
  affects:
    - "114-07 (backfills the CONCEPT DOI 10.5281/zenodo.22692575)"
tech-stack:
  added: []
  patterns:
    - "Deliberate annotated tag as sole release trigger; GitHub Release as the separate Zenodo trigger"
key-files:
  created: []
  modified: []
---

# Plan 114-06: Cut v4.0.0

No repository file was modified by this plan.

## Task 1 — Branch Decision

**Measured divergence before deciding**, per the acceptance criteria:

```
git rev-list --left-right --count origin/main...dev  →  0    7
git merge-base --is-ancestor origin/main dev         →  true
```

`main` was 7 commits behind `dev` and a **strict ancestor** of it, so reconciling was a
fast-forward with no merge commit.

**Developer selection, recorded verbatim:** `merge-main — fast-forward main, tag there`
(2026-09-10, in response to the Task 1 checkpoint).

The plan's stated objection to `merge-main` — that "the tagged commit would be a merge
commit that Plan 05's verification never built from, so the verified-artifact-equals-
shipped-artifact chain is weakened" — did not apply. A fast-forward leaves `main` and
`dev` at the identical SHA, so the tagged tree is exactly the tree that was verified.
The build, `twine check --strict`, and long-description identity check were nonetheless
re-run on the exact tagged commit before tagging, and all passed.

Note that an earlier fast-forward of `main` had already occurred during 114-02 (to
unblock the RTD docs target), which is why the divergence was 7 rather than 1732.

## Task 2 — Tag, Publish, Release

| Step | Value |
|---|---|
| Tagged commit | `907425affa7d9bd2110bbf5f7f377507249e2d3f` |
| Branch | `main` (identical to `dev` at tag time) |
| Tag | `v4.0.0`, annotated, message "AquaPose 4.0.0 — first public release" |
| Tag object | `1c2a7e507e8936530eb5452788976e404db43e64` |
| Workflow run | https://github.com/McGrathLab/AquaPose/actions/runs/34488481160 |

Tag created with a plain `git tag -a`. `semantic-release version` was **not** used
(114-03's recorded trap), and automated versioning had already been retired in 114-02.

### publish.yml job results

| Job | Result |
|---|---|
| `test` | success |
| `build` | success |
| `publish-testpypi` | success |
| `publish` | success |

`publish.yml` was not modified. No `twine upload` was run.

### PyPI

Verified against the **simple index** and the versioned JSON API rather than the
project HTML page — see "Verification Caveat" below.

```
simple index : aquapose-4.0.0-py3-none-any.whl, aquapose-4.0.0.tar.gz
4.0.0 JSON   : version 4.0.0
               summary "3D fish pose estimation via refractive multi-view triangulation"
               license AGPL-3.0-or-later
               project_urls -> github.com/McGrathLab/AquaPose
```

PyPI's project metadata flipped from `github.com/tlancaster6/aquapose` to
`github.com/McGrathLab/AquaPose`, propagating 114-01's URL correction to the index.

`aquapose` now carries two releases: the pre-existing `1.0.0` (2026-02-19) and `4.0.0`.
This was not a first upload — see 114-05's correction of that phase-wide premise.

### GitHub Release

| Property | Value |
|---|---|
| URL | https://github.com/McGrathLab/AquaPose/releases/tag/v4.0.0 |
| Draft | `false` |
| Prerelease | `false` |
| Target | `main` |
| Published | 2026-09-10T14:27:35Z |

### Zenodo

| Identifier | Value |
|---|---|
| **Concept DOI** | **`10.5281/zenodo.22692575`** — stable across versions; **this is what 114-07 backfills** |
| **Version DOI** | `10.5281/zenodo.22692576` — pins this release |
| Record | https://zenodo.org/records/22692576 |

Record metadata, cross-checked against `CITATION.cff`:

| Field | Zenodo | Matches CITATION.cff |
|---|---|---|
| Title | `AquaPose` | yes |
| Resource type | `software` | n/a (correct type) |
| Version | `v4.0.0` | yes (`4.0.0`) |
| License | `agpl-3.0-or-later` | yes |
| Creator | `Lancaster, Tucker` | yes |
| Files | `McGrathLab/AquaPose-v4.0.0.zip` (4,296,293 bytes) | n/a |

Both DOIs resolve through `doi.org` to the record (HTTP 200). Both are distinct from
the dataset DOIs `10.5281/zenodo.22264079` (version) and `10.5281/zenodo.22264078`
(concept).

## Webhook Anomaly — Recorded for Future Releases

The Zenodo webhook fired three deliveries for the Release event. **Two returned 500:**

| Delivery | Time | Status |
|---|---|---|
| `release` / `created` | 14:27:39Z | **202 OK** |
| `release` / `published` | 14:27:46Z | **500** — `context deadline exceeded (Client.Timeout exceeded while awaiting headers)` |
| `release` / `released` | 14:27:46Z | **500** — same |

**The archive was created successfully regardless.** Zenodo accepted the `created`
delivery with a 202 and processed the deposit asynchronously; the two 500s are GitHub
reporting that Zenodo's HTTP response exceeded the delivery timeout, not evidence that
the event was lost.

This was established by querying the Zenodo API for the record directly rather than
inferring success from the delivery log. **Future releases showing these 500s should
check `https://zenodo.org/api/records?q=aquapose&all_versions=true` before concluding
the archival failed** — and must not create a manual Zenodo upload as a workaround,
which would produce a competing record with a separate DOI.

## Task 3 — End-to-End Verification

### Install from the real index

A fresh Python 3.13 virtualenv outside the repository, installing **by name from
PyPI** — not by local path:

| Check | Result |
|---|---|
| `pip install aquapose==4.0.0` | succeeded, full dependency tree (torch, ultralytics, aquacal 2.1.0) — no `--no-deps` fallback needed |
| Installed version | `4.0.0` |
| `aquapose --help` | exit 0 |
| Subcommands present | `run`, `viz`, `data`, `eval`, `init`, `prep` — all six |

`pip install aquapose` is now true. Phase 113 shipped that line in the installation and
tutorial docs on the accepted risk (113 D-09) that this phase would make it so; that
risk is now discharged.

### README URL sweep — every URL in the shipped file

| URL | Status | Label |
|---|---|---|
| `aquapose.readthedocs.io/en/latest/` | 200 | |
| `aquapose.readthedocs.io/en/latest/getting-started/installation.html` | 200 | |
| `aquapose.readthedocs.io/en/latest/getting-started/concepts.html` | 200 | |
| `aquapose.readthedocs.io/en/latest/getting-started/tutorial.html` | 200 | |
| `aquapose.readthedocs.io/en/latest/api/index.html` | 200 | |
| `codecov.io/gh/McGrathLab/AquaPose` | 200 | |
| `github.com/McGrathLab/AquaPose/actions/workflows/test.yml` | 200 | |
| `github.com/McGrathLab/AquaPose/blob/main/CITATION.cff` | 200 | |
| `github.com/McGrathLab/AquaPose/blob/main/LICENSE` | 200 | |
| `github.com/McGrathLab/AquaPose/blob/main/LICENSING.md` | 200 | |
| `pypi.org/project/aquapose/` | 200 | |
| `zenodo.org/records/22264079` | 200 | |
| `img.shields.io/readthedocs/aquapose/latest` | 200 | `docs: passing` |
| `img.shields.io/codecov/c/github/McGrathLab/AquaPose/main` | 200 | `coverage: 69%` |
| `img.shields.io/github/actions/workflow/status/.../test.yml?branch=main` | 200 | `build: passing` |
| `img.shields.io/pypi/pyversions/aquapose` | 200 | `python: 3.11 \| 3.12 \| 3.13` |
| `img.shields.io/badge/license-AGPL--3.0--or--later-blue` | 200 | `license: AGPL-3.0-or-later` |
| `img.shields.io/pypi/v/aquapose` | 200 | `pypi: v1.0.0` — **stale cache, see below** |

No URL returned non-200. No badge renders `unknown` or `not found`, so D-04 is
satisfied.

### PyPI long description

Verified via the versioned JSON API:

| Check | Result |
|---|---|
| Character-identical to local `README.md` | **yes** (3860 chars both) |
| `description_content_type` | `text/markdown` |
| Contains `aquapose.readthedocs.io` | yes (9 occurrences) |
| Contains `CITATION.cff` | yes |
| Contains `img.shields.io` | yes (6 badges) |
| Contains `pip install aquapose` | yes |

The absolute-URL discipline from 114-04 survived the trip: the docs funnel works from
PyPI, not only from GitHub.

## Verification Caveat — PyPI HTML is not directly checkable

`curl` against `https://pypi.org/project/aquapose/` returns a **`<title>Client
Challenge</title>`** bot-protection page (3038 bytes), HTTP 200, regardless of user
agent. Two consequences worth recording:

1. **A 200 from any `pypi.org/project/...` URL proves nothing.** A control request for
   `https://pypi.org/project/aquapose/9.9.9/` — a version that does not exist — also
   returned 200. Any check asserting on that endpoint's status code is vacuous.
2. All PyPI assertions in this summary therefore use the **simple index**
   (`pypi.org/simple/aquapose/`) and the **JSON API**
   (`pypi.org/pypi/aquapose/4.0.0/json`), which are not challenge-protected.

The plan's `<verify>` block asserts `curl ... https://pypi.org/project/aquapose/4.0.0/`
returns 200. That assertion passes but is meaningless; it was replaced with the two
authoritative checks above.

## Findings for 114-07

1. **Backfill the CONCEPT DOI `10.5281/zenodo.22692575`**, not the version DOI. The
   concept DOI always resolves to the latest version and is the correct citation target.
2. **The `pypi/v` badge still reads `v1.0.0`** at the time of writing. This is shields.io
   caching PyPI data (`cache-control: max-age=900`); PyPI's own JSON API already reports
   `4.0.0` as the latest version. Re-check before closing the phase; no code change is
   needed.
3. **The tests badge renders `build: passing`, not `tests: passing`.** Shields' default
   label for the `github/actions/workflow/status` endpoint is `build`, which does not
   match the badge's `[![tests]...]` alt text. Adding `&label=tests` to the badge URL
   fixes it. Cosmetic, not a D-04 violation — but 114-07 already edits the README badge
   row to add the DOI badge, so it is a free fix to bundle.

## Deviations

| # | Deviation | Rationale |
|---|---|---|
| 1 | Task 1's decision was already effectively made before the checkpoint | The developer selected `merge-main` earlier in the phase; the checkpoint was still run to satisfy the acceptance criteria (measure divergence, record the selection verbatim) |
| 2 | Build/`twine check` re-run before tagging, beyond the plan's letter | 7 commits landed after 114-05's verification; the acceptance criteria require the tagged tree to be a verified tree |
| 3 | PyPI page-content check performed via JSON API instead of the HTML page | The HTML endpoint is bot-challenge-protected and its status code is not a meaningful signal — see Verification Caveat |
| 4 | Task 2 split between agent and developer | The developer published the GitHub Release; the agent created and pushed the tag and monitored the workflow |
