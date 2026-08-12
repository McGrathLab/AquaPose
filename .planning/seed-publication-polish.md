# Publication Polish Milestone Seed

## Problem

AquaPose's core pipeline works end-to-end and is well-documented at the docstring
level, but the project is not in a publishable state. Three gaps:

1. **Branch divergence.** `main` and `dev` have drifted far enough apart that
   continuing to release from `main` would make the eventual reconciliation
   expensive. Right now it is still nearly free.
2. **No narrative documentation.** The docs are four authored pages and seven
   `automodule` stubs. Half the source tree never appears in the rendered docs,
   and there is no install guide, tutorial, concepts page, CLI reference, or
   config reference.
3. **Publication mechanics unaddressed.** No example dataset, no README that
   introduces the library, no badges, and an unreviewed license that conflicts
   with the dependency stack.

## Goal

Get AquaPose to a state where an outside researcher can find it, understand what
it does, install it, run it end-to-end on real data, and cite it — with a
correct license and green CI.

---

## Findings: Current State (audited 2026-08-12)

### Branch strategy

`origin/dev` is **1494 commits ahead** of `main`; `main` is 4 commits ahead of
`dev`. Local `dev` is stale (frozen 2026-03-02) — all comparisons below are
against `origin/dev`.

| | `main` | `origin/dev` |
|---|---|---|
| Tip | 2026-08-12 (`chore(release): 1.1.1`) | 2026-08-12 |
| Version | `1.1.1` | `1.1.0-dev.7` (behind) |
| `src/` delta | — | +17,305 / −6,495 lines |
| Tests | 1,045 — **25 failing** | 1,295 — **4–6 failing** |
| Docs | builds clean under `-W` | **broken**, never CI-tested |

`dev` has carried the project through phases ~70–107: ReID embeddings, swap
detection, hard-example mining, streaming eval, LabelStudio integration,
retuned training defaults. It also renamed `core/midline` → `core/pose` and
added `core/reid`.

**Decision: develop on `dev`; `main` becomes a release-only branch.**
`semantic_release` is already configured for this (`dev` is registered as a
prerelease branch with `prerelease_token = "dev"`).

Two premises that needed correcting during the audit:

- **It is not currently a fast-forward.** `origin/dev..main` is 4 commits, and
  one is unique work: **`a66287a` "fix(docs): repair Sphinx build and gate it on
  push."** It rewrote `docs/conf.py` (+61 lines — mock imports, detached env,
  `napoleon_use_ivar`), replaced dead `mesh`/`optimization`/`segmentation`/
  `utils` `.rst` files with `engine`/`evaluation`/`synthetic`/`training`, added
  `docs.yml` push gating, and fixed 4 source docstrings needed for `-W` to pass.
  `19ea21e` (the v3.5 squash) is substantively redundant — `tools/` is
  byte-identical across branches, so that work is already in `dev` granularly.
- **`dev`'s docs are actively broken.** Its `.rst` files `automodule` on
  `aquapose.mesh`, `aquapose.optimization`, `aquapose.segmentation`, and
  `aquapose.utils`, none of which exist in `dev`'s tree. Under `-W` that is a
  hard failure. The Documentation workflow has **never run on a `dev` push** —
  the `branches: [main, dev]` gating only exists in `a66287a`.

So the first task on `dev` is forward-porting `a66287a`, not writing docs.

### What is already solid

- **Docstring coverage: 99.7%** (382/383 public defs and classes), Google style,
  Napoleon configured. The expensive part of doc work is done.
- Docs build passes `-W --keep-going`; `.readthedocs.yaml` configured; detached
  docs env avoids the CUDA-torch size blowup on RTD.
- Packaging scaffolding complete: semantic-release, CHANGELOG, pre-commit, ruff,
  basedpyright, MIT license file, code of conduct.
- CI matrix: 3 Python versions × Linux/Windows, plus typecheck and docs jobs.

### Known defects

- **`loguru` imported but undeclared** in `main`'s `pyproject.toml` — 25 CI
  failures and a failed PyPI publish. **`dev` is unaffected** (`logging.py` was
  deleted). Basing on `dev` makes this disappear rather than needing a fix.
- **`dev`: 8 distinct failing tests.** One is tier-one core
  (`test_luts.py::test_forward_lut_cast_ray_matches_model`); the rest are stale
  CLI-help assertions and fixtures in `training/` and `evaluation/`.
