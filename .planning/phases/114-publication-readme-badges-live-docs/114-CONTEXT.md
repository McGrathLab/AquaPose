# Phase 114: Publication — README, Badges, Live Docs - Context

**Gathered:** 2026-09-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the repo's landing surface publication-ready so an outside researcher who
has never heard of AquaPose understands it, trusts it, and can install, run, and
cite it. Delivers **README-01**, **README-02**, **README-04**, **DOCS-08** —
plus the two Phase 113 carry-ins that block them (PyPI publication, stale
`tlancaster6` URLs).

Concrete deliverables:

1. **A rewritten `README.md`** — a tight landing page: badge row, what-problem /
   what-you-get / who-it's-for opening, minimal quick start, links out to Read
   the Docs, citation pointer, license.
2. **A green badge row** — tests, docs, coverage, Python versions, PyPI version,
   license, Zenodo DOI — each backed by something that is actually live.
3. **A first PyPI release, `v4.0.0`** — which makes the `pip install aquapose`
   that Phase 113 already shipped into the docs true, and makes the PyPI badge
   resolve.
4. **A software DOI** — minted via Zenodo↔GitHub release integration, distinct
   from the existing *dataset* DOI.
5. **`CITATION.cff`** — drives GitHub's "Cite this repository" button and feeds
   Zenodo's release metadata.
6. **Read the Docs live from `dev`** — project activated, building green, and
   reachable at the URL already declared in `pyproject.toml`.

**Explicitly NOT this phase (scope fence):**

- **Hero media (README-03)** — dropped by user decision during this discussion.
  See `<deferred>`. Success criterion 3 in ROADMAP.md and requirement README-03
  in REQUIREMENTS.md must be **marked deferred, not deleted**, and a backlog
  todo filed.
- **TestPyPI dry run** — the user reversed an earlier decision and chose to
  publish straight to PyPI. See D-02.
- The ~829 historical `tlancaster6` links in `CHANGELOG.md` (D-13).
- Any doc *content* work — Installation, Concepts, Tutorial (Phase 113), CLI and
  config reference (Phase 112), API reference (Phase 110) all stay as-is. This
  phase links to them, it does not rewrite them.
- Any pipeline behavior change. This is a publication milestone.
- The GUIDEBOOK §§3/4/7/8/14 drift — see Reviewed Todos.

</domain>

<decisions>
## Implementation Decisions

### PyPI publication and versioning

- **D-01:** **First PyPI version is `v4.0.0`**, aligning the package version to
  the GSD milestone (v4.0 Publication). The repo currently carries two
  incompatible schemes: `pyproject.toml` is at `1.2.0-dev.6` (driven by
  python-semantic-release, `pyproject.toml:156-166`) while the git tags read
  `v3.4 … v3.9` (milestone numbers — and note **none of those tags match
  `publish.yml`'s `v[0-9]+.[0-9]+.[0-9]+` trigger**, which is why nothing has
  ever published). Requires a **one-time python-semantic-release version reset**
  to `4.0.0` and a `CHANGELOG.md` note explaining the jump from 1.2.0-dev.
- **D-02:** **Publish straight to PyPI — no TestPyPI dry run.** *(Supersedes an
  earlier in-discussion selection of "TestPyPI first, then real"; the user
  reversed it when the sequencing was laid out.)* **Accepted risk, stated to the
  user and accepted:** PyPI filenames are immutable, so a bad first upload cannot
  be replaced — it would burn `v4.0.0` and force a `v4.0.1`. The planner should
  compensate with pre-tag local verification (build the sdist+wheel, check
  `twine check`, confirm the README renders as PyPI long-description, install the
  built wheel into a clean env) rather than with a TestPyPI round trip.
- **D-03:** The existing `publish.yml` release path is used **unmodified** — no
  new `workflow_dispatch` TestPyPI job. Tagging `v4.0.0` is the trigger.

### Badge row

- **D-04:** Badge row covers **tests, docs, coverage, Python versions, PyPI
  version, license, Zenodo DOI** (README-02). Every badge must be backed by
  something live before it ships — no aspirational badges.
