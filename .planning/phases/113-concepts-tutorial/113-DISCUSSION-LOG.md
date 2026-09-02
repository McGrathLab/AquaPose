# Phase 113: Concepts & Tutorial - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-02
**Phase:** 113-concepts-tutorial
**Areas discussed:** Concepts page scope, Dataset & the missing DOI, Install guide, Tutorial verification

---

## Concepts page scope

### Q1 — The `{p, ψ, κ, s}` state vector required by DOCS-04 does not exist in the code

| Option | Description | Selected |
|--------|-------------|----------|
| Document what it actually computes | Drop the state vector; explain the real representation (arc-length-sampled midline points → B-spline). Record the requirement discrepancy like 112's D-06 | ✓ |
| Explain it as derived kinematics | Keep the framing but present it as quantities derived *from* the midline, not stored by the pipeline | |
| Cover both, clearly separated | B-spline representation plus a section on the classic parameterization and how to compute it | |
| You decide | Let the researcher/planner determine the framing | |

**User's choice:** Document what it actually computes
**Notes:** Evidence presented: grep across `src/` finds only `InitialFishState` (`synthetic/trajectory.py:133` — position, heading_xy, speed), a synthetic trajectory seed. The state vector survives only in `CLAUDE.md`'s Domain Conventions, a v1.x differentiable-rendering leftover.

### Q2 — Depth on refractive projection

| Option | Description | Selected |
|--------|-------------|----------|
| Intuition + the consequence | Why the interface bends rays, why naïve triangulation is wrong underwater, what AquaPose does instead. No derivations | ✓ |
| Intuition + the actual math | Plus Snell's law stated, forward/inverse LUT formulation, flat-surface assumption as a limitation | |
| Brief mention, link to API | Short paragraph, defer detail to `calibration.projection` | |

**User's choice:** Intuition + the consequence

### Q3 — Diagrams

| Option | Description | Selected |
|--------|-------------|----------|
| Mermaid diagrams only | Stage flow and data flow as Mermaid; `sphinxcontrib-mermaid` already in the docs env. No binary assets | ✓ |
| Mermaid + one refraction figure | Plus an authored SVG ray-bending diagram | |
| Mermaid + reuse reference outputs | Plus a still from the overlay mosaic and/or an `animation_3d.html` embed | |
| Text only | No diagrams | |

**User's choice:** Mermaid diagrams only
**Notes:** Docs currently contain zero images; this keeps it that way.

### Q4 — Treatment of tier-two research utilities

| Option | Description | Selected |
|--------|-------------|----------|
| Tier-one pipeline only | Five production stages, calibration, refraction. Research utilities stay in the Phase 110 API tiering | ✓ |
| Pipeline + a short "what else is here" section | Plus a closing orientation paragraph pointing at tier-two pages | |
| You decide | Let the planner size it | |

**User's choice:** Tier-one pipeline only

---

## Dataset & the missing DOI

### Q1 — How to proceed with no minted DOI

| Option | Description | Selected |
|--------|-------------|----------|
| Mint the DOI first, as a phase task | Make the manual Zenodo upload an explicit checkpoint task, then write against the real DOI | ✓ |
| Write against a placeholder | Author now with `<DOI pending>` and one substitution point | |
| Write against the concept, not the link | Keep content DOI-agnostic, isolate the URL in one admonition | |
| You decide | Let the planner sequence it | |

**User's choice:** Mint the DOI first, as a phase task
**Notes:** Mid-discussion the user downloaded the deposit to `~/Downloads/aquapose-tutorial-data.zip`. Extracted to the repo root (covered by `.gitignore:104`) and verified: `sha256sum -c` → **22/22 OK**, 215 MB. This removed the practical blocker — no regeneration or `D:/` staging access needed.

### Q2 — Three deposit doc errors would be frozen into the Zenodo record

| Option | Description | Selected |
|--------|-------------|----------|
| Fix deposit, re-checksum, then upload | Correct the errors, re-run `write_checksums()`, then mint the DOI | ✓ |
| Fix in the script, regenerate the tree | Patch templates and rebuild from source — needs the `D:/` staging videos | |
| Upload now, correct in v2 | Mint from the current tree, publish a corrected version later | |
| You decide | Let the planner sequence it | |

**User's choice:** Fix deposit, re-checksum, then upload
**Notes:** Errors found by reading the deposit against the actual CLI: (1) `config.yaml` names a `--config` flag that does not exist on `run` (`cli.py:41-88`); (2) README links `github.com/tucklancaster/AquaPose` instead of `McGrathLab/AquaPose`; (3) `pip install aquapose` — not on PyPI. The README's `cd` + bare `aquapose run` sequence was verified correct via `cli_utils.py:33-47` CWD-upward resolution.

