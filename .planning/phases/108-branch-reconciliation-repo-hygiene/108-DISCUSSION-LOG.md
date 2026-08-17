# Phase 108: Branch Reconciliation & Repo Hygiene - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-17
**Phase:** 108-branch-reconciliation-repo-hygiene
**Areas discussed:** Branch reconciliation, AGPL relicense scope, Sphinx forward-port, Hygiene scope

---

## Preamble — scout corrections presented before discussion

Before any question was asked, the repo was scouted and five ROADMAP.md / REQUIREMENTS.md
assumptions were found inaccurate: stray artifacts were already gitignored/untracked; the
"dead" `reconstruction/` and `tracking/` dirs are live production code; the SAM2 clone lives
at `~/PycharmProjects/sam2` rather than in the repo; docs CI is already gated on `dev` from
`main` (the reverse of the roadmap's claim); and `.planning/` is simultaneously gitignored and
force-tracked. Full table in `108-CONTEXT.md` `<scout_findings>`.

---

## Branch Reconciliation

### Q1 — How should main's 4 commits (including the a66287a Sphinx repair) get onto dev?

| Option | Description | Selected |
|--------|-------------|----------|
| Merge main into dev | `git merge main` on dev. Records real ancestry, so every future main→dev sync is conflict-free. Conflicts confined to pyproject.toml and docs/api/*.rst. | ✓ |
| Cherry-pick a66287a only | Smallest diff, but branches keep no recent common ancestor — same 4 commits re-conflict on every future sync; release commits stay orphaned. | |
| Rebase dev onto main | Rewrites 1496 published commits on origin/dev. Breaks clones/forks, destroys SHAs referenced across .planning/. | |

**User's choice:** Merge main into dev (recommended option)

### Q2 — How should the 1.1.0-dev.7 (dev) vs 1.1.1 (main) version conflict resolve?

| Option | Description | Selected |
|--------|-------------|----------|
| Bump dev to 1.2.0-dev.0 | Acknowledges 1.1.1 released; keeps dev on a prerelease channel ahead of it; semantic-release continues normally. Keeps the GSD "v4.0" milestone label separate from the package version. | ✓ |
| Adopt 1.1.1 flat on dev | Simple, but dev builds become indistinguishable from the released 1.1.1. | |
| Jump to 2.0.0-dev.0 | Signals the AGPL relicense as a breaking change. Heavier signal. | |

**User's choice:** Bump dev to 1.2.0-dev.0 (recommended option)

### Q3 — When does `main` get synced to dev's content?

| Option | Description | Selected |
|--------|-------------|----------|
| At end of Phase 114 only | main stays release-only, frozen at 1.1.1 until the publication release cuts. | ✓ |
| Sync main to dev now, in Phase 108 | Branches identical immediately, but publishes 1496 unreleased commits as "main" with no tag and unfinished AGPL/docs work. | |
| Cut an interim release at end of Phase 109 | Sync once tests are green, giving main a trustworthy tagged mid-milestone state. | |

**User's choice:** At end of Phase 114 only (recommended option)

### Q4 — GitHub's default branch is `main`. What should a visitor land on?

| Option | Description | Selected |
|--------|-------------|----------|
| Switch default to dev | Visitors and RTD both see the live tree; matches DOCS-08. Requires a manual GitHub repo setting change. | |
| Keep main as default | Conventional, but only works if main is synced soon — otherwise visitors land on a 1496-commit-stale MIT tree for the rest of the milestone. | ✓ |
| You decide | Let the planner pick based on how the main-sync answer lands. | |

**User's choice:** Keep main as default

**Notes:** Q3 and Q4 were flagged as coupled. Taken together they mean a GitHub visitor lands
on a stale, MIT-declaring tree for Phases 108–113. Confirmed as an accepted consequence on the
grounds that the repository is not announced until Phase 114 — recorded as D-06 so a downstream
planner does not "helpfully" flip the default branch. RTD source-branch reconciliation (RTD must
build from `dev` while `main` is default) was pushed to Phase 114 with DOCS-08.

---

## AGPL Relicense Scope

### Q1 — What should the AGPL copyright line say?

| Option | Description | Selected |
|--------|-------------|----------|
| Real name | e.g. `Copyright (C) 2026 Tucker Lancaster`. Standard for a single-author academic tool. | |
| Name + institution | Correct if produced under an institutional appointment; many universities assert copyright in research software. | ✓ |
| Keep the GitHub handle | `tlancaster6`. Unambiguous but reads as a placeholder and won't match the citation block. | |

**User's choice:** Name + institution

**Notes:** Exact strings were not supplied at selection time, so this was recorded as blocking
open item OI-01. The user supplied the institution later in the session —
"the McGrath Lab at the Georgia Institute of Technology". The personal name was taken from
`docs/conf.py` (`author = "Tucker Lancaster"`), already the repo's declared author. Final
string locked in D-08; OI-01 closed.

### Q2 — Which AGPL-3.0 variant?

| Option | Description | Selected |
|--------|-------------|----------|
| AGPL-3.0-or-later | FSF-recommended default; allows future AGPLv4; matches Ultralytics' own AGPL-3.0 posture. | ✓ |
| AGPL-3.0-only | Pins to exactly v3; maximally predictable, forecloses future-version compatibility. | |

**User's choice:** AGPL-3.0-or-later (recommended option)

### Q3 — Should the repo explain *why* it's AGPL rather than just declaring it?

| Option | Description | Selected |
|--------|-------------|----------|
| Short LICENSING.md + README note | Names the copyleft chain forcing AGPL — Ultralytics (AGPL-3.0), python-igraph/leidenalg (GPL-2.0+) — plus a README pointer. Preempts "why can't I use this commercially" issues. | ✓ |
| One README paragraph only | Lighter, but buried in a doc Phase 114 rewrites anyway. | |
| Declare only, no rationale | Minimal work; leaves AGPL looking like a preference rather than a constraint. | |

**User's choice:** Short LICENSING.md + README note (recommended option)

### Q4 — How should the MIT-released v1.1.0 / v1.1.1 tags be handled?

| Option | Description | Selected |
|--------|-------------|----------|
| Leave them MIT, note the change forward | An MIT grant already made can't be revoked. Record the boundary in CHANGELOG.md, stated factually without adjudicating whether those releases were already non-compliant. | ✓ |
| Also yank the MIT releases from PyPI | Removes the mislicensed artifacts but breaks pinned users and invites questions. | |
| You decide | Least-noisy correct handling. | |

**User's choice:** Leave them MIT, note the change forward (recommended option)

---

## Sphinx Forward-Port

Context supplied before the questions: `main`'s `docs/api/*.rst` set maps cleanly onto `dev`'s
top-level packages; `dev`'s `conf.py` lacks `napoleon_use_ivar`, mock imports, and the
`version`-as-string fix; `dev`'s `[tool.hatch.envs.docs]` is not detached and still pulls
~5.8 GB of CUDA torch.

### Q1 — How should the docs/api/*.rst set be established on dev?

| Option | Description | Selected |
|--------|-------------|----------|
| Take main's set, then verify | Merge brings main's 8 .rst files; delete dev's dead mesh/optimization/segmentation/utils.rst; verify each automodule target resolves and repair drift. | ✓ |
| Re-derive from scratch via sphinx-apidoc | Guarantees completeness but produces flat output Phase 110 would have to restructure. | |
| Hand-author against dev's tree | Most control, most effort, duplicates Phase 110's IA work. | |

**User's choice:** Take main's set, then verify (recommended option)

### Q2 — How much API coverage should land in Phase 108 vs Phase 110?

| Option | Description | Selected |
|--------|-------------|----------|
| Green build only — 108 | Bar is `sphinx-build -W --keep-going` exits 0. Coverage and tiering are Phase 110's job per DOCS-01/02. Avoids two phases editing the same .rst files. | ✓ |
| Green build + all top-level packages present | Slightly wider; leaves only submodule depth and tiering for 110. | |
| Pull DOCS-02 forward into 108 | Would collapse 110 into 108 and mix "make it build" with "make it good". | |

**User's choice:** Green build only — 108 (recommended option)

### Q3 — How should the docs environment resolve heavy deps?

| Option | Description | Selected |
|--------|-------------|----------|
| Detached + mock imports, per a66287a | `detached = true`, autodoc via sys.path, heavy deps mocked; env drops to ~203MB. Mock list must be re-derived against dev's grown dep set (timm, boxmot, leidenalg/igraph, ultralytics). | ✓ |
| Install project with CPU-only torch | Autodoc imports real modules — catches errors mocking hides — but slower and more fragile. | |
| You decide | Let research determine what survives RTD limits. | |

**User's choice:** Detached + mock imports, per a66287a (recommended option)

### Q4 — Where should the docs build be enforced?

| Option | Description | Selected |
|--------|-------------|----------|
| CI on push to dev + PR to main | Forward-ports main's `on: push: [main, dev]`, satisfying FOUND-02 as a side effect of the merge. | ✓ |
| CI + a pre-push hook | Catches breakage before it reaches GitHub but adds a slow Sphinx build to every push; pre-push already runs tests. | |
| CI only, plus RTD build status as a required check | Strongest signal, but RTD config work is scoped to Phase 114 (DOCS-08). | |

**User's choice:** CI on push to dev + PR to main (recommended option)

---

## Hygiene Scope

Context supplied before the questions: the SAM2 clone was located at `~/PycharmProjects/sam2`
(a literal `~` dir from a bad shell expansion); `11.0` is a `pip install boxmot` redirect log;
`.gitignore:100` ignores `.planning/` while 31 planning files are force-tracked; MILESTONES.md
is missing v2.2 as well as v3.11 and its tail entries are out of chronological order.

### Q1 — How should the `.planning/` gitignore-vs-tracked contradiction resolve?

| Option | Description | Selected |
|--------|-------------|----------|
| Un-ignore and track .planning/ | Drop the .gitignore:100 rule; ends `git add -f` friction. Safe because pyproject.toml:57 already excludes .planning/ from the sdist. | ✓ |
| Keep ignored, untrack the 31 files | Honest in the other direction, but deletes the committed record and makes every future GSD commit a forced add. | |
| Keep as-is, document the add -f | Zero risk; friction and inconsistency persist through six more phases. | |

**User's choice:** Un-ignore and track .planning/ (recommended option)

### Q2 — How should the untracked junk be handled?

| Option | Description | Selected |
|--------|-------------|----------|
| Delete both + harden .gitignore | Remove from working tree plus defensive ignore entries against recurrence. | |
| Delete only | Remove the files; skip ignore entries since neither was ever tracked and the "clean fresh clone" criterion is already met. | ✓ |
| Gitignore only, leave files on disk | Preserves the local SAM2 clone; leaves the working tree cluttered. | |

**User's choice:** Delete only

**Notes:** Flagged back to the user that `~/PycharmProjects/sam2` contains a `checkpoints/`
directory of downloaded model weights, that deleting it is not required by any success
criterion, and that the plan should move it aside rather than `rm -rf` and confirm at
execution time. Recorded as open item OI-02 qualifying D-19. `11.0` can be deleted
unconditionally.

### Q3 — What dead code is in scope?

| Option | Description | Selected |
|--------|-------------|----------|
| Docs .rst + empty test package | Delete docs/api/{mesh,optimization,segmentation,utils}.rst (needed for -W anyway) and the empty tests/integration/segmentation/__init__.py from the v3.7 segmentation removal. | ✓ |
| Docs .rst only | Touch only what blocks the Sphinx build. | |
| Add a broader dead-code sweep | Real value, but it's an audit, not hygiene — REQUIREMENTS caps this milestone at bug fixes and config-path consolidation. | |

**User's choice:** Docs .rst + empty test package (recommended option)

### Q4 — How far should the MILESTONES.md repair go?

| Option | Description | Selected |
|--------|-------------|----------|
| Backfill v3.11 + v2.2, fix ordering | REC-01 names only v3.11, but v2.2 is the same class of gap and equally reconstructable; re-sorting the tail is mechanical. | ✓ |
| v3.11 only, exactly as REC-01 states | Strict requirement adherence; leaves v2.2 missing and ordering scrambled in a publication-facing file. | |
| Full pass — also fill v2.1's "(none recorded)" | Most complete, but archaeology across 14 milestones, well past FOUND/REC scope. | |

**User's choice:** Backfill v3.11 + v2.2, fix ordering (recommended option)

---

## Claude's Discretion

No question was answered with an explicit "You decide". Discretion was assigned in CONTEXT.md
for four implementation-level items the user's answers did not constrain:

- Merge-conflict resolution mechanics for the `main`→`dev` merge (within D-02, D-03, D-07).
- Work ordering — merge first vs. relicense first (recommendation: merge first, so license and
  docs edits are applied once to the merged result).
- The precise `autodoc_mock_imports` list, derived empirically from a clean detached build.
- Wording of `LICENSING.md` and the `CHANGELOG.md` license-boundary entry.

## Deferred Ideas

No scope creep was proposed by the user. The deferrals below are rejected alternatives and
adjacent gaps surfaced during scouting, recorded so they are not lost:

- Broader dead-code sweep across `dev` (unreferenced modules, stale `scripts/`/`tools/`).
- Filling `(none recorded)` accomplishment lists in older MILESTONES.md entries (v2.1 et al.).
- Per-file AGPL header comments — already tracked as deferred requirement `PKG-02`.
- Switching GitHub's default branch to `dev` — revisit in Phase 114.
- An interim release at end of Phase 109 to give `main` a tagged mid-milestone state.
- Adding `hatch run docs:build` to the pre-push hook.
- Defensive `.gitignore` entries for `~/` and pip-redirect logs.
- Yanking the MIT PyPI releases.
