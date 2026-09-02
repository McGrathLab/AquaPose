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

Pick one; option 1 is smallest and matches the documented design:

1. Have `init_cmd` write the int sentinel `0` and keep the human hint in a
   YAML comment (the generator already injects a comment before `pose:`, so the
   same `str.replace` trick works):
   `n_animals: 0  # REQUIRED -- set to the number of animals in the scene`
2. Or make the guard type-safe before comparing, so any non-int value
   (string, null, float) produces the friendly `ValueError`.

Doing **both** is defensible: 1 fixes the generated artifact, 2 hardens the
guard against hand-edited configs that reintroduce a non-int.

Terminal gate: `aquapose init probe` followed immediately by a pipeline run
fails with `ValueError: n_animals is required and must be > 0`, not `TypeError`.
Add a regression test asserting the error type and message for an unedited
init-generated config.

## Notes

Found while spot-checking a freshly generated config during Phase 113 execution;
deliberately **not** folded into Phase 113, which is a documentation phase whose
only sanctioned behavior change is the D-08 install-path fix.
