---
phase: 114-publication-readme-badges-live-docs
plan: 02
subsystem: external-services
tags: [readthedocs, codecov, badges, release-automation, docs-hosting]
dependency-graph:
  requires: []
  provides:
    - "Verified RTD base URL and four funnel-destination URLs (observed 200)"
    - "Verified shields.io badge endpoints with observed label text"
    - "Live Codecov coverage figure for main"
    - "release.yml retired to workflow_dispatch (unblocks all pushes)"
  affects:
    - "114-04 (README consumes the verified URL table below)"
    - "114-05 (release preconditions: PyPI project already exists; see Findings)"
    - "114-06 (tagging is now the ONLY release path; merge-main pre-decided)"
tech-stack:
  added: []
  patterns:
    - "Deliberate annotated tags as the sole release trigger; no automated version computation"
key-files:
  created: []
  modified:
    - .github/workflows/release.yml
---

# Plan 114-02: Live External Services

## What Changed vs the Plan

The plan's central premise was wrong. It assumed Read the Docs "has never been
imported, so the declared URL 404s" and that the Codecov link was unverified. Both
services were already live and correctly owned. What was actually broken was that
both pointed at branches carrying stale or failing state, and — unplanned by any
plan in this phase — that `release.yml` made every push to `main` or `dev` unsafe.

No RTD import was performed. No Codecov account action was performed. Neither was
needed.

## Decision Overrides

Two decisions recorded in `114-CONTEXT.md` were overridden by the developer during
execution. Both are deliberate and both are load-bearing for later plans.

### Override of D-07 — docs target is `main`/`latest`, not `dev`

D-07 set RTD's default version to `dev`. Overridden: the README badge row and funnel
links target `main` via RTD's `latest` version.

Rationale: `main` was 1732 commits behind `dev` and its `docs/` tree predated the
`getting-started/` and `reference/` sections entirely, so three of the four README
funnel destinations 404'd on the published docs. Rather than repoint docs at `dev`,
the developer elected to fix `main` — "the merge into main is inevitable; main is so
stale it's useless at this point." `main` turned out to be a strict ancestor of `dev`
(0 commits unique to `main`), so the merge was a clean fast-forward.

### Pre-emption of 114-06 Task 1 — merge-main, not tag-dev

114-06 Task 1 stages a `tag-dev` vs `merge-main` decision. That decision is now made:
**merge-main**. `main` was fast-forwarded to `dev` (`2aba732..4e6f179`) during this
plan to unblock the docs target. 114-06 should treat its Task 1 as already decided
and re-merge `dev` into `main` before tagging.

## Blocker Found and Fixed: release.yml

`release.yml` triggered on every push to `main` and `dev`, running
`semantic-release version`. It was live and active — it had been cutting
`1.2.0-dev.N` tags on dev pushes as recently as 2026-09-03, and `RELEASE_TOKEN` works.

Consequences had it been left in place:

- **On `dev`** (`branches.dev.prerelease = true`): every push rewrites
  `pyproject.toml:project.version` from commit history, silently clobbering the
  deliberate `4.0.0` reset that plan 114-03 had just committed.
- **On `main`** (`branches.main.prerelease = false`): additionally cuts a tag matching
  `publish.yml`'s `v[0-9]+.[0-9]+.[0-9]+` trigger and **publishes to PyPI**. Its
  version baseline was `git describe` giving `v1.2.0-dev.6`, so it would have
  published roughly `1.2.0`/`1.3.0` — not `4.0.0` — into an immutable filename.

The workflow's skip guard (`!startsWith(head_commit.message, 'chore(release):')`)
would not have caught this; the head commit was an ordinary `docs(...)` commit.

