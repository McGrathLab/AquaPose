---
phase: 114-publication-readme-badges-live-docs
plan: 04
subsystem: readme-and-docs
tags: [readme, badges, readthedocs, pypi-long-description, citation]
dependency-graph:
  requires:
    - "114-01 (repo URL corrections, README-03 hero-media deferral)"
    - "114-02 (verified RTD/shields/Codecov URL table; docs target overridden to main/latest)"
    - "114-03 (version = 4.0.0, CITATION.cff without doi key)"
  provides:
    - "Rewritten README.md: D-12 landing page (badges, framing, quick start, docs funnel, citation, license)"
    - "Coverage mapping proving Development and GPU Support content already lives in docs/contributing.md and docs/getting-started/installation.md"
  affects:
    - "114-05 (pre-tag verification builds/installs the artifact; README ships as PyPI long description)"
    - "114-06 (post-publish, the two PyPI-sourced badges/links go from v1.0.0-pointing to v4.0.0-pointing)"
    - "114-07 (Pass B appends the Zenodo software DOI badge and citation sentence)"
tech-stack:
  added: []
  patterns:
    - "Every README link absolute (http-prefixed) because pyproject.toml:9 makes README.md the PyPI long description"
    - "Badge row sourced entirely from a pre-verified URL table (114-02-SUMMARY.md) rather than hand-typed endpoints"
key-files:
  created: []
  modified:
    - README.md
decisions:
  - "Docs/badge target is main/latest, not dev — D-07 override recorded in 114-02-SUMMARY.md and restated in this plan's correction note; every /en/dev/ URL in the stale plan text was replaced with /en/latest/, and branch=dev badge params were replaced with branch=main."
metrics:
  duration: "~20m"
  completed: "2026-09-10"
---

# Phase 114 Plan 04: README Rewrite Summary

Rewrote `README.md` into the tight D-12 landing page: a six-badge row, a
three-beat framing paragraph, a minimal quick start funneling to the
tutorial's Zenodo dataset, four verified Read the Docs links, a
`CITATION.cff` pointer, and an absolute-link license section — with the
`Development` and `GPU Support` sections removed after confirming their
content already lives in the docs.

## Deviations from Plan

### 1. D-07 override applied — docs/badges target `main`/`latest`, not `dev`

The plan text (written before Wave 1 execution) specifies `/en/dev/` URLs and
`branch=dev` badge parameters throughout Task 2's `action` and
`acceptance_criteria`. This is stale: D-07 was overridden during 114-02's
execution because `main` was 1732 commits behind `dev` and three of the four
funnel destinations 404'd on it. The developer chose to fast-forward `main`
to `dev` rather than repoint docs at `dev`, so RTD's `latest` (tracking
`main`) is now the correct target, and `main` is the branch the tests badge
should read.

Every URL and badge parameter in the shipped README uses `main`/`latest`,
matching `114-02-SUMMARY.md`'s verified table exactly:

| Plan said | Shipped instead |
|---|---|
| `aquapose.readthedocs.io/en/dev/...` (4 funnel links) | `aquapose.readthedocs.io/en/latest/...` |
| RTD badge `readthedocs/aquapose/dev` | `readthedocs/aquapose/latest` |
| tests badge `test.yml?branch=dev` | `test.yml?branch=main` |
| codecov badge `.../AquaPose/dev` | `.../AquaPose/main` |
| LICENSE/LICENSING.md/CITATION.cff blob links `blob/dev/...` | `blob/main/...` |

No `/en/dev/` substring and no `branch=dev` substring appears anywhere in the
shipped `README.md` — verified by grep before commit. This correction was
supplied directly in the task prompt (which cites `114-02-SUMMARY.md` as
authoritative over the plan text) rather than discovered independently
during execution, but it is recorded here per the prompt's instruction.

No other deviations. Both tasks otherwise matched their `action` and
`acceptance_criteria` blocks.

## Task 1: Coverage mapping (Development / GPU Support -> docs)

No docs files were modified — every command and claim in the README's
doomed `## Development` and `### GPU Support` sections was already present
in `docs/contributing.md` or `docs/getting-started/installation.md`.

### Development section mapping

| README command/claim | Docs location |
|---|---|
| `pip install hatch` | `docs/contributing.md` -> Development Setup |
| `hatch env create` | `docs/contributing.md` -> Development Setup |
| `hatch run pre-commit install` | `docs/contributing.md` -> Development Setup |
| `hatch run pre-commit install --hook-type pre-push` | `docs/contributing.md` -> Development Setup |
| `hatch run test` | `docs/contributing.md` -> Running Tests |
| `hatch run lint` | `docs/contributing.md` -> Code Quality |
| `hatch run typecheck` | `docs/contributing.md` -> Type Checking |

Full coverage confirmed; nothing added.

### GPU Support section mapping

| README command/claim | Docs location | Disposition |
|---|---|---|
| CPU-only PyTorch installed by default | `docs/getting-started/installation.md` -> Install PyTorch for your platform | covered (implicit: no pin, pytorch.org selector) |
| `--force-reinstall --index-url .../whl/cu124` | (none — deliberately not relocated) | **not carried forward**: contradicts Phase 113 D-08, which replaced pinned CUDA install guidance with the pytorch.org selector. This is the factual error being removed, not moved. |
| `nvrtc: error: failed to open libnvrtc-builtins.so` tip | `docs/getting-started/installation.md` -> Troubleshooting | **already present verbatim** (`grep -n nvrtc docs/getting-started/installation.md` found the exact symptom string with a pin-free pytorch.org-selector resolution) — no edit needed |

Full coverage confirmed (with the one command correctly excluded rather than
relocated); nothing added. `hatch run docs:build` exited 0 both before and
after Task 2's README edit (Sphinx `-W --keep-going`, no new warnings).

