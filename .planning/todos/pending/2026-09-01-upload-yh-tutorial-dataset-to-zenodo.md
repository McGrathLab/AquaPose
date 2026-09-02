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