- **Repo root is dirty**: untracked `11.0` (a stray pip log from `boxmot>=11.0`),
  an untracked `~/` directory containing a **full SAM2 clone**, plus four
  `yolo26n*.pt` weights and `runs/`, `tmp/` at top level.
- **Tutorial config uses absolute Windows paths**, and `keypoint_weights_path` is
  absolute while `detection.model_path` is relative to `project_dir`. There is
  already a captured todo on `dev` to consolidate these fields; promote it.

### Docs coverage gap

Prose today is **~110 lines across four pages**. Two concrete deficits:

**API reference is half-empty.** `automodule:: aquapose.core` only documents what
`core/__init__.py` re-exports. Diffing built module pages against source:
**52 of 105 modules never appear in the docs.** The missing set is precisely the
interesting core — all of `core/association/*`, all of `core/tracking/*`, all of
`core/types/*` (`Detection`, `Midline2D`, `Midline3D`, `CropRegion` — the data
contracts a user needs first), all three `backends/` packages, `cli.py`,
`io/video.py`, and the entire `visualization/` package (which has no `.rst` at
all). Module paths shift on `dev` (`core/midline` → `core/pose`, plus
`core/reid`), so recompute after the forward-port.

**Zero narrative documentation.** No install guide, no tutorial, no concepts page
(refractive projection, the `{p, ψ, κ, s}` state vector, the five stages), no CLI
reference for the 6 commands, and no config reference for **71 fields across 9
dataclasses**. A user running `aquapose init-config` gets a YAML file with 71
knobs and nothing explaining any of them.

---

## Work Item 1: Core vs. research documentation tiering

**This is a docs information-architecture and QA-effort decision, not an
architectural firewall.** Everything ships in one package; core is allowed to
depend on shared utilities. An import-boundary rule was considered and
**rejected** — it would enforce a separation the project does not want.

- **Tier one — core production pipeline.** Detection → tracking → association →
  pose/midline → reconstruction, plus calibration and engine. Gets the tutorial
  path, narrative concepts docs, the full config reference, and an airtight
  testing bar (e2e coverage, golden regression, zero known failures).
- **Tier two — research and beta utilities.** `training/`, `evaluation/`,
  `core/reid/`, dataset and pseudo-labeling tooling. Ships with the library and
  gets complete API reference plus a short "what this is for / how to invoke it"
  page each, with honest status labeling. Bar is "works as documented," not
  airtight. Excluded from the end-to-end tutorial.

`docs/api/index.rst` currently lists `training` and `evaluation` as peers of
`core` — that flattening is what this tiering undoes.

Consequence for the failing tests: the 7 tier-two failures are low-priority
cleanup; the calibration LUT failure is a tier-one blocker.

## Work Item 2: README badges

Repo is **public** with MIT declared on GitHub. Codecov is already wired
(`codecov/codecov-action@v5` with `secrets.CODECOV_TOKEN` in `test.yml`), so a
coverage badge needs no new setup.

Badges to add:

- Tests (GitHub Actions `test.yml` status)
- Docs (GitHub Actions `docs.yml` status, or Read the Docs once deployed)
- Coverage (Codecov)
- Python versions supported (3.11–3.13)
- PyPI version
- License — **wait for Work Item 5 before choosing this badge**
- Zenodo DOI (from Work Item 3)

Blocked on green CI; a red badge is worse than no badge.

## Work Item 3: Zenodo example dataset

**Source assets:** 12 cameras × 667 MB = **7.5 GB** total. 1600×1200, 30 fps,
h264 @ **17 Mbps**, 315 s each. Models are trivial (18 MB for all three);
calibration is 1.5 MB.

7.5 GB is too large to hand a tutorial reader, but two things make this cheap:

1. **17 Mbps is near-lossless at this resolution** — re-encoding at CRF ~23
   without touching resolution should give 4–5× reduction with no meaningful
   impact on detection quality.
2. **The config already truncates** (`stop_frame: 100`) — the tutorial run is
   3.3 seconds, not 5 minutes.

A **30-second trim across 12 cameras, re-encoded, lands around 150–200 MB** — a
normal Zenodo deposit, and Zenodo issues a DOI, which is wanted for the
publication anyway.

