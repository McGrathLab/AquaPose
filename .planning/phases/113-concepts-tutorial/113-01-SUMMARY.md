---
phase: 113-concepts-tutorial
plan: 01
subsystem: docs
tags: [sphinx, myst, hatch, pytorch, packaging]

requires:
  - phase: 112-config-cli-reference
    provides: docs/reference/{index.md,cli.rst,config.md} — the section-index shape and cross-link idiom this plan mirrors and links into
provides:
  - "docs/getting-started/ Sphinx section (index.md + installation.md) wired into docs/index.md's card grid and root toctree"
  - "End-user install guide covering pip install (with PyPI-not-yet-published disclosure), platform torch via pytorch.org, CUDA verification, prerequisites, and troubleshooting"
  - "Default hatch environment with no third-party wheel-index pin (D-08)"
affects: [113-04-concepts-page, 113-07-tutorial-page, 114-publication]

actuals:
  tokens: 1524
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Getting Started docs section mirrors docs/reference/index.md's grid-item-card + hidden toctree shape"
    - "Narrative pages cross-link to reference pages (../reference/cli.rst, ../reference/config.md) instead of restating options"

key-files:
  created:
    - docs/getting-started/index.md
    - docs/getting-started/installation.md
    - .planning/phases/113-concepts-tutorial/deferred-items.md
  modified:
    - docs/index.md
    - pyproject.toml

key-decisions:
  - "docs/index.md card ordering: Getting Started placed FIRST, before Reference/API Reference/Contributing/Reports (beginner-first flow, per plan instruction and 113-PATTERNS.md's stated rationale)"
  - "README's nvrtc troubleshooting note (libnvrtc-builtins.so) carried into installation.md's Troubleshooting section verbatim in spirit, reframed as a torch/driver CUDA-version mismatch resolved via the pytorch.org selector rather than a hardcoded cu124 reinstall command"
  - "Getting Started index.md contains exactly one card/toctree entry (installation) in this plan; concepts and tutorial cards are deferred to plans 04 and 07 per the plan's explicit instruction to avoid an unresolved toctree reference under sphinx-build -W"

requirements-completed: [DOCS-03]

coverage:
  - id: D1
    description: "Getting Started docs section (index.md + installation.md) built and wired into docs/index.md, building clean under sphinx-build -W --keep-going"
    requirement: "DOCS-03"
    verification:
      - kind: other
        ref: "hatch run docs:build (exit 0); test -f docs/_build/html/getting-started/installation.html; test -f docs/_build/html/getting-started/index.html"
        status: pass
    human_judgment: false
  - id: D2
    description: "installation.md covers install (with PyPI disclosure + interim GitHub install command), platform torch via pytorch.org, CUDA verification, prerequisites (ffmpeg, 600 MB LUTs + 215 MB dataset, GTX 1660 SUPER 6.4 GB floor), and troubleshooting"
    requirement: "DOCS-03"
    verification:
      - kind: other
        ref: "grep checks in plan 113-01 acceptance_criteria (pytorch.org, torch.cuda.is_available, ffmpeg, 600 MB, 215 MB, GTX 1660 SUPER, PyPI, McGrathLab/AquaPose, contributing, reference/cli) — all matched"
        status: pass
    human_judgment: false
  - id: D3
    description: "Default hatch environment no longer pins the cu121 wheel index; CUDA-enabled torch still resolves on this machine (D-08)"
    requirement: "DOCS-03"
    verification:
      - kind: other
        ref: "grep -c UV_EXTRA_INDEX_URL/cu121/env-vars pyproject.toml == 0; hatch run python -c \"import torch; print(torch.cuda.is_available())\" -> True"
        status: pass
    human_judgment: false

duration: 4min
completed: 2026-09-02
status: complete
---

# Phase 113 Plan 01: Getting Started Section & Install Guide Summary

**New docs/getting-started/ Sphinx section with an end-to-end install guide (DOCS-03), wired into the docs root, plus removal of the cu121 wheel-index pin from the default hatch environment (D-08) with CUDA verified still working.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-09-02T12:29:46Z
- **Completed:** 2026-09-02T12:33:21Z
- **Tasks:** 2
- **Files modified:** 5 (3 created, 2 modified)

## Accomplishments

- Created `docs/getting-started/index.md` (section landing page: one `grid-item-card` for Installation, hidden toctree) mirroring `docs/reference/index.md`'s exact structure.
- Wrote `docs/getting-started/installation.md` (96 lines): pip install with explicit PyPI-not-yet-published disclosure and a working interim `pip install git+https://github.com/McGrathLab/AquaPose.git` command (D-09); platform-specific torch via pytorch.org (D-08); a `torch.cuda.is_available()` verification step with explicit True/False interpretation; a Prerequisites section covering ffmpeg on PATH, ~600 MB LUT + 215 MB dataset disk headroom, and the GTX 1660 SUPER 6.4 GB GPU floor (D-10); a Troubleshooting section carrying forward the README's `nvrtc` CUDA-mismatch note; and cross-links to `../contributing.md`, `../reference/cli.rst`, and `../reference/config.md` instead of restating their content.
- Wired `docs/index.md`: added a "Getting Started" `grid-item-card` as the first card (before Reference) and `getting-started/index` as the first root toctree entry.
- Removed `[tool.hatch.envs.default.env-vars]` (the `UV_EXTRA_INDEX_URL` cu121 pin) from `pyproject.toml` entirely (D-08) — confirmed no other keys in `[tool.hatch.envs.default]` referenced it.
- Verified the tracer end-to-end: `hatch run docs:build` (`sphinx-build -W --keep-going`) exits 0 with both new HTML pages produced.
- Verified D-08's acceptance gate: torch baseline captured before the change (2.5.1+cu121, `torch.cuda.is_available()` → `True`) and confirmed unchanged after (same env, not recreated, since `hatch env create` was not re-run).

