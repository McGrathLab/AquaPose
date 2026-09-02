# API Coverage — Phase 113.2 (Typecheck Backlog)

No external API integration: the phase edits type annotations and adds one runtime-checked
h5py narrowing helper inside `src/aquapose/`, integrating no external API, SDK, or service.

## Detector result

The deterministic scan over the phase scope (ROADMAP section 113.2 + `113.2-CONTEXT.md`)
returned `{"detected": false, "signals": []}`, agreeing with the reading above. The scope was
re-read to confirm the detector was not producing a false negative: every file the phase
touches is first-party source under `src/aquapose/`, and the only third-party surfaces
involved are pre-existing pinned dependencies that this phase reads types from rather than
integrates against:

| Third-party surface | Relationship in this phase |
|---|---|
| `h5py` 3.16.0 | Already imported by all five h5py-cluster files. The phase narrows the return type of `Group.__getitem__` at existing call sites. No new call, no new capability, no version change. |
| `pytorch_metric_learning` | Already imported by `training/reid_training.py`. The phase adds two comments beside an existing `MultiSimilarityLoss` construction. No new call. |
| `basedpyright` | The tool being satisfied, run via the existing `hatch run typecheck` script. Not integrated against. |

No package is added, removed, or version-changed; `113.2-06-PLAN.md` gates
`git diff d3e6073 -- pyproject.toml` to zero lines, which proves it mechanically.

There is therefore no capability surface to enumerate and no opt-out to reason about — a
matrix here would be fabricated rows for capabilities that do not exist.