114-03 anticipated the *manual* form of this trap ("never run `semantic-release
version` on dev to cut the tag") but no plan accounted for the workflow doing it
automatically on push.

**Fix:** `release.yml`'s trigger changed to `workflow_dispatch` only, committed as
`4e6f179`. `publish.yml` is untouched and remains the tag-driven PyPI path. This
aligns automation with the phase's own design, in which 114-06 cuts `v4.0.0` as a
plain annotated tag.

Verified post-push: only `Tests` and `Documentation` fired on both refs; `release.yml`
did not run; no new tags appeared on the remote.

## Verified URL Table

Every URL below was fetched and observed. **Plan 04 must not introduce a URL absent
from this table.**

### Documentation destinations

RTD project slug: `aquapose` (pre-existing, correctly owned).
Canonical base URL: `https://aquapose.readthedocs.io/en/latest/`
Bare domain `https://aquapose.readthedocs.io` redirects to `/en/latest/`.

| URL | Status | Note |
|---|---|---|
| `https://aquapose.readthedocs.io/en/latest/` | 200 | Identity confirmed — serves AquaPose's own content |
| `https://aquapose.readthedocs.io/en/latest/getting-started/installation.html` | 200 | Installation |
| `https://aquapose.readthedocs.io/en/latest/getting-started/concepts.html` | 200 | Concepts |
| `https://aquapose.readthedocs.io/en/latest/getting-started/tutorial.html` | 200 | Tutorial |
| `https://aquapose.readthedocs.io/en/latest/api/index.html` | 200 | API reference |
| `https://aquapose.readthedocs.io/en/latest/reference/index.html` | 200 | CLI/config reference |
| `https://aquapose.readthedocs.io/en/latest/contributing.html` | 200 | Contributing |

All four funnel destinations 404'd before the `main` fast-forward. RTD rebuilt
`latest` automatically via webhook (build 34490897, commit `4e6f179`,
Finished/success).

### Badge endpoints (shields.io, per D-06)

| Endpoint | Status | Observed label |
|---|---|---|
| `img.shields.io/readthedocs/aquapose/latest` | 200 | `docs: passing` |
| `img.shields.io/codecov/c/github/McGrathLab/AquaPose/main` | 200 | `coverage: 69%` |
| `img.shields.io/pypi/pyversions/aquapose` | 200 | `python: 3.11 / 3.12 / 3.13` |
| `img.shields.io/pypi/v/aquapose` | 200 | `pypi: v1.0.0` — will read `v4.0.0` after 114-06 |
| `img.shields.io/badge/license-AGPL--3.0--or--later-blue` | 200 | `license: AGPL-3.0-or-later` |
| `img.shields.io/github/actions/workflow/status/McGrathLab/AquaPose/test.yml?branch=main` | 200 | see Tests Badge below |

### Tests badge

`img.shields.io/github/actions/workflow/status/McGrathLab/AquaPose/test.yml?branch=main`
returns 200 with label **`tests: passing`**.

This is the first green `Tests` run on `main` since 2026-02-19. Run 34480322646
(commit `4e6f179`) succeeded on all 8 jobs: `pre-commit`, `typecheck`, and all six
matrix legs (ubuntu + windows on Python 3.11/3.12/3.13). Notably all three Windows
legs passed, so the badge is honest rather than merely reachable.

All six badges in the D-04 row are therefore shippable. The two PyPI-sourced badges
currently read `v1.0.0`; per the plan they are re-verified in 114-06 after publication.

## Codecov

No account action was required. The project pre-existed and was correctly linked.

The staleness had a benign explanation: Codecov's last report was 2026-02-19, which
is exactly the date of the last **successful** `Tests` run on `main`. The two runs
since (2026-03-06, 2026-08-12) both failed, so nothing uploaded. The upload token was
never broken.

| | Before | After |
|---|---|---|
| `main` coverage | 31%, dated 2026-02-19 | **69.34%**, dated 2026-09-10 |

Per D-05 the badge is informational; no `codecov.yml`, floor, or target was added.

No credential value, partial value, or length appears anywhere in this record.

## Findings for Later Plans

**PyPI project already exists.** `114-03-PLAN.md:17` states the historical tags never
matched `publish.yml`'s trigger, "which is why nothing has ever published." That is
incorrect: `aquapose` **1.0.0** was published to PyPI on 2026-02-19. Implications:

- `v4.0.0` publishes into an existing project, not a fresh name. 114-05 must confirm
  `publish.yml`'s credentials are still valid for it — a precondition no plan lists.
- PyPI's project metadata still points at `github.com/tlancaster6/aquapose`. 114-01
  corrected those URLs in-repo; publishing `v4.0.0` is what propagates the fix to PyPI.

**RTD `stable` version is broken.** Its last build (2026-08-12, commit `45972d9a`)
failed. Not used by this phase, but relevant if docs are ever repointed at a tagged
version.

## Deviations

| # | Deviation | Rationale |
|---|---|---|
| 1 | No RTD import performed | Plan premise false — project already existed and was correctly owned |
| 2 | No Codecov account action performed | Plan premise false — project already linked; staleness caused by failing tests, not a bad token |
| 3 | Docs target `latest`/`main` instead of `dev` | Developer decision, overrides D-07 |
| 4 | `main` fast-forwarded to `dev` during this plan | Developer decision, pre-empts 114-06 Task 1 in favour of merge-main |
| 5 | `.github/workflows/release.yml` modified | Plan declares `files_modified: []`; leaving it unmodified made every subsequent push unsafe and risked an irreversible PyPI publish |

Deviation 5 is the one worth flagging at review: this plan was scoped to modify no
repository files, and it modified one. The alternative was to proceed with a workflow
that would have overwritten plan 114-03's work on the next push and could have burned
a wrong version on PyPI permanently.
