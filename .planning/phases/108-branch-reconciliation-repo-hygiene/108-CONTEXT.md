# Phase 108: Branch Reconciliation & Repo Hygiene - Context

**Gathered:** 2026-08-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Make `dev` the single source of truth for AquaPose: reconciled with `main`, relicensed to
AGPL-3.0-or-later, with a green `sphinx-build -W --keep-going`, a clean working tree, and a
complete milestone record.

Covers requirements **FOUND-01, FOUND-02, FOUND-03, FOUND-04, FOUND-05, REC-01**.

**Not in this phase:** test-suite repair (Phase 109), API coverage / docs tiering (Phase 110),
the Zenodo dataset (Phase 111), CLI/config reference (Phase 112), tutorial (Phase 113),
README / badges / Read the Docs wiring (Phase 114). No pipeline behavior changes.

</domain>

<scout_findings>
## Repo Reality Check (scouted 2026-08-17 on `dev`)

**Several ROADMAP.md success criteria for this phase are written against assumptions that do
not match the repo. The planner must plan against the facts below, not the roadmap text.**

| ROADMAP.md / REQUIREMENTS.md claim | Verified actual state |
|---|---|
| Fresh clone of `dev` contains stray artifacts: vendored SAM2 clone, `11.0` pip log, top-level `yolo26n*.pt`, `runs/`, `tmp/` | **Already clean.** `git ls-files` tracks none of them. `.gitignore` already covers `tmp/` (:94), `*.pt` (:97), `runs/` (:99). Only `11.0` and `~/` are untracked-and-unignored, and both are local working-tree junk. FOUND-04's "fresh clone" half is effectively already satisfied. |
| Dead `reconstruction/`, `segmentation/`, `tracking/` directories | `src/aquapose/core/reconstruction/` and `src/aquapose/core/tracking/` are **live production code** — do not touch. The genuinely dead artifacts are `docs/api/{mesh,optimization,segmentation,utils}.rst` and the empty package `tests/integration/segmentation/__init__.py`. |
| Vendored SAM2 clone | Real, but located at `~/PycharmProjects/sam2` — inside a literal `~` directory created by a bad shell expansion. Untracked. Contains a `checkpoints/` dir (downloaded model weights). |
| `11.0` | A pip install log from `pip install boxmot`, captured by a stray shell redirect. Untracked. |
| Docs CI only runs on `main` | **Backwards.** `main`'s `.github/workflows/docs.yml` already has `on: push: branches: [main, dev]`. `dev`'s still has `pull_request` only. Merging `main` into `dev` satisfies FOUND-02 as a side effect. |
| — (not in roadmap) | `.gitignore:100` ignores `.planning/` while **31 `.planning/` files are force-added and tracked**. The rule and the repo contradict each other; every GSD phase commit currently needs `git add -f`. |
| — (not in roadmap) | `MILESTONES.md` is missing **v2.2 Backends** as well as v3.11, and the tail entries are out of chronological order (v1.0 sits between v3.0 and v2.0). |

**Branch state:** `dev` is 1496 commits ahead of `main`. `main` has 4 commits not in `dev`:
`19ea21e` (v3.5 feat), `9aa1fd6` (chore(release): 1.1.0), `a66287a` (fix(docs): repair Sphinx
build and gate it on push), `2aba732` (chore(release): 1.1.1).

**Docs delta on `dev` vs `main`:** `dev`'s `docs/conf.py` lacks `napoleon_use_ivar`,
`autodoc_mock_imports`, the `_resolve_release()` fallback, and the `version`-must-be-a-string
fix. `dev`'s `[tool.hatch.envs.docs]` is **not** detached, so it still installs the project and
pulls ~5.8 GB of CUDA torch — the thing that broke Read the Docs.

**`.rst` set alignment:** `main`'s `docs/api/` (calibration, core, engine, evaluation, io,
synthetic, training, index) maps cleanly onto `dev`'s top-level packages (calibration, core,
engine, evaluation, io, synthetic, training + `cli.py`, `cli_utils.py`). The forward-port is
less hostile than the 1496-commit gap suggests.

</scout_findings>

<decisions>
## Implementation Decisions

### Branch Reconciliation