> **Hard constraint: do not spatially downscale.** Calibration intrinsics and the
> refractive projection are tied to 1600×1200; halving resolution silently
> invalidates every ray cast unless the calibration is rescaled to match.
> Temporal trimming and bitrate reduction are both safe. This belongs in the docs
> as a note too — users will try it on their own footage.

**Deposit contents:**

```
aquapose-tutorial-data/
├── videos/           # 12 × 30s trimmed, re-encoded (~150-200 MB)
├── geometry/
│   └── calibration.json          # 1.5 MB
├── models/
│   ├── yolo_obb.pt   yolo_pose.pt   yolo_seg.pt    # 18 MB total
├── config.yaml       # relative paths, platform-neutral
├── reference_outputs/
│   ├── outputs.h5              # ~50 KB
│   ├── animation_3d.html       # ~5.7 MB
│   ├── overlay_mosaic.mp4      # ~19 MB
│   └── timing.txt
└── README.md         # provenance, rig description, citation, license
```

Reference outputs are cheap (~25 MB) and make the tutorial verifiable. **They
must be regenerated on `dev`** — the existing runs in `runs/` are from March on
the `main`-era codebase.

Packaging is scriptable (ffmpeg trim + re-encode, assemble tree, checksum);
upload is manual via the Zenodo UI.

## Work Item 4: README refresh

Current README is 65 lines, opens with a dense one-paragraph description, and has
the docs link commented out pending deployment.

Needs:

- **Hero media.** An embedded YouTube video is *not* directly playable in GitHub
  README markdown — GitHub strips `<iframe>`. The standard workaround is a
  thumbnail image linked to the video, which renders as a clickable poster
  frame. Alternative: commit a short looping GIF or MP4 of the 3D reconstruction
  overlay. **Recommendation: do both** — an autoplaying GIF/MP4 as the hero, with
  a linked thumbnail to the full YouTube video below it. GitHub does render
  uploaded `.mp4` inline when attached via the web UI, which is the better-looking
  option if the file is small.
- Brief but descriptive intro — what problem it solves, what a user gets out
  (3D midlines + kinematics), who it is for.
- Badge row (Work Item 2).
- Install section, including the GPU/CUDA caveat already documented.
- Quick start pointing at the Zenodo dataset.
- Link to full docs (uncomment once RTD is live).
- Citation block with the Zenodo DOI.

## Work Item 5: Relicense to AGPL-3.0 — **DECIDED 2026-08-12**

**Decision: relicense AquaPose from MIT to AGPL-3.0**, matching the strongest
copyleft dependency in the stack. Chosen deliberately as the conservative option
— the alternatives all leave residual risk or cost, and permissive downstream
reuse is not a project goal. Rationale and the rejected alternatives are recorded
below.

The project ships **MIT**, but the dependency stack contains copyleft licenses.
Audited from installed metadata:

| Dependency | License | Used by |
|---|---|---|
| **ultralytics** | **AGPL-3.0** | `core/detection/backends/yolo.py`, `yolo_obb.py`, `core/pose/backends/pose_estimation.py`, `training/` |
| **leidenalg** | **GPL-3.0-or-later** | `core/association/clustering.py` |
| **igraph** | **GPL-2.0+** | `core/association/clustering.py` |
| boxmot | AGPL-3.0 | **dropped on `dev`** (replaced by in-house `keypoint_tracker.py`) |
| torch, torchvision, h5py, click, numpy, scipy, scikit-image, pycocotools | BSD variants | — |
| opencv-python | Apache-2.0 | — |
| plotly, aquacal, loguru | MIT | — |

**The issue.** Licensing your own original code MIT is always permissible. But
AquaPose's core pipeline cannot function without Ultralytics — every detection
and pose backend imports it — and Ultralytics is AGPL-3.0, which is strongly
copyleft with a network-use clause. Advertising the package as "MIT" while its
core functionality requires AGPL code is misleading to downstream users, who may
reasonably believe they can use it in closed-source or hosted contexts. Ultralytics
sells a commercial license specifically to relieve this obligation. The Leiden
clustering deps add GPL on top, though those are confined to one module.

**Options considered:**

1. **Relicense as AGPL-3.0.** ✅ **SELECTED.** Simplest and most honest; matches
   the strongest dependency; common for academic CV code. Accepted cost:
   downstream adoption friction for industry users.
2. **Keep MIT, isolate copyleft behind optional extras.** ❌ Not realistic for
   Ultralytics — it *is* the pipeline. Would have been feasible for
   `igraph`/`leidenalg` alone, which touch one module.