### Q3 — Whether to patch the generating script too

| Option | Description | Selected |
|--------|-------------|----------|
| Patch script and tree together | Fix templates in `scripts/package_tutorial_dataset.py` AND the extracted tree | ✓ |
| Patch the tree only | Hand-edit the deposit; leave the script alone | |
| Patch the script only, then regenerate the docs files | Fix templates, re-run just the doc-writing steps, re-checksum | |

**User's choice:** Patch script and tree together
**Notes:** The script is tracked, tested, and is the reproducibility claim behind DATA-01.

### Q4 — Install step given AquaPose is not on PyPI

| Option | Description | Selected |
|--------|-------------|----------|
| pip install from GitHub | `pip install git+https://github.com/McGrathLab/AquaPose.git` — works today | |
| Clone + hatch env create | Mirror the documented dev workflow | |
| Both, with pip as the default | Lead with the one-liner, offer hatch for developers | |
| Keep `pip install aquapose`, publish to PyPI first | Treat PyPI publication as a prerequisite | |

**User's choice:** *(free text)* "Phase 114 will handle the pip publication and I plan to handle it immediately after this phase. So go ahead and include the pip install in the readme. It's technically untrue at this moment, but will be true shortly."
**Notes:** Recorded in CONTEXT.md as D-09 with an explicit accepted-risk note and a Phase 114 dependency in Deferred Ideas. Narrowed the deposit fixes from three errors to two.

### Q5 — Relationship between the deposit README and the docs tutorial

| Option | Description | Selected |
|--------|-------------|----------|
| Docs tutorial is the long form | Deposit README stays the terse recipe; docs expand each step with explanation and interpretation | ✓ |
| Single source, deposit points at docs | Trim the README to a link — but the Zenodo record becomes less self-contained | |
| Mirror them deliberately | Keep both complete and identical, noted as needing sync | |

**User's choice:** Docs tutorial is the long form

---

## Install guide

### Q1 — Where the install guide lives

| Option | Description | Selected |
|--------|-------------|----------|
| New "Getting Started" section | Top-level section holding Installation, Concepts, Tutorial — parallel to Phase 112's Reference section | ✓ |
| Three standalone top-level pages | Flat in the root toctree; crowds the index card grid | |
| Fold install into the tutorial | Fewer pages, but DOCS-03 wants install findable on its own | |

**User's choice:** New "Getting Started" section

### Q2 — What to say about GPU/CUDA

| Option | Description | Selected |
|--------|-------------|----------|
| Document verified reality, per install path | State what each path yields, how to verify, how to fix a CPU-only install | |
| Minimum-requirements framing | Hardware/driver floor plus one recommended command | |
| Both: requirements up front, troubleshooting after | Requirements, recommended command, then a troubleshooting subsection | |

**User's choice:** *(free text)* "pinning a specific cuda version in the default env feels questionable? Should we default to CPU in the env, but point the user to the pytorch getting started page (https://pytorch.org/get-started/locally/) for their specific install command? I feel like i see that a lot in other libraries"
**Notes:** User rejected the framing of the question and proposed fixing the underlying cause instead. Prompted the follow-up in Q3.

### Q3 — Whether to drop the cu121 pin in this phase

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — do it in this phase | Remove `UV_EXTRA_INDEX_URL` from the default env; install guide defers torch to pytorch.org with a `torch.cuda.is_available()` verify | ✓ |
| Yes — but defer the change to Phase 114 | Write against the intended end state; make the pyproject change part of 114 | |
| No — keep the pin, document it | Zero code change; CI keeps pulling CUDA wheels | |