- **D-01:** Bring `main`'s 4 commits onto `dev` with **`git merge main`** (a real merge, on
  `dev`). Records true ancestry so every future `main`→`dev` sync is conflict-free. Do **not**
  cherry-pick `a66287a` alone (leaves the branches without a recent common ancestor, so the
  same 4 commits re-conflict forever) and do **not** rebase `dev` onto `main` (would rewrite
  1496 published commits on `origin/dev`).
- **D-02:** Expected merge conflicts are confined to `pyproject.toml` (version + license
  fields) and `docs/` — both of which this phase rewrites anyway. Resolve in favor of the
  decisions in this document, not by mechanical "theirs"/"ours".
- **D-03:** Resolve the version conflict by setting `dev` to **`1.2.0-dev.0`**. This
  acknowledges that `1.1.1` shipped, keeps `dev` on a prerelease channel ahead of it, and lets
  `python-semantic-release` continue normally. **Do not conflate the GSD "v4.0 Publication"
  milestone label with the package version** — the package stays on 1.x; a `4.0.0` on PyPI
  would be misleading.
- **D-04:** `main` stays **release-only and frozen at `1.1.1` until the end of Phase 114**. No
  interim sync at Phase 109. `main` is not touched by this phase beyond being merged *from*.
- **D-05:** GitHub's default branch **stays `main`** (`origin/HEAD → main` unchanged). Do not
  change the repo setting.
- **D-06 (accepted consequence):** D-04 + D-05 together mean that for Phases 108–113 a GitHub
  visitor lands on a tree that is 1496 commits stale and still declares MIT. This is
  acceptable **only because the repository is not announced until Phase 114**. Phase 114 owns
  the `main` sync, the release tag, and the Read the Docs source-branch decision (RTD must
  build from `dev` per DOCS-08 while `main` remains default). Planner: do not silently
  "improve" this by flipping the default branch.

### AGPL Relicense

- **D-07:** License is **`AGPL-3.0-or-later`** (SPDX). Apply consistently to `LICENSE`,
  `pyproject.toml` `license` field, and the OSI classifier
  (`License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)`).
  Use the modern PEP 639 SPDX string form where the build backend supports it.
- **D-08:** Copyright line is **name + institution**, replacing `Copyright (c) 2026
  tlancaster6`. Use verbatim:

  ```
  Copyright (C) 2026 Tucker Lancaster and the McGrath Lab at the Georgia Institute of Technology
  ```

  The institution string was supplied by the user. The personal name matches
  `docs/conf.py` (`author = "Tucker Lancaster"`), which is already the repo's declared author —
  keep the two consistent. Do **not** fall back to the `tlancaster6` GitHub handle anywhere.
  Phase 114's citation block must use this same attribution.
- **D-09:** Add a short **`LICENSING.md`** at repo root explaining *why* AGPL rather than just
  declaring it — naming the copyleft chain that forces it: Ultralytics (AGPL-3.0) for
  detection/pose, and python-igraph / leidenalg (GPL-2.0+) for association. Add a one-line
  pointer from the README license section. This preempts the "why can't I use this in a closed
  product" issue that MIT-expecting researchers will file.
- **D-10:** The existing `v1.1.0` and `v1.1.1` tags **stay MIT**. An MIT grant already made
  cannot be retroactively revoked. Record the boundary in `CHANGELOG.md` — "as of `1.2.0`,
  AquaPose is licensed AGPL-3.0-or-later" — stated factually, without adjudicating whether
  those MIT releases were already non-compliant given the AGPL/GPL dependency chain.
- **D-11:** Do **not** yank the MIT releases from PyPI.
- **D-12 (pre-decided, from REQUIREMENTS.md):** Per-file AGPL header comments are **out of
  scope** — tracked as deferred requirement `PKG-02`. Repo-level `LICENSE` is sufficient.

### Sphinx Forward-Port

