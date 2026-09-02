# Phase 113: Concepts & Tutorial - Context

**Gathered:** 2026-09-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the **narrative documentation layer** — the install guide (DOCS-03), the
concepts page (DOCS-04), and the end-to-end tutorial against the Zenodo deposit
(DOCS-07) — so a new user can install AquaPose, understand what the pipeline
computes, and run it on real data with confidence in the results.

Phase 112 built the **lookup** surface (CLI + config reference). This phase
builds the **learning** surface. Unlike Phases 110/112 (which were IA and
structuring work over existing docstrings), this phase is genuinely
**prose-writing** — the narrative content does not exist anywhere yet.

**In scope:**
- A new user-facing **"Getting Started"** docs section holding three pages:
  Installation, Concepts, and Tutorial (D-07).
- Correcting the install path: drop the cu121 pin from the default hatch env and
  defer torch installation to pytorch.org (D-08) — a `pyproject.toml` change.
- Two factual corrections to the Zenodo deposit tree **and** to the templates in
  `scripts/package_tutorial_dataset.py` that generate it (D-04, D-05).
- Minting the Zenodo DOI (human step) and writing the tutorial against it (D-03).
- An end-to-end verification run of the tutorial on the extracted deposit (D-14).
- Keeping the docs build green (`sphinx-build -W --keep-going`).
- **Three folded-in CI fixes** (D-16, D-17, D-18) — see "CI green-up" below. Added
  after the main discussion, when the user flagged that the Tests workflow is red
  on `dev`.

**Explicitly NOT this phase (scope fence):**
- README refresh, badge row, hero media, citation block, Read the Docs publish →
  **Phase 114** (README-01..04, DOCS-08).
- **PyPI publication** → **Phase 114**. This phase writes `pip install aquapose`
  as the install step on the user's explicit instruction that 114 follows
  immediately (D-09) — see the accepted risk note there.
- CLI command reference and config field reference → already shipped in
  **Phase 112**; cross-link to them, do not duplicate.
- The API reference module pages from **Phase 110** stay as-is.
- Re-encoding or regenerating the deposit videos/models/reference outputs —
  Phase 111 delivered them and they verify clean (22/22 checksums OK).
- Any pipeline behavior change. This is a publication milestone.
- **The 98-error basedpyright typecheck backlog** → captured as
  `.planning/todos/pending/2026-09-02-fix-basedpyright-typecheck-backlog.md`,
  deliberately NOT folded in (D-19).

</domain>

<decisions>
## Implementation Decisions

### Concepts page (DOCS-04)

- **D-01:** **Document what the pipeline actually computes — drop the
  `{p, ψ, κ, s}` state vector.** DOCS-04 and the ROADMAP SC#2 both require
  explaining a `{p, ψ, κ, s}` state vector, but **no such structure exists in the
  production pipeline.** A grep across `src/` finds only `InitialFishState`
  (`synthetic/trajectory.py:133` — position, `heading_xy`, speed), a synthetic
  trajectory seed, not the same thing. The state vector is a leftover from the
  v1.x differentiable-rendering architecture and survives only in `CLAUDE.md`'s
  "Domain Conventions" section. The current pipeline performs **direct
  triangulation** into B-spline midlines.
  The concepts page must therefore explain the **real** representation:
  arc-length-sampled midline points → B-spline (control points, knot vector,
  degree), as confirmed against the reference `outputs.h5` schema (see
  `<code_context>`).
  **⚠ Requirement discrepancy — do not treat DOCS-04's literal wording as the
  coverage target.** This is the same class of stale-requirement problem as
  Phase 112's "71 config fields" (D-06 there) and Phase 110's non-existent
  `io/video.py`. Record the correction; do not invent a state vector to satisfy
  the requirement text.
