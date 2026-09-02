---
phase: 113-concepts-tutorial
plan: 07
subsystem: docs
tags: [tutorial, myst, sphinx, zenodo-pending, docs-ia]

requires:
  - phase: 113-concepts-tutorial
    provides: "Plan 05's measured verification run (two-point GPU timing, D-12 statistics comparison, corrected LUT timing) and Plan 03's corrected deposit recipe (bare aquapose run, bare aquapose viz, midlines.h5 naming), both quoted verbatim on the tutorial page; Plan 04's installation/concepts pages this one follows and cross-links into"
provides:
  - "docs/getting-started/tutorial.md: the complete DOCS-07 end-to-end walkthrough (download through interpreted 3D output) with a tolerance-ranged results check, the outputs.h5 schema walk, the D-20 smooth-z post-processing step, and a normal-vs-failure guide"
  - "A completed three-card Getting Started section (installation, concepts, tutorial) wired into docs/getting-started/index.md's grid and toctree"
  - "An explicit, mechanically-greppable <!-- ZENODO-DOI-PENDING --> placeholder at every archive-reference site on the tutorial page, per D-21, with no doi.org link or invented DOI anywhere"
  - "The reopened upload todo updated (not closed) to record that the tutorial is fully written and blocked only on the DOI fill-in pass"
affects: [114-publication]

actuals:
  tokens: 4920
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Author a user-facing page against a deposit that is verified-but-unpublished by placing an explicit, greppable placeholder token at every archive-reference site rather than a fabricated identifier, so a later fill-in pass is mechanical (D-21)"

key-files:
  created:
    - docs/getting-started/tutorial.md
  modified:
    - docs/getting-started/index.md
    - .planning/todos/pending/2026-09-01-upload-yh-tutorial-dataset-to-zenodo.md

key-decisions:
  - "Followed the rescoped plan (D-21, commit 3ca5388) over the plan file's stale Task-1 and Task-3 text: no Zenodo publish task exists, no DOI is cited, and 113-06-SUMMARY.md was correctly treated as intentionally absent."
  - "Overrode Task 3's literal action text ('close the folded todo... move to done/') with the executor's explicit D-21 rescoping instruction to keep the todo open. Updated it in place with a new status section instead of moving it to .planning/todos/done/, since DATA-03 is not satisfied and the Zenodo publish has not happened."
  - "Removed a MyST cross-reference anchor (concepts.md#why-refraction-changes-the-problem) that sphinx-build -W flagged as myst.xref_missing (heading_anchors=0 in conf.py means no auto-generated anchors) -- replaced with a plain page link to concepts.md. Applied under deviation Rule 1 (build-breaking bug) since -W is a hard gate."
  - "Chose to quote D-12's tolerance ranges as a single table (reconstructed %, residual, n_cameras, low-confidence %, fish-per-frame) rather than prose, and to state both measured data points (Plan 05's run and the deposit reference) inline as a range per metric, per Claude's Discretion in 113-CONTEXT.md."

requirements-completed: [DOCS-07]

coverage:
  - id: D1
    description: "docs/getting-started/tutorial.md exists (399 lines) and covers the full path: dataset download, prep generate-luts with the fail-fast LUTs-not-found warning, aquapose run, aquapose viz, a tolerance-ranged results check with a runnable verification snippet, the outputs.h5 schema walk with fish_id identity guidance, the D-20 smooth-z step, a normal-vs-failure section, and the never-downscale closing constraint"
    requirement: "DOCS-07"
    verification:
      - kind: other
        ref: "test -f docs/getting-started/tutorial.md; wc -l -> 399; grep checks for generate-luts, ZENODO-DOI-PENDING, smooth-z, dry-run, _smoothed.h5, -o/--output-dir all pass (recorded in Verification section below)"
        status: pass
    human_judgment: false
  - id: D2
    description: "No doi.org link or invented DOI string appears anywhere on the tutorial page; every archive-reference site instead carries the literal ZENODO-DOI-PENDING token (D-21)"
    requirement: "DOCS-07"
    verification:
      - kind: other
        ref: "grep -q 'doi\\.org' docs/getting-started/tutorial.md fails (exit 1); grep -c 'ZENODO-DOI-PENDING' docs/getting-started/tutorial.md -> 2 (the comment token after the pending-publication note, and the bibtex doi field)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Getting Started section completed with a third Tutorial grid-item-card and toctree entry; docs build stays green under sphinx-build -W --keep-going with all three pages reachable"
    requirement: "DOCS-07"
    verification:
      - kind: other
        ref: "hatch run docs:build -> exit 0; docs/_build/html/getting-started/{installation,concepts,tutorial}.html all exist; grep -c 'grid-item-card' docs/getting-started/index.md -> 3"
        status: pass
    human_judgment: false
  - id: D4
    description: "hatch run test stays green apart from the one pre-existing, already-logged, unrelated failure"
    requirement: "DOCS-07"
    verification:
      - kind: other
        ref: "hatch run test -> 1379 passed, 1 pre-existing failure (test_pseudo_label_cli.py::TestGenerateCommand::test_generates_merged_obb_and_separate_pose, logged in deferred-items.md by Plan 01/confirmed unrelated by Plan 05), 3 skipped"
        status: pass
    human_judgment: false
  - id: D5
    description: "Every numeric expectation on the tutorial page traces to a source (Plan 05 measurement or deposit reference); the boundary-value sentence, the fish_id identity sentence, and the normal-vs-not section headings are all present verbatim"
    requirement: "DOCS-07"
    verification: []
    human_judgment: true
    rationale: "Traceability of prose claims to source data is a documentation-accuracy judgment, not something a unit test can verify -- the tracing table and verbatim quotes are recorded below in this SUMMARY for human/reviewer confirmation."