3. **Obtain an Ultralytics Enterprise License.** ❌ Costs money and does not
   address the GPL Leiden deps.
4. **Replace Ultralytics.** ❌ Not realistic at this stage.

### Relicensing checklist

The license must be consistent everywhere it is asserted, or the ambiguity is
nearly as bad as the original conflict:

- [ ] `LICENSE` — replace MIT text with the full AGPL-3.0 text
- [ ] `pyproject.toml` — `license = {text = "AGPL-3.0-or-later"}` and swap the
      `License :: OSI Approved :: MIT License` classifier for the AGPLv3+ one
- [ ] README badge (Work Item 2) and any license mention in the intro
- [ ] `docs/` — license statement and Sphinx footer
- [ ] GitHub repo license detection (updates automatically from `LICENSE`)
- [ ] Citation block — license line, if present
- [ ] Consider a short AGPL header comment in source files (optional; the
      repo-level `LICENSE` is sufficient, but headers help when files are copied)

**Note: the Zenodo *data* deposit takes a separate license from the code.**
AGPL-3.0 is a software license and is a poor fit for video and calibration data.
Use a data-appropriate license for the deposit — **CC-BY-4.0** is the
conventional choice for research datasets and keeps attribution requirements
without imposing copyleft on derived analyses. The bundled model weights are the
ambiguous case: they are trained artifacts derived from an AGPL-3.0 toolchain, so
label them explicitly rather than leaving them to inherit the deposit-wide
license.

*Not legal advice — worth confirming with the institution's tech-transfer or
licensing office given this is headed for publication, particularly the model-
weights question.*

---

## Sequence and Estimate

| # | Work | Size |
|---|---|---|
| 1 | Forward-port `a66287a` docs repair onto `dev`; confirm green docs build | ~1 day |
| 2 | Merge `dev`→`main`, make `main` release-only, reconcile `1.1.0-dev.7` vs `1.1.1` | ~0.5 day |
| 3 | Repo hygiene (`.gitignore`, remove SAM2 clone, stray weights, `11.0`) | ~0.5 day |
| 4 | **Relicense to AGPL-3.0** (Work Item 5) — gates 8 and 13 | ~0.5 day |
| 5 | Fix failing tests (1 tier-one calibration, 7 tier-two) | ~1 day |
| 6 | Consolidate weights-path config fields; platform-neutral tutorial config | ~0.5 day |
| 7 | Two-tier docs IA; expand API `.rst` to cover the missing modules | ~1.5 days |
| 8 | Package + deposit Zenodo dataset, regenerate reference outputs on `dev` | ~1 day |
| 9 | Config reference (71 fields, tiered) | ~2–3 days |
| 10 | CLI reference | ~1 day |
| 11 | Concepts page (refraction, state vector, five stages) | ~2–3 days |
| 12 | Install + e2e tutorial against the deposited data | ~2 days |
| 13 | README refresh + hero media + badges | ~1 day |

**Roughly 2.5 weeks of focused work.** High docstring coverage means most of this
is connective tissue rather than writing from cold. Items 1–4 are prerequisites
and should land before doc authoring starts in earnest.

## Resolved Decisions

- **Branch strategy** (2026-08-12) — develop on `dev`; `main` becomes
  release-only. See Findings.
- **License** (2026-08-12) — relicense to **AGPL-3.0**, chosen as the
  conservative option given the Ultralytics/Leiden copyleft stack. See Work
  Item 5.
- **Core/research separation** (2026-08-12) — docs tiering and QA-effort
  allocation only; no import-boundary enforcement. See Work Item 1.

## Open Decisions

1. **Zenodo data license** — CC-BY-4.0 recommended for the video/calibration
   deposit, with the model weights labeled separately. See Work Item 5.
2. **Read the Docs deployment** — `.readthedocs.yaml` exists but docs are not
   live and the README link is commented out. Needs the RTD project connected.
3. **Do tier-two utilities stay in the default install**, or move behind a
   `pip install aquapose[research]` extra? Not needed for this milestone, but the
   docs tiering makes it a cheap follow-up if wanted.
4. **Hero media format** — GIF/MP4 loop, linked YouTube thumbnail, or both.
5. **Zenodo deposit granularity** — one deposit containing data + models +
   reference outputs, or separate deposits with separate DOIs.
