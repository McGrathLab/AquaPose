# Requirements: AquaPose

**Defined:** 2026-08-12
**Core Value:** Accurate 3D fish midline reconstruction from multi-view silhouettes via refractive multi-view triangulation

## v4.0 Requirements

Requirements for the publication milestone. Each maps to exactly one roadmap phase.

Prior milestone requirements archived to `.planning/milestones/v3.11-REQUIREMENTS.md`.

**Milestone goal:** An outside researcher can find AquaPose, understand what it does, install it, run it end-to-end on real data, and cite it — under a correct license, with green CI and live documentation.

### Foundation

Prerequisites. These gate doc authoring and the badge row.

- [x] **FOUND-01**: The Sphinx repair from `a66287a` is forward-ported onto `dev` — `conf.py` mock imports, detached docs env, `napoleon_use_ivar`, and `.rst` files matching the actual module tree — so `sphinx-build -W --keep-going` exits clean
- [x] **FOUND-02**: Documentation CI runs on pushes to `dev`, so docs breakage is caught at push rather than at release
- [x] **FOUND-03**: `dev` and `main` are reconciled with `main` as a release-only branch, and the `1.1.0-dev.7` vs `1.1.1` version conflict is resolved
- [x] **FOUND-04**: The repository contains no stray artifacts — the vendored SAM2 clone, `11.0` pip log, top-level `yolo26n*.pt` weights, `runs/`, `tmp/`, and the dead `reconstruction/`, `segmentation/`, `tracking/` directories are gone and `.gitignore` prevents their return
- [x] **FOUND-05**: AquaPose is licensed AGPL-3.0 consistently across `LICENSE`, `pyproject.toml` (license field and OSI classifier), README, docs, and the citation block

### Correctness

- [x] **QA-01**: `test_luts.py::test_forward_lut_cast_ray_matches_model` passes — the tier-one calibration failure is resolved, not skipped
- [x] **QA-02**: The 7 tier-two failures in `training/` and `evaluation/` pass, so the full suite is green and the coverage badge is honest
- [x] **QA-03**: Model weights-path config fields resolve consistently — `keypoint_weights_path` and `detection.model_path` use one convention relative to `project_dir`
- [x] **QA-04**: The tutorial config uses relative, platform-neutral paths and runs unmodified on Linux, macOS, and Windows

### Documentation

- [x] **DOCS-01**: Documentation distinguishes the tier-one production pipeline (detection → tracking → association → pose → reconstruction, plus calibration and engine) from tier-two research utilities (`training/`, `evaluation/`, `core/reid/`, pseudo-labeling), with honest status labels on tier two
- [x] **DOCS-02**: Every public module appears in the rendered API reference — including `core/association/*`, `core/tracking/*`, `core/types/*`, all `backends/` packages, `cli.py`, `io/video.py`, and `visualization/`
- [ ] **DOCS-03**: A user can install AquaPose from written instructions, including the GPU/CUDA caveat, without reading source
- [ ] **DOCS-04**: A concepts page explains refractive projection, the `{p, ψ, κ, s}` state vector, and the five pipeline stages well enough that a reader understands what the pipeline computes before running it
- [x] **DOCS-05**: Every CLI command group is documented with purpose, arguments, and a worked example
- [x] **DOCS-06**: Every config field across the 9 dataclasses is documented with type, default, and effect, tiered so a tutorial user is not confronted with all 71 at once
- [ ] **DOCS-07**: A tutorial walks a new user from install through a complete pipeline run on the published dataset to interpreting the 3D output, with expected results at each step
- [ ] **DOCS-08**: Documentation builds green on Read the Docs from `dev` and is reachable at the URL declared in `pyproject.toml`

### Example Dataset

- [ ] **DATA-01**: A reproducible script packages the tutorial deposit — temporal trim and re-encode across 12 cameras, assemble the tree, emit checksums — with no spatial downscaling
- [ ] **DATA-02**: Reference outputs (`outputs.h5`, animation, overlay mosaic, timing) are regenerated on `dev` with current production models, so the tutorial is verifiable against what the code actually produces
- [ ] **DATA-03**: The dataset is deposited on Zenodo with a citable DOI, videos and calibration under CC-BY-4.0, and bundled model weights labeled separately as AGPL-derived artifacts