duration: ~14min
completed: 2026-09-02
status: complete
---

# Phase 113 Plan 07: End-to-End Tutorial Page Summary

**Authored `docs/getting-started/tutorial.md` — a 399-line, ten-step walkthrough from downloading the (not-yet-published) tutorial dataset through an interpreted 3D fish midline, quoting only measured numbers from Plan 05's verification run and the deposit's reference outputs, with every archive-reference site carrying an explicit `<!-- ZENODO-DOI-PENDING -->` placeholder instead of a fabricated DOI, and no `doi.org` link anywhere on the page.**

## Performance

- **Duration:** ~14 min
- **Started:** 2026-09-02T13:48:00Z (approx.)
- **Completed:** 2026-09-02T14:02:19Z
- **Tasks:** 2
- **Files modified:** 3 (1 created, 2 modified)

## Accomplishments

- Wrote `docs/getting-started/tutorial.md` (399 lines) covering: hardware/disk expectations with both D-15 GPU timing data points; getting the dataset with a visible "pending publication" admonition and a placeholder-guarded citation block; the one-time `prep generate-luts` step and its fail-fast `LUTs not found` guard; `aquapose run` (no `--config` flag, CWD-upward resolution, `-v`/`--max-chunks` named); `aquapose viz` (all three real outputs named, `detections` skip explained); a D-12 tolerance-ranged results table plus a runnable Python verification snippet against a reader's own `midlines.h5`; the real `outputs.h5` schema walk with all four quality fields and an explicit `fish_id`-not-slot-order identity statement; the full D-20 `smooth-z` step (copy-not-in-place write path, automatic `viz` preference for smoothed files, the `-o` side-by-side comparison recipe, and the one-way "no flag back to unsmoothed" edge); a normal-vs-genuine-failure section; and the closing never-downscale constraint for a reader's own footage.
- Verified every quoted number against `113-05-SUMMARY.md` and the deposit's `reference_outputs/` — none estimated (see traceability table below).
- Completed the Getting Started section: added the third `Tutorial` grid-item-card and toctree entry to `docs/getting-started/index.md` (now 3 cards, matching `installation`/`concepts` syntax exactly). Confirmed `docs/index.md`'s root Getting Started card description ("Install AquaPose, understand the pipeline, and run the tutorial dataset end-to-end.") already accurately describes all three pages — left unchanged.
- Fixed a build-breaking MyST cross-reference (`concepts.md#why-refraction-changes-the-problem`) that `sphinx-build -W` flagged as `myst.xref_missing` — `conf.py` sets `heading_anchors=0`, so no such anchor exists. Replaced with a plain link to the page.
- Confirmed `hatch run docs:build` exits 0 with zero warnings and all three Getting Started HTML pages present.
- Confirmed `hatch run test` stays at 1379 passed / 1 pre-existing unrelated failure / 3 skipped — no regression introduced.
- Updated (not closed) `.planning/todos/pending/2026-09-01-upload-yh-tutorial-dataset-to-zenodo.md` per D-21: added a status section recording that the tutorial is now fully written and blocked only on the DOI fill-in pass. Confirmed `.planning/todos/pending/2026-09-02-fix-basedpyright-typecheck-backlog.md` (D-19) remains untouched and pending.

