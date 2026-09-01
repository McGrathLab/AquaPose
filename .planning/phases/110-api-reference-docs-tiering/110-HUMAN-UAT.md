---
status: partial
phase: 110-api-reference-docs-tiering
source: [110-VERIFICATION.md]
started: 2026-09-01T21:39:48Z
updated: 2026-09-01T21:39:48Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. Sidebar tier split renders (D-04)
expected: Open `docs/_build/html/api/index.html` — the Furo sidebar shows "Core Pipeline" and "Research Utilities" as two distinct sections before clicking into any page.
result: [pending]

### 2. Tier-two note admonition renders (D-05)
expected: Open `docs/_build/html/api/evaluation.html` — a styled note box appears immediately after the "Evaluation" heading with the verbatim text "Research utility — not part of the supported pipeline API." (em-dash preserved).
result: [pending]

### 3. Formerly-invisible modules now render (DOCS-02)
expected: Open `docs/_build/html/api/core/association.html` (clustering/recovery/scoring/validation members render) and `docs/_build/html/api/evaluation/viz.html` (animation/overlay render; no `_frames`/`_loader`).
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps
