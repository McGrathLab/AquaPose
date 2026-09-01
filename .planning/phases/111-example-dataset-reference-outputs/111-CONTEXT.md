# Phase 111: Example Dataset & Reference Outputs - Context

**Gathered:** 2026-09-01
**Status:** Ready for planning

> **Mode:** `--auto` — gray areas were auto-selected and each resolved to its
> recommended option. Decisions below are the recommended defaults; the executor
> may adjust within the "Claude's Discretion" bounds. See the `[auto]` log at the
> bottom for the selection trail.

<domain>
## Phase Boundary

Produce and deposit the **Zenodo tutorial dataset** for the YH project so an
outside researcher can download a citable, correctly licensed clip with
**verifiable reference outputs**. Delivers DATA-01, DATA-02, DATA-03.

Three concrete deliverables:
1. **A reproducible packaging script** that temporally trims + re-encodes all 12
   camera videos (no spatial downscale), assembles the deposit tree, and emits
   checksums.
2. **Regenerated reference outputs** (`outputs.h5`, 3D animation, overlay mosaic,
   timing) produced on `dev` with the current production models, from the
   **deposited** clip so the tutorial is verifiable against what the code emits.
3. **A single Zenodo deposit with a DOI** — videos + calibration under CC-BY-4.0,
   bundled model weights labeled separately as AGPL-derived artifacts.

**In scope:** the packaging/re-encode script, deposit tree assembly + checksums,
reference-output regeneration, the platform-neutral deposit `config.yaml`, the
deposit `README.md`, and Zenodo metadata prep.

**Explicitly NOT this phase (scope fence):**
- README refresh, badge row, hero media, DOI/license badges → **Phase 114**
- CLI command reference and 71-field config reference → **Phase 112**
- Concepts page, install guide, and the end-to-end tutorial that *consumes* this
  deposit → **Phase 113**
- Relicensing the code MIT→AGPL-3.0 → already shipped in **Phase 108**
- Any calibration-algorithm or LUT-refactor work (see Reviewed Todos)
</domain>

<decisions>
## Implementation Decisions

### Source assets & models to bundle
- **D-01:** Source clip is the YH `videos/core_videos/` set — 12 camera streams
  `e3v8*-20260218T145915-150429.mp4` (~5-min, 7.46 GiB), staged locally at
  `D:\AquaPose_Zenodo_staging\YH\` (rclone remote `cichlidVideo:`). Treat the
  `zenodo-package-components` memory as ground truth for source layout.
- **D-02:** Bundle the **canonical YH production models** the live YH `config.yaml`
  points to: OBB `training/obb/run_20260318_082016/best_model.pt` and pose
  `training/pose/run_20260318_013005/best_model.pt`. Copy them into the deposit
  renamed to friendly names (`models/yolo_obb.pt`, `models/yolo_pose.pt`).
  **No segmentation model** — YH runs `midline.backend: pose_estimation` only.
  ⚠ Do **not** grab the `run_20260310_*` models cited as "production" in
  PROJECT.md — those are the benchmark-clip models; the YH deposit uses the
  `run_20260318_*` runs. Confirm against the deposit config before copying.
- **D-03:** Ship `geometry/calibration.json` only (~1.5 MB). **Do not ship the
  refractive LUTs** (~597 MiB) — they auto-generate on first pipeline run (existing
  "auto-generate LUTs on first run" decision). Keeps the deposit small.

### Trim & re-encode
- **D-04:** **30-second temporal trim** per camera (~900 frames @ 30 fps) — lands
  the deposit around ~150–200 MB (seed Work Item 3) with headroom over the
  tutorial run. Start offset: a representative segment where most/all 9 fish are
  visible and dispersed (see Discretion).
- **D-05:** Re-encode with **ffmpeg H.264 (libx264), CRF 23, preset slow,
  yuv420p, 1600×1200 @ 30 fps, audio stripped** — ~4–5× reduction, near-lossless
  for detection. **HARD CONSTRAINT: never spatially downscale** — calibration
  intrinsics and refractive projection are bound to 1600×1200. Temporal trim +
  bitrate reduction only.

### Deposit tree & config
- **D-06:** Deposit layout:
  ```
  aquapose-tutorial-data/
  ├── videos/                     # 12 × 30s trimmed, re-encoded
  ├── geometry/calibration.json   # LUTs omitted (auto-generated)
  ├── models/{yolo_obb.pt, yolo_pose.pt}
  ├── config.yaml                 # NEW, platform-neutral, relative paths
  ├── reference_outputs/{outputs.h5, animation_3d.html, overlay_mosaic.mp4, timing.txt}
  ├── README.md                   # provenance, rig, citation, license breakdown
  └── checksums.sha256            # SHA-256 of every deposit file
  ```
- **D-07:** Author a **fresh deposit `config.yaml`** with **relative, platform-neutral
  paths** (`video_dir: videos`, `calibration_path: geometry/calibration.json`,
  `detection.weights_path: models/yolo_obb.pt`, `midline.weights_path:
  models/yolo_pose.pt`). Do **not** ship the live YH config — it has absolute
  `/home/tlancaster6/...` paths. Preserve YH's tuned values (`n_animals: 9`,
  `chunk_size: 300`, backends, thresholds).

### Reference outputs
- **D-08:** Regenerate `outputs.h5`, a **3D animation**, an **overlay mosaic MP4**,
  and **timing** by running the pipeline (`aquapose run`, diagnostic mode) on the
  **deposited trimmed clip + deposited config** on `dev` with the D-02 models,
  then `aquapose viz` for the animation and overlay. Generating from the deposited
  tree (not the full 5-min clip) is what makes the tutorial reproducible.

### Packaging script & checksums
- **D-09:** A **single standalone reproducible script** at
  `scripts/package_tutorial_dataset.py` (a publication tool — **not** a shipped
  `aquapose` CLI subcommand). It orchestrates: ffmpeg trim+re-encode of the 12
  cameras → assemble the tree → copy models/calibration → write the deposit
  `config.yaml` and `README.md` → (optionally, `--regenerate-outputs`) run the
  pipeline + viz for reference outputs → emit `checksums.sha256`.
- **D-10:** Checksums as a `checksums.sha256` manifest, one `sha256␠␠relpath` line
  per deposit file (verifiable with `sha256sum -c`).

### Zenodo deposit
- **D-11:** **Single deposit, one DOI**, containing data + models + config +
  reference outputs + README. **Upload is manual via the Zenodo web UI**
  (human-in-the-loop for the external publish — no automated upload). The script
  produces the ready-to-upload tree plus a `zenodo-metadata.json`
  (title, creators, description, keywords, license).
- **D-12:** **Licensing:** deposit-wide **CC-BY-4.0** for videos + calibration;
  the `README.md` explicitly labels bundled model weights as
  **"AGPL-3.0-derived artifacts (trained with Ultralytics, AGPL-3.0)"**. Per the
  2026-08-12 PROJECT decision.

### Claude's Discretion
- Exact 30 s trim **start offset** — pick a representative segment (inspect one
  camera); default to a fixed, documented offset.
- 3D animation format — interactive **HTML** (~5.7 MB) vs **MP4**, or both;
  default HTML for interactivity plus the small overlay MP4.
- Exact CRF within **20–24** if 23 yields a too-large/too-small deposit.
- Script filename, flag surface, and `zenodo-metadata.json` schema.

### Reviewed Todos (not folded)
See Deferred Ideas — 5 lexically-matched todos were reviewed and **not folded**
(all out of scope for dataset packaging).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase requirements & scope
- `.planning/ROADMAP.md` — Phase 111 section: goal + 3 success criteria.
- `.planning/REQUIREMENTS.md` — DATA-01 (reproducible packaging script, no spatial
  downscale), DATA-02 (reference outputs regenerated on `dev`), DATA-03 (Zenodo
  DOI, CC-BY-4.0 data, AGPL-labeled weights).

### Dataset design & licensing (authoritative)
- `.planning/seed-publication-polish.md` — **Work Item 3** (source sizes, the
  ~150–200 MB target, CRF ~23 guidance, the deposit tree, the hard no-spatial-
  downscale constraint) and **Work Item 5** (data license = CC-BY-4.0; model
  weights labeled separately as AGPL-derived).
- `.planning/PROJECT.md` — Key Decisions rows dated 2026-08-12 (CC-BY-4.0 for the
  data deposit; temporal trim + bitrate only, never spatial downscale; AGPL-3.0
  relicense) and the **Rig Geometry** + **Subjects** sections for README provenance.

### Source assets (ground truth for the executor)
- Memory `zenodo-package-components` (Claude memory, not in-repo) — the
  authoritative source path (`cichlidVideo:.../AquaPose/projects/YH`), staging dir
  `D:\AquaPose_Zenodo_staging\YH\`, canonical model runs, "YH has no seg model,"
  and the cruft-exclusion list. Treat its facts as ground truth for source assets.
- `D:\AquaPose_Zenodo_staging\YH\config.yaml` — live YH config: model run paths,
  `n_animals: 9`, `chunk_size: 300`, backends, tuned thresholds. The deposit
  `config.yaml` derives from this but with relative paths (D-07).

### Reference-output generation
- `src/aquapose/cli.py` — `aquapose run` (diagnostic mode → per-chunk cache) and
  `aquapose viz` (animation / overlay / trails; MP4 export shells out to ffmpeg).
- `src/aquapose/evaluation/viz/animation.py`, `.../viz/overlay.py` — the 3D
  animation and overlay-mosaic generators.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `aquapose viz` (animation.py / overlay.py): produces the 3D animation and
  overlay mosaic from a diagnostic run's per-chunk pickle cache — the mechanism
  for `reference_outputs/`. ffmpeg is already a runtime dependency (animation.py
  shells out to it), so the packaging script can reuse ffmpeg for trim/re-encode.
- `scripts/` (detect_swaps.py) and `tools/` (import_boundary_checker.py,
  smoke_test.py): established homes for standalone, non-shipped tooling — the
  packaging script joins `scripts/`.

### Established Patterns
- Diagnostic mode + per-chunk pickle cache (`chunk_NNN/cache.pkl` + `manifest.json`)
  is the input to `aquapose viz`; `outputs.h5` is the HDF5 pipeline output.
- Platform-neutral relative-path config was established in Phase 109 (tutorial
  config) — the deposit `config.yaml` follows that pattern.
- LUTs auto-generate on first pipeline run — no need to ship `geometry/luts/`.

### Integration Points
- The deposit `config.yaml` is consumed by `aquapose run --config` (or `--project`)
  pointing at the deposit tree itself; reference outputs are produced by running
  the pipeline against the deposited clip so a tutorial user reproduces them.

</code_context>

<specifics>
## Specific Ideas

- Deposit target size ~**150–200 MB** (seed Work Item 3).
- Source: 12 × `e3v8*-20260218T145915-150429.mp4` under `videos/core_videos/`
  (~5-min clips, 7.46 GiB total); staged `D:\AquaPose_Zenodo_staging\YH\`.
- Canonical models: OBB `run_20260318_082016/best_model.pt`, pose
  `run_20260318_013005/best_model.pt`.
- License wording — data: **CC-BY-4.0**; weights: **"AGPL-3.0-derived artifacts
  (trained with Ultralytics, AGPL-3.0)."**
- Hard constraint (also belongs in the deposit README for users re-encoding their
  own footage): **never spatially downscale.**

</specifics>

<deferred>
## Deferred Ideas

- README refresh, badge row, hero media, DOI/license badges — **Phase 114**.
- CLI command reference + 71-field config reference — **Phase 112**.
- Concepts page, install guide, and the end-to-end tutorial that consumes this
  deposit — **Phase 113**.
- Moving tier-two utilities behind a `pip install aquapose[research]` extra —
  future **PKG-01**, not this milestone.

### Reviewed Todos (not folded)
All lexical (keyword) matches on "calibration / data / camera" — none concern
dataset packaging; deferred as out of scope:
- **Active calibration refinement** (score 0.9) — calibration-algorithm work.
- **Integrate full-frame exclusion masks from AquaMVS** (0.7) — calibration/masking.
- **Move LUT generation to pre-pipeline setup** (0.5) — thematically adjacent
  (we chose to auto-generate rather than ship LUTs, D-03), but the refactor itself
  is a separate change.
- **Regenerate golden regression test data for v2.1** (0.4) — test fixtures.
- **Fix core import boundary violation in frame_source** (0.4) — core refactor.

</deferred>

---

*Phase: 111-example-dataset-reference-outputs*
*Context gathered: 2026-09-01*

<!--
[auto] Selected all gray areas: Source assets & models, Trim & re-encode,
       Deposit tree & config, Reference outputs, Packaging script & checksums,
       Zenodo deposit & licensing.
[auto] Source/models — Q: "Which models + geometry to bundle?" → Selected:
       "Canonical YH config runs (run_20260318_*), calibration.json only, no LUTs,
       no seg model" (recommended; grounded in live YH config.yaml + memory).
[auto] Trim & re-encode — Q: "Trim length + codec?" → Selected: "30s trim,
       H.264 CRF 23, no spatial downscale" (recommended; seed Work Item 3).
[auto] Deposit tree/config — Q: "Ship YH config or author fresh?" → Selected:
       "Fresh platform-neutral relative-path config.yaml" (recommended;
       live YH config has absolute paths).
[auto] Reference outputs — Q: "Generate from full clip or deposited clip?" →
       Selected: "From the deposited trimmed clip for reproducibility"
       (recommended; DATA-02 verifiability).
[auto] Packaging — Q: "Standalone script or shipped CLI subcommand?" → Selected:
       "Standalone scripts/package_tutorial_dataset.py + SHA-256 manifest"
       (recommended; publication tooling, not runtime).
[auto] Zenodo — Q: "Single or multi deposit; auto or manual upload?" → Selected:
       "Single deposit/one DOI, manual UI upload, CC-BY-4.0 data + AGPL-labeled
       weights" (recommended; human-in-the-loop for external publish).
[auto] Todos — reviewed 5 matches (score ≥ 0.4); none folded (lexical
       false-positives, out of scope). Logged in Deferred Ideas.
-->