## Task Commits

1. **Task 2: Author the end-to-end tutorial against the published dataset (D-11, D-12, D-13, D-15)** - `e5a79e9` (feat)
2. **Task 3: Complete the Getting Started section and keep the folded upload todo open (D-21)** - `7be960d` (docs)

**Plan metadata:** (this commit, docs-only)

*Note: this plan's Task 1 (Zenodo upload/publish) was removed from the plan file itself by the D-21 rescoping commit `3ca5388`, before this executor run began — there is no Task 1 to report on.*

## Files Created/Modified

- `docs/getting-started/tutorial.md` - New: the complete end-to-end tutorial (399 lines, 10 numbered sections)
- `docs/getting-started/index.md` - Added the third Tutorial grid-item-card and toctree entry
- `.planning/todos/pending/2026-09-01-upload-yh-tutorial-dataset-to-zenodo.md` - Appended a status update recording the tutorial is written and awaiting only the DOI; left in `pending/` per D-21

## Decisions Made

See `key-decisions` in frontmatter. In short: followed the rescoped plan (D-21) over stale plan text that still described closing the todo and citing a DOI; fixed one build-breaking cross-reference; chose a table format for the D-12 tolerance ranges.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed a MyST cross-reference anchor that does not exist under this project's Sphinx config**
- **Found during:** Task 2, first `hatch run docs:build` after authoring the page.
- **Issue:** `[Concepts](concepts.md#why-refraction-changes-the-problem)` produced `WARNING: local id not found in doc 'getting-started/concepts': 'why-refraction-changes-the-problem' [myst.xref_missing]`, which fails the build under `-W`. `conf.py` sets `heading_anchors=0`, so MyST does not auto-generate heading anchors on this project's narrative pages, unlike some other MyST configurations.
- **Fix:** Changed the link to a plain `[Concepts](concepts.md)` page reference.
- **Files modified:** `docs/getting-started/tutorial.md`
- **Verification:** `hatch run docs:build` — RED (1 xref warning) before the fix, GREEN (0 warnings) after, confirmed with a full `rm -rf docs/_build` clean rebuild.
- **Committed in:** `e5a79e9` (Task 2 commit).

---

**Total deviations:** 1 auto-fixed (Rule 1 - build-breaking cross-reference)
**Impact on plan:** Necessary to keep `sphinx-build -W --keep-going` green, which both this plan and the phase's inherited gate require. No scope creep: the fix touches one line in the file this task already owns.

### Plan-Text Corrections (not Rule 1-4 deviations — following explicit rescoping instructions over stale plan prose)

The plan file (`113-07-PLAN.md`) still contains prose from before the D-21 rescoping commit (`3ca5388`) that was not fully scrubbed:

- **Task 2's `<verify>` automated block** includes `grep -q 'doi.org' docs/getting-started/tutorial.md` as a required-pass condition, directly contradicting the same task's own `<acceptance_criteria>` ("`grep -q 'doi\.org'` ... must FAIL") and D-21 in CONTEXT.md. Followed the acceptance criteria and D-21 (no `doi.org` anywhere) — this is the correct, current requirement; the `<verify>` line is leftover from before the rescoping and was not run literally.
- **Task 2's `<read_first>`** references `113-06-SUMMARY.md` for "the DOI and record URL to cite" — that file does not exist by design (D-21); skipped, as instructed by the executor's `<critical_scope_change>`.
- **Task 3's `<action>`** instructs moving the upload todo to `.planning/todos/done/` and recording a DOI in the completion note. This directly contradicts D-21 and the executor's explicit instruction to keep the todo open. Followed D-21: the todo was updated in place under `.planning/todos/pending/`, not moved.

None of these are treated as plan deviations requiring a fix-and-verify cycle — they are stale prose in the plan file from before its own rescoping commit, and the correct behavior (per the plan's own frontmatter `must_haves`, the executor's rescoping brief, and D-21) was followed instead.

## Issues Encountered

None beyond the documented deviation above.

## Known Stubs

None — the `<!-- ZENODO-DOI-PENDING -->` placeholders are not stubs in the broken-windows sense; they are the deliberate, plan-mandated (D-21) output of this task, tracked by the still-open todo `2026-09-01-upload-yh-tutorial-dataset-to-zenodo.md` rather than by a new ledger entry.