## Task Commits

1. **Task 1 (tracer): Getting Started section + install guide + docs root wiring** - `bb4f325` (feat)
2. **Task 2: Drop cu121 wheel-index pin (D-08)** - `07e27e6` (fix)

**Plan metadata:** (this commit, docs-only)

## Files Created/Modified

- `docs/getting-started/index.md` - New section landing page: 1 grid-item-card + hidden toctree (installation only; concepts/tutorial added by plans 04/07)
- `docs/getting-started/installation.md` - New end-user install guide (96 lines): install, torch-for-platform, CUDA verify, prerequisites, troubleshooting, next steps
- `docs/index.md` - Added Getting Started card (first) + toctree entry (first)
- `pyproject.toml` - Removed `[tool.hatch.envs.default.env-vars]` / `UV_EXTRA_INDEX_URL` (cu121 pin)
- `.planning/phases/113-concepts-tutorial/deferred-items.md` - New: logs one pre-existing, out-of-scope test failure discovered during Task 2 verification

## Decisions Made

- **Card ordering:** Getting Started placed first in `docs/index.md`'s grid and toctree (beginner-first flow), ahead of Reference/API Reference/Contributing/Reports — Claude's Discretion per 113-CONTEXT.md.
- **Torch baseline recorded (D-08 acceptance criterion):** before change — `torch==2.5.1+cu121`, `torch.cuda.is_available()` → `True`. After change — identical (`torch==2.5.1+cu121`, `True`), because the existing hatch environment was not recreated; the pin's removal takes effect on the next `hatch env create`, which this plan does not trigger. This matches the plan's precondition/acceptance intent: the *default environment configuration* no longer pins a wheel index, and the machine's CUDA torch is unaffected right now.
- **README `nvrtc` note carried forward:** Yes — `installation.md`'s Troubleshooting section keeps the `nvrtc: error: failed to open libnvrtc-builtins.so` symptom, but reframes the fix as "reinstall via the pytorch.org selector matching your driver" rather than the README's hardcoded `--index-url .../cu124` command, since AquaPose no longer prescribes a specific CUDA build.

## Deviations from Plan

None - plan executed exactly as written. No Rule 1-4 auto-fixes were required in either task's own file scope.

**Out-of-scope discovery (not a deviation, logged per scope-boundary rule):** During Task 2's `hatch run test` verification, `tests/unit/training/test_pseudo_label_cli.py::TestGenerateCommand::test_generates_merged_obb_and_separate_pose` failed (`assert len(parts) == 9` receives 18 — an OBB label-format mismatch unrelated to `pyproject.toml`). Confirmed pre-existing by reverting the `pyproject.toml` edit and re-running the single test in isolation: identical failure before and after. Per the scope-boundary rule ("only auto-fix issues directly caused by the current task's changes"), this was **not** fixed — logged to `.planning/phases/113-concepts-tutorial/deferred-items.md` instead. Full suite: 1374 passed, 1 failed (this pre-existing case), 3 skipped, 17 deselected.

## Issues Encountered

None beyond the out-of-scope test failure documented above.

## Known Stubs

None. Both new pages are fully authored end-user content with no placeholder text, and `docs/getting-started/index.md` intentionally contains only the Installation card/toctree entry per the plan's explicit instruction (concepts.md/tutorial.md do not exist yet and adding forward references would break `sphinx-build -W`) — this is a scoped plan boundary, not a stub.

## Threat Flags

None. Both threats this plan owns (T-113-01 spoofing via the install command, T-113-02 tampering via the third-party wheel index) were mitigated exactly as the plan's threat model specified — no new unmitigated surface was introduced.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The Getting Started IA skeleton (`docs/getting-started/index.md`, root wiring) is in place and ready for Plan 04 (concepts.md) and Plan 07 (tutorial.md) to each add their own card + toctree entry — do not re-copy the grid/toctree structure, extend it.
- `pyproject.toml`'s default environment is now pin-free; Plan 05's GPU verification run depends on this same environment still resolving CUDA torch, which is confirmed unaffected on this machine.
- One pre-existing, unrelated test failure (`test_pseudo_label_cli.py`) remains open in `deferred-items.md` — not a blocker for this phase's scope, but worth flagging if a future phase touches `training/pseudo_label_cli.py`.

## Self-Check: PASSED

- FOUND: docs/getting-started/index.md
- FOUND: docs/getting-started/installation.md
- FOUND: docs/index.md (modified, contains getting-started/index x2)
- FOUND: pyproject.toml (modified, env-vars table removed)
- FOUND: .planning/phases/113-concepts-tutorial/deferred-items.md
- FOUND commit: bb4f325
- FOUND commit: 07e27e6

---
*Phase: 113-concepts-tutorial*
*Completed: 2026-09-02*