- **D-13:** Establish `docs/api/*.rst` by **taking `main`'s set (which the merge brings), then
  verifying**. Delete `dev`'s dead `mesh.rst`, `optimization.rst`, `segmentation.rst`,
  `utils.rst`. Then confirm every `automodule` target in the surviving files still resolves
  against `dev`'s tree and repair whatever drifted over 1496 commits. Do **not** regenerate
  with `sphinx-apidoc` (flat, unstructured output that Phase 110 would have to redo) and do
  **not** hand-author a fresh tree (duplicates Phase 110's IA work).
- **D-14:** Phase 108's docs bar is **a green build only** — `sphinx-build -W --keep-going`
  exits 0. Module coverage gaps (~52 missing modules) and the tier-one/tier-two IA are
  explicitly **Phase 110's** job per DOCS-01/DOCS-02. Two phases must not both be editing the
  same `.rst` files. Planner: resist widening this.
- **D-15:** Make the docs env **detached with mocked heavy imports**, per `a66287a`
  (`detached = true`; autodoc imports from `src/` via `sys.path`). **The mock list must be
  re-derived against `dev`'s actual imports, not copied blind from `main`** — `dev` has grown
  `timm`, `boxmot`, `leidenalg`/`igraph`, and `ultralytics` since that commit. Rejected
  alternative: installing the project against a CPU-only torch index.
- **D-16:** Forward-port the rest of `a66287a`'s `conf.py` repair: `napoleon_use_ivar` (kills
  the ~53 duplicate-object-description warnings from Google-style `Attributes:` sections
  colliding with `:undoc-members:` dataclass fields), the `version`-as-string fix, and the
  `_resolve_release()` pyproject fallback for the detached env.
- **D-17:** Enforcement is **CI on push to `dev` + PR to `main`** — i.e. `main`'s existing
  `on: push: branches: [main, dev]` in `docs.yml`, which the merge delivers. This is what
  satisfies FOUND-02. Do **not** add `hatch run docs:build` to the pre-push hook (pre-push
  already runs tests; adding a Sphinx build makes every push slow). Wiring the Read the Docs
  build itself as a required check belongs to Phase 114 (DOCS-08).

### Repo Hygiene

- **D-18:** **Un-ignore `.planning/`** — remove the `.gitignore:100` rule and track the
  directory normally. Ends the `git add -f` friction and makes the project record
  reproducible. Safe to do: `pyproject.toml:57` already excludes `.planning/` from the sdist,
  so it never ships to PyPI.
- **D-19:** Delete the untracked junk — `11.0` and the `~/` directory containing the SAM2
  clone — **without** adding defensive `.gitignore` entries. Neither was ever tracked, so the
  "clean fresh clone" criterion is already met and extra ignore rules would be noise.
  **⚠ Execution caveat: see Open Items — `~/PycharmProjects/sam2` contains a `checkpoints/`
  directory of downloaded model weights.**
- **D-20:** Dead-code removal is scoped to exactly two things: `docs/api/{mesh,optimization,
  segmentation,utils}.rst` (needed for the `-W` build regardless) and the empty
  `tests/integration/segmentation/__init__.py` left over from the v3.7 segmentation removal.
  **No broader dead-code sweep** — REQUIREMENTS.md caps this milestone at "bug fixes and
  config-path consolidation", and an audit is not repo hygiene.
- **D-21:** MILESTONES.md repair: backfill **v3.11 Appearance-Based ReID** (REC-01) **and
  v2.2 Backends** (same class of gap, same reconstructability from `ROADMAP.md` +
  `.planning/phases/`), and **re-sort the tail into chronological order**. Do **not** attempt
  to fill the `(none recorded)` accomplishment lists on older entries (e.g. v2.1) — that is
  archaeology across 14 milestones and drifts past FOUND/REC scope.
- **D-22:** Match the existing MILESTONES.md entry format (heading with ship date, phase/plan
  counts, key accomplishments, known gaps) rather than inventing a richer schema.

### Claude's Discretion

- Merge-conflict resolution mechanics for the `main`→`dev` merge, within the constraints of
  D-02, D-03, and D-07.
- Exact ordering of the work (merge first vs. relicense first). Recommended: merge first, so
  the license and docs edits are applied once to the merged result rather than twice.
- The precise `autodoc_mock_imports` list (D-15), derived empirically from a clean detached
  build.
- The wording of the `LICENSING.md` explanation and the `CHANGELOG.md` license-boundary entry.

</decisions>

<open_items>
## Open Items — MUST resolve before execution

- ~~**OI-01 (blocks D-08):** exact copyright string.~~ **RESOLVED 2026-08-17** — user supplied
  the institution; string is locked in D-08.
