# Deferred Items — Phase 113

Out-of-scope discoveries logged during execution but not fixed (per executor
scope-boundary rule: only auto-fix issues directly caused by the current
task's changes).

## Plan 01, Task 2

- **`tests/unit/training/test_pseudo_label_cli.py::TestGenerateCommand::test_generates_merged_obb_and_separate_pose`**
  fails on `dev` independent of this plan's changes. Assertion
  `assert len(parts) == 9  # cls + 4 corners x 2` receives 18 parts instead of
  9 — an OBB label-content-format mismatch in `training/pseudo_label_cli.py`
  or its test fixture, unrelated to `pyproject.toml`'s wheel-index pin.
  Confirmed pre-existing by reverting the `pyproject.toml` edit and
  re-running the single test in isolation: identical failure before and
  after. Out of scope for a documentation phase; not fixed here.

## Plan 04, Task 1/2

- **`GUIDEBOOK.md` §6 "Pipeline Stages" describes a stale pipeline order/shape.**
  It states the order as Detection → 2D Tracking → Cross-Camera Association →
  Midline → Reconstruction, with "Midline" as Stage 4 (running after
  association) offering swappable `segment_then_extract` / `direct_pose`
  backends. The actual v3.7+ pipeline (confirmed via
  `src/aquapose/engine/pipeline.py::build_stages`'s own docstring, the Phase
  110 tier-one API page titles in `docs/api/core/*.rst`, and each stage
  module's docstring) is Detection → Pose (raw keypoint/midline extraction,
  Stage 2) → Tracking (2D, per-camera, Stage 3) → Association (cross-camera,
  Stage 4) → Reconstruction (Stage 5). The segmentation midline backend was
  removed entirely in v3.7; midline extraction now happens via the Pose stage
  *before* tracking/association, not via a dedicated stage *after* them.
  `docs/getting-started/concepts.md` was written against the verified current
  source order, not GUIDEBOOK's stale order — see 113-04-SUMMARY.md for the
  full reasoning. GUIDEBOOK.md itself was not corrected (out of scope: it is
  an internal planning document, not touched by this plan's `files_modified`,
  and CLAUDE.md's `discuss-phase` instruction reads it verbatim for future
  phase discussions — a future phase or maintenance task should refresh it).
- **`CLAUDE.md`'s "Domain Conventions" bullets for direct triangulation and
  cross-view identity are also stale**, independent of the state-vector bullet
  this plan corrected. "Direct triangulation: ... RANSAC triangulation ..."
  is superseded by confidence-weighted DLT (v3.1 decision), and "Cross-view
  identity: RANSAC centroid clustering" is superseded by Leiden clustering
  (v2.1 decision) — both per `PROJECT.md`'s Key Decisions table. The plan's
  `<action>` text explicitly scoped this task to only the fish-state-vector
  bullet ("Keep the surrounding Domain Conventions bullets ... exactly as
  they are ... Do not restructure CLAUDE.md or touch any other section of
  it"), so these two bullets were left untouched.