### README

- [ ] **README-01**: The README opens with what problem AquaPose solves, what a user gets out (3D midlines and kinematics), and who it is for — legible to a researcher who has never heard of it
- [ ] **README-02**: A badge row shows tests, docs, coverage, supported Python versions, PyPI version, license, and the Zenodo DOI — added only once CI is green
- [ ] **README-03**: Hero media shows a 3D reconstruction rendering inline on GitHub
- [ ] **README-04**: Install, quick start against the Zenodo dataset, docs link, and a citation block with the DOI are all present and correct

### Project Record

- [x] **REC-01**: MILESTONES.md contains the missing v3.11 Appearance-Based ReID entry, reconstructed from ROADMAP.md and `phases/102-107/`

## Open Decisions

Resolve during phase planning. Neither changes phase structure.

| Decision | Default | Notes |
|----------|---------|-------|
| Zenodo deposit granularity | One deposit containing data + models + reference outputs | Separate DOIs give finer citation but triple the deposit maintenance |
| Hero media format | Both — inline GIF/MP4 loop plus a linked YouTube thumbnail | GitHub strips `<iframe>`; uploaded `.mp4` renders inline if small |

## Future Requirements

Deferred to a future release. Tracked but not in this roadmap.

### Packaging

- **PKG-01**: Tier-two utilities move behind a `pip install aquapose[research]` extra
- **PKG-02**: AGPL header comments in individual source files (repo-level `LICENSE` is sufficient today; headers help when files are copied)

### Data Quality

- **QUAL-01**: Cross-camera positive pair enforcement (>= 50% cross-camera pairs in training batches)
- **QUAL-02**: HDF5 embedding storage with camera_id and detection confidence metadata
- **QUAL-03**: Reprojection error regression check on repaired segments

### Production

- **PROD-01**: Embed runner resume support (skip already-computed embeddings)
- **PROD-02**: Confidence-gated prototype update (gate on OBB confidence + camera count)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Import-boundary enforcement between core and research code | Considered and rejected — would enforce a separation the project does not want; tiering is a docs and QA-effort decision only |
| Ultralytics Enterprise License | Costs money and does not address the GPL Leiden dependencies; AGPL relicense is the chosen resolution |
| Replacing Ultralytics to preserve MIT | Not realistic at this stage — it is the detection and pose pipeline |
| Spatially downscaling tutorial videos | Calibration intrinsics and refractive projection are bound to 1600×1200; downscaling silently invalidates ray casting |
| Publishing the full 7.5 GB source recording | A 30s trim across 12 cameras is sufficient for the tutorial and a normal Zenodo deposit size |
| Rewriting docstrings | Coverage is already 99.7% Google-style; this milestone adds narrative and reference structure around them |
| New pipeline capability | This is a publication milestone — behavior changes are limited to bug fixes and config-path consolidation |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | 108 | Complete |
| FOUND-02 | 108 | Complete |
| FOUND-03 | 108 | Complete |
| FOUND-04 | 108 | Complete |
| FOUND-05 | 108 | Complete |
| QA-01 | 109 | Complete |
| QA-02 | 109 | Complete |
| QA-03 | 109 | In progress (Plan 01 done) |
| QA-04 | 109 | Complete |
| DOCS-01 | 110 | Complete |
| DOCS-02 | 110 | Complete |
| DOCS-03 | 113 | Pending |
| DOCS-04 | 113 | Pending |
| DOCS-05 | 112 | Complete |
| DOCS-06 | 112 | Complete |
| DOCS-07 | 113 | Pending |
| DOCS-08 | 114 | Pending |
| DATA-01 | 111 | Pending |
| DATA-02 | 111 | Pending |
| DATA-03 | 111 | Pending |
| README-01 | 114 | Pending |
| README-02 | 114 | Pending |
| README-03 | 114 | Pending |
| README-04 | 114 | Pending |
| REC-01 | 108 | Complete |

**Coverage:**

- v4.0 requirements: 25 total
- Mapped to phases: 25 (Phases 108-114)
- Unmapped: 0

---
*Requirements defined: 2026-08-12*
*Last updated: 2026-08-12 — ROADMAP.md created, all 25 requirements mapped to Phases 108-114*
