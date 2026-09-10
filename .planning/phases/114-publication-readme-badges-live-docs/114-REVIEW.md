---
phase: 114-publication-readme-badges-live-docs
reviewed: 2026-09-10T00:00:00Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - .github/workflows/release.yml
  - CHANGELOG.md
  - CITATION.cff
  - CODE_OF_CONDUCT.md
  - README.md
  - docs/contributing.md
  - pyproject.toml
findings:
  critical: 2
  warning: 2
  info: 1
  total: 5
status: issues_found
---

# Phase 114: Code Review Report

**Reviewed:** 2026-09-10
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

This phase is documentation/packaging-only, and its stated goal — a correct, live,
citable publication — is largely met: the release.yml trigger change is sound and
correctly reasoned, CITATION.cff carries the concept DOI as intended, and the DOI/URL
verification tables in the plan summaries are thorough. However, two BLOCKER-grade
factual defects survive into permanently-published artifacts (README.md is PyPI's
immutable long description for 4.0.0; CHANGELOG.md ships in the sdist/repo as the
canonical release history):

1. README's "Pipeline" section describes a 3-version-stale architecture (OC-SORT
   tracking, YOLO-seg midline backend, wrong stage order) that was already fact-checked
   twice for CLI commands in this phase but never checked against the actual pipeline
   code or PROJECT.md.
2. CHANGELOG.md's "Migration Notes" asserts "AquaPose had never been published to PyPI
   before `4.0.0`" — a claim this very phase's own plan summaries (114-02, 114-06)
   falsify: `aquapose` 1.0.0 was found live on PyPI, published 2026-02-19.

Both are checked-in facts an outside researcher (the stated audience for this
milestone) would read and rely on. Two WARNING-level findings concern leftover
automation configuration that is misleading now that release automation is retired
but not removed.

## Critical Issues

### CR-01: README "Pipeline" section describes a stale, removed architecture

**File:** `README.md:22-32`
**Issue:** The pipeline description reads:

```
1. **Detection** — YOLO-based fish detection (standard or oriented bounding boxes)
2. **Tracking** — Per-camera 2D temporal tracking via OC-SORT
3. **Association** — Cross-camera tracklet association using ray-ray geometry and Leiden clustering
4. **Midline** — 2D midline extraction via YOLO-seg or YOLO-pose backends
5. **Reconstruction** — DLT triangulation of 2D midlines into 3D B-spline midlines
```

Per `PROJECT.md`, `CLAUDE.md`, and the actual stage implementations
(`src/aquapose/core/{detection,pose,tracking,association,reconstruction}/stage.py`,
`src/aquapose/engine/pipeline.py:280-289`), every one of these claims is stale by at
least one major version:

- OC-SORT/BoxMot was **completely removed in v3.7** and replaced by a custom
  OKS-based `KeypointTracker` (24-dim Kalman filter). There is no OC-SORT dependency
  in `pyproject.toml`.
- The segmentation midline backend (`YOLO-seg`) was **fully removed in v3.7**
  (`SegmentationStage`/`backends/segmentation.py` deleted). `YOLO-pose` is the sole
  midline/keypoint source, and it now runs as **Stage 2** (`PoseStage`), not Stage 4.
