---
phase: 113-concepts-tutorial
plan: 03
subsystem: docs
tags: [zenodo, packaging, cli-verification, checksums]

requires:
  - phase: 111-example-dataset-reference-outputs
    provides: "The finalized aquapose-tutorial-data/ deposit tree (215 MB, 22/22 checksums OK) and the write_deposit_config/write_deposit_readme/verify_deposit/finalize_deposit/write_checksums functions this plan corrects and re-runs"
provides:
  - "Corrected write_deposit_config header (bare `aquapose run`, no --config flag)"
  - "Corrected write_deposit_readme repo URL (McGrathLab/AquaPose, not tucklancaster)"
  - "Two additional confirmed-and-corrected README defects discovered by empirical CLI verification: the double-nesting `aquapose viz runs/<run_dir>` form, and the false `generates outputs.h5` claim"
  - "TestDepositDocCorrections regression test class (4 assertions) locking all four corrections against the templates"
  - "Re-emitted 22-file checksums.sha256 for the extracted deposit tree, verified 22/22 OK"
affects: [113-06-zenodo-upload, 113-07-tutorial-page, 114-publication]

actuals:
  tokens: 1200
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Empirical CLI verification before freezing docs into a permanent record: every command claim was checked against the real cli.py/cli_utils.py surface, not assumed correct from prior context"

key-files:
  created: []
  modified:
    - scripts/package_tutorial_dataset.py
    - tests/scripts/test_package_tutorial_dataset.py
    - aquapose-tutorial-data/config.yaml
    - aquapose-tutorial-data/README.md
    - aquapose-tutorial-data/checksums.sha256

key-decisions:
  - "Confirmed the third defect (viz double-nesting) empirically by invoking resolve_run() directly against a temporary project directory: `resolve_run('runs/run_20260306_075925', project_dir)` raised `Run path does not exist: .../runs/runs/run_20260306_075925`, proving the double-nest. Corrected to the bare `aquapose viz` (newest-run) form the plan suggested."
  - "Discovered and fixed a fourth, previously-unlisted defect: the README's 'generates outputs.h5' comment before `aquapose run`. Confirmed via grep across src/aquapose/engine/ and src/aquapose/orchestrator.py that the real pipeline writes `midlines.h5` — `outputs.h5` exists only as this script's own `regenerate_reference_outputs()` rename of midlines.h5 for the shipped reference_outputs/ folder, never as something a user's own `aquapose run` produces. Corrected the comment to name the real file. Applied under deviation Rule 1 (bug fix) since it is a command-adjacent factual claim the plan's must-haves require checked against the real CLI/pipeline surface, even though the plan's <action> text did not explicitly enumerate it as a fourth defect."
  - "Verified template and tree are byte-identical after corrections by round-tripping write_deposit_config()/write_deposit_readme() into a temp dir and diffing against the tree copies — both matched exactly (D-06)."

requirements-completed: [DOCS-07, DATA-01]

