---
phase: 109-correctness-green-test-suite-config-consolidation
plan: "03"
subsystem: test-suite / cli / packaging
tags: [correctness, encoding, platform-neutral, cli-help, pyproject]
dependency_graph:
  requires: []
  provides: [green-train-help-tests, utf8-viz-read, utf8-init-write, platform-neutral-tutorial-config, corrected-pyproject-urls]
  affects: [tests/unit/training/test_training_cli.py, tests/unit/evaluation/test_viz.py, src/aquapose/cli.py, pyproject.toml]
tech_stack:
  added: []
  patterns: [encoding="utf-8" for all user-facing text I/O]
key_files:
  modified:
    - tests/unit/training/test_training_cli.py
    - tests/unit/evaluation/test_viz.py
    - src/aquapose/cli.py
    - pyproject.toml
decisions:
  - "D-11 root cause: --val-split was never defined in train obb/seg/pose commands; dataset splitting is data assemble's responsibility (val_fraction); assertions were stale, not dropped feature"
  - "D-08 root cause (test_viz): out_path.read_text() used OS default encoding (cp1252 on Windows); animation file is text/HTML written utf-8; fix is read_text(encoding='utf-8')"
  - "D-08 root cause (init_cmd): write_text() had no encoding= argument; fix is encoding='utf-8'"
  - "D-05/QA-04: Scaffolded config already uses all-relative sub-paths; only project_dir is absolute (correct by design); no path changes needed"
  - "D-06: tlancaster6/aquapose replaced with McGrathLab/AquaPose in Homepage/Repository/Issues; Documentation URL left unchanged (readthedocs); CHANGELOG/CODE_OF_CONDUCT deferred to Phase 114"
metrics:
  duration: "~5 minutes"
  completed: "2026-09-01"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 4
---

# Phase 109 Plan 03: Platform-Neutral Miscellany Summary

Platform-independent CLI-help failures and Windows encoding failures fixed; tutorial config made utf-8/portable; PyPI metadata URLs corrected.

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Fix stale --val-split assertions (D-11) and cp1252 encoding read (D-08) | `7ed3979` | test_training_cli.py, test_viz.py |
| 2 | utf-8 init_cmd config write + correct pyproject URLs (D-05/D-08/D-06) | `056f50d` | cli.py, pyproject.toml |

## What Was Built

Fixed 3 stale `--val-split` train-help test assertions, 1 Windows cp1252 encoding failure in test_viz, added `encoding="utf-8"` to the `init_cmd` config write, and corrected 3 stale `tlancaster6/AquaPose` PyPI metadata URLs to `McGrathLab/AquaPose`.

## Root-Cause Notes (D-11 per test)

**test_train_obb_help_shows_expected_flags (D-11):** `--val-split` was in the expected_flags list but the `train obb` command never defines it. Train/val splitting is performed by `data assemble` via `val_fraction`; the train command receives a pre-split data directory. The assertion was stale from an earlier design where splitting lived in the train command. Fix: remove `--val-split` from the expected_flags list.

**test_train_seg_help_shows_expected_flags (D-11):** Same root cause — `train seg` never defines `--val-split`. The split responsibility belongs to `data assemble`. Fix: remove `--val-split` from the expected_flags list.

**test_train_pose_help_shows_expected_flags (D-11):** Same root cause — `train pose` never defines `--val-split`. Fix: remove `--val-split` from the expected_flags list.

**test_prefers_stitched_h5 (D-08):** `out_path.read_text()` used the OS default encoding. On Windows the default is cp1252; the animation file is HTML/text written as utf-8 and contains non-ASCII characters that fail to decode under cp1252. Fix: `read_text(encoding="utf-8")`.

## Deviations from Plan

None — plan executed exactly as written. Pre-existing typecheck errors (reid_training.py, yolo_training.py) were noted as out-of-scope; `hatch run lint` exits 0 for the edited files.

## Verification Results

- `hatch run test tests/unit/training/test_training_cli.py tests/unit/evaluation/test_viz.py -q` — 1295 passed, 3 skipped, 0 failures
- `grep -c 'encoding="utf-8"' src/aquapose/cli.py` — 1 (was 0)
- `grep -ci "tlancaster6" pyproject.toml` — 0 (was 3)
- `hatch run lint` — All checks passed

## Known Stubs

None.

## Threat Flags

None — no new network endpoints, auth paths, or trust-boundary changes introduced.

## Self-Check: PASSED

- `7ed3979` exists in git log
- `056f50d` exists in git log
- `tests/unit/training/test_training_cli.py` modified (no --val-split in any expected_flags)
- `tests/unit/evaluation/test_viz.py` modified (encoding="utf-8")
- `src/aquapose/cli.py` modified (encoding="utf-8")
- `pyproject.toml` modified (McGrathLab/AquaPose URLs)
