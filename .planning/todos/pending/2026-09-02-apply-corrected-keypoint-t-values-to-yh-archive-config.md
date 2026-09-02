---
created: 2026-09-02T21:21:23.000Z
title: Apply corrected keypoint_t_values to the production YH archive config
area: training
files:
  - cichlidVideo:.../__AnalysisStates/AquaPose/projects/YH/config.yaml
---

## Problem

The production YH project config that determines every future YH pipeline run
and pseudo-label round carries a biased `keypoint_t_values` vector, computed
before `113.1-01` fixed the two `calibrate-keypoints` defects (legacy
`midline:` write key, normalized- instead of pixel-space arc length):

**Archive path (as recorded in the originating todo, verbatim, including its
own `...` elision — see Reachability below):**
```
cichlidVideo:.../__AnalysisStates/AquaPose/projects/YH/config.yaml
```

**Biased vector currently in that config** (under the legacy `midline:` key):
```
[0.0, 0.1653, 0.3411, 0.5241, 0.7368, 1.0]
```

**Corrected vector to write** (into `pose.keypoint_t_values`, removing any
`midline.keypoint_t_values` if still present):
```
[0.0, 0.149, 0.3269, 0.5187, 0.7403, 1.0]
```

Per-keypoint delta (corrected minus biased): nose +0.0000, head -0.0163,
spine1 -0.0142, spine2 -0.0054, spine3 +0.0035, tail +0.0000.

## How the corrected vector was measured

Phase `113.1`, plan `113.1-05`, 2026-09-02. `prep calibrate-keypoints` (fixed
by `113.1-01`) run once over a symlinked staging tree presenting the two
manual, non-augmented corpora directly on this machine:

- `/home/tlancaster/Downloads/pose/datasets/pose_ablation_a_manual/labels/train`
  — 258 label files, all with matching images.
- `/home/tlancaster/Downloads/pose/datasets/round1-curated/labels/val` — 64
  label files, all with matching images.

322 label files total, 644 symlinks (322 labels + 322 images), 325 keypoint
instances processed (a file can carry more than one annotated instance). See
`.planning/phases/113.1-pre-release-bug-fixes/113.1-05-SUMMARY.md` for the
full verbatim command output, the four-vector comparison table, and the two
deliberately excluded contaminated splits.

## Consequence of not applying this

Every YH pipeline run and every pseudo-label generation round continues to use
the biased arc-length parameterization until this config is edited. Confirmed
downstream consumers of `pose.keypoint_t_values`, verified against source:

- `core/reconstruction/stage.py` (`ReconstructionStage`, lines 179-183 and
  310) — wired from config via `engine/pipeline.py:344`. This is the live
  pipeline's 3D reconstruction stage: it genuinely consumes
  `keypoint_t_values` to parameterize 2D-keypoints-to-midline conversion
  before triangulation, for **any project whose config sets the value**. YH's
  config does; the arc-length bias therefore reaches YH's actual 3D
  reconstruction output, not just pseudo-labels or evaluation scores.
- `training/pseudo_labels.py` (`reproject_spline_keypoints`) and
  `training/pseudo_label_cli.py` — pseudo-label generation.
- `evaluation/tuning.py` and `evaluation/runner.py` — evaluation scoring.

**Correction from an earlier draft of this analysis:** the *pose backend*
(`core/pose/backends/pose_estimation.py:59`,
`PoseEstimationBackend.__init__`) does accept a `keypoint_t_values`
constructor parameter that it never references again — that one component
genuinely ignores it, confirmed by a single-occurrence grep. But that does
NOT mean the value is inert for YH: `ReconstructionStage` is a different,
downstream pipeline stage that does consume it (see above), so the bias
reaches YH's live 3D pose output via reconstruction, not via the pose
backend.

## Reachability (checked 2026-09-02, plan 113.1-05)

The originating todo (`2026-09-02-calibrate-keypoints-yolo-path-measures-arc-length-in-normalized-space.md`)
itself recorded the archive path with a literal `...` elision — the exact
full path was never fully captured, even at discovery time.

Checked again during this plan:

1. `rclone listremotes` confirms a configured remote named `cichlidVideo:`.
2. `rclone lsf cichlidVideo:` succeeds and lists the remote's top-level
   contents (17 entries: `021026/`, `2025 Spring/`, `Code/`,
   `mbuna_singlenuc_project/`, `mvs/`, `output/`, `videos/`, `weights/`, etc.)
   — the remote itself is reachable.
3. `rclone lsf cichlidVideo:__AnalysisStates --dirs-only` fails:
   `ERROR: : error listing: directory not found`.
4. A full recursive listing, `rclone lsf cichlidVideo: -R --max-depth 8`,
   enumerated 11748 entries in ~2 min and exited 0. Grepping that listing for
   `YH`, `AnalysisState`, and `AquaPose` (case-insensitive) found no matching
   directory or file anywhere in the remote to that depth — the only `YH`
   hits are unrelated genetics files (`2025 Spring/Data/YHPedigree_Class.vcf`,
   `YH_MC_samples_Chr1.vcf`). The only `config.yaml` files present belong to
   an unrelated `mbuna_singlenuc_project` DeepLabCut project.

**Conclusion: the archive config is not reachable from this machine at the
path on record.** This is a blocked application, not an oversight — the
remote exists and is browsable, but the specific `__AnalysisStates/AquaPose/projects/YH/`
subtree could not be located. Whoever picks this up needs either the correct
full path (the `...` was never resolved) or direct access to wherever the
AquaPose YH project state actually lives, then should write the corrected
vector above into `pose.keypoint_t_values` and delete any legacy
`midline.keypoint_t_values`.

## Notes

Filed by Phase 113.1, Plan 05 (`113.1-05-PLAN.md`, D-11). Do not close this
todo by editing anywhere other than the actual production YH archive config —
recomputing the vector again elsewhere does not apply it.