- **D-05:** **Coverage: live Codecov badge showing whatever it actually reads.**
  No `codecov.yml` floor/target is added this phase. `test.yml:38-44` already
  uploads with `fail_ci_if_error: false` and a `CODECOV_TOKEN` secret, but
  **whether the repo is linked on codecov.io is unverified** — the planner must
  treat "confirm the Codecov project exists and has received an upload" as a
  human-gated precondition, not an assumption.
- **D-06:** Badge providers, ordering, and style were **not** discussed — Claude's
  discretion (see below).

### Read the Docs (DOCS-08)

- **D-07:** **Activate the RTD project and point the default version at `dev`.**
  Verify the build goes green and the site resolves at
  `https://aquapose.readthedocs.io` (already declared at `pyproject.toml:53`).
- **D-08:** **No `pyproject.toml` or `.readthedocs.yaml` change is needed for
  build weight.** A correction surfaced during discussion: the `docs` hatch env
  is already `detached = true` with only Sphinx + extensions + numpy
  (`pyproject.toml:88-103`), so `hatch run docs:build` on RTD never installs the
  project or torch. The user's "switch to a lean docs env" choice is already the
  live state. Do **not** re-plan a lean-env migration.

### Citation and DOI

- **D-09:** **Mint a software DOI** via Zenodo's GitHub-release integration, so
  tagging `v4.0.0` auto-archives the source. The existing
  **`10.5281/zenodo.22264079` is the *dataset* DOI** (Phase 111's tutorial
  deposit: videos, models, calibration, reference outputs) and **stays with the
  tutorial page** — it must not be repurposed as the project DOI.
- **D-10:** **`CITATION.cff` only** — no BibTeX block in the README. The `.cff`
  at repo root drives GitHub's "Cite this repository" button *and* feeds Zenodo's
  archive metadata, so it is the single source of truth. The README links to it
  rather than duplicating a citation. **Note:** the existing BibTeX block at
  `docs/getting-started/tutorial.md:85` cites the *dataset* and is correct as-is
  — leave it, but check it stays consistent.
- **D-11:** **Two-pass DOI sequencing** — the DOI is circular (Zenodo mints only
  after the release publishes, but the release snapshot is what Zenodo reads
  metadata from; Zenodo's "reserve a DOI" only works on manually-created drafts,
  not the webhook path). Resolution:
  - **Pass A:** write `CITATION.cff` with authors/title/license and **no DOI**;
    enable the Zenodo↔GitHub webhook; cut and publish `v4.0.0` → Zenodo mints a
    **concept DOI** (stable across all future versions) and a version DOI.
  - **Pass B:** backfill the **concept DOI** into `CITATION.cff` and the README
    badge; commit post-tag.
  - Accepted consequence: the `v4.0.0` tagged snapshot does not itself carry the
    DOI. The concept DOI never changes again, so this is a one-time cost.

### README structure

- **D-12:** **Tight landing page that funnels to Read the Docs.** Contents:
  badge row → one-paragraph what problem / what you get (3D midlines and
  kinematics) / who it's for → minimal quick start → links to Installation,
  Concepts, Tutorial, and API reference on RTD → citation pointer → license.
  **Move out of the README:** the `Development` section and the `GPU Support`
  section (the latter is now **factually wrong** — Phase 113's D-08 removed the
  cu121 pin and deferred torch installation to pytorch.org). Development content
  goes to `docs/contributing.md`; GPU/torch content belongs in the Phase 113
  install guide, which should already cover it — **verify before moving, don't
  duplicate**. Nothing is duplicated between README and docs, so nothing drifts.

### Repo hygiene carry-in

- **D-13:** **Fix the stale `tlancaster6` GitHub URLs in the two files a visitor
  actually reads** — `CODE_OF_CONDUCT.md` (1 occurrence) and
  `docs/contributing.md` (1 occurrence) — pointing them at `McGrathLab/AquaPose`.
  **Leave the ~829 historical links in `CHANGELOG.md` alone**: they are a
  historical record and GitHub redirects renamed repos.

### Claude's Discretion

- Badge providers (shields.io vs native GitHub/Codecov/RTD badges), badge
  ordering, and style/flat-square choices — not discussed, planner's call.