- **D-02:** **Refractive projection at intuition depth, not derivation depth.**
  Explain why a flat air-water interface bends rays, why naïve multi-view
  triangulation is therefore wrong underwater, and what AquaPose does instead
  (Snell's law at the interface; LUTs to make it fast). No derivations. Rejected:
  stating Snell's law with the full forward/inverse LUT formulation, and the
  minimal "we handle refraction, see the API" treatment.
- **D-03a:** **Mermaid diagrams only — no image assets.** The 5-stage pipeline
  flow and data flow render as Mermaid blocks. `sphinxcontrib-mermaid` is already
  in the docs env and `GUIDEBOOK.md` §6 has the stage/data-flow table to adapt.
  No `docs/_static/` images, no binary assets, nothing to regenerate. Rejected:
  an authored SVG refraction figure, and embedding the deposit's
  `animation_3d.html` / overlay stills.
- **D-03b:** **Tier-one pipeline only.** Concepts covers the five production
  stages, calibration, and refraction. Training, evaluation, ReID, and
  pseudo-labeling stay in the API reference where Phase 110 already tiered and
  status-labeled them.

### Zenodo deposit & DOI (DOCS-07 prerequisite)

- **D-04:** **Mint the DOI within this phase, as an explicit human checkpoint
  task**, then write the tutorial against the real DOI/URL. Rejected: authoring
  against a `<DOI pending>` placeholder. Rationale: SC#3 says "the published
  dataset", and Phase 114's DOI badge and citation block block on it regardless.
  **This is now unblocked** — the 215 MB deposit was downloaded and extracted to
  `aquapose-tutorial-data/` during this discussion and verifies clean
  (`sha256sum -c` → **22/22 OK**). No regeneration and no `D:/` staging access is
  required. — **Reversibility:** one-way — a minted DOI is a permanent public
  record; a mistake requires publishing a corrected Zenodo *version*, and the
  original DOI keeps resolving to the flawed files forever. This is why D-05
  must land before the upload.
- **D-05:** **Fix the deposit's two factual errors before uploading, then
  re-emit `checksums.sha256`.** Reading the deposit against the actual CLI
  surfaced three defects; two are real and must be fixed:
  1. `aquapose-tutorial-data/config.yaml` (header comment) says
     `aquapose run --config config.yaml`. **There is no `--config` flag** on
     `run` (`src/aquapose/cli.py:41-88`). Config resolves either via `-p NAME`
     or by walking CWD upward for `config.yaml`
     (`src/aquapose/cli_utils.py:33-47`). Correct it to the `cd` + bare
     `aquapose run` form.
  2. `aquapose-tutorial-data/README.md:3` links to
     `github.com/tucklancaster/AquaPose`. The repo is **`McGrathLab/AquaPose`**.
     (A third wrong variant — Phase 109-03 fixed the `pyproject.toml` URLs but
     this file was missed.)
  The third apparent defect — `pip install aquapose` — is **deliberately kept**;
  see D-09. Note that the deposit README's `cd aquapose-tutorial-data &&
  aquapose run` sequence **is correct** as written; only the `config.yaml`
  comment is wrong.
- **D-06:** **Patch the generating templates in
  `scripts/package_tutorial_dataset.py` AND the extracted tree together.** The
  script writes the deposit `README.md` and `config.yaml` from templates, so
  fixing only the tree would let both errors reappear on any regeneration. The
  script is tracked, tested, and is the reproducibility claim behind DATA-01.
  Rejected: tree-only patching, and script-only patching with partial
  regeneration.

### Install guide (DOCS-03)

- **D-07:** **New top-level "Getting Started" docs section** holding
  Installation, Concepts, and Tutorial as three pages — parallel to Phase 112's
  "Reference" section (D-10 there), wired into `docs/index.md`'s card grid and
  the root toctree. All three DOCS-03/04/07 deliverables land in one coherent
  IA. Rejected: three standalone root-level pages, and folding install into the
  tutorial.
- **D-08:** **Drop `UV_EXTRA_INDEX_URL` (cu121) from
  `[tool.hatch.envs.default.env-vars]`; point users to
  <https://pytorch.org/get-started/locally/> for their platform's torch command.**
  User-initiated — the pin was questioned as non-standard practice. Verified
  supporting evidence:
  - **CI has no GPU.** `test.yml` runs `ubuntu-latest` + `windows-latest` across
    Python 3.11/3.12/3.13, and `slow-tests.yml` defaults to `ubuntu-latest`. All
    six matrix jobs currently pull multi-GB CUDA wheels from the cu121 index to
    run CPU tests. Removing the pin makes CI materially lighter and faster.
  - **The pin caps torch.** cu121 is CUDA 12.1; current torch ships
    cu124/cu126/cu128. Pinning the old index constrains version resolution for
    no benefit on a GPU-less CI.
  - **The README already contradicts it** — it tells users to reinstall with
    cu124, which only makes sense if the default were not pinned.
  The install guide then documents: install AquaPose → install torch for your
  platform per pytorch.org → verify with `torch.cuda.is_available()`.
  — **Reversibility:** costly — the change is one line in `pyproject.toml`, but
  it alters what every fresh `hatch env create` produces for every developer and
  all six CI matrix jobs; reverting means re-pinning and re-establishing that
  GPU wheels resolve. Note this session's existing env (torch 2.5.1+cu121, CUDA
  verified working on an RTX 4070 Ti) is unaffected until it is recreated.
- **D-09:** **Keep `pip install aquapose` as the documented install step**, in
  both the deposit README and the docs install guide, even though AquaPose is
  **not on PyPI today**. User decision, stated explicitly: Phase 114 handles the
  PyPI publication and the user plans to do it immediately after this phase —
  "technically untrue at this moment, but will be true shortly."
  **Accepted risk, tracked:** between this phase shipping and 114 publishing,
  the documented install command does not work. If 114 slips, this is the first
  thing a new user hits. See `<deferred>`.
- **D-10:** **Full prerequisites section** in the install guide, covering the
  non-obvious things that actually break a first run:
  - **ffmpeg on PATH** — `aquapose viz` shells out to it for MP4 export.
  - **~600 MB free** for the generated refractive LUTs (not shipped; the
    pipeline **fail-fasts** without them — see D-13), plus 215 MB for the dataset.
  - **GPU footprint** — the reference run fit on a GTX 1660 SUPER (6.4 GB), a
    usable practical floor.

### Tutorial (DOCS-07)

- **D-11:** **The docs tutorial is the long form; the deposit README stays the
  terse recipe.** The deposit README already contains a working short-form
  walkthrough (install → `cd` → `prep generate-luts` → `run` → `viz`). The docs
  tutorial expands each step with what is happening, what to expect, how long it
  takes, and how to read the output. DOCS-07 asks for interpretation, not just
  commands. Rejected: trimming the deposit README to a link (the Zenodo record
  should stay self-contained), and maintaining two identical mirrored copies.
- **D-12:** **Expected results as quoted statistics with tolerance ranges.**
  GPU nondeterminism means a user's run will not match the reference
  bit-for-bit, so express expectations as approximate values a user can check
  their run against. Real measured values from the deposit's `outputs.h5` (see
  `<specifics>`) — e.g. "~95% of fish-frames reconstructed", "median
  reprojection residual ~3 px", "9 fish tracked, 6–9 visible in any given
  frame". Rejected: qualitative-only ("looks right"), and checksum-plus-eyeball.
- **D-13:** **Walk the real `outputs.h5` schema** in the interpretation step —
  this is the payload users came for. Document the `midlines` group as it
  actually exists (verified, see `<code_context>`), including the quality fields
  (`mean_residual`, `n_cameras`, `is_low_confidence`) that let a user judge their
  own run, and show loading and plotting one fish. Rejected: a load-and-plot
  recipe with no schema, and deferring the schema to the API reference.
  The tutorial must also cover the **one-time `aquapose prep generate-luts`
  step** — Phase 111's corrected D-03 established that the pipeline fail-fasts
  with `FileNotFoundError: LUTs not found` if it is skipped.
- **D-14:** **Execute the tutorial end-to-end once during this phase** on the
  extracted deposit (`prep generate-luts` → `run` → `viz`) and correct anything
  that does not match, rather than authoring from the reference outputs and
  spot-checking `--help`. This is the only way SC#3 is actually true, and both
  the deposit and a working GPU are present on this machine now. Expect roughly
  ~13 min pipeline + ~2.5 min viz scaled from the reference hardware.
- **D-15:** **Quote both hardware timings as a range.** The deposit's
  `timing.txt` records 786.45 s pipeline / 150.85 s viz / 937.30 s total on a
  GTX 1660 SUPER; the D-14 verification run will produce a second data point on
  an RTX 4070 Ti. Present both so a user can locate their own GPU between them.
  Rejected: quoting only the deposit reference, and an order-of-magnitude range.

### CI green-up (folded in 2026-09-02)

Raised by the user after the main discussion: the Tests workflow is red on `dev`.
Diagnosed run **33620368943** (commit `497ac5b`). Four distinct failures; three
are folded into this phase, one is deferred (D-19). Windows 3.11 and 3.12 passed;
the Documentation workflow is green.

- **D-16:** **`ruff format` on the two Phase 111 files — ALREADY DONE, commit
  `39a1bf1`.** `scripts/package_tutorial_dataset.py` and
  `tests/scripts/test_package_tutorial_dataset.py` were committed unformatted in
  `9dfa6bf`/`e531009`, so the `pre-commit` CI job fails ("2 files reformatted",
  exit 1). Pure formatting, no semantic change; the 80 packaging tests still
  pass. **No remaining work — do not re-plan this.** Noted because D-06 patches
  the same script and must not reintroduce the drift.
- **D-17:** **Fix the ill-conditioned angular-error metric in
  `tests/unit/calibration/test_luts.py` (both sites, lines ~152 and ~189).**
  This is the `test (ubuntu-latest, 3.12)` failure:
  `test_forward_lut_cast_ray_matches_model` — `assert 0.01978234015405178 < 0.01`.
  **Root cause (verified, not assumed): the test's metric is broken, the LUT is
  fine.** `torch.acos(dot)` on a float32 dot product of two nearly-parallel unit
  vectors is numerically ill-conditioned — `d(acos)/dx → ∞` as `x → 1`. Measured
  locally: the float32 dot lands on exactly `1.0` (max observed `1.0000001192`,
  clamped), so `acos` returns **0.000000°** and the assertion passes *trivially,
  measuring nothing*. On CI a 1-ulp difference puts the dot at ~`1 − 6e-8`, which
  `acos` amplifies to 0.0198°. Computed stably as
  `atan2(‖a×b‖, a·b)` in float64, the **true** max angular error is
  **2.07e-5°** — 500× under the 0.01° threshold.
  **Fix:** compute the angle via `torch.atan2(torch.linalg.cross(a, b).norm(-1),
  (a*b).sum(-1))` in float64. **Keep the 0.01° and 0.1° thresholds unchanged** —
  this is not a tolerance relaxation; the real margin becomes 500×.
  **⚠ Corrects the record on QA-01.** Phase 109-05 reported this test "confirmed
  green (resolved, not skipped, tolerances intact)" and attributed the CI failure
  to a stale "Linux/CI estimate". That conclusion was luck: `acos(1.0) == 0`
  locally. The requirement was never genuinely verified until now.
- **D-18:** **Apply the same stable-angle formula to
  `src/aquapose/calibration/luts.py:439`** (`validate_forward_lut`). Production
  code with the identical `acos(dot)` pattern, whose reported
  `max_angular_error_deg` is therefore float32 rounding noise rather than signal,
  and which **raises `ValueError`** above 0.1°. Verified **not** tutorial-blocking:
  `validate_forward_lut` is only reachable from `calibration/__init__.py`'s
  re-export and `tests/unit/calibration/test_luts.py` — `aquapose prep
  generate-luts` never calls it, so the tutorial's first step (D-13) cannot trip
  it. Folded in anyway because it is the same one-line fix and the function's
  whole purpose is to report a trustworthy number.
- **D-19:** **Do NOT fold in the basedpyright typecheck backlog.** `hatch run
  typecheck` reports **98 errors, 0 warnings**, and the CI `typecheck` job has
  failed on every run examined (2026-09-02 and both 2026-08-17 runs) — a
  long-standing backlog, **not** a regression from the recent push. It spans
  `core/reid/runner.py` (h5py `Dataset`/`Datatype` narrowing), `evaluation/
  stages/smoothing.py` (`float` → `int` params), and `training/reid_training.py`
  (a `ReidConfigLike` protocol that declares writable attributes against frozen
  dataclasses). Far too large and too unrelated for a documentation phase.
  **Captured as** `.planning/todos/pending/2026-09-02-fix-basedpyright-typecheck-backlog.md`
  with the error clusters and a suggested phase shape.
- **Note — D-08 already fixes the largest CI failure.** Three of the six test
  matrix jobs (ubuntu 3.11, ubuntu 3.13, windows 3.13) failed at **Create
  environment**, not at the tests:
  ```
  error: Request failed after 3 retries in 8.5s
    Caused by: Failed to fetch: `https://download.pytorch.org/whl/cu121/ultralytics-thop/`
    Caused by: HTTP status server error (503 Service Unavailable)
  ```
  `UV_EXTRA_INDEX_URL` makes uv query `download.pytorch.org` for **every**
  package — including pure-Python ones like `ultralytics-thop` — so any hiccup on
  that index breaks environment creation. This is independent evidence for D-08
  beyond the wasted-bandwidth argument: the pin is an active flakiness source.

### smooth-z post-processing (folded in 2026-09-02, mid-execution)

**D-20.** The tutorial and the deposit's "How to Reproduce" recipe both gain a
final **`aquapose smooth-z`** step. Reference outputs are **not** regenerated.

Raised by the user after visually inspecting the Plan 05 verification run's
`animation_3d.html` and observing excessive z jitter. Investigation confirmed:

- `aquapose smooth-z` (`src/aquapose/cli.py` `smooth_z_cmd`) already exists and is
  already documented in Phase 112's CLI reference (`docs/reference/cli.rst:97`),
  but appears in **neither** the deposit README recipe nor the Phase 113 tutorial
  plan — a real gap between shipped capability and the documented happy path.
- It works on the tutorial data unchanged. `midlines/centroid_z (900, 9)` is
  present in the verification run's `midlines.h5`, so no `z_denoising` config
  change is needed.
- Measured effect on the verification run, via `aquapose smooth-z --dry-run` at
  the default `--sigma-frames 3`: mean frame-to-frame centroid z jitter
  **0.500 cm → 0.082 cm** across 13 fish and 7769 fish-frames (~6x reduction).

**Why z jitter exists at all:** depth along the camera ray is the
weakest-constrained axis in refractive multi-view reconstruction, so per-frame z
scatters more than x and y. Smoothing is what makes 3D trajectories usable for
downstream kinematics — squarely inside this phase's "confidence in the results"
goal.

**Scope boundary, deliberately drawn:** `regenerate_reference_outputs` in
`scripts/package_tutorial_dataset.py` runs only `aquapose run` then `aquapose viz`
— **no smoothing pass** — so the deposit's shipped `reference_outputs/` are
pre-smoothing. They are **not** regenerated here: the Phase Boundary above fences
"re-encoding or regenerating the deposit videos/models/reference outputs", they
currently verify clean at 22/22, and reopening a Phase 111 artifact immediately
before an irreversible DOI mint is not a trade worth making.

The consequence must be stated in **both** documents rather than left implicit:
the results comparison happens *before* smoothing, so a reader who smooths first
and then compares against `reference_outputs/` does not mistake the improvement
for a divergence.

Ordering: in the tutorial, `smooth-z` lands **after** the results check and schema
walk (new step 8), not in the run→viz sequence. In the deposit README it is
appended as a final recommended step. Both note that it rewrites the HDF5 in place
and that `--dry-run` is the safe first move.

Alternatives considered and rejected: regenerating reference outputs with
smoothing applied (breaches the Phase 111 scope fence, invalidates the current
22/22 verification, adds a GPU cycle before the mint); tutorial-only (leaves
standalone deposit users, who reach the data by DOI and read only its README,
never learning the step exists); deferring entirely (a later docs change cannot
alter an already-minted deposit README).

Applies to: Plan 113-06 Task 3 (deposit README, template and tree together per
D-06) and Plan 113-07 Task 2 (tutorial step 8).

### Claude's Discretion

- Exact page filenames and whether "Getting Started" is a directory
  (`docs/getting-started/`) or flat files; MyST `.md` vs `.rst` per page
  (Phase 112 D-12 established `.md` for narrative, `.rst` where directives are
  needed — narrative pages should be `.md`).
- Ordering of the Getting Started cards in `docs/index.md` relative to the
  existing Reference / API Reference / Contributing / Reports cards.
- Exact Mermaid diagram shapes and how many (stage flow is required; a data-flow
  or identity-model diagram is optional).
- Precise wording of the tolerance ranges in D-12, and which subset of the
  measured statistics to quote.
- How the cu121 removal (D-08) is phrased in the install guide and whether the
  README's existing `nvrtc: error: failed to open libnvrtc-builtins.so`
  troubleshooting note is carried into the install guide's troubleshooting.
- Whether to also correct `CLAUDE.md`'s stale `{p, ψ, κ, s}` "Domain
  Conventions" line while fixing D-01 (small, in the spirit of the phase, but
  not required by any success criterion).

### Folded Todos

- **`.planning/todos/pending/2026-09-01-upload-yh-tutorial-dataset-to-zenodo.md`**
  — "Upload AquaPose YH tutorial dataset to Zenodo and record the DOI"
  (area: publication, match score 0.6). **Folded into scope by D-04.** Original
  problem: Phase 111 assembled and verified the deposit but the manual upload and
  DOI mint were deferred (D-11 there, human-only external publish), leaving a
  `<DOI filled after upload>` placeholder that blocks the Phase 113 tutorial
  citation and the Phase 114 DOI badge. It fits this phase because the tutorial
  cannot honestly claim "the published dataset" without it, and because the
  deposit is now present and verified locally. **Note:** the todo's step 1
  (regenerate the tree from `D:/AquaPose_Zenodo_staging/YH`) is **not needed** —
  the finalized tree was downloaded and verifies 22/22. Its steps 2–5 (Zenodo
  upload, metadata from `zenodo-metadata.json`, publish, record DOI, re-emit
  checksums) apply, amended by D-05/D-06 to fix the two doc errors first.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase requirements & scope
- `.planning/ROADMAP.md` — Phase 113 section (goal + 3 success criteria).
  **⚠ Correction:** SC#2's `{p, ψ, κ, s}` state vector does not exist in the
  codebase — see **D-01**. Document the real B-spline midline representation and
  record the discrepancy; do not invent a state vector to match the wording.
- `.planning/REQUIREMENTS.md` — DOCS-03 (install from written instructions
  including the GPU/CUDA caveat), DOCS-04 (concepts page), DOCS-07 (end-to-end
  tutorial with expected results at each step). Also the **Out of Scope** table
  — "New pipeline capability" is excluded; behavior changes this milestone are
  limited to bug fixes and config-path consolidation (D-08 is scoped as an
  install-path fix under that allowance).

### Prior-phase precedent (build ON this, don't undo it)
- `.planning/phases/112-config-cli-reference/112-CONTEXT.md` — the docs IA this
  phase extends. Especially **D-09** (CLI examples kept generic, with
  dataset-anchored runnable examples explicitly deferred *to this phase*),
  **D-10** (top-level "Reference" section — D-07 here mirrors its shape),
  **D-12** (MyST `.md` for narrative, `.rst` for directives, Furo), and **D-06**
  (the precedent for recording a stale-requirement discrepancy rather than
  obeying it).
- `.planning/phases/111-example-dataset-reference-outputs/111-CONTEXT.md` —
  deposit design and licensing. Especially the **corrected D-03**: LUTs are NOT
  shipped and the pipeline **fail-fasts** without them
  (`engine/pipeline.py::_check_luts_if_needed`), so the tutorial MUST include the
  one-time `aquapose prep generate-luts` step; and **D-12** (data CC-BY-4.0,
  weights labeled AGPL-derived).
- `.planning/phases/111-example-dataset-reference-outputs/111-03-SUMMARY.md` —
  records the deferred Zenodo upload, the 215 MB final tree, the `verify_deposit`
  /`finalize_deposit`/`write_checksums` gate, and the LF-forced manifest.
- `.planning/phases/110-api-reference-docs-tiering/110-CONTEXT.md` — the
  tier-one/tier-two split that **D-03b** relies on to keep research utilities out
  of the concepts page.
- `.planning/GUIDEBOOK.md` — **§6 Pipeline Stages** (the five stages, their
  in/out contracts, the PipelineContext data-flow table, and the Identity Model —
  primary source for the concepts page and the Mermaid diagrams), **§5
  Pre-Pipeline** (frame source, calibration, the forward/inverse refractive LUTs
  — source for D-02 and the LUT prerequisite), **§14 CLI**, and **§2 Core
  Identity**.

### The deposit (present and verified locally)
- `aquapose-tutorial-data/` — the extracted 215 MB Zenodo deposit, `sha256sum -c`
  **22/22 OK**. Contains `videos/` (12 × 30 s), `models/{yolo_obb,yolo_pose}.pt`,
  `geometry/calibration.json`, `config.yaml`, `reference_outputs/`,
  `checksums.sha256`, `zenodo-metadata.json`. Covered by `.gitignore:104` — it is
  intentionally **not** version-controlled.
- `aquapose-tutorial-data/README.md` — the short-form walkthrough D-11 keeps, the
  rig/subject provenance the concepts page can reuse, the licensing breakdown,
  and the citation block whose `<DOI filled after upload>` D-04 fills. **Contains
  the wrong repo URL — see D-05.**
- `aquapose-tutorial-data/config.yaml` — the real working tutorial config.
  **Its header comment names a `--config` flag that does not exist — see D-05.**
- `aquapose-tutorial-data/reference_outputs/timing.txt` — 786.45 s pipeline /
  150.85 s viz / 937.30 s total (GTX 1660 SUPER), the first half of D-15's range.
- `scripts/package_tutorial_dataset.py` — generates the deposit README and
  `config.yaml` from templates; **D-06 patches those templates**. Also holds
  `verify_deposit()`, `finalize_deposit()`, and `write_checksums()` — the last is
  what D-05 re-runs after the fixes.

### Source of truth for the concepts page and install guide
- `src/aquapose/cli.py:41-88` — the `run` command's real option surface (**no
  `--config` flag**; `--mode`, `--set`, `--add-observer`, `--stop-after`,
  `--verbose`, `--max-chunks`).
- `src/aquapose/cli_utils.py:14-47` — `resolve_project()`: `-p NAME` looks under
  `~/aquapose/projects/`, otherwise it walks CWD upward for `config.yaml`. This
  is why the deposit README's `cd` + bare `aquapose run` works.
- `pyproject.toml:69-71` — `[tool.hatch.envs.default.env-vars]`
  `UV_EXTRA_INDEX_URL` (cu121). **D-08 removes this.**
- `.github/workflows/test.yml:14-40` and `.github/workflows/slow-tests.yml:26` —
  the GPU-less CI runners that justify D-08.
- `src/aquapose/synthetic/trajectory.py:133` — `InitialFishState`, the only
  "fish state" in the codebase; a synthetic trajectory seed, **not** the
  `{p, ψ, κ, s}` vector DOCS-04 describes (D-01 evidence).

### Existing docs to extend
- `docs/index.md` — root toctree and card grid; the "Getting Started" section
  card and toctree entry go here (D-07).
- `docs/reference/index.md`, `docs/reference/cli.rst`, `docs/reference/config.md`
  — Phase 112's Reference section. D-07 mirrors its structure; the tutorial and
  install guide should cross-link into these rather than restate options.
- `docs/contributing.md` — already holds the dev-setup commands. Keep the
  developer path there; the new install guide serves *users*, not contributors.
  Note it still links `github.com/tlancaster6/aquapose` (stale, deferred to 114).
- `README.md` — its "GPU Support" section is factually wrong (claims CPU-only
  default, tells users to reinstall with cu124). D-08 resolves the underlying
  cause; the README rewrite itself is **Phase 114**.

### CI green-up (D-16..D-19)
- `.github/workflows/test.yml` — the failing workflow. Jobs: `pre-commit`,
  `typecheck`, and a `test` matrix of {ubuntu,windows}-latest ×
  Python 3.11/3.12/3.13. **No GPU on any runner** (D-08 evidence).
- Failing run: `gh run view 33620368943` (commit `497ac5b`, 2026-09-02).
- `tests/unit/calibration/test_luts.py` lines ~146-155 and ~183-192 — the two
  `acos(dot)` angular-error assertions D-17 replaces.
- `src/aquapose/calibration/luts.py:394-455` — `validate_forward_lut`, the
  production twin D-18 fixes. Docstring already promises `ValueError` above 0.1°.
- `.planning/todos/pending/2026-09-02-fix-basedpyright-typecheck-backlog.md` —
  the deferred typecheck work (D-19), with error clusters and a phase shape.

### Build gate
- `sphinx-build -W --keep-going` must stay clean, via `hatch run docs:build`.
  Inherited hard gate from Phases 110/112.
- `hatch run test` must pass, and the `pre-commit` CI job must pass. The
  `typecheck` job stays red by design this phase (D-19) — do not treat it as a
  phase failure, and do not add `# type: ignore` suppressions to make it green.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`aquapose-tutorial-data/reference_outputs/outputs.h5`** — inspected directly;
  the authoritative schema for D-13. One group, `midlines`, with attrs
  `SPLINE_K=3` and an 11-element `SPLINE_KNOTS` vector
  `[0,0,0,0,.25,.5,.75,1,1,1,1]`, and datasets:
  `points (900,9,6,3)`, `control_points (900,9,7,3)`, `half_widths (900,9,6)`,
  `z_offsets (900,9,6)`, `arc_length (900,9)`, `centroid_z (900,9)`,
  `fish_id (900,9)`, `frame_index (900,)`, `n_cameras (900,9)`,
  `mean_residual (900,9)`, `max_residual (900,9)`, `is_low_confidence (900,9)`.
  This is exactly the "6 anatomical keypoints → B-spline" contract that D-01
  says to document in place of the state vector.
- `aquapose-tutorial-data/reference_outputs/{animation_3d.html,
  overlay_mosaic.mp4}` — the artifacts the tutorial's final step interprets.
- `docs/reference/` (Phase 112) — the structural template for a new user-facing
  docs section: `index.md` with a `grid-item-card` grid plus a hidden toctree.
  D-07's Getting Started section should copy this shape.
- `sphinxcontrib-mermaid` — already in the `[tool.hatch.envs.docs]` dependency
  list, so D-03a needs no new dependency.

### Established Patterns
- Docs are MyST `.md` for narrative + `.rst` where directives are required;
  Furo theme; `suppress_warnings=['ref.python']` in `conf.py` resolves
  re-exported-symbol ambiguity without relaxing `-W`.
- The `docs` hatch env is **detached** and mocks the heavy runtime imports —
  installing the project there would pull CUDA torch, which exceeds Read the Docs
  build limits (`pyproject.toml:78-80`). New narrative pages must not require
  importing the package at build time.
- Config precedence (GUIDEBOOK §11): defaults → YAML → CLI `--set` → freeze.
- Config resolution for the CLI: `-p NAME` under `~/aquapose/projects/`, else
  CWD-upward search for `config.yaml`.

### Integration Points
- New `docs/getting-started/` (or equivalent) wired into `docs/index.md`'s card
  grid and root toctree, ordered ahead of `reference/index`.
- Cross-links from the tutorial into `docs/reference/cli.rst` (command options)
  and `docs/reference/config.md` (field meanings), so the tutorial narrates and
  the reference enumerates.
- `pyproject.toml` `[tool.hatch.envs.default.env-vars]` — the single line D-08
  removes.
- `scripts/package_tutorial_dataset.py` README/config templates — D-06's patch
  site; `tests/scripts/test_package_tutorial_dataset.py` is the existing test
  file to extend.

</code_context>

<specifics>
## Specific Ideas

**Measured reference statistics** (computed from
`aquapose-tutorial-data/reference_outputs/outputs.h5` during this discussion —
these are the real numbers D-12 turns into tolerance ranges):

- 900 frames × 9 fish slots × 6 keypoints, 3D.
- **7711 / 8100 fish-frames reconstructed = 95.2%.**
- **Mean reprojection residual: median 2.84 px**, mean 3.92 px, p95 9.73 px.
  (111-02-SUMMARY quotes 2.75 px median — a slightly different computation over
  a different subset; prefer a "~3 px" range over either exact figure.)
- **Cameras per reconstructed fish: median 4**, range 0–6 (of 12) — a concrete
  illustration of the GUIDEBOOK's "partial observability, 4–5 of 12 cameras"
  claim, useful in the concepts page.
- **4.0% of fish-frames flagged `is_low_confidence`.**
- **Fish visible per frame: 6 min, 9 median, 9 max** — worth calling out so a
  user does not read fewer-than-9 in a frame as a failure.
- Timing: **786.45 s pipeline + 150.85 s viz = 937.30 s** on a GTX 1660 SUPER
  (6.4 GB).

**Deposit provenance** (from `aquapose-tutorial-data/README.md`, reusable in the
concepts page): 12-camera ring rig at ~0.6 m radius over a 2 m cylindrical tank,
cameras straight down through a flat air-water interface (no glass), 30 fps,
1600×1200; 9 cichlids (3 male, 6 female), ~10 cm body length.

**Hard constraint worth restating in the tutorial:** never spatially downscale
video — calibration intrinsics and refractive ray-casting are bound to 1600×1200.

</specifics>

<deferred>
## Deferred Ideas

- **PyPI publication of `aquapose`** → **Phase 114**. This is a *prerequisite for
  D-09 being true*: both the deposit README and the docs install guide will say
  `pip install aquapose` before the package exists on PyPI. User accepted this
  knowingly, planning to publish immediately after this phase. If 114 slips, the
  documented install command is the first thing a new user hits.
- **README refresh, badge row, hero media, citation block, Read the Docs
  publish** → **Phase 114** (README-01..04, DOCS-08). Includes rewriting the
  README's factually wrong "GPU Support" section once D-08 lands.
- **Stale `tlancaster6` URLs** in `CODE_OF_CONDUCT.md` (1), `docs/contributing.md`
  (1), and ~829 historical `CHANGELOG.md` links → already deferred to Phase 114
  by STATE.md. D-05 fixes only the deposit's `tucklancaster` variant, because that
  one is about to be frozen into a permanent Zenodo record.
- **Correcting `CLAUDE.md`'s `{p, ψ, κ, s}` "Domain Conventions" line** — the
  source of the D-01 discrepancy. Listed under Claude's Discretion; small enough
  to fold in, but not required by any success criterion.
- **The 98-error basedpyright typecheck backlog** → own phase, tracked as
  `.planning/todos/pending/2026-09-02-fix-basedpyright-typecheck-backlog.md`
  (D-19). Blocks the honest **README-02 badge row** in Phase 114, so it should be
  scheduled before or alongside 114.

### Reviewed Todos (not folded)

13 of the 14 lexical matches from `todo.match-phase 113` were reviewed and **not
folded** — all matched on generic keywords ("aquapose", "pipeline", "data") and
none concern install, concepts, or tutorial documentation:

- **Add per-stage diagnostic visualizations** (0.6) — pipeline observability.
- **Move LUT generation to pre-pipeline setup** (0.6) — thematically adjacent
  (the tutorial documents the manual `prep generate-luts` step per D-13), but the
  refactor itself is a behavior change, excluded by the milestone's scope fence.
- **Wire frame selection into pseudo-label assembly CLI** (0.6) — training.
- **Fix core import boundary violation in frame_source** (0.6) — core refactor.
- **Generate augmentations on-the-fly at assembly time** (0.6) — training.
- **Adapt pseudo-label pipeline for hard case mining** (0.6) — training.
- **Triangulate keypoints directly instead of 6-to-15 upsampling** (0.6) —
  reconstruction behavior change.
- **Active calibration refinement** (0.4) — calibration algorithm.
- **Extract frame status strings to constants or enum** (0.4) — tracking cleanup.
- **Regenerate golden regression test data for v2.1** (0.4) — test fixtures.
- **Iterate only active frames in reconstruction per-fish loop** (0.4) — perf.
- **Integrate full-frame exclusion masks from AquaMVS** (0.2) — calibration.
- **Speed correlation as second discriminant for association** (0.2) —
  association algorithm.

</deferred>

---

*Phase: 113-concepts-tutorial*
*Context gathered: 2026-09-02*
