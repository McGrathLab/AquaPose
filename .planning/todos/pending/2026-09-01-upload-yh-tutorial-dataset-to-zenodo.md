---
created: 2026-09-01T00:00:00.000Z
title: Upload AquaPose YH tutorial dataset to Zenodo and record the DOI
area: publication
files:
  - scripts/package_tutorial_dataset.py
  - aquapose-tutorial-data/
---

## Problem

Phase 111 assembled, verified, and finalized the Zenodo tutorial deposit
(`aquapose-tutorial-data/`, 215 MB, `sha256sum -c` clean, CC-BY-4.0 data +
AGPL-derived model weights). The **manual Zenodo upload + DOI minting was
deferred** (D-11 — human-only external publish). The deposit README carries a
`<DOI filled after upload>` placeholder. DATA-03's automatable portion is done;
the DOI is outstanding.

This blocks the citation/DOI badge work in **Phase 114** (README-*, DOI badge)
and the tutorial's citation block in **Phase 113**.

## Solution

1. Regenerate the publish-ready tree if stale: `hatch run python scripts/package_tutorial_dataset.py --source-dir D:/AquaPose_Zenodo_staging/YH --output-dir ./aquapose-tutorial-data --regenerate-outputs` (GPU + local staging required; LUTs auto-generated via prep, excluded from the shipped tree).
2. Log in at https://zenodo.org (ORCID/GitHub) → New upload → upload the contents of `aquapose-tutorial-data/` (one deposit / one DOI).
3. Fill metadata from `aquapose-tutorial-data/zenodo-metadata.json`; License = CC-BY-4.0; Upload type = Dataset; Access = Open. Keep the AGPL-derived-weights note in the description.
4. Publish to mint the DOI.
5. Record the DOI into the deposit `README.md` citation block (replace `<DOI filled after upload>`), re-emit `checksums.sha256`, and (Zenodo versioning) upload the corrected README as a new version if the DOI must live inside the published files.

## Status update — 2026-09-02 (Phase 113, D-21)

**Still open. Phase 113 did NOT close this.** The deposit is fully prepared but
deliberately **not published**.

**Ready and verified:**
- Tree verifies 22/22 OK; `verify_deposit()` returns `[]`; no transient
  `runs/` or `geometry/luts` artifacts.
- Four factual doc errors corrected in template and tree, locked by
  `TestDepositDocCorrections` (Plan 113-03).
- Disproven "~2-5 min" LUT timing corrected to the measured 7s (Plan 113-05).
- Full recipe proven end to end on an RTX 4070 Ti: 224s pipeline / 85s viz,
  statistics within tolerance of the reference (Plan 113-05).

**Why it is blocked:** two `calibrate-keypoints` correctness bugs
(`2026-09-02-calibrate-keypoints-writes-t-values-to-legacy-midline-config-key.md`,
`2026-09-02-calibrate-keypoints-yolo-path-measures-arc-length-in-normalized-space.md`).
`aquapose prep calibrate-keypoints` is step 3 of the path the tutorial documents,
and a published DOI cannot be withdrawn — only superseded.

**Sequence to close:**
1. Fix both `calibrate-keypoints` bugs.
2. Re-run plan `113-06-PLAN.md` (marked `deferred: true`): reserve the DOI, write
   it into the deposit README **and** the template in
   `scripts/package_tutorial_dataset.py` (D-06), re-emit checksums, verify 22 OK,
   produce the 22-path upload list mechanically from the manifest.
3. Upload exactly those 22 files and publish.
4. Fill every `<!-- ZENODO-DOI-PENDING -->` site: `docs/getting-started/tutorial.md`
   (prose link + bibtex `doi` field) and the deposit README citation block.
   `grep -rn 'ZENODO-DOI-PENDING'` finds them all.
5. Mark **DATA-03** complete — Phase 113 leaves it deliberately unsatisfied.