**User's choice:** Yes — do it in this phase
**Notes:** Supporting evidence gathered before asking: CI has no GPU (`test.yml` runs ubuntu/windows-latest across Python 3.11/3.12/3.13; `slow-tests.yml` defaults to ubuntu-latest), so all six matrix jobs pull multi-GB CUDA wheels to run CPU tests. The cu121 pin also caps torch version resolution, and the README already contradicts it by telling users to reinstall with cu124. Scope caveat raised (a `pyproject.toml` change in a docs phase, against the milestone's "bug fixes only" fence); user confirmed.

### Q4 — Depth on non-obvious prerequisites

| Option | Description | Selected |
|--------|-------------|----------|
| Full prerequisites section | ffmpeg on PATH, ~600 MB for generated LUTs plus 215 MB dataset, GPU floor from the 1660 SUPER reference run | ✓ |
| Minimal — Python and torch only | Surface the rest at point of use in the tutorial | |
| Both — checklist here, detail in the tutorial | Short checklist, LUT specifics where it's run | |

**User's choice:** Full prerequisites section

---

## Tutorial verification

### Q1 — How to express "expected results at each step"

| Option | Description | Selected |
|--------|-------------|----------|
| Quoted stats with tolerance ranges | Real numbers as approximate expectations, so a user can tell a good run from a broken one without exact matching | ✓ |
| A verification snippet they run | Copy-pasteable h5py snippet printing the same statistics next to reference values | |
| Qualitative only | "Your animation should show 9 fish swimming coherently" | |
| Checksum the reference, compare visually | Verify the download, then compare by eye | |

**User's choice:** Quoted stats with tolerance ranges
**Notes:** Statistics computed live from the deposit's `outputs.h5`: 900 frames × 9 fish × 6 keypoints; 7711/8100 fish-frames reconstructed (95.2%); median mean-residual 2.84 px (mean 3.92, p95 9.73); median 4 cameras per fish (range 0–6); 4.0% flagged low-confidence; 6–9 fish visible per frame.

### Q2 — Depth on the `outputs.h5` format

| Option | Description | Selected |
|--------|-------------|----------|
| Walk the real schema | Document the `midlines` group as it exists, including the quality fields, and show loading and plotting one fish | ✓ |
| Load-and-plot recipe only | Working snippet with field meanings inline | |
| Point at the viz commands | Interpretation through `aquapose viz`; defer schema to the API reference | |

**User's choice:** Walk the real schema
**Notes:** Schema verified by direct inspection — `SPLINE_K=3`, 11-element knot vector, `points (900,9,6,3)`, `control_points (900,9,7,3)`, plus `mean_residual` / `n_cameras` / `is_low_confidence` quality fields.

### Q3 — Verify by running, or author from reference outputs

| Option | Description | Selected |
|--------|-------------|----------|
| Execute the tutorial end-to-end once | Run `prep generate-luts` → `run` → `viz` on the extracted deposit and correct anything that doesn't match | ✓ |
| Author from reference outputs, spot-check commands | Use the verified outputs and check `--help` rather than running the pipeline | |
| You decide | Let the planner decide | |

**User's choice:** Execute the tutorial end-to-end once
**Notes:** Feasible because the deposit and a working GPU (RTX 4070 Ti, torch 2.5.1+cu121, CUDA verified) are both present on this machine.

### Q4 — Which hardware timings to quote

| Option | Description | Selected |
|--------|-------------|----------|
| Both, framed as a range | Quote the 1660 SUPER reference and the 4070 Ti measurement so users can locate their own GPU | ✓ |
| Keep the deposit's reference timing | Only `timing.txt`'s numbers | |
| Order-of-magnitude only | "Roughly 10–20 minutes on a consumer GPU" | |

**User's choice:** Both, framed as a range

---

## Claude's Discretion

- Exact page filenames; whether "Getting Started" is a directory or flat files; `.md` vs `.rst` per page.
- Ordering of the Getting Started cards in `docs/index.md`.
- Exact Mermaid diagram shapes and count (stage flow required, others optional).
- Precise wording of the D-12 tolerance ranges and which statistics to quote.
- How the cu121 removal is phrased, and whether the README's `nvrtc` troubleshooting note carries into the install guide.
- Whether to also correct `CLAUDE.md`'s stale `{p, ψ, κ, s}` line.

## Deferred Ideas

- **PyPI publication** → Phase 114. Prerequisite for D-09's `pip install aquapose` being true.
- **README refresh, badges, hero media, citation block, Read the Docs** → Phase 114.
- **Stale `tlancaster6` URLs** in `CODE_OF_CONDUCT.md`, `docs/contributing.md`, and ~829 `CHANGELOG.md` links → Phase 114. D-05 fixes only the deposit's `tucklancaster` variant, because that one is about to be frozen into a permanent Zenodo record.
- **Correcting `CLAUDE.md`'s Domain Conventions state-vector line** — source of the D-01 discrepancy.

### Todos

**Folded:** `2026-09-01-upload-yh-tutorial-dataset-to-zenodo.md` (score 0.6, area publication) — folded by D-04.

**Reviewed, not folded (13):** Add per-stage diagnostic visualizations (0.6); Move LUT generation to pre-pipeline setup (0.6); Wire frame selection into pseudo-label assembly CLI (0.6); Fix core import boundary violation in frame_source (0.6); Generate augmentations on-the-fly at assembly time (0.6); Adapt pseudo-label pipeline for hard case mining (0.6); Triangulate keypoints directly instead of 6-to-15 upsampling (0.6); Active calibration refinement (0.4); Extract frame status strings to constants or enum (0.4); Regenerate golden regression test data for v2.1 (0.4); Iterate only active frames in reconstruction per-fish loop (0.4); Integrate full-frame exclusion masks from AquaMVS (0.2); Speed correlation as second discriminant for association (0.2). All matched on generic keywords; none concern install, concepts, or tutorial documentation.
