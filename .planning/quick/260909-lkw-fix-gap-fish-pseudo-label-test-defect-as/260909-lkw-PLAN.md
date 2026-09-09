---
phase: quick-260909-lkw
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - tests/unit/training/test_pseudo_label_cli.py
  - .planning/todos/pending/2026-09-03-gap-fish-pseudo-label-emission-varies-by-platform.md
  - .planning/todos/done/2026-09-03-gap-fish-pseudo-label-emission-varies-by-platform.md
autonomous: true
requirements: []

must_haves:
  truths:
    - "test_generates_merged_obb_and_separate_pose asserts exact OBB line counts against named label files, not glob()[0]"
    - "The test passes deterministically on Windows and would pass on any filesystem ordering"
    - "No file under src/ is modified"
    - "The mis-diagnosed platform-variance todo no longer sits in .planning/todos/pending/"
    - "The closed todo records the real cause (unsorted glob()[0] in the test) and states the production emission path was not found defective"
  artifacts:
    - path: "tests/unit/training/test_pseudo_label_cli.py"
      provides: "Deterministic named-file OBB assertions restoring merge coverage"
      contains: "000000_cam1.txt"
    - path: ".planning/todos/done/2026-09-03-gap-fish-pseudo-label-emission-varies-by-platform.md"
      provides: "Closed todo with corrected diagnosis"
      contains: "## Resolved"
  key_links:
    - from: "tests/unit/training/test_pseudo_label_cli.py"
      to: "pseudo_labels/obb/labels/train/000000_cam1.txt"
      via: "direct named-path read"
      pattern: "000000_cam1\\.txt"
---

<objective>
Fix a test-only defect in `test_generates_merged_obb_and_separate_pose`: it selects
an OBB label file with `list(dir.glob("*.txt"))[0]`, which is unordered, so it
reads a `cam0` file (1 consensus line) on NTFS and an arbitrary file on ext4.
Replace the selection with assertions against NAMED files so exact line counts are
pinned on every platform. Then close the todo that mis-diagnosed this as a
platform-dependent production emission bug.

Purpose: restore the merge coverage Phase 113.1-06 intended (currently relaxed to
`assert len(lines) >= 1` by Phase 113.2) without re-introducing a platform-fragile
assertion, and stop a wrong diagnosis from sending someone hunting for an ordering
bug in `pseudo_label_cli.py` that does not exist.

Output: a stronger, deterministic test; a resolved todo in `.planning/todos/done/`.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.claude/rules/code-style.md
@tests/unit/training/test_pseudo_label_cli.py
@.planning/todos/pending/2026-09-03-gap-fish-pseudo-label-emission-varies-by-platform.md

<verified_facts>
Diagnosis is complete and empirically verified this session. Do NOT re-investigate.

- The test mocks two cameras (`cam0`, `cam1`) and two frames, with gaps mocked for
  `cam1` only: `mock_detect_gaps.return_value = [("cam1", "no-detection")]`.
- `pseudo_label_cli.py:462,479` writes one label file per (frame, camera) named
  `f"{frame_idx:06d}_{cam_id}.txt"`. So the run deterministically produces FOUR
  files: `000000_cam0.txt` (1 line), `000000_cam1.txt` (2 lines),
  `000001_cam0.txt` (1 line), `000001_cam1.txt` (2 lines).
- `Path.glob` does not sort. `[0]` is whichever entry the OS yields first:
  alphabetical on NTFS (always a `cam0` file), hash-seeded and effectively
  arbitrary on ext4.
- The CI failure text quoted in the todo shows the surviving line as
  `0.0 0.233333 ...` — the CONSENSUS line. The mocked gap line is
  `0 0.1 0.2 0.3 ...`, a different leading token and different numbers. CI was
  reading a `cam0` file, which contains no gap line on any platform. Nothing was
  dropped.
- `frame_tracklet_index` is empty in this test, so `_count_detected_tracklets`
  returns 0 and the completeness filter (`n_labeled < n_tracked`) is disabled
  entirely. It cannot be the cause.
- The todo's "Python 3.11 vs 3.12 on ubuntu is the cleanest discriminator" is a red
  herring: ext4 htree ordering depends on a per-directory hash seed and varies run
  to run, not by interpreter.
</verified_facts>

<hard_constraint>
Do NOT modify `src/aquapose/training/pseudo_label_cli.py` or any other file under
`src/`. No production defect was demonstrated; changing production code would be
acting on a diagnosis the evidence contradicts.
</hard_constraint>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Pin OBB label assertions to named files</name>
  <files>tests/unit/training/test_pseudo_label_cli.py</files>
  <action>