## Threat Flags

None new. T-113-26 (spoofing via dataset download link) is mitigated by construction: the page contains no `doi.org` link or download URL at all while the record is unpublished, only the placeholder token and an instruction to obtain the deposit directly from the maintainers. T-113-27 (repudiation of quoted expected results) is mitigated by the traceability table below, sourced entirely from `113-05-SUMMARY.md` and the deposit's `reference_outputs/`. T-113-28 (never-downscale constraint) is restated in tutorial step 10 with the reason (1600x1200-bound calibration).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The Getting Started section (DOCS-03/04/07) is now complete: three pages, three cards, clean `sphinx-build -W --keep-going`.
- DATA-03 remains deliberately unsatisfied, per D-21 — do not mark it complete. The path to closing it is unchanged and recorded in the reopened todo: fix the two `calibrate-keypoints` bugs, re-run `113-06-PLAN.md`, publish, then fill every `ZENODO-DOI-PENDING` site (`grep -rn 'ZENODO-DOI-PENDING' docs/` finds all of them on this page; the deposit README's own placeholder is a separate, already-tracked site).
- Phase 114 (Publication) can proceed on PyPI publication and the README refresh independent of the Zenodo DOI; the DOI fill-in itself is not gated on Phase 114 and can happen whenever the `calibrate-keypoints` bugs are fixed.

## Numeric Traceability Table (acceptance criterion)

Every figure quoted on the tutorial page, traced to its source:

| Figure on the page | Source |
|---|---|
| Pipeline 786.45 s / viz 150.85 s / total 937.30 s, GTX 1660 SUPER, 6.4 GB | `113-05-SUMMARY.md` "Two-Point Timing Range" table, deposit reference column (originally `aquapose-tutorial-data/reference_outputs/timing.txt`) |
| Pipeline 224 s / viz 85 s / total 309 s, RTX 4070 Ti | `113-05-SUMMARY.md` "Two-Point Timing Range" table, this-run column |
| Dataset size 215 MB | `113-CONTEXT.md` `<domain>`/`<canonical_refs>` (Phase 111 deposit size, unchanged) |
| LUT disk ~600 MB | `113-05-SUMMARY.md` Accomplishments ("`geometry/luts/` measured 597 MB") |
| LUT generation 7 s (RTX 4070 Ti); "2-5 min" disproven | `113-05-SUMMARY.md` Command Sequence table + Deviation Log #1 |
| 22 files in `checksums.sha256` | `113-05-SUMMARY.md` coverage D6 / directly re-confirmed via `wc -l aquapose-tutorial-data/checksums.sha256` (22) |
| ~95% fish-frames reconstructed (95.2% / 95.9%) | `113-05-SUMMARY.md` "Statistics Comparison (D-12)" table |
| Median residual ~3 px (2.82 px / 2.84 px); mean ~3.9 px; p95 ~9.7-9.8 px | `113-05-SUMMARY.md` "Statistics Comparison (D-12)" table |
| Median `n_cameras` 4 of 12, range 0-6 | `113-05-SUMMARY.md` "Statistics Comparison (D-12)" table |
| Low-confidence fraction 3.8% / 4.0% | `113-05-SUMMARY.md` "Statistics Comparison (D-12)" table |
| Fish per frame: min 6 / median 9 / max 9 | `113-05-SUMMARY.md` "Statistics Comparison (D-12)" table |
| `smooth-z` jitter 0.500 cm -> 0.082 cm, 13 fish, 7,769 fish-frames, default sigma=3 | `113-CONTEXT.md` D-20 ("Measured effect ... via `--dry-run`") |
| `outputs.h5`/`midlines.h5` schema (`points (900,9,6,3)`, `control_points (900,9,7,3)`, etc.) | `113-CONTEXT.md` `<code_context>` "Reusable Assets", directly inspected `aquapose-tutorial-data/reference_outputs/outputs.h5` |
| `SPLINE_K=3`, `SPLINE_KNOTS=[0,0,0,0,.25,.5,.75,1,1,1,1]` | `113-CONTEXT.md` `<code_context>`, same source |
| `run` has no `--config` flag; CWD-upward `config.yaml` resolution | `src/aquapose/cli_utils.py::resolve_project` (read directly) |
| `smooth-z` writes `{stem}_smoothed.h5` via `shutil.copy2`, never edits in place | `src/aquapose/cli.py::smooth_z_cmd` (read directly, lines ~845-875) |
| `viz` prefers `midlines_stitched_smoothed.h5` -> `midlines_stitched.h5` -> `midlines_smoothed.h5` -> `midlines.h5` | `src/aquapose/evaluation/viz/_loader.py::resolve_h5_path` (read directly, line ~151) |
| `viz` outputs `animation_3d.html`, `overlay_mosaic.mp4`, `association_mosaic.mp4`; `detections` skipped by default | `113-05-SUMMARY.md` Step 3 output transcript, Run Directory File Listing, Deviation Log #6 |
| LUTs-not-found fail-fast error text | `src/aquapose/engine/pipeline.py::_check_luts_if_needed` (read directly) |
| Bare `aquapose viz` (not `aquapose viz runs/<dir>`, which double-nests) | `113-03-SUMMARY.md` (confirmed empirically via `resolve_run()`) |
| `aquapose run` writes `midlines.h5`, not `outputs.h5` | `113-03-SUMMARY.md` Decision #2 |
| 1600x1200 capture resolution, never spatially downscale | `113-CONTEXT.md` `<specifics>` "Hard constraint" |
| Association clustering-count WARNING and per-chunk "more dropped than kept" are expected, not defects | `113-05-SUMMARY.md` Deviation Log #3, #4 |

## Verbatim Required Quotes (acceptance criterion)

**Boundary-value sentence** (tutorial.md, step 6): "**Landing exactly on a quoted boundary counts as a pass, not a failure** — for example, a median reprojection residual of exactly the quoted figure, or a frame with exactly the minimum quoted number of fish visible, is within expectation, not a sign that something regressed."

**`fish_id` identity sentence** (tutorial.md, step 7): "**Identity comes from `fish_id`, not from position.** A fish's slot index within a frame (the second axis, 0-8) is not a stable identity across frames — a given fish can occupy slot 2 in one frame and slot 5 in the next. Always look up a fish by its `fish_id` value, never by row order."

**Partial-observability section headings** (tutorial.md, step 9, "What is normal and what is not"): `**Normal, expected outcomes:**` / `**Genuine signs of a problem**, by contrast:`

**Tutorial section heading list** (10 top-level sections): "1. Before you start" / "2. Get the dataset" / "3. Generate the refractive lookup tables" / "4. Run the pipeline" / "5. Visualize" / "6. Check your results" / "7. Read the output" / "8. Reduce z jitter with `smooth-z`" / "9. What is normal and what is not" / "10. Using your own footage"

**Tolerance wording chosen** (Claude's Discretion per CONTEXT.md): a single Markdown table in step 6 pairing each metric with a plain-English approximate value ("roughly", "around", "a few percent") followed by the parenthetical exact two-point measurement (e.g. "measured 95.2% and 95.9%"), so a reader gets both the intuitive range and the underlying precision without either number reading as an exact target.

## Self-Check: PASSED

- FOUND: docs/getting-started/tutorial.md (399 lines)
- FOUND: docs/getting-started/index.md (modified, 3 grid-item-cards, 3 toctree entries)
- FOUND: .planning/todos/pending/2026-09-01-upload-yh-tutorial-dataset-to-zenodo.md (modified, still in pending/)
- FOUND commit: e5a79e9
- FOUND commit: 7be960d
- CONFIRMED: grep -c 'ZENODO-DOI-PENDING' docs/getting-started/tutorial.md >= 1 (2 occurrences)
- CONFIRMED: grep -q 'doi\.org' docs/getting-started/tutorial.md FAILS (exit 1, no match)
- CONFIRMED: hatch run docs:build -> exit 0, 0 warnings, docs/_build/html/getting-started/{installation,concepts,tutorial}.html all exist
- CONFIRMED: grep -c 'grid-item-card' docs/getting-started/index.md -> 3
- CONFIRMED: hatch run test -> 1379 passed, 1 pre-existing unrelated failure, 3 skipped
- CONFIRMED: test -f .planning/todos/pending/2026-09-02-fix-basedpyright-typecheck-backlog.md succeeds (D-19 untouched)
- CONFIRMED: test -f .planning/todos/pending/2026-09-01-upload-yh-tutorial-dataset-to-zenodo.md succeeds (kept open per D-21, not moved to done/)

---
*Phase: 113-concepts-tutorial*
*Completed: 2026-09-02*