- Whether the tests badge points at `test.yml` on `dev` or on `main`, and whether
  the `typecheck` job earns its own badge — not discussed.
- The exact wording and length of the README's opening framing paragraph, within
  the D-12 structure.
- Whether RTD also publishes a `stable` version tracking the `v4.0.0` tag
  alongside the `dev` default — not discussed; `dev` as default is locked (D-07).
- The precise pre-tag verification checklist compensating for D-02's no-TestPyPI
  risk.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §"Phase 114: Publication — README, Badges, Live Docs" —
  goal, dependencies (Phases 111 and 113), and the 5 success criteria.
  **Criterion 3 (hero media) is deferred by this discussion** — see `<deferred>`.
- `.planning/REQUIREMENTS.md` — README-01, README-02, README-04, DOCS-08 are in
  scope; **README-03 is deferred**. Also records the QA-02/QA-06 preconditions
  (green suite, green typecheck) that make the badge row honest.
- `.planning/STATE.md` — confirms both Phase 114 dependencies are closed:
  113.2's green CI typecheck and 113's minted dataset DOI.

### Prior-phase decisions this phase inherits
- `.planning/phases/113-concepts-tutorial/113-CONTEXT.md` — D-09 (docs already
  say `pip install aquapose`, accepted risk explicitly deferred to this phase),
  D-08 (cu121 pin removed → README's GPU section is stale), and the scope fence
  that assigns README/badges/hero/citation/RTD **and PyPI publication** to 114.
  Also lists the `tlancaster6` URL cleanup as deferred here.
- `.planning/phases/111-example-dataset-reference-outputs/111-CONTEXT.md` — the
  Zenodo dataset deposit's contents and licensing; establishes that
  `10.5281/zenodo.22264079` is a *data* deposit.
- `.planning/phases/111-example-dataset-reference-outputs/111-03-SUMMARY.md` —
  the deposit tree as shipped (`reference_outputs/{outputs.h5,
  animation_3d.html, overlay_mosaic.mp4, timing.txt}`); the source assets a
  future hero-media phase would draw from.

### Files this phase modifies
- `README.md` — 66 lines today; a commented-out docs link at the tail, no
  badges, and a factually wrong `GPU Support` section.
- `pyproject.toml` — `version` (line 7), `[project.urls]` (51-55),
  `[tool.hatch.envs.docs]` (88-106, **already lean — do not change**),
  `[tool.semantic_release]` (156-166, needs the one-time 4.0.0 reset).
- `.github/workflows/publish.yml` — the `v[0-9]+.[0-9]+.[0-9]+` tag trigger used
  unmodified (D-03).
- `.github/workflows/test.yml:38-44` — the existing Codecov upload backing D-05.
- `.readthedocs.yaml` — exists and is correct; the work is activating the RTD
  project, not editing this file.
- `CITATION.cff` — **does not exist yet**; created by D-10.
- `CODE_OF_CONDUCT.md`, `docs/contributing.md` — the D-13 URL fixes.
- `docs/getting-started/tutorial.md:40,45,85` — existing dataset-DOI references;
  must stay pointed at the dataset DOI, not the new software DOI.

### Human-gated steps (cannot be automated by an executor)
- Confirming/activating the **Codecov** project link (D-05).
- Activating the **Read the Docs** project and setting the default version
  (D-07).
- Enabling the **Zenodo↔GitHub** release integration (D-09, D-11 Pass A).
- Creating **PyPI** credentials/trusted publishing for `publish.yml` (D-02).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`.github/workflows/publish.yml`** — a complete test → build → publish chain
  already gated on full-release tags. Nothing to build; just needs a matching
  tag and credentials.
- **`.github/workflows/test.yml`** — already emits `--cov --cov-report=xml` and
  uploads to Codecov, so the coverage badge needs no CI work (D-05).
- **`.github/workflows/docs.yml`** — builds docs on push to `main` and `dev`;
  gives the docs badge a target independent of RTD.
- **`.readthedocs.yaml`** + the detached `docs` hatch env — a working, lean docs
  build already exists (D-08).
- **`docs/index.md`** — a `sphinx-design` grid card layout already organizing
  Getting Started / Reference / API / Contributing / Reports. The README's
  funnel links (D-12) should mirror these destinations rather than invent new
  ones.

### Established Patterns
- **`sphinx-build -W --keep-going`** — docs build is warning-as-error
  (`pyproject.toml:106`). Any new cross-link or file added this phase must not
  introduce a warning.
- **Human-gated external publication** — Phases 111 and 113 both handled the
  Zenodo deposit as a blocking `checkpoint:human-action` performed by the
  maintainer in their own authenticated browser session, never as an SDK
  integration. This phase's PyPI/Zenodo/RTD/Codecov steps follow the same
  pattern.
- **AGPL-3.0-or-later** is declared consistently across `LICENSE`,
  `pyproject.toml:11`, and `LICENSING.md` (Phase 108, FOUND-05). The license
  badge and `CITATION.cff` `license:` field must match.

### Integration Points
- `pyproject.toml:53` already declares `Documentation = "https://aquapose.readthedocs.io"`
  — DOCS-08 is satisfied by making that URL resolve, not by changing it.
- The README becomes PyPI's long description (`readme = "README.md"`,
  `pyproject.toml:9`), so D-12's rewrite is simultaneously the PyPI project page.
  Relative links in the README will break on PyPI — use absolute URLs.