- **OI-02 (qualifies D-19):** `~/PycharmProjects/sam2` includes a `checkpoints/` directory —
  potentially multi-GB of downloaded SAM2 model weights that are not trivially re-obtainable
  offline. The user chose "delete only," but deleting it is **not required** by any success
  criterion (it was never tracked). **Confirm with the user at execution time before removing
  it**, and prefer moving it aside over `rm -rf`. `11.0` is a throwaway pip log and can be
  deleted unconditionally.

</open_items>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` § "Phase 108: Branch Reconciliation & Repo Hygiene" — goal and the 6
  success criteria. **Read alongside `<scout_findings>` above — criteria 4 is written against
  an inaccurate picture of the repo.**
- `.planning/REQUIREMENTS.md` § Foundation (FOUND-01..05), § Project Record (REC-01),
  § Out of Scope, § Future Requirements (PKG-02 defers per-file AGPL headers).
- `.planning/STATE.md` § Blockers/Concerns — records the RED docs build, the `.planning/`
  gitignore situation, and the missing v3.11 milestone entry.

### The commit being forward-ported
- Git commit `a66287a` (`fix(docs): repair Sphinx build and gate it on push`, on `main`) — the
  full commit message is the specification for the Sphinx repair. Read it with
  `git show a66287a`. It enumerates every warning class that was fatal under `-W`.
- `git show main:docs/conf.py` — the repaired conf, including `napoleon_use_ivar`,
  `_resolve_release()`, and the `version`-as-string fix.
- `git show main:.github/workflows/docs.yml` — already has `on: push: branches: [main, dev]`
  (this is what satisfies FOUND-02).
- `git ls-tree -r --name-only main -- docs/api` — the target `.rst` set.

### Project architecture (for verifying automodule targets resolve)
- `.planning/GUIDEBOOK.md` § 4 "Source Layout" — the canonical package map that `docs/api/*.rst`
  must agree with. **Note:** the Guidebook's § 4 layout is itself slightly stale (it lists
  `core/midline/`; `dev` has `core/pose/` and `core/reid/`). Trust `git ls-files
  'src/aquapose/**/*.py'` over the Guidebook where they disagree.

### Files this phase edits
- `LICENSE`, `pyproject.toml` (`version`, `license`, classifiers, `[tool.hatch.envs.docs]`),
  `.gitignore` (line 100, `.planning/`), `CHANGELOG.md`, `README.md` (license section only),
  `docs/conf.py`, `docs/api/*.rst`, `.github/workflows/docs.yml`,
  `.planning/MILESTONES.md`. New file: `LICENSING.md`.

### Milestone record reconstruction sources (for D-21)
- `.planning/ROADMAP.md` § "v3.11 Appearance-Based ReID (Phases 102-107)" and
  § "v2.2 Backends (Phases 29-33.1)" — phase lists, goals, success criteria, plan counts.
- `.planning/phases/102-*` through `.planning/phases/107-*` — per-phase plans and summaries.
- `.planning/MILESTONES.md` — existing entries define the format to match (D-22).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`main`'s `docs/` tree is the artifact to reuse.** `conf.py`, the 8 `.rst` files, and
  `docs.yml` on `main` are a known-good, verified-from-clean-checkout configuration
  (`a66287a` states it was verified at exit 0 with zero warnings). The merge delivers all of
  them; the work is verification and drift repair, not authorship.
- **`.gitignore` is already substantially correct** for build artifacts — `tmp/` (:94),
  `*.pt` (:97), `runs/` (:99), `docs/_build/`. Only the `.planning/` rule (:100) is wrong.
- **`pyproject.toml:57`** already excludes `.planning/`, `.claude/`, `.hooks/` from the sdist —
  this is what makes D-18 (un-ignoring `.planning/`) safe.

### Established Patterns
- **Hatch env conventions:** `[tool.hatch.envs.docs.scripts] build = "sphinx-build -W
  --keep-going -b html docs docs/_build/html"` already exists on `dev` — the `-W` gate is in
  place, it's the env and the `.rst` targets that fail it.