coverage:
  - id: D1
    description: "write_deposit_config's header template shows a bare `aquapose run` with no --config flag (D-05.1), locked by a regression test that fails against the unpatched template"
    requirement: "DOCS-07"
    verification:
      - kind: unit
        ref: "tests/scripts/test_package_tutorial_dataset.py::TestDepositDocCorrections::test_config_header_has_bare_run_no_config_flag"
        status: pass
    human_judgment: false
  - id: D2
    description: "write_deposit_readme's repo link points at McGrathLab/AquaPose, not tucklancaster/AquaPose (D-05.2), locked by regression test"
    requirement: "DOCS-07"
    verification:
      - kind: unit
        ref: "tests/scripts/test_package_tutorial_dataset.py::TestDepositDocCorrections::test_readme_links_mcgrathlab_not_tucklancaster"
        status: pass
    human_judgment: false
  - id: D3
    description: "The README's `aquapose viz runs/<run_dir>` double-nesting defect (confirmed empirically against resolve_run) is corrected to the bare `aquapose viz` form"
    requirement: "DOCS-07"
    verification:
      - kind: unit
        ref: "tests/scripts/test_package_tutorial_dataset.py::TestDepositDocCorrections::test_readme_viz_command_does_not_double_nest"
        status: pass
    human_judgment: false
  - id: D4
    description: "The README's false 'generates outputs.h5' claim (aquapose run actually writes midlines.h5) is corrected"
    requirement: "DOCS-07"
    verification:
      - kind: unit
        ref: "tests/scripts/test_package_tutorial_dataset.py::TestDepositDocCorrections::test_readme_run_step_names_real_output_file"
        status: pass
    human_judgment: false
  - id: D5
    description: "Both template corrections applied identically to the extracted aquapose-tutorial-data/ tree (D-06), confirmed byte-identical to what the corrected templates now generate"
    requirement: "DATA-01"
    verification:
      - kind: other
        ref: "Round-tripped write_deposit_config()/write_deposit_readme() into a temp dir and diffed against aquapose-tutorial-data/config.yaml and README.md — exact match, no diff"
        status: pass
    human_judgment: false
  - id: D6
    description: "verify_deposit() returns an empty problem list and checksums.sha256 is re-emitted covering exactly 22 files, with sha256sum -c reporting 22 OK"
    requirement: "DATA-01"
    verification:
      - kind: other
        ref: "verify_deposit(Path('aquapose-tutorial-data')) -> []; sha256sum -c checksums.sha256 -> 22 OK, 0 failed; wc -l checksums.sha256 -> 22"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-09-02
status: complete
---

# Phase 113 Plan 03: Deposit Doc Corrections & Checksum Re-emission Summary

**Corrected the two known D-05 factual errors in both `scripts/package_tutorial_dataset.py`'s templates and the extracted `aquapose-tutorial-data/` tree, discovered and fixed two additional command-accuracy defects via empirical CLI verification, locked all four with regression tests, and re-emitted a clean 22/22 checksum manifest.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-09-02T12:40:40Z
- **Completed:** 2026-09-02T12:46:35Z
- **Tasks:** 2
- **Files modified:** 5 (2 committed template/test files, 3 uncommitted deposit-tree files per `.gitignore`)

## Accomplishments

- Fixed `write_deposit_config`'s header comment: replaced `aquapose run --config config.yaml` (no such flag exists on the `run` command) with the bare `aquapose run` form that actually works via CWD-upward `config.yaml` resolution.
- Fixed `write_deposit_readme`'s repo link: `https://github.com/tucklancaster/AquaPose` → `https://github.com/McGrathLab/AquaPose` (the repo's actual org, matching Phase 109-03's `pyproject.toml` fix that missed this template).
- **Verified and confirmed the plan's suspected "third command" defect**: read `resolve_run()` in `src/aquapose/cli_utils.py` and then empirically invoked it — `resolve_run('runs/run_20260306_075925', project_dir)` raised `Run path does not exist: .../runs/runs/run_20260306_075925`, proving the README's `aquapose viz runs/<run_dir>` form double-nests. Corrected to the bare `aquapose viz` (newest-run) form, matching the CWD-based resolution the rest of the block relies on.
- **Discovered a fourth defect not listed in D-05 or the plan's explicit task text**: the README's "Run the pipeline" step claims `aquapose run` "generates outputs.h5" — confirmed false by grepping `src/aquapose/engine/orchestrator.py` (writes `midlines.h5`) and `scripts/package_tutorial_dataset.py`'s own `regenerate_reference_outputs()` (the only place `outputs.h5` is ever written, by renaming `midlines.h5` for the shipped `reference_outputs/` folder). Corrected the comment to name the real output file.
- Added `TestDepositDocCorrections` (4 tests) to `tests/scripts/test_package_tutorial_dataset.py`, written first and confirmed RED against the unpatched templates, then GREEN after the fixes.
- Applied all four corrections identically to the extracted `aquapose-tutorial-data/` tree, then proved template/tree byte-equivalence by round-tripping `write_deposit_config()`/`write_deposit_readme()` into a temp directory and diffing — exact match.
- Ran `finalize_deposit()` (no-op: tree already had no `geometry/luts/` or `reference_outputs/run_*/` cache dirs), then `verify_deposit()` → returned `[]` (empty problem list), then `write_checksums()` → re-emitted a 22-line manifest.
- Confirmed `sha256sum -c checksums.sha256` from inside `aquapose-tutorial-data/` reports **22 OK, 0 failed**, and that exactly two digest lines changed (`config.yaml`, `README.md`) versus the pre-edit manifest.
- Confirmed `hatch run test` (1378 passed, 1 pre-existing unrelated failure already logged in `deferred-items.md`, 3 skipped), `hatch run lint` (all checks passed), and `hatch run ruff format --check src/ tests/ scripts/` (238 files formatted) all stayed green.

