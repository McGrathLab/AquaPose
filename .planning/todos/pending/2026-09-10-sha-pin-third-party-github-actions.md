---
created: 2026-09-10T00:00:00.000Z
title: SHA-pin third-party GitHub Actions, especially in the publish path
area: security
files:
  - .github/workflows/publish.yml
  - .github/workflows/test.yml
  - .github/workflows/docs.yml
  - .github/workflows/release.yml
  - .github/workflows/slow-tests.yml
---

## Problem

Third-party GitHub Actions are pinned to mutable tags rather than commit SHAs. This
was recorded as an accepted residual risk during Phase 114 — threat `T-114-02-04` in
`114-02-PLAN.md`'s threat model — with the note that SHA-pinning is "a reasonable
follow-up hygiene item." This todo is that follow-up.

The two that matter most:

- `pypa/gh-action-pypi-publish@release/v1` in `publish.yml` — runs in the publish
  jobs, which hold `id-token: write` and the `pypi` / `testpypi` environments. A
  compromised upstream tag could mint an OIDC token and publish to PyPI as this
  project.
- `codecov/codecov-action@v5` in `test.yml` — runs with `CODECOV_TOKEN` in scope.

`actions/*` (checkout, setup-python, upload-artifact, download-artifact) are
first-party GitHub actions; the risk there is lower, though the same argument applies.

## Why this matters

The exposure changed materially in Phase 114. Before, nothing had published from this
repo since 2026-02-19 and the publish path was effectively dormant. Now `v4.0.0` is
live, trusted publishing is confirmed working on both indexes, and the release
procedure is a tag push away. The publish path is a live, credentialed supply-chain
surface rather than a theoretical one, and PyPI filenames are immutable — an
unintended publish cannot be withdrawn, only superseded.

This is hygiene, not an incident. There is no indication any action was compromised.

## Solution

Pin each third-party action to a full 40-character commit SHA with the human-readable
version in a trailing comment, which is the convention GitHub's own hardening guidance
recommends:

```yaml
- uses: pypa/gh-action-pypi-publish@<40-char-sha>  # release/v1
- uses: codecov/codecov-action@<40-char-sha>       # v5
```

Resolve each SHA from the action's repository at the tag currently in use, so pinning
does not silently change behaviour. Consider enabling Dependabot for
`package-ecosystem: github-actions` so pins are proposed for update rather than
frozen indefinitely — a stale pin is its own risk.

**Do not bundle this with a release.** Change the workflows, let CI run green on `dev`,
and only then cut any tag. `publish.yml` in particular should not be edited and
exercised in the same motion — Phase 114 established the rule that a failing publish
is fixed by deleting the tag and re-cutting, never by editing the workflow to unblock it.

## Verification

- Every `uses:` line referencing a non-`actions/*` org specifies a 40-character
  commit SHA, with the version in a comment.
- Each pinned SHA is reachable in the upstream repository and corresponds to the tag
  named in the comment.
- `Tests` and `Documentation` workflows run green on `dev` after the change.
- `publish.yml` is verified by inspection only — do not cut a throwaway tag to test
  it. Its next real exercise is the next release.
- If Dependabot is enabled: `.github/dependabot.yml` includes a
  `github-actions` ecosystem entry.
