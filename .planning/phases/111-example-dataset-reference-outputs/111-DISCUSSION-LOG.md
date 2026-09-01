# Phase 111: Example Dataset & Reference Outputs - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-01
**Phase:** 111-example-dataset-reference-outputs
**Mode:** `--auto` (all gray areas auto-selected; recommended option chosen per area)
**Areas discussed:** Source assets & models, Trim & re-encode, Deposit tree & config, Reference outputs, Packaging script & checksums, Zenodo deposit & licensing

---

## Source assets & models to bundle

| Option | Description | Selected |
|--------|-------------|----------|
| Canonical YH config runs, calibration.json only, no LUTs | Bundle the models the live YH `config.yaml` points to (`run_20260318_*`); ship calibration.json only, LUTs auto-generate; no seg model | ✓ |
| PROJECT.md "production models" (`run_20260310_*`) | Use the models PROJECT.md labels production | |
| Ship full geometry incl. LUTs | Bundle `geometry/luts/` (~597 MiB) instead of auto-generating | |

**Selected:** Canonical YH config runs + calibration.json only.
**Notes:** Grounded in `D:\AquaPose_Zenodo_staging\YH\config.yaml` and the
`zenodo-package-components` memory. Flagged the `run_20260310_*` vs `run_20260318_*`
discrepancy for the executor to confirm.

---

## Trim & re-encode

| Option | Description | Selected |
|--------|-------------|----------|
| 30s trim, H.264 CRF 23, no spatial downscale | ~150–200 MB deposit, near-lossless | ✓ |
| Match config truncation (~100 frames / 3.3s) | Minimal clip covering only the tutorial run | |
| Full 5-min clip, re-encode only | No temporal trim; larger deposit | |

**Selected:** 30s trim, H.264 CRF 23.
**Notes:** Hard constraint recorded — never spatially downscale (calibration
intrinsics bound to 1600×1200). Seed Work Item 3.

---

## Deposit tree & config

| Option | Description | Selected |
|--------|-------------|----------|
| Fresh platform-neutral relative-path config.yaml | Author a new deposit config with relative paths | ✓ |
| Ship the live YH config | Reuse `D:\...\YH\config.yaml` as-is (absolute `/home/tlancaster6` paths) | |

**Selected:** Fresh platform-neutral config.yaml (preserving YH's tuned values).
**Notes:** Follows the Phase 109 platform-neutral config pattern.

---

## Reference outputs

| Option | Description | Selected |
|--------|-------------|----------|
| Generate from the deposited trimmed clip | Run pipeline + viz on the deposit tree itself | ✓ |
| Generate from the full 5-min clip | Produce outputs from source, ship alongside trimmed videos | |

**Selected:** Generate from the deposited trimmed clip.
**Notes:** DATA-02 verifiability — a tutorial user reproduces the outputs from the
deposited videos + config on `dev` with the canonical models.

---

## Packaging script & checksums

| Option | Description | Selected |
|--------|-------------|----------|
| Standalone `scripts/package_tutorial_dataset.py` + SHA-256 manifest | Publication tool, not shipped CLI | ✓ |
| New `aquapose data package-deposit` CLI subcommand | Add to the shipped CLI surface | |

**Selected:** Standalone script + `checksums.sha256`.
**Notes:** Publication tooling, not pipeline runtime; joins `scripts/`.

---

## Zenodo deposit & licensing

| Option | Description | Selected |
|--------|-------------|----------|
| Single deposit/one DOI, manual UI upload, CC-BY-4.0 + AGPL-labeled weights | One tree + `zenodo-metadata.json`; human uploads | ✓ |
| Separate deposits (data / models / outputs) with separate DOIs | Multiple citations | |
| Automated/scripted upload | Script performs the Zenodo upload | |

**Selected:** Single deposit, manual UI upload, CC-BY-4.0 data + AGPL-labeled weights.
**Notes:** Human-in-the-loop for the external publish; script prepares the tree and
metadata only. Data license CC-BY-4.0, weights labeled AGPL-derived (2026-08-12 decision).

---

## Claude's Discretion

- Exact 30s trim start offset (representative segment).
- 3D animation format — HTML vs MP4 vs both (default HTML + small overlay MP4).
- Exact CRF within 20–24 if 23 mis-sizes the deposit.
- Script filename, flag surface, and `zenodo-metadata.json` schema.

## Deferred Ideas

- README refresh / badges / hero media / DOI badge → Phase 114.
- CLI + config reference → Phase 112.
- Concepts page, install guide, e2e tutorial (consumes this deposit) → Phase 113.
- Tier-two `pip install aquapose[research]` extra → future PKG-01.
- 5 lexically-matched todos reviewed, not folded (calibration/testing/core work
  unrelated to dataset packaging) — see CONTEXT.md Deferred Ideas.