In `TestGenerateCommand::test_generates_merged_obb_and_separate_pose` (around
lines 252-372), rewrite the OBB label assertion block.

Delete the `obb_labels = list((pseudo_dir / "obb" / "labels" / "train").glob("*.txt"))`
selection, the `obb_labels[0].read_text()` read, the `assert len(lines) >= 1`
relaxation, and the entire preceding comment block that describes the line count as
"environment-dependent" and points at
`.planning/todos/pending/2026-09-03-gap-fish-pseudo-label-emission-varies-by-platform.md`.
That explanation is wrong and the todo is being closed in Task 2, so the reference
must not survive.

Replace it with assertions against NAMED files under
`pseudo_dir / "obb" / "labels" / "train"`:

- `000000_cam1.txt` exists and has EXACTLY 2 lines — consensus fish plus the gap
  fish injected by the mocked `detect_gaps` result for `cam1`.
- `000000_cam0.txt` exists and has EXACTLY 1 line — consensus only, since no gap
  was mocked for `cam0`.
- Every line in BOTH files splits into exactly 9 whitespace-separated tokens
  (class + 4 corners x 2). Keep this per-line format check — it is the invariant
  Phase 113.1-06 correctly identified, guarding against the original whole-file
  `.split()` defect that collapsed a multi-line file into one 18-token list. Loop
  over both files so the check covers both.

Keep assertion messages that include the offending content (`{lines!r}`,
`{line!r}`) so a future failure is diagnosable without a rerun.

Replace the deleted comment block with a short comment stating the real invariant:
label files are named `{frame:06d}_{cam_id}.txt`; gaps were mocked for `cam1` only,
so `cam1` files carry the merged consensus+gap pair and `cam0` files carry consensus
alone. Note explicitly that files are addressed by name rather than via `glob()[0]`
because `Path.glob` is unordered, which is what made this assertion appear
platform-dependent.

Do not change any other assertion in the test (directory-structure checks,
`dataset.yaml` checks, confidence-sidecar checks, pose-image stem checks all stay).
Do not touch any other test in the file.

Follow the project's Ruff formatting and existing style in the file.
  </action>
  <verify>
    <automated>hatch run test -k test_generates_merged_obb_and_separate_pose</automated>
  </verify>
  <done>
`hatch run test -k test_generates_merged_obb_and_separate_pose` passes on Windows.
The test file contains no `glob("*.txt"))[0]`-style selection in this test and no
reference to the pending-todo path. `grep -c` confirms both `000000_cam1.txt` and
`000000_cam0.txt` appear as literal named-path assertions. `git status` shows no
file under `src/` modified.
  </done>
</task>

<task type="auto">
  <name>Task 2: Resolve the mis-diagnosed platform-variance todo</name>
  <files>.planning/todos/pending/2026-09-03-gap-fish-pseudo-label-emission-varies-by-platform.md, .planning/todos/done/2026-09-03-gap-fish-pseudo-label-emission-varies-by-platform.md</files>
  <action>
First read one existing closed todo to match the convention exactly, e.g.
`.planning/todos/done/2026-09-02-calibrate-keypoints-writes-t-values-to-legacy-midline-config-key.md`.
That file keeps the original frontmatter and body intact and appends a closure
section (`## Fixed` with **Date:** / **Fixed by:** / **Evidence:** lines). Match
whatever form the done/ files actually use; prefer `## Resolved` here since the
outcome is "diagnosis was wrong, test fixed" rather than a production fix — but
keep the same Date / Resolved by / Evidence field shape.

Move the file with `git mv` from `.planning/todos/pending/` to
`.planning/todos/done/`, preserving the filename.

Preserve the original Problem / Why it matters / Investigation starting points /
Solution / Notes body verbatim — the record of what was believed matters. Append the
closure section, which MUST state:

1. **The real cause:** the test selected an OBB label file via an unordered
   `list(...glob("*.txt"))[0]`. Files are written per (frame, camera) as
   `{frame:06d}_{cam_id}.txt`; gaps were mocked for `cam1` only, so `cam0` files
   legitimately contain 1 line and `cam1` files 2. `[0]` returns whichever file the
   filesystem yields first — alphabetical on NTFS (always `cam0`), hash-seeded on
   ext4.