## Task Commits

1. **Task 1 (TDD): Correct both deposit templates and lock with regression tests (D-05, D-06)** - `13e5737` (fix)
2. **Task 2: Apply the corrections to the extracted deposit tree and re-emit the checksum manifest** - not committed (`aquapose-tutorial-data/` is `.gitignore`-covered per D-06/plan instruction; the committed half of D-06 is Task 1's template change)

**Plan metadata:** (this commit, docs-only)

## Files Created/Modified

- `scripts/package_tutorial_dataset.py` - `write_deposit_config`'s header now shows bare `aquapose run`; `write_deposit_readme`'s repo URL corrected to `McGrathLab/AquaPose`, its "How to Reproduce" block's `aquapose run` comment corrected to name `midlines.h5`, and its `aquapose viz runs/<run_dir>` line corrected to bare `aquapose viz`
- `tests/scripts/test_package_tutorial_dataset.py` - New `TestDepositDocCorrections` class, 4 regression assertions
- `aquapose-tutorial-data/config.yaml` - Header comment corrected identically to the template (not committed, gitignored)
- `aquapose-tutorial-data/README.md` - Repo URL, run comment, and viz command corrected identically to the template (not committed, gitignored)
- `aquapose-tutorial-data/checksums.sha256` - Re-emitted; exactly 2 of 22 digest lines changed (`config.yaml`, `README.md`) (not committed, gitignored)

## Decisions Made

- **Third command (viz double-nesting): confirmed defect, corrected.** `resolve_run()` treats any non-absolute, non-timestamp reference as `project_dir / "runs" / <reference>`. A reference of `runs/<run_dir>` therefore resolves to `project_dir/runs/runs/<run_dir>`, which does not exist. Verified this empirically (not just by reading the code) with a direct `resolve_run()` call against a temporary project directory, which raised exactly the predicted `ClickException`. Corrected the README's viz line to the bare `aquapose viz` form (newest-run default), which is what the rest of the "How to Reproduce" block already relies on via CWD-based project resolution.
- **Fourth defect (outputs.h5 claim): confirmed defect, corrected.** Not part of the plan's explicit task text, but flagged for empirical verification per the executor's project-specific warnings and squarely covered by the plan's must-have truth "every command...is checked against the real CLI surface...before the deposit is frozen." Grepped `src/aquapose/engine/` and `src/aquapose/cli.py` — no code path writes a file literally named `outputs.h5` during a normal `aquapose run`; only `scripts/package_tutorial_dataset.py::regenerate_reference_outputs()` produces `outputs.h5`, by copying `midlines.h5` for the deposit's own precomputed `reference_outputs/` folder. A user following the recipe would look for `outputs.h5` and not find it. Corrected the comment to say "generates midlines.h5".
- **Template/tree equivalence proven programmatically**, not just visually: round-tripped both write functions into a temp directory and diffed the output against the tree files, confirming an exact match (including the still-open `<DOI filled after upload>` citation placeholder, which neither this plan nor the templates touch).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed the false "generates outputs.h5" claim in the deposit README's "How to Reproduce" block**
- **Found during:** Task 1, while verifying the plan's suspected "third command" (the viz line) — grepping the pipeline's actual output paths surfaced this second, previously unlisted discrepancy in the same code block.
- **Issue:** The template (and tree) claimed `aquapose run` "generates outputs.h5 + per-chunk diagnostic cache." The real pipeline (`src/aquapose/engine/orchestrator.py:222`) writes `midlines.h5`. `outputs.h5` exists only as this packaging script's own rename of `midlines.h5` for the shipped `reference_outputs/` folder (`regenerate_reference_outputs()`), never as something a user's own run produces.
- **Fix:** Changed the comment to "generates midlines.h5 + per-chunk diagnostic cache" in both the template and the extracted tree.
- **Files modified:** `scripts/package_tutorial_dataset.py`, `tests/scripts/test_package_tutorial_dataset.py` (new assertion), `aquapose-tutorial-data/README.md` (not committed, gitignored)
- **Verification:** `TestDepositDocCorrections::test_readme_run_step_names_real_output_file` — RED before the fix, GREEN after.
- **Committed in:** `13e5737` (template + test); the tree edit is intentionally uncommitted per D-06/.gitignore.

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug in documented command output claim)
**Impact on plan:** Necessary for the plan's own must-have ("every command...checked against the real CLI surface...before the deposit is frozen") — a second latent defect in the exact code block the plan asked to be verified. No scope creep: the fix touches the same lines the plan already scoped for editing.

