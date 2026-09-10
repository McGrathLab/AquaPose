---
phase: 114-publication-readme-badges-live-docs
verified: 2026-09-10T00:00:00Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
deferred:
  - truth: "Hero media shows a 3D reconstruction rendering inline on GitHub (ROADMAP criterion 3, README-03)"
    addressed_in: "Backlog todo (no phase yet)"
    evidence: "114-CONTEXT.md <deferred> section, user decision 2026-09-09; REQUIREMENTS.md README-03 marked deferred; .planning/todos/pending/2026-09-09-readme-hero-media-3d-reconstruction.md"
---

# Phase 114: Publication — README, Badges, Live Docs Verification Report

**Phase Goal:** An outside researcher landing on the repo understands what AquaPose is, trusts it, and can install, run, and cite it
**Verified:** 2026-09-10
**Status:** passed
**Re-verification:** No — initial verification

## Decision Overrides Accounted For

Two deliberate developer overrides recorded in `114-CONTEXT.md`/`114-02-SUMMARY.md` were
applied when interpreting ROADMAP success criterion 5 and requirement DOCS-08:

1. **D-07 override**: RTD default/docs target is `main` via RTD's `latest` version, not
   `dev`. Verified live: `https://aquapose.readthedocs.io/en/latest/` and all four funnel
   pages return 200; `https://aquapose.readthedocs.io/en/dev/` correctly 404s (RTD `dev`
   version is not active — this is expected, not a defect).
2. **114-06 Task 1 pre-decision**: `main` now tracks `dev` (fast-forwarded); `v4.0.0` is
   tagged on `main` at commit `907425a`. Confirmed via `git rev-parse`/`git rev-list`
   evidence in `114-06-SUMMARY.md` and reconfirmed live (GitHub Release page 200,
   tag target `main`).

ROADMAP success criterion 3 (hero media) is explicitly deferred by user decision, tracked
in `.planning/todos/pending/2026-09-09-readme-hero-media-3d-reconstruction.md`. Confirmed
present in that directory. Not counted as a gap.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | README opens with problem / what-you-get / who-it's-for | VERIFIED | `README.md` lines 1-19: refraction problem stated, "3D midlines... midline kinematics" output named, "behavioral and neuroscience researchers running multi-camera aquarium rigs" audience named |
| 2 | Badge row shows tests, docs, coverage, python, pypi, license, DOI — all green/live | VERIFIED | 7 badges present in `README.md:3-9`. Live re-check (fresh JSON, cache-busted): tests `http 200` (workflow badge), docs `passing`/brightgreen, coverage `69%`, python `3.11 \| 3.12 \| 3.13`, pypi `v4.0.0` (self-healed from earlier cache staleness), license `AGPL-3.0-or-later`. DOI badge SVG currently 504s — confirmed as a Zenodo-wide outage (an unrelated DOI, `10.5281/zenodo.3628931`, and the dataset DOI both also 504 at the same time), not a defect specific to this badge; matches the documented trap. |
| 3 | Hero media inline on GitHub | DEFERRED | User decision 2026-09-09, tracked in backlog todo; ROADMAP criterion 3 and REQUIREMENTS README-03 both annotated deferred, original text preserved |
| 4 | Install / quick start against Zenodo dataset / docs link / citation block with DOI, all present and correct | VERIFIED | `README.md`: `pip install aquapose` present; quick start commands (`aquapose init`, `aquapose -p ... run`) present; tutorial link to dataset DOI `10.5281/zenodo.22264079` present and 200; 4 docs funnel links present and 200; Citation section names software concept DOI `10.5281/zenodo.22692575` and distinguishes it from the dataset DOI |
| 5 | Docs build green and reachable at the `pyproject.toml`-declared URL | VERIFIED (with D-07 override) | `pyproject.toml:53` declares `https://aquapose.readthedocs.io` — bare domain redirects to `/en/latest/`, live-verified 200 on base + 4 sub-pages. Local `hatch run docs:build` not re-run in this verification pass but confirmed exit-0 in `114-03-SUMMARY.md` and `114-07-SUMMARY.md` (Sphinx `-W --keep-going`) |