2. **Evidence disproving the original diagnosis:**
   - The CI output quoted in the Problem section shows the surviving line as
     `0.0 0.233333 ...`, which is the CONSENSUS line, not a truncated gap line. The
     mocked gap line is `0 0.1 0.2 0.3 ...` — different leading token, different
     numbers. CI was reading a `cam0` file all along.
   - `frame_tracklet_index` is empty in this test, so `_count_detected_tracklets`
     returns 0 and the completeness filter at `pseudo_label_cli.py:467-480` is
     disabled outright. It could not have fired.
   - The "3.11 vs 3.12 on ubuntu is the cleanest discriminator" starting point was a
     red herring: ext4 htree ordering depends on a per-directory hash seed, so it
     varies run to run, not by interpreter version.

3. **An explicit non-defect note:** the production emission path in
   `src/aquapose/training/pseudo_label_cli.py` was NOT found to be defective. No
   ordering, hash, or platform dependency was demonstrated there and no `src/` file
   was changed. Nobody should re-open a hunt for an ordering bug in that module on
   the strength of this todo's original text.

4. **The fix that landed:** `test_generates_merged_obb_and_separate_pose` now
   asserts against named files (`000000_cam1.txt` == 2 lines,
   `000000_cam0.txt` == 1 line, 9 tokens per line in both), which is strictly
   stronger than both the 113.1-06 `len(lines) == 2` pin and the 113.2 `>= 1`
   relaxation, and is deterministic on every platform.

Correct the framing so the file no longer reads as an open production bug — the
title stays (it is the filename and the historical record) but the closure section
must plainly say the title is inaccurate.
  </action>
    <automated>test ! -f .planning/todos/pending/2026-09-03-gap-fish-pseudo-label-emission-varies-by-platform.md && test -f .planning/todos/done/2026-09-03-gap-fish-pseudo-label-emission-varies-by-platform.md && grep -qi "glob" .planning/todos/done/2026-09-03-gap-fish-pseudo-label-emission-varies-by-platform.md && grep -qi "not found to be defective" .planning/todos/done/2026-09-03-gap-fish-pseudo-label-emission-varies-by-platform.md && echo PASS</automated>
  </verify>
  <done>
The todo file exists only under `.planning/todos/done/`, moved via `git mv` so
history is preserved. Its closure section names the unsorted `glob()[0]` as the real
cause, cites the consensus-vs-gap line content and the disabled completeness filter
as evidence against the original diagnosis, and states explicitly that the
production emission path was not found to be defective. Original body text is
unchanged above the closure section.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| none | Test-only and planning-doc-only change; no runtime input crosses any boundary |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-quick-01 | Tampering | tests/unit/training/test_pseudo_label_cli.py | mitigate | Assertions are strengthened, not weakened; exact counts replace a `>= 1` relaxation, so coverage cannot silently regress |
| T-quick-02 | Repudiation | .planning/todos/done/... | mitigate | Original todo body preserved verbatim under `git mv`; closure section appended rather than overwriting the historical record |
| T-quick-03 | Information Disclosure | n/a | accept | No secrets, no network, no user data touched |

No package-manager installs in this plan, so no supply-chain gate applies.
</threat_model>

<verification>
1. `hatch run test -k test_generates_merged_obb_and_separate_pose` exits 0.
2. `hatch run test` exits 0 (no collateral breakage in the pseudo-label suite).
3. `hatch run lint` and `hatch run format --check` clean on the edited test file.
4. `git status --porcelain` shows changes ONLY under `tests/` and `.planning/` —
   zero files under `src/`.
5. `grep -rn "gap-fish-pseudo-label-emission-varies-by-platform" tests/` returns
   nothing (the stale comment reference is gone).
</verification>

<success_criteria>
- `test_generates_merged_obb_and_separate_pose` asserts `000000_cam1.txt` has exactly
  2 lines and `000000_cam0.txt` exactly 1, with a 9-token-per-line format check on
  both files.
- No `glob(...)[0]` selection remains in that test.
- The misleading "environment-dependent" comment block is replaced by an accurate
  statement of the cam0/cam1 invariant.
- `src/aquapose/training/pseudo_label_cli.py` is byte-identical to its pre-plan state.
- The todo now lives in `.planning/todos/done/` with a closure section carrying the
  corrected diagnosis, the disproving evidence, and an explicit no-production-defect
  note.
- Full fast suite green via `hatch run test`.
</success_criteria>

<output>
Create `.planning/quick/260909-lkw-fix-gap-fish-pseudo-label-test-defect-as/260909-lkw-SUMMARY.md` when done
</output>