- `CITATION.cff` is read by two consumers (GitHub's cite button, Zenodo's
  archiver), which is what makes the D-11 two-pass ordering necessary.

</code_context>

<specifics>
## Specific Ideas

- The user reversed the TestPyPI decision on seeing the sequencing laid out,
  choosing speed over the safety round-trip. Treat D-02 as deliberate, and put
  the compensating rigor into pre-tag local verification.
- The user chose to drop hero media outright rather than negotiate a cheaper
  version of it — do not reintroduce it as a "small" scope addition.
- "Tight landing page" is the explicit framing for the README: RTD is the real
  documentation, and the README's job is to convert a stranger into a reader of
  it.

</specifics>

<deferred>
## Deferred Ideas

- **Hero media (README-03 + ROADMAP criterion 3)** — dropped from this phase by
  user decision. **Deferred, not deleted:** the planner must mark README-03 as
  deferred in `.planning/REQUIREMENTS.md`, annotate criterion 3 in
  `.planning/ROADMAP.md`, and file a backlog todo. Source assets already exist
  in the Zenodo deposit (`reference_outputs/animation_3d.html`,
  `overlay_mosaic.mp4`) whenever it is picked back up.
- **`codecov.yml` coverage floor/target** — considered under D-05 and not taken;
  the badge is informational this phase, not a gate.
- **A `workflow_dispatch` TestPyPI job in `publish.yml`** — considered under
  D-02/D-03 and not taken. Still a reasonable future addition for later releases.
- **The ~829 historical `tlancaster6` links in `CHANGELOG.md`** — left for a
  future hygiene pass (D-13).
- **An RTD `stable` version tracking release tags** alongside the `dev` default
  — not discussed; a natural follow-up once `v4.0.0` exists.

### Reviewed Todos (not folded)
- **`2026-09-01-upload-yh-tutorial-dataset-to-zenodo.md`** — already completed by
  Phase 113 plan 06 (DOI `10.5281/zenodo.22264079` minted and filled in
  repo-wide). Matched only on stale keywords; should be moved to
  `.planning/todos/done/`.
- **`2026-09-02-guidebook-sections-3-4-7-8-14-drift-beyond-section-6.md`** —
  GUIDEBOOK is human-oriented reference, deliberately left unfixed per the user
  decision recorded in `CLAUDE.md`; not a publication-surface document.
- **`2026-03-12-iterate-only-active-frames-in-reconstruction-per-fish-loop.md`**,
  **`2026-03-12-triangulate-keypoints-directly-instead-of-6-to-15-upsampling.md`**,
  **`2026-02-28-add-per-stage-diagnostic-visualizations.md`**,
  **`2026-02-28-extract-frame-status-constants.md`** — pipeline-behavior changes.
  This is a publication milestone; matched on generic keywords only.

</deferred>

---

*Phase: 114-Publication — README, Badges, Live Docs*
*Context gathered: 2026-09-09*
