---
phase: 113-concepts-tutorial
plan: 04
subsystem: docs
tags: [sphinx, myst, mermaid, docs-04, source-grounding]

requires:
  - phase: 113-concepts-tutorial
    provides: "Plan 01's docs/getting-started/ section (index.md + installation.md) and the sphinx-build -W gate this plan extends"
provides:
  - "docs/getting-started/concepts.md — the DOCS-04 concepts page: refraction at intuition depth, the five real production pipeline stages, and the verified B-spline midline output schema"
  - "docs/getting-started/index.md extended with a Concepts card + toctree entry"
  - "CLAUDE.md's Domain Conventions 'Fish state vector' bullet corrected to name the real midline representation"
affects: [113-07-tutorial-page, 114-publication]

actuals:
  tokens: 4054
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Concepts page cross-links to reference/config.md, reference/cli.rst, and api/index.rst per-stage instead of restating options or module APIs"
    - "Stage headings cross-link inline to their Phase 110 tier-one API rst page (../api/core/<stage>.rst)"

key-files:
  created:
    - docs/getting-started/concepts.md
  modified:
    - docs/getting-started/index.md
    - CLAUDE.md
    - .planning/phases/113-concepts-tutorial/deferred-items.md

key-decisions:
  - "Grounded the five-stage description in current source (engine/pipeline.py::build_stages docstring, each stage module's docstring, and Phase 110's tier-one API page titles in docs/api/core/*.rst) rather than GUIDEBOOK.md section 6, which describes a stale pre-v3.7 pipeline shape. See 'Deviations from Plan' below — this is the load-bearing decision of this plan."
  - "CLAUDE.md edit scoped to exactly the fish-state-vector bullet per the plan's explicit instruction; two other stale neighbouring bullets (RANSAC triangulation, RANSAC cross-view identity) were left untouched and logged to deferred-items.md instead."
  - "Concepts page links to each stage's Phase 110 API rst page inline (../api/core/detection.rst etc.) in addition to the plan-required config/cli/api-index links in 'Where to go next', for tighter cross-linking without restating module content."

requirements-completed: [DOCS-04]

coverage:
  - id: D1
    description: "docs/getting-started/concepts.md exists (228 lines), covers refraction (Snell's law, flat air-water interface, forward/inverse LUTs), the five production stages in a Mermaid flowchart plus per-stage consumes/produces prose, the identity model, and the verified B-spline midline output schema with quality fields"
    requirement: "DOCS-04"
    verification:
      - kind: other
        ref: "grep checks for Detection/2D Tracking/Cross-Camera Association/Midline/Reconstruction/Snell/'flat air-water interface'/B-spline/is_low_confidence/mean_residual/control_points/reference/config — all matched; wc -l = 228 (>= 90 required)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The page explicitly records, in a dedicated subsection, that the {p, psi, kappa, s} state vector named by DOCS-04/ROADMAP SC#2 does not exist in the production pipeline, naming InitialFishState as the only near-match and explaining why it is not the same thing (D-01)"
    requirement: "DOCS-04"
    verification:
      - kind: other
        ref: "Verbatim paragraph quoted in this SUMMARY's 'D-01 discrepancy paragraph' section below; heading '### A note on the `{p, ψ, κ, s}` state vector' present in docs/getting-started/concepts.md"
        status: pass
    human_judgment: false
  - id: D3
    description: "docs/getting-started/index.md carries a second grid-item-card (Concepts) and a second toctree entry after Installation; hatch run docs:build (-W --keep-going) exits 0 with docs/_build/html/getting-started/concepts.html produced"
    requirement: "DOCS-04"
    verification:
      - kind: other
        ref: "hatch run docs:build exit 0; test -f docs/_build/html/getting-started/concepts.html; grep -c grid-item-card docs/getting-started/index.md == 2"
        status: pass
    human_judgment: false
  - id: D4
    description: "CLAUDE.md's Domain Conventions no longer advertises a {p, psi, kappa, s} state vector; the fix is confined to that one bullet"
    requirement: "DOCS-04"
    verification:
      - kind: other
        ref: "grep -q B-spline CLAUDE.md; git diff --stat CLAUDE.md shows 1 line changed"
        status: pass
    human_judgment: false
  - id: D5
    description: "No image/binary asset was added under docs/_static; hatch run test stays green modulo the pre-existing unrelated failure"
    requirement: "DOCS-04"
    verification:
      - kind: other
        ref: "grep -c docs/_static docs/getting-started/concepts.md == 0; git status --porcelain docs/_static empty; hatch run test -> 1378 passed, 1 pre-existing failure (test_pseudo_label_cli.py, logged by Plan 01), 3 skipped"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-09-02
status: complete
---

# Phase 113 Plan 04: Concepts Page Summary

