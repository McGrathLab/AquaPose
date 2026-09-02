---
created: 2026-09-02T00:00:00.000Z
title: aquapose init emits a string n_animals sentinel that crashes load_config with TypeError
area: cli
files:
  - src/aquapose/cli.py
  - src/aquapose/engine/config.py
---

## Problem

`aquapose init <name>` scaffolds a starter `config.yaml` containing:

```yaml
n_animals: SET_ME
```

but `PipelineConfig` declares `n_animals: int = 0` (`src/aquapose/engine/config.py:472`)
and `load_config` validates the sentinel numerically:

```python
resolved_n_animals = top_kwargs.get("n_animals", 0)
if resolved_n_animals <= 0:
    raise ValueError("n_animals is required and must be > 0")
```

(`src/aquapose/engine/config.py:777-779`)

`"SET_ME" <= 0` compares `str` to `int`, so the guard never reaches its own
`raise`. A new user who runs `aquapose init` and then runs the pipeline without
editing the config gets:

```
TypeError: '<=' not supported between instances of 'str' and 'int'
```

instead of the intended, actionable `ValueError: n_animals is required and must be > 0`.

Reproduced on `dev` at `68ab734` (aquapose 1.1.0.dev7):

```
$ aquapose init probe
$ python -c "from aquapose.engine.config import load_config; load_config('.../probe/config.yaml')"
TypeError: '<=' not supported between instances of 'str' and 'int'
```

The writer is `init_cmd` in `src/aquapose/cli.py`:
`data["n_animals"] = "SET_ME"  # required -- must be an integer`.

## Why it matters

This is the **first command a new user runs**, and the failure lands on the
init → run path that Phase 113's install guide and tutorial now walk people
down. The docstring's stated design ("Sentinel value of 0 means not set;
`load_config` raises `ValueError` when this is...", `config.py:438-439`) is
correct — the CLI writer just does not honor it.

## Solution

Three parts. 1 and 2 are the bug fix; 3 is the guidance gap that let a new user
hit it in the first place.

1. Have `init_cmd` write the int sentinel `0` and keep the human hint in a
   YAML comment (the generator already injects a comment before `pose:`, so the
   same `str.replace` trick works):
   `n_animals: 0  # REQUIRED -- set to the number of animals in the scene`
2. Or make the guard type-safe before comparing, so any non-int value
   (string, null, float) produces the friendly `ValueError`.

Doing **both** is defensible: 1 fixes the generated artifact, 2 hardens the
guard against hand-edited configs that reintroduce a non-int.

3. **Add the missing `n_animals` step to the post-init console guidance.**
   `init_cmd` currently prints (`src/aquapose/cli.py:210-217`):

   ```
   Next steps:
     1. Place calibration JSON in geometry/calibration.json
     2. Run: aquapose --project <name> prep generate-luts
     3. Run: aquapose --project <name> prep calibrate-keypoints --annotations <json>
   ```

   Every listed step is about *external* inputs; none tells the user to edit
   the config it just generated. Setting `n_animals` is the one edit that is
   **mandatory before anything runs**, and it is the only required field the
   scaffold cannot infer -- yet it is the only next step not mentioned. Add it
   as the new step 1 (it gates every later step, and the user is already
   looking at the file path that was just printed):

   ```
   Next steps:
     1. Edit config.yaml -- set n_animals to the number of animals in the scene
     2. Place calibration JSON in geometry/calibration.json
     3. Run: aquapose --project <name> prep generate-luts
     4. Run: aquapose --project <name> prep calibrate-keypoints --annotations <json>
   ```

   Keep it consistent with whatever sentinel option 1 lands on -- if the
   generated line becomes `n_animals: 0`, the guidance should say so, so the
   printed text and the file agree.

Terminal gate: `aquapose init probe` followed immediately by a pipeline run
fails with `ValueError: n_animals is required and must be > 0`, not `TypeError`.
Add a regression test asserting the error type and message for an unedited
init-generated config. Assert the `n_animals` guidance line is present in the
`init` stdout so the instruction cannot be dropped silently later.

## Notes

Found while spot-checking a freshly generated config during Phase 113 execution;
deliberately **not** folded into Phase 113, which is a documentation phase whose
only sanctioned behavior change is the D-08 install-path fix.

## Fixed

**Date:** 2026-09-02
**Fixed by:** Phase 113.1, Plan 02 (`113.1-02-PLAN.md`, D-12, D-13).
**Evidence:** `init_cmd` in `src/aquapose/cli.py` now writes the int sentinel
`n_animals: 0` (commit `1e652f9`) with the human hint preserved as a YAML
comment; the post-scaffold guidance leads with the `n_animals` edit as the new
step 1 (commit `c216a77`); and the `load_config` guard in
`src/aquapose/engine/config.py` was made type-safe (rejects non-int and bool
values before the numeric comparison) via TDD — RED `f897803`, GREEN
`1b290f0`. Terminal gate (`aquapose init probe` followed by a pipeline run
fails with `ValueError: n_animals is required and must be > 0`, not
`TypeError`) verified in `113.1-02-SUMMARY.md`.