- The actual stage order (confirmed in `engine/pipeline.py:280-289`, "v3.7 pipeline
  ordering") is **Detection → Pose → 2D Tracking → Association → Reconstruction** —
  tracking and midline extraction are transposed relative to what the README states,
  and "Midline" is not a separate stage from pose estimation at all.
- "DLT triangulation of 2D midlines into 3D B-spline midlines" is also stale: since
  v3.9, raw triangulated keypoints are the **primary** output (`spline_enabled=False`
  by default); B-spline fitting is optional post-processing, not the pipeline's
  standard output.

This is the top-level architecture description in the file PyPI displays as the
package's long description — already published and immutable for 4.0.0 — read by
exactly the audience (outside researchers) this milestone targets. This phase's own
plan summaries record a prior pass that fixed two nonexistent CLI commands in this
same file but evidently didn't cross-check the pipeline narrative against the current
codebase.

**Fix:** Correct the ordered list to match `engine/pipeline.py`'s documented v3.7
ordering, e.g.:

```markdown
1. **Detection** — YOLO-based fish detection (oriented bounding boxes)
2. **Pose Estimation** — 2D keypoint extraction via YOLO-pose (6 anatomical keypoints)
3. **Tracking** — Per-camera 2D temporal tracking via a custom OKS-based keypoint tracker
4. **Association** — Cross-camera tracklet association using ray-ray geometry and Leiden clustering
5. **Reconstruction** — Confidence-weighted DLT triangulation of 2D keypoints into 3D midlines, with optional B-spline fitting
```

Since this reaches PyPI verbatim, a follow-up release (patch or otherwise) is needed
to correct the already-published copy — this cannot be silently fixed in the repo
without also being republished.

### CR-02: CHANGELOG.md falsely claims AquaPose was never published to PyPI before 4.0.0

**File:** `CHANGELOG.md:21-23`
**Issue:**

```markdown
AquaPose had never been published to PyPI before `4.0.0`. If you go looking for
`2.x` or `3.x` releases on PyPI, you will not find them, because none were ever
made; `4.0.0` is the first release that exists there at all.
```

This is directly contradicted by this same phase's own plan summaries:
`114-02-SUMMARY.md` ("**PyPI project already exists.** ... `aquapose` **1.0.0** was
published to PyPI on 2026-02-19.") and `114-06-SUMMARY.md` ("`aquapose` now carries
two releases: the pre-existing `1.0.0` (2026-02-19) and `4.0.0`. This was not a first
upload"). The CHANGELOG entry appears to have been written from the earlier, false
premise in `114-03-PLAN.md` ("nothing has ever published") before that premise was
overturned during 114-02/114-06, and was never corrected.

The claim is technically true only in the narrow sense that no *2.x/3.x* release
exists (version numbers were never published, since 1.0.0 was published under the old
scheme) — but the surrounding sentence ("never been published... 4.0.0 is the first
release that exists there at all") is flatly false and will mislead anyone checking
PyPI's release history against this file, where they will find `1.0.0` sitting
alongside `4.0.0`.

**Fix:**

```markdown
No `2.x` or `3.x` release was ever published to PyPI under this version scheme — an
earlier `1.0.0` release exists on PyPI (published 2026-02-19, predating this
milestone's version reset), so `pypi.org/project/aquapose/` shows two releases:
`1.0.0` and `4.0.0`. Users should treat `4.0.0` as the first release produced under
the current (post-reset) versioning and packaging.
```

## Warnings

### WR-01: release.yml's guard condition is vestigial and misleading for its new (sole) trigger

**File:** `.github/workflows/release.yml:20`
**Issue:** The job condition is:

```yaml
if: "!startsWith(github.event.head_commit.message, 'chore(release):')"
```

This was meaningful when the trigger was `push`, where `github.event.head_commit`
exists. Now that the trigger is `workflow_dispatch` only (as the file's own header
comment explains), `github.event.head_commit` is undefined for that event type, so
`github.event.head_commit.message` evaluates to `null`, `startsWith(null, ...)`
coerces to `false`, and the guard always evaluates to `true` — i.e., it is a no-op
that happens to not block the (now-manual) run, but for reasons unrelated to its
stated purpose. This is exactly the kind of leftover the phase context flagged as
worth checking. It doesn't cause incorrect behavior today (workflow_dispatch always
proceeds, which is the desired manual-trigger behavior), but it will confuse the next
person editing this file, who will reasonably assume the guard does something for
manual runs.

**Fix:** Either remove the now-meaningless condition, or replace it with something
that actually gates manual dispatch (e.g., nothing — a human invoking
`workflow_dispatch` has already opted in):

```yaml
jobs:
  release:
    runs-on: ubuntu-latest
    concurrency: release
```

### WR-02: `[tool.semantic_release]` / `[tool.hatch.envs.release]` remain fully wired for a workflow that's retired

**File:** `pyproject.toml:108-109, 155-179`
**Issue:** `114-02-SUMMARY.md` documents in detail that `semantic-release version` is
a live trap — running it (in CI or manually) rewrites `project.version` from commit
history and would clobber the deliberate `4.0.0` reset, and that `114-03` had already
identified "never run `semantic-release version` on dev to cut the tag" as a manual
hazard. `release.yml`'s trigger was disabled specifically to prevent CI from doing
this automatically. But `pyproject.toml` still declares a fully configured
`[tool.hatch.envs.release]` environment with `python-semantic-release` installed and
a complete `[tool.semantic_release]` config (branches, changelog, commit parser,
`GH_TOKEN` remote). This means the exact command the project has twice identified as
dangerous (`hatch run -e release semantic-release version`) remains one command away
for any contributor or future CI author who doesn't know the history documented only
in a plan summary buried in `.planning/`. The phase context explicitly invited
scrutiny of "whether leaving this config in place is now misleading or a latent trap
given automation is retired" — it is.

**Fix:** At minimum, add a comment above `[tool.hatch.envs.release]` and
`[tool.semantic_release]` cross-referencing why automated versioning is retired (the
`release.yml` header comment is a good model) so the hazard is discoverable without
digging into `.planning/`. Consider whether the env/config should be removed entirely
now that tagging is manual, or gated more visibly (e.g., a script wrapper that refuses
to run outside an explicit `--i-know-this-clobbers-the-version` flag).

## Info

### IN-01: README pipeline stage count claim ("5-stage") is still numerically correct but reinforces CR-01

**File:** `README.md:24`
**Issue:** "AquaPose processes multi-view video through a 5-stage pipeline" — the
stage *count* is accurate (Detection, Pose, Tracking, Association, Reconstruction),
so this line itself needs no change, but note it when fixing CR-01: the list below it
must still enumerate exactly 5 items after correction (adding "Pose Estimation" as
its own stage and folding "Midline" into it, rather than simply adding a 6th bullet).

**Fix:** No standalone action; verify the corrected CR-01 list still totals 5 items
consistent with this sentence.

---

_Reviewed: 2026-09-10_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