- **python-semantic-release** owns version bumps (`version_toml =
  ["pyproject.toml:project.version"]`, `tag_format = "v{version}"`, `commit_message =
  "chore(release): {version}"`). The D-03 version set must be compatible with it — a manual
  edit to `1.2.0-dev.0` is fine, but do not hand-craft a release commit or tag.
- **GSD planning commits** currently require `git add -f` because of the `.gitignore` conflict.
  D-18 removes this; expect the first post-D-18 commit to want to add `.planning/` files that
  were previously invisible to `git status`.
- **Pre-commit / pre-push hooks** exist (`.pre-commit-config.yaml`, `.hooks/`), including an
  AST import-boundary checker. D-17 deliberately keeps the docs build out of them.

### Integration Points
- **Merge blast radius:** `pyproject.toml` and `docs/` are the only expected conflict sites.
  Everything else on `main` is 1496 commits behind and will merge cleanly or be superseded.
- **FOUND-02 comes free:** merging `main` brings the `docs.yml` `push: [main, dev]` trigger.
  Verify it survives the merge rather than re-authoring it.
- **Phase 109 hand-off:** the test suite is red (8 failures) and stays red through this phase.
  Do not let a docs-CI change or the merge mask or entangle with those failures.
- **Phase 110 hand-off:** leave the `.rst` tree in a state that is *green but admittedly
  incomplete*. Phase 110 restructures it for tiering and full coverage.
- **Phase 114 hand-off:** `main` sync, release tag, default-branch/RTD-source reconciliation
  (D-04/D-05/D-06), badge row, and the citation block that must match the D-08 copyright
  string.

</code_context>

<specifics>
## Specific Ideas

- The user explicitly wants **`main` left alone** this phase — frozen at `1.1.1`, still the
  GitHub default. The staleness is a knowingly accepted trade, justified by the repo not being
  announced until Phase 114.
- The user chose the **SPDX `-or-later`** form deliberately (FSF-recommended default,
  future-AGPLv4 compatible, matches Ultralytics' own AGPL-3.0 posture).
- The AGPL should read as a **constraint, not a preference** — hence `LICENSING.md` naming the
  specific dependencies (Ultralytics AGPL-3.0; python-igraph / leidenalg GPL-2.0+) that force
  it. `REQUIREMENTS.md` § Out of Scope already records that both escape hatches were considered
  and rejected: Ultralytics Enterprise License (costs money, doesn't address Leiden) and
  replacing Ultralytics to preserve MIT (not realistic — it is the detection and pose
  pipeline).
- The user consistently chose the **bounded** option over the thorough one where the two
  competed (green build not full coverage; two dead artifacts not a sweep), but chose the
  **wider** option where a gap was of the same kind as a required fix (v2.2 alongside v3.11).
  Read that as: fix the class of problem, don't expand into a new class.

</specifics>

<deferred>
## Deferred Ideas

- **Broader dead-code sweep** across `dev` (unreferenced modules, stale `scripts/` and
  `tools/` entries) — an audit, not hygiene. Out of scope per REQUIREMENTS.md § Out of Scope
  ("New pipeline capability … behavior changes are limited to bug fixes and config-path
  consolidation"). Candidate for a future cleanup phase.
- **Filling `(none recorded)` accomplishment lists** in older MILESTONES.md entries (v2.1 and
  others). Archaeology across 14 milestones; not required by REC-01.
- **Per-file AGPL header comments** — already tracked as deferred requirement `PKG-02` in
  REQUIREMENTS.md § Future Requirements.
- **Switching GitHub's default branch to `dev`** — considered and explicitly rejected for this
  phase (D-05). Revisit in Phase 114 alongside the `main` sync and the Read the Docs
  source-branch setting.
- **An interim release at end of Phase 109** to give `main` a trustworthy tagged mid-milestone
  state — considered and rejected (D-04). Could be revisited if Phases 110–113 stretch.
- **Adding `hatch run docs:build` to the pre-push hook** — rejected (D-17) on push-latency
  grounds. Revisit if docs breakage recurs despite CI.
- **Defensive `.gitignore` entries** for `~/` and pip-redirect logs — rejected (D-19) as noise,
  since neither artifact was ever tracked.
- **Yanking the MIT PyPI releases** — rejected (D-11).

</deferred>

---

*Phase: 108-branch-reconciliation-repo-hygiene*
*Context gathered: 2026-08-17*