## Issues Encountered

None beyond the deviation documented above. The precondition (`sha256sum -c checksums.sha256` reporting 22 OK before any edit) was verified true before starting Task 2. `finalize_deposit()` was a no-op — the tree already had no `geometry/luts/` or `reference_outputs/run_*/` cache directories to remove.

## Known Stubs

None. Both corrected files are complete, real content — no placeholders introduced.

## Threat Flags

None new. T-113-08 (spoofing via wrong repo URL) and T-113-09 (tampering via stale checksum manifest) were mitigated exactly as the plan's threat model specified — the manifest re-emission and repo-URL fix close both. No new unmitigated surface was introduced by the two additional command-accuracy fixes (they narrow, not widen, the deposit's instructed command surface).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both templates and the extracted tree now agree byte-for-byte on every corrected line; regenerating the deposit from the script would reproduce the exact same corrected `config.yaml` and `README.md`.
- `verify_deposit()` returns `[]` and the checksum manifest verifies 22/22 — the deposit is in a known-good state for Plan 06 to mint the Zenodo DOI and upload.
- The `<DOI filled after upload>` citation placeholder is untouched, as expected — Plan 06 owns filling it in.
- Plan 07 (tutorial page) can now safely quote the corrected "How to Reproduce" recipe verbatim — the bare `aquapose run`, bare `aquapose viz`, and `midlines.h5` output name are all now accurate against the real CLI.
- One pre-existing, unrelated test failure (`test_pseudo_label_cli.py`, logged in `deferred-items.md` by Plan 01) remains open and untouched — not a regression from this plan.

## Self-Check: PASSED

- FOUND: scripts/package_tutorial_dataset.py (modified — 3 corrected lines: header, repo URL, run comment, viz line)
- FOUND: tests/scripts/test_package_tutorial_dataset.py (modified — TestDepositDocCorrections, 4 tests)
- FOUND: aquapose-tutorial-data/config.yaml (modified, gitignored)
- FOUND: aquapose-tutorial-data/README.md (modified, gitignored)
- FOUND: aquapose-tutorial-data/checksums.sha256 (re-emitted, 22 lines, gitignored)
- FOUND commit: 13e5737
- CONFIRMED: sha256sum -c checksums.sha256 -> 22 OK, 0 failed
- CONFIRMED: verify_deposit(Path("aquapose-tutorial-data")) -> []

---
*Phase: 113-concepts-tutorial*
*Completed: 2026-09-02*