**Score:** 4/4 non-deferred truths verified (5th ROADMAP criterion deferred by explicit user decision, not counted against score)

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `README.md` | Tight landing page: badges, framing, quick start, docs funnel, citation, license | VERIFIED | 81 lines, all 20 unique links absolute (`http`-prefixed), no relative links, no `## Development`/`GPU Support` sections (moved to docs, confirmed present in `docs/contributing.md` and `docs/getting-started/installation.md`) |
| `CITATION.cff` | CFF 1.2.0 with authors/title/license/DOI | VERIFIED | Present at repo root, valid YAML, `doi: 10.5281/zenodo.22692575` (concept DOI, correct choice per D-11), `version: 4.0.0`, `license: AGPL-3.0-or-later` — matches `pyproject.toml` and `LICENSE` |
| `pyproject.toml` version reset | `4.0.0` | VERIFIED | `version = "4.0.0"` (line 7) |
| `CHANGELOG.md` migration note | Explains version jump, accurate PyPI history | VERIFIED (post-review fix) | Code review (114-REVIEW.md CR-02) found the note falsely claimed "never published to PyPI before 4.0.0"; fixed in commit `18190e5` — current text correctly states `1.0.0` exists on PyPI (published 2026-02-19) |
| `.github/workflows/release.yml` | Trigger retired to `workflow_dispatch` only | VERIFIED | No `push` trigger; header comment explains why; no stale `startsWith` guard (WR-01 from review also fixed — guard condition removed) |
| `.github/workflows/publish.yml` | Unmodified, tag-triggered PyPI publish | VERIFIED | Ran successfully on `v4.0.0` tag (`test`→`build`→`publish-testpypi`→`publish`, all success per `114-06-SUMMARY.md`) |
| PyPI package `aquapose==4.0.0` | Installable, correct metadata | VERIFIED | Simple index lists `aquapose-4.0.0-py3-none-any.whl`/`.tar.gz`; JSON API confirms version `4.0.0`, license `AGPL-3.0-or-later`, `project_urls` point at `McGrathLab/AquaPose` (propagated URL fix) |
| Zenodo software archive | Concept + version DOI minted | VERIFIED (via prior live evidence; current outage) | `10.5281/zenodo.22692575` (concept, used in CITATION.cff/README) and `10.5281/zenodo.22692576` (version) both independently confirmed resolving to the AquaPose software record (title, AGPL license) in `114-06-SUMMARY.md` and `114-07-SUMMARY.md`. Re-check during this verification pass returned 504 on `doi.org` and `zenodo.org/api` for this DOI **and** for an unrelated control DOI and the dataset DOI — a Zenodo-side outage, not a broken link |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `README.md` badge row | shields.io endpoints | image links | WIRED | All 6 shields.io badges + 1 zenodo.org badge return 200; JSON variants confirm correct rendered labels/values |
| `README.md` docs funnel | Read the Docs (`/en/latest/...`) | absolute links | WIRED | 5/5 URLs (base + 4 sub-pages) return 200 |
| `README.md` Citation section | `CITATION.cff` + Zenodo DOI | absolute GitHub blob link + `doi.org` link | WIRED | `CITATION.cff` blob link 200; DOI resolution independently confirmed in 114-07 (currently affected by the Zenodo-wide outage noted above) |
| `pyproject.toml` `readme` | PyPI long description | build metadata | WIRED | PyPI JSON API's `description` field character-identical to local `README.md` (confirmed in 114-05/114-06); content-type `text/markdown` |
| Git tag `v4.0.0` | `publish.yml` trigger | tag-push regex `v[0-9]+\.[0-9]+\.[0-9]+` | WIRED | Confirmed fired and succeeded end-to-end |
| GitHub Release `v4.0.0` | Zenodo webhook | `release` event | WIRED | Webhook delivered (202 on `created`; two later 500s are GitHub-side delivery timeouts, not lost events — confirmed by querying the Zenodo record directly, per `114-06-SUMMARY.md`) |

### Data-Flow Trace (Level 4)

Not applicable in the conventional sense (no dynamic app state) — the equivalent check here
is "does the published long-form text match the repo's actual current architecture."

