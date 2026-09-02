# API Coverage — Phase 113.1 (Pre-Release Bug Fixes)

No external API integration: this phase fixes four in-repo defects (the
`prep calibrate-keypoints` config-key writer and its YOLO arc-length
measurement, the `aquapose init` scaffold sentinel plus the `load_config`
`n_animals` guard, the stale `.planning/GUIDEBOOK.md` §6 stage order, and the
`core/` → `aquapose.io` import-boundary violation) and files two stale todos —
no external service, SDK, REST/gRPC client, webhook, or third-party API surface
is added, wrapped, called, or configured anywhere in its scope.

The one network-adjacent item in the surrounding milestone — the Zenodo deposit
and DOI mint — is explicitly **out of scope** here (CONTEXT.md D-05); it stays
in the deferred plan `113-06-PLAN.md` in Phase 113. Nothing in this phase talks
to Zenodo, and `grep -q 'doi\.org' docs/getting-started/tutorial.md` must still
FAIL when the phase ends.

No package-manager install task exists in this phase either, so no Package
Legitimacy Audit table is required: no dependency is added, removed, pinned, or
upgraded in `pyproject.toml`. (One latent finding — `pillow` is imported
directly by three `training/` modules but is not a declared dependency — is
filed as a follow-up todo by `113.1-03`, not fixed here.)

*Written at plan time by the GSD planner, 2026-09-02.*