## Task 2: README rewrite

Rewrote `README.md` top to bottom (81 lines, up from 66):

1. **Title + framing paragraph** — merged the old one-line description into
   a single paragraph hitting all three README-01 beats (refraction problem,
   3D midline/kinematics output, target researcher audience) ahead of any
   technical content. Corrected `13-camera` -> `12-camera` to match
   `CLAUDE.md` and `docs/getting-started/concepts.md` (both say 12; the
   `13-camera` in `src/aquapose/calibration/uncertainty.py` describes a
   synthetic rig, not the real one, so it is not evidence for 13).
2. **Badge row** — six shields.io badges in the D-04 order (tests, docs,
   coverage, python, pypi, license), each linked to its service page, all
   URLs drawn from `114-02-SUMMARY.md`'s verified table with the D-07
   override applied. No Zenodo DOI badge.
3. **Pipeline** — kept unchanged (5-stage list + chunking sentence).
4. **Quick start** — `pip install aquapose`, a sentence deferring to
   Installation for the PyTorch step (no inline torch command), the
   existing `aquapose init-config` / `aquapose run` invocations, and a
   tutorial pointer naming the Zenodo dataset DOI `10.5281/zenodo.22264079`.
5. **Documentation funnel** — four plain-Markdown absolute links
   (Installation, Concepts, Tutorial, API reference) mirroring
   `docs/index.md`'s structure, no MyST directives.
6. **Citation** — points at `CITATION.cff`'s absolute GitHub blob URL and
   GitHub's "Cite this repository" button, with one sentence distinguishing
   software citation from dataset citation. No placeholder token for the
   future software DOI (Plan 07 adds it as a real sentence, not a `TBD`).
7. **License** — kept the two-sentence section, converted `LICENSE` and
   `LICENSING.md` links to absolute GitHub blob URLs.

Deleted: `## Development`, `### GPU Support`, and the commented-out
`## Documentation` TODO stub.

## Verification

- `python -c "..."` link/content assertions (relative-link scan, badge
  presence, forbidden strings) — **all passed**.
- `grep -c '13-camera' README.md` -> 0; `grep -c '12-camera' README.md` -> 1.
- `grep -n 'zenodo.org/badge' README.md` -> no match (no DOI badge).
- `hatch run docs:build` -> exit 0, build succeeded, no new warnings.
- **Live URL re-verification** (curl, every absolute URL in the shipped
  README, run against the committed content, not the plan's stale table):

| URL | Status |
|---|---|
| `https://aquapose.readthedocs.io/en/latest/` | 200 |
| `https://aquapose.readthedocs.io/en/latest/api/index.html` | 200 |
| `https://aquapose.readthedocs.io/en/latest/getting-started/concepts.html` | 200 |
| `https://aquapose.readthedocs.io/en/latest/getting-started/installation.html` | 200 |
| `https://aquapose.readthedocs.io/en/latest/getting-started/tutorial.html` | 200 |
| `https://codecov.io/gh/McGrathLab/AquaPose` | 200 |
| `https://github.com/McGrathLab/AquaPose/actions/workflows/test.yml` | 200 |
| `https://github.com/McGrathLab/AquaPose/blob/main/CITATION.cff` | 200 |
| `https://github.com/McGrathLab/AquaPose/blob/main/LICENSE` | 200 |
| `https://github.com/McGrathLab/AquaPose/blob/main/LICENSING.md` | 200 |
| `https://img.shields.io/badge/license-AGPL--3.0--or--later-blue` | 200 |
| `https://img.shields.io/codecov/c/github/McGrathLab/AquaPose/main` | 200 |
| `https://img.shields.io/github/actions/workflow/status/McGrathLab/AquaPose/test.yml?branch=main` | 200 |
| `https://img.shields.io/readthedocs/aquapose/latest` | 200 |
| `https://zenodo.org/records/22264079` | 200 |

**Pending Plan 06 (PyPI-sourced, exempted per the plan's own acceptance
criteria):**

| URL | Status now | Note |
|---|---|---|
| `https://img.shields.io/pypi/pyversions/aquapose` | 200 | currently reflects `aquapose` 1.0.0's classifiers; will reflect 4.0.0's 3.11/3.12/3.13 classifiers after Plan 06 publishes |
| `https://img.shields.io/pypi/v/aquapose` | 200 | currently reads `v1.0.0`; expected to read `v4.0.0` after Plan 06 |
| `https://pypi.org/project/aquapose/` | 200 | serves the 1.0.0 project page until Plan 06 publishes 4.0.0 |

The `CITATION.cff` blob link at `blob/main/` returned 200 with the correct
title and content — confirming `origin/main` already carries 114-03's
commits (`dde7a4d`/`605560f`/`a6b54c8`) even though the local `main` branch
ref is stale; `origin/main` is authoritative here and was fetched and
checked directly.

- No repo-relative link survives in `README.md` (all 17 unique link targets
  begin with `http`).
- `README.md` contains no `## Development` heading, no `GPU Support`
  heading, no `TODO`, and no `download.pytorch.org/whl/cu` substring.
- `README.md` is 81 lines (min_lines requirement: 45).

## Commits

- `dc339c5` — `docs(114-04): rewrite README as D-12 landing page`

(Task 1 produced no commit — no docs files required edits; the coverage
mapping above is the evidence of that.)

## Self-Check: PASSED

- FOUND: `README.md` at repo root, contains `https://aquapose.readthedocs.io`
- FOUND: commit `dc339c5` in `git log`
- FOUND: `docs/contributing.md` contains `hatch` (development setup section)
- FOUND: `docs/getting-started/installation.md` contains the `nvrtc`
  troubleshooting entry (pre-existing, unmodified)
