---
phase: 113-concepts-tutorial
plan: 06
subsystem: data-publication
tags: [zenodo, doi, dataset, tutorial, one-way-door]

# Dependency graph
requires:
  - phase: 113-concepts-tutorial
    provides: "113-03 deposit factual corrections and 113-05 end-to-end verification run — the deposit was publish-ready and verified 22/22 before the mint"
  - phase: 113.1-pre-release-bug-fixes
    provides: "Both calibrate-keypoints correctness fixes — the D-21 blocker that deferred this plan for a permanent, unwithdrawable DOI"
provides:
  - "A published, citable Zenodo record for the tutorial dataset: 10.5281/zenodo.22264079 (concept DOI 10.5281/zenodo.22264078)"
  - "docs/getting-started/tutorial.md carrying a real download URL, verification step and citation block instead of placeholders"
  - "scripts/package_tutorial_dataset.py README template carrying the DOI, so a regenerated deposit self-cites correctly"
affects: ["114"]

actuals:
  tasks: 3
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Verifying a published artifact without downloading it: the deposit README and checksum manifest were read out of the 206 MB Zenodo zip over HTTP Range requests (EOCD -> central directory -> per-entry local header -> raw deflate stream), so the claim 'the published record self-cites correctly' rests on the published bytes rather than on the local staging copy."

key-files:
  created: []
  modified:
    - docs/getting-started/tutorial.md
    - scripts/package_tutorial_dataset.py

key-decisions:
  - "The mint itself was performed by the developer outside the agent loop on 2026-09-03, satisfying the plan's first must_have (a human, not an agent, performs the account action that creates a permanent public artifact under the maintainer's identity). This summary is written after the fact and verifies the outcome against the live record rather than narrating an action it did not take."
  - "The tutorial cites the VERSION DOI (10.5281/zenodo.22264079), not the concept DOI, because every number on that page was verified against these exact files and the version DOI is what keeps resolving to them. The concept DOI (10.5281/zenodo.22264078) is documented alongside it as the right citation for the dataset in general."
  - "No new version was uploaded. The published deposit README already carries the correct version DOI in its bibtex block, so the plan's 'the published record cites itself correctly' requirement was met at upload time and there is nothing to correct. A new version purely to fix self-citation would have been the only reason to touch the record."

patterns-established:
  - "A one-way-door plan can be closed retroactively by verifying the live artifact, but the verification must read the published bytes, not the local copy that was supposed to have been uploaded. The two can differ, and only one of them is what users get."

requirements-completed: [DATA-03]

coverage:
  - id: D1
    description: "The Zenodo record is live, published, open-access, correctly licensed, and authored — the DATA-03 deliverable"
    requirement: DATA-03
    verification:
      - kind: e2e
        ref: "https://zenodo.org/api/records/22264079 — DOI 10.5281/zenodo.22264079, concept DOI 10.5281/zenodo.22264078, title 'AquaPose YH Tutorial Dataset', creator Tucker Lancaster (ORCID 0000-0003-4074-7128, Georgia Institute of Technology), published 2026-09-03, type dataset, CC-BY-4.0, is_last true, one file aquapose-tutorial-data.zip (215,579,929 bytes)"
        status: pass
      - kind: e2e
        ref: "Description declares the mixed licensing — CC-BY-4.0 for videos/calibration, AGPL-3.0-derived for the bundled model weights — which is the half of DATA-03 that a bare CC-BY-4.0 record would have gotten wrong"
        status: pass
    human_judgment: false
  - id: D2
    description: "The published archive is structurally what the tutorial promises: extracts to aquapose-tutorial-data/, carries a 22-entry SHA-256 manifest, and its README self-cites with the real DOI rather than the pre-upload placeholder"
    requirement: DATA-03
    verification:
      - kind: e2e
        ref: "Remote zip read over HTTP Range: 28 central-directory entries = 23 files + 5 directory entries, top-level dir aquapose-tutorial-data/. README.md bibtex reads doi = {10.5281/zenodo.22264079} — NOT the '<DOI filled after upload>' placeholder the script template emitted"
        status: pass
      - kind: e2e
        ref: "checksums.sha256 read from the published archive: exactly 22 lines, covering all 23 files except the manifest itself (config.yaml, geometry/calibration.json, 2 models, README.md, 4 reference_outputs, 12 videos, zenodo-metadata.json)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every ZENODO-DOI-PENDING placeholder in the repo is replaced with the real DOI, download URL and citation; the packaging script's README template carries the DOI so a regeneration reproduces a self-citing deposit"
    requirement: DOCS-07
    verification:
      - kind: unit
        ref: "grep -rn 'ZENODO-DOI-PENDING|DOI filled after upload' over *.md/*.py outside .planning/ returns nothing"
        status: pass
      - kind: integration
        ref: "hatch run docs:build (sphinx-build -W --keep-going) — build succeeded, 0 warnings"
        status: pass
      - kind: integration
        ref: "hatch run test — 1410 passed, 2 skipped, 17 deselected (TestDepositDocCorrections unaffected)"
        status: pass
    human_judgment: false

duration: mint 2026-09-03 (developer); local fill-in 2026-09-09
completed: 2026-09-09
status: complete
---

# Phase 113 Plan 06: Zenodo DOI Mint Summary

**The tutorial dataset is published at [10.5281/zenodo.22264079](https://zenodo.org/records/22264079) and the repo no longer says "pending" anywhere — the download URL, verification step and citation block are real, and the published archive was confirmed to self-cite correctly by reading its README out of the live 206 MB zip rather than trusting the local staging copy.**

## What actually happened, and when

This plan was `deferred: true` on 2026-09-02 under D-21: the Zenodo publish was
blocked on the two `calibrate-keypoints` correctness bugs, because `prep
calibrate-keypoints` is step 3 of the documented tutorial path and *a published
DOI cannot be withdrawn*. Phase 113.1 cleared both bugs on 2026-09-02.

The developer then performed the mint on **2026-09-03**, outside the agent loop.
That ordering satisfies the plan's first and most important must-have — a human,
not an agent, performs the account action that creates a permanent public artifact
under the maintainer's identity (D-04) — and it is why this summary verifies an
outcome instead of narrating an action.

What had *not* happened until now is the local half: the repo still carried
`ZENODO-DOI-PENDING` placeholders, an interim "ask the maintainers for the data"
paragraph, and a packaging template that emitted `<DOI filled after upload>`. That
is the work committed here.

## Verification of the published record

Two independent reads, neither of which trusts the local staging directory (which
no longer exists on this machine):

**1. The record metadata**, from `https://zenodo.org/api/records/22264079`:

| Field | Value |
|---|---|
| Version DOI | `10.5281/zenodo.22264079` |
| Concept DOI | `10.5281/zenodo.22264078` |
| Title | AquaPose YH Tutorial Dataset |
| Creator | Tucker Lancaster, Georgia Institute of Technology (ORCID 0000-0003-4074-7128) |
| Published | 2026-09-03 |
| Type / access | Dataset, open |
| License | CC-BY-4.0, with the model-weight AGPL derivation declared in the description |
| Files | `aquapose-tutorial-data.zip`, 215,579,929 bytes |

The mixed-licensing declaration matters: DATA-03 requires the videos and
calibration under CC-BY-4.0 *and* the bundled weights labelled separately as
AGPL-derived artifacts. A record that claimed a flat CC-BY-4.0 over the weights
would have satisfied the checkbox and misstated the license.

**2. The archive contents**, read over HTTP Range requests rather than downloaded:
parse the end-of-central-directory record, walk the central directory, then
range-fetch and inflate only the two small entries of interest. 28 central-directory
entries = 23 files + 5 directory entries, rooted at `aquapose-tutorial-data/` —
confirming the directory name every command in the tutorial assumes.

- **`README.md`** bibtex block reads `doi = {10.5281/zenodo.22264079}`. **Not** the
  `<DOI filled after upload>` placeholder that the packaging script's template
  emitted. The pre-upload fill-in the plan required was genuinely done, so the
  published record cites itself correctly and **no new version upload is needed**.
- **`checksums.sha256`** has exactly **22 lines**, covering all 23 files except the
  manifest itself. This is the "All 22 files should report `OK`" figure the tutorial
  tells users to expect, verified against the published bytes.

## Local fill-in

- `docs/getting-started/tutorial.md` — replaced the "being prepared for publication"
  admonition with the real DOI link and a `curl`/`unzip` download block; removed the
  now-false "it is not yet available at a public URL, ask the maintainers" paragraph;
  filled the bibtex `doi` field; explained version-vs-concept DOI so a reader cites
  the snapshot these numbers were verified against rather than a moving target.
- `scripts/package_tutorial_dataset.py` — README template now emits the real DOI, so
  regenerating the deposit reproduces a self-citing record (the plan's D-04/D-06
  requirement that the fix survive regeneration).

## Deviations from Plan

- **Task ordering inverted.** The plan sequenced *reserve DOI -> write it into the
  deposit -> re-emit checksums -> upload*. What happened is that the developer
  completed the entire deposit-side sequence and published, and the repo-side
  fill-in happened six days later. The end state is identical and the published
  record is correct; the plan's checkpoint gate was satisfied by the developer's
  own judgment at mint time rather than by an agent pausing for approval.
- **`checksums.sha256` was not re-emitted by this plan**, because it did not need to
  be: the manifest in the published archive already covers a README containing the
  real DOI. Re-emitting locally would have produced a manifest for files nobody can
  download.
- **The deposit directory is not present on this machine**, so no local artifact was
  inspected or modified. Everything asserted about the deposit is asserted about the
  published archive, which is the only copy that matters to a user.

## Issues Encountered

None. The one thing that could have gone wrong — the placeholder shipping into a
permanent record — did not.

## Next Phase Readiness

DATA-03 is satisfied and DOCS-07's "on the **published** dataset" wording is now
literally true rather than aspirational; the open question the 113 handoff left for
the developer (whether DOCS-07 should be flipped back to Pending) is resolved by
publication rather than by a judgment call. Phase 113's three success criteria are
all met. Phase 114 (README, badge row, citation block) can now cite a real DOI, and
together with 113.2's green CI typecheck job, its badge row has nothing left to fake.

## Self-Check: PASSED

The DOI, concept DOI, file count, byte size, manifest line count and the deposit
README's bibtex line were all read from the live Zenodo record and its published
archive during this session, not copied from planning documents. One error was made
and corrected before commit: an added sentence claimed `zenodo-metadata.json` was
outside the 22-file manifest — reading all 22 lines showed it is inside.

---
*Phase: 113-concepts-tutorial*
*Mint: 2026-09-03 (developer) — Local fill-in and verification: 2026-09-09*