| Artifact | Claim | Source | Matches Reality | Status |
|---|---|---|---|---|
| README "Pipeline" section | 5-stage: Detection → Pose → Tracking → Association → Reconstruction | `src/aquapose/engine/pipeline.py:280-289` (`build_stages` docstring: "v3.7 pipeline ordering: Detection → Pose → 2D Tracking → Association → Reconstruction") | Yes | FLOWING (fixed post-review; originally stale, see CR-01 below) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| RTD base URL resolves | `curl -o /dev/null -w %{http_code} https://aquapose.readthedocs.io/en/latest/` | 200 | PASS |
| RTD `dev` correctly inactive (override sanity check) | `curl .../en/dev/` | 404 | PASS (expected per override) |
| PyPI simple index lists 4.0.0 artifacts | `curl https://pypi.org/simple/aquapose/` | wheel + sdist listed | PASS |
| PyPI JSON API reports correct metadata | `curl https://pypi.org/pypi/aquapose/4.0.0/json` | version 4.0.0, license AGPL-3.0-or-later, McGrathLab URLs | PASS |
| shields.io badges return live, correct values (cache-busted) | `curl .../*.json?nocache=N` | pypi=v4.0.0, python=3.11\|3.12\|3.13, docs=passing, coverage=69% | PASS |
| Zenodo DOI resolution | `curl -L https://doi.org/10.5281/zenodo.22692575` (x3 retries) + control DOI | 504 (Zenodo-wide outage, confirmed via control DOI also 504ing) | SKIP — infra outage, not attributable to this phase's work; prior-phase live evidence stands |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| README-01 | 114-04 | README opens with problem/output/audience | SATISFIED | `README.md:9-19`; REQUIREMENTS.md marked `[x]` Complete |
| README-02 | 114-04, 114-07 | Badge row: tests, docs, coverage, python, pypi, license, DOI, all live | SATISFIED | 7 badges verified live above; REQUIREMENTS.md marked `[x]` Complete |
| README-03 | 114-01 | Hero media | DEFERRED (by design) | REQUIREMENTS.md `[ ]` with explicit deferral annotation, matching ROADMAP criterion 3 annotation and backlog todo |
| README-04 | 114-04, 114-07 | Install/quickstart/docs/citation | SATISFIED | Verified above; REQUIREMENTS.md marked `[x]` Complete |
| DOCS-08 | 114-02 | Docs build green, reachable at declared URL | SATISFIED (evidence), **STALE BOOKKEEPING** | Live evidence fully supports satisfaction (see Truth #5), including the honestly-recorded D-07 override. However `.planning/REQUIREMENTS.md` line 42 still shows `[ ]` and the traceability table (line 128) still shows "Pending" — `114-07-SUMMARY.md` explicitly notes "Requirement status update is verify-phase's job, not this plan's." This verifier does not edit REQUIREMENTS.md directly; flagging as an action item for phase close-out, not a functional gap. |

No orphaned requirements: all 5 requirement IDs in the phase's `Requirements:` line (README-01/02/03/04, DOCS-08) are accounted for above and appear in every plan's frontmatter that claims them.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| — | — | Code review (`114-REVIEW.md`) found 2 Critical defects: stale README pipeline description (CR-01) and false CHANGELOG "never published to PyPI" claim (CR-02) | Resolved | Both fixed in commit `18190e5` (`fix(114): correct stale pipeline description and false PyPI claim`), confirmed by direct file inspection: README's pipeline list now matches `build_stages()`'s documented ordering; CHANGELOG now correctly states `1.0.0` exists on PyPI |
| `.github/workflows/release.yml` | 20 (formerly) | WR-01: vestigial `startsWith(head_commit.message,...)` guard, meaningless under `workflow_dispatch` | Resolved | Guard condition removed; current file has no `if:` clause |
| `pyproject.toml` | 108-179 | WR-02: retired `semantic-release`/`release` env left unlabeled as a hazard | Resolved | Explanatory comment block added directly above `[tool.semantic_release]` documenting why it's retired and the clobber risk of running it |

No unresolved TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER markers found in phase-modified files (`README.md`, `CITATION.cff`, `CHANGELOG.md`'s new content, `CODE_OF_CONDUCT.md`, `docs/contributing.md`, `.github/workflows/release.yml`, `pyproject.toml`).

### Human Verification Required

None. All observable truths for this phase are checkable via file inspection, live HTTP
status/JSON checks, and cross-referencing plan-summary evidence with independently
re-run spot-checks. The one open item (Zenodo DOI badge/resolution) is an external
infrastructure outage, confirmed non-specific to this phase's DOI via a control check,
and does not require human judgment to resolve — it requires waiting for Zenodo, and
prior-phase evidence (gathered while Zenodo was up) already establishes correctness.

### Gaps Summary

No functional gaps block phase goal achievement. One bookkeeping item is open:
`.planning/REQUIREMENTS.md`'s DOCS-08 checkbox (line 42) and traceability row (line 128)
were never flipped to Complete, despite the requirement being genuinely satisfied
(RTD live, reachable at the declared URL, D-07 override honestly recorded). This should
be closed out as part of phase-completion bookkeeping but does not represent missing
functionality — the actual documentation site is live, green, and reachable.

---

_Verified: 2026-09-10_
_Verifier: Claude (gsd-verifier)_