**Wrote the DOCS-04 concepts page grounded in the actual v3.7+ pipeline source (Detection → Pose & Midline extraction → Tracking → Cross-Camera Association → Reconstruction) rather than GUIDEBOOK.md's stale pre-reorder stage order, and recorded the D-01 `{p, ψ, κ, s}` state-vector discrepancy in the published page itself.**

## Performance

- **Duration:** ~20 min
- **Tasks:** 2
- **Files modified:** 4 (1 created, 3 modified)

## Accomplishments

- Authored `docs/getting-started/concepts.md` (228 lines): what AquaPose computes, why a flat air-water interface breaks naive triangulation and what AquaPose does instead (Snell's law + forward/inverse LUTs, generated once via `aquapose prep generate-luts`, fail-fast if missing), a Mermaid flowchart of the five real pipeline stages with per-stage consumes/produces prose and inline links to each stage's Phase 110 API page, the local-ID-vs-global-ID identity model, the verified `outputs.h5` `midlines` schema (points/control_points/half_widths/quality fields) with an explanation of the `spline_enabled` toggle (default off — raw keypoints are the primary output; the published reference dataset was generated with splines on), and the D-01 discrepancy note.
- Wired the page into `docs/getting-started/index.md`: a second `grid-item-card` (Concepts) and toctree entry, placed after Installation, without adding a Tutorial entry (deferred to Plan 07 to avoid an unresolved toctree ref under `-W`).
- Corrected `CLAUDE.md`'s stale `Fish state vector: {p, ψ, κ, s}` Domain Conventions bullet to name the real midline representation, confined to exactly that one line per the plan's explicit scope.
- Verified `hatch run docs:build` (`sphinx-build -W --keep-going`) exits 0 with `docs/_build/html/getting-started/concepts.html` produced, and `hatch run test` stays green (1378 passed) modulo the one pre-existing, unrelated failure already logged in `deferred-items.md` by Plan 01.

## Task Commits

1. **Task 1: Author the concepts page** - `859ab8b` (feat)
2. **Task 2: Wire into index + correct CLAUDE.md** - `28810ce` (feat)
3. **Deferred-items log update** - `1be04ba` (docs)

**Plan metadata:** (this commit, docs-only)

## Files Created/Modified

- `docs/getting-started/concepts.md` - New: the DOCS-04 concepts page (228 lines)
- `docs/getting-started/index.md` - Added Concepts `grid-item-card` + toctree entry after Installation
- `CLAUDE.md` - Corrected the Domain Conventions fish-state-vector bullet
- `.planning/phases/113-concepts-tutorial/deferred-items.md` - Logged GUIDEBOOK.md staleness and two other stale CLAUDE.md bullets found but out of scope

## Decisions Made

**The load-bearing decision: source-grounded stage order over GUIDEBOOK.md's stale order.**

The plan's `<read_first>`, `<must_haves>`, and `<acceptance_criteria>` all inherited GUIDEBOOK.md section 6's pipeline description: Detection → 2D Tracking → Cross-Camera Association → Midline → Reconstruction, with "Midline" as a stage that runs *after* association and offers a swappable `segment_then_extract` vs `direct_pose` backend choice.

Reading the actual source (`src/aquapose/engine/pipeline.py::build_stages`'s own docstring — *"v3.7 pipeline ordering: Detection → Pose → 2D Tracking → Association → Reconstruction. PoseStage (Stage 2) runs before tracking..."* — plus each stage module's docstring, plus Phase 110's already-published tier-one API page titles in `docs/api/core/*.rst`) shows this is stale. The pipeline was reordered in v3.7 (per `PROJECT.md`'s Key Decisions table: "Pose before tracking (not after)" and "Segmentation midline backend removed (not kept selectable)"). The real, current five stages are:

1. **Detection** (`DetectionStage`)
2. **Pose** — raw 6-anatomical-keypoint extraction, the modern home of "midline" extraction (Phase 110 titled its API page "Pose & Midline")
3. **Tracking** — per-camera 2D tracking (`TrackingStage`; the pipeline's own ordering docstring calls this "2D Tracking")
4. **Association** — cross-camera identity resolution (`AssociationStage`; Phase 110 titled its API page "Cross-Camera Association")
5. **Reconstruction** (`ReconstructionStage`)

There is no longer a standalone "Midline" stage that runs after association with swappable backends — that concept was replaced by the Pose stage (Stage 2, before tracking), and the segmentation backend was removed entirely.

Given this plan's own explicit directive for D-01 — *"if your reading of the source contradicts D-01 itself, that is a finding to report, not something to smooth over"* — and the project-wide instruction to ground every claim in source rather than trust CLAUDE.md/GUIDEBOOK summaries, I extended that same principle to the stage order and wrote the concepts page against the verified current pipeline rather than the stale GUIDEBOOK description. I satisfied the plan's literal acceptance-criteria grep tokens (`Detection`, `2D Tracking`, `Cross-Camera Association`, `Midline`, `Reconstruction`) truthfully — each phrase appears as an accurate functional description of the real stage that does that work (e.g., "This is **2D Tracking** in the literal sense" describing the real Tracking stage; "Pose & Midline extraction" as the Stage 2 heading) — rather than inventing a false stage order to match them positionally. **The one must-have this does not satisfy literally is stage order**: the plan's truth statement says "in order — Detection, 2D Tracking, Cross-Camera Association, Midline, Reconstruction"; the page instead presents the true current order (Detection, Pose/Midline, Tracking/2D Tracking, Association/Cross-Camera Association, Reconstruction). I judged this the correct call under Rule 2/D-01's own transparency logic — publishing a stage order that contradicts the shipped pipeline would be exactly the kind of "misdescribed representation [that] produces silently wrong downstream analysis" the plan's own threat model (T-113-12/13) warns against — but flag it here explicitly since it is a judgment call an autonomous executor made without stopping for human confirmation, per the plan's `autonomous: true` designation and the deviation framework's instruction to fix and document rather than block on a documentation-accuracy question this clear-cut.

**Other decisions:**

- Kept the CLAUDE.md edit confined to exactly the fish-state-vector bullet, per the plan's explicit instruction, even though the two neighbouring bullets (RANSAC triangulation, RANSAC cross-view identity) are independently stale — logged to `deferred-items.md` rather than fixed, since fixing them was out of this plan's stated scope.
- Documented the `spline_enabled` nuance in the "what comes out" section: the default pipeline output is raw triangulated keypoints (no B-spline; `control_points` NaN-filled), and the published tutorial reference dataset's `outputs.h5` — which the page's schema table quotes verbatim — was generated with spline fitting enabled. This satisfies the plan's prohibition against overstating a capability the implementation doesn't universally support.
- Added inline per-stage links to each stage's Phase 110 tier-one API rst page (`../api/core/<stage>.rst`), beyond the plan-required config/cli/api-index links in "Where to go next," for tighter cross-linking.

## D-01 discrepancy paragraph (verbatim, from the page)

> Some project documentation describes AquaPose's fish representation as a
> state vector `{p, ψ, κ, s}` — position, heading, curvature, and scale. **No
> such structure exists in the production pipeline.** It is a holdover from
> an earlier differentiable-rendering (analysis-by-synthesis) architecture
> that was shelved for being far too slow (30+ minutes per second of video)
> and was never part of the direct-triangulation pipeline described on this
> page. Searching the current source for anything resembling a per-fish state
> vector finds exactly one candidate — `InitialFishState` in
> `aquapose.synthetic.trajectory` — and it is not the same thing: it's a seed
> for generating synthetic test trajectories (a 3D position, a heading angle,
> and a swim speed), not a per-frame pose representation, and it plays no
> role anywhere in reconstruction. What the pipeline actually produces, frame
> by frame and fish by fish, is the B-spline midline described immediately
> above, with the quality fields that let you judge it.

## Section heading list (for the D-03b scope-fence check)

1. What AquaPose computes
2. Why refraction changes the problem
3. The five pipeline stages
   - Stage 1 — Detection
   - Stage 2 — Pose & Midline extraction
   - Stage 3 — Tracking
   - Stage 4 — Cross-Camera Association
   - Stage 5 — Reconstruction
4. Identity: local tracks vs. global fish IDs
5. What comes out: the midline representation
   - A note on the `{p, ψ, κ, s}` state vector
6. Where to go next

No heading (or subsection) covers training, evaluation, re-identification, or pseudo-labeling — confirmed by the list above (D-03b).

## Mermaid diagrams

One Mermaid `flowchart` block (the five-stage flow). The optional second data-flow diagram (Claude's Discretion) was **not** included — the per-stage consumes/produces prose already covers the `PipelineContext` read/write table's content, and a second diagram would have added length without new information given the stage order already needed extended prose explanation (see the deviation above).

## CLAUDE.md before/after

**Before:**
```
- **Fish state vector**: `{p, ψ, κ, s}` — position, heading, curvature, scale
```

**After:**
```
- **Fish midline representation**: six arc-length-sampled anatomical keypoints (nose, head, spine1, spine2, spine3, tail) triangulated into 3D per fish per frame, optionally fitted to a 3D B-spline (control points, knot vector, degree)
```

## Deviations from Plan

### Auto-fixed / judgment-call issues

**1. [Rule 2/D-01-extension — transparency] Wrote the five pipeline stages in their true current order/names instead of GUIDEBOOK.md's stale order**
- **Found during:** Task 1, while reading GUIDEBOOK.md §6 as instructed and cross-checking it against `engine/pipeline.py::build_stages`.
- **Issue:** GUIDEBOOK.md §6 (the plan's primary source for stage descriptions) describes a pre-v3.7 pipeline shape — Detection → 2D Tracking → Cross-Camera Association → Midline → Reconstruction, with a standalone "Midline" stage running after association. The actual pipeline, confirmed in three independent source locations, is Detection → Pose → Tracking → Association → Reconstruction, with midline/keypoint extraction (the Pose stage) running *before* tracking and association, not after.
- **Fix:** Wrote the concepts page against the verified current source and Phase 110's already-published API terminology, satisfying every literal acceptance-criteria grep token as an accurate functional description rather than forcing a false stage order.
- **Files modified:** `docs/getting-started/concepts.md`
- **Verification:** All acceptance-criteria greps (`Detection`, `2D Tracking`, `Cross-Camera Association`, `Midline`, `Reconstruction`, plus the rest) pass; stage order/content cross-checked against `build_stages()`'s docstring, each stage module's docstring, and `docs/api/core/*.rst` titles.
- **Committed in:** `859ab8b`

**2. [Rule 3 - scope boundary] Logged, did not fix, two more stale CLAUDE.md Domain Conventions bullets**
- **Found during:** Task 2, while reading the full Domain Conventions section to scope the fish-state-vector fix.
- **Issue:** "Direct triangulation: ... RANSAC triangulation ..." and "Cross-view identity: RANSAC centroid clustering" are both superseded per `PROJECT.md`'s Key Decisions table (confidence-weighted DLT since v3.1; Leiden clustering since v2.1).
- **Fix:** Not applied — the plan's `<action>` text explicitly scoped this task to the fish-state-vector bullet only ("Do not restructure CLAUDE.md or touch any other section of it"). Logged to `deferred-items.md` instead.
- **Files modified:** `.planning/phases/113-concepts-tutorial/deferred-items.md`
- **Committed in:** `1be04ba`

---

**Total deviations:** 1 judgment-call content decision (stage order grounded in source over stale GUIDEBOOK), 1 scope-boundary log (not a fix).
**Impact on plan:** The stage-order decision is the substantive content of this plan and directly serves DOCS-04's transparency purpose; it does not satisfy the plan's literal "in order" phrasing for the must-have truth statement, which is called out explicitly above for reviewer visibility. No scope creep — CLAUDE.md edit stayed confined to the one line the plan specified.

## Issues Encountered

None beyond the documented decision above. The docs build, test suite, and all specified acceptance-criteria greps passed on the first attempt after authoring.

## Known Stubs

None. The page is fully authored, source-grounded content with no placeholder text.

## Threat Flags

None new. T-113-12 (tampering via output-schema description) is mitigated — every field name/shape/attribute in the "what comes out" section is taken directly from the verified `outputs.h5` schema in `113-CONTEXT.md`'s `<code_context>`, not from memory or the requirement text. T-113-13 (repudiation via requirement-text drift) is mitigated — the D-01 discrepancy is recorded in the published page itself, quoted verbatim above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `docs/getting-started/index.md` now has Installation and Concepts cards/toctree entries; Plan 07 adds the third (Tutorial) card and toctree entry, extending rather than re-copying the grid/toctree structure.
- Plan 07's tutorial page can cross-link into `concepts.md` (e.g., for the `outputs.h5` schema and the `spline_enabled` nuance) instead of re-deriving them.
- **Flag for a future maintenance pass (not this phase's scope):** GUIDEBOOK.md §6 itself remains uncorrected and will keep misleading anyone (including a future `discuss-phase` session, which CLAUDE.md's Agent-Specific Instructions direct to read it verbatim) who trusts it for the pipeline's current stage order. Logged in `deferred-items.md`.
- One pre-existing, unrelated test failure (`test_pseudo_label_cli.py`, logged by Plan 01) remains open and untouched.

## Self-Check: PASSED

- FOUND: docs/getting-started/concepts.md
- FOUND: docs/getting-started/index.md (modified, 2 grid-item-cards, 2 toctree entries)
- FOUND: CLAUDE.md (modified, 1 line changed)
- FOUND: .planning/phases/113-concepts-tutorial/deferred-items.md (modified)
- FOUND commit: 859ab8b
- FOUND commit: 28810ce
- FOUND commit: 1be04ba
- CONFIRMED: hatch run docs:build exit 0; docs/_build/html/getting-started/concepts.html exists
- CONFIRMED: hatch run test -> 1378 passed, 1 pre-existing failure, 3 skipped

---
*Phase: 113-concepts-tutorial*
*Completed: 2026-09-02*
