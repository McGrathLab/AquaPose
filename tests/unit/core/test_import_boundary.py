"""AST-based guard for the ``core/`` package's import boundary.

Enforces GUIDEBOOK section 3's import-discipline rule that ``core/`` may
only import stdlib, third-party, and core-internal modules at runtime.
Every module under ``src/aquapose/core/`` is parsed with :mod:`ast` rather
than grepped, so module-level, function-local, and ``TYPE_CHECKING``-guarded
imports are all caught -- a grep for import lines cannot see nested imports,
and a function-local or ``TYPE_CHECKING``-guarded import still resolves at
runtime (the former on call, the latter is not a safe place to hide a
forbidden dependency from this guard).
"""

from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CORE_ROOT = _REPO_ROOT / "src" / "aquapose" / "core"


def _iter_core_python_files() -> list[Path]:
    """Return every ``.py`` file under ``src/aquapose/core/``, sorted."""
    return sorted(_CORE_ROOT.rglob("*.py"))


def _collect_imports(path: Path) -> list[tuple[int, str]]:
    """Return ``(lineno, imported_module)`` pairs for every import in *path*.

    Walks the full AST (:func:`ast.walk`), not just the module body, so
    imports nested inside functions or ``if TYPE_CHECKING:`` blocks are
    included alongside top-level ones.

    Args:
        path: Path to a Python source file, read as UTF-8.

    Returns:
        A list of ``(lineno, module_name)`` tuples, one per ``import`` or
        ``from ... import ...`` statement found anywhere in the module.
    """
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            found.append((node.lineno, node.module))
    return found


def _matching_forbidden_package(module: str) -> str | None:
    """Return the ``_FORBIDDEN_PACKAGES`` entry *module* falls under, if any."""
    for package in _FORBIDDEN_PACKAGES:
        if module == package or module.startswith(package + "."):
            return package
    return None


# Every package `core/` may not import at runtime, however the import is
# spelled (module-level, function-local, or TYPE_CHECKING-guarded).
#
# `aquapose.calibration` is deliberately NOT included here: GUIDEBOOK
# section 3 places calibration in Layer 1 alongside `core/`, so a `core/`
# to `calibration/` import is within-layer, not a boundary crossing --
# even though `calibration/` lives in a sibling directory rather than
# under `core/` itself.
_FORBIDDEN_PACKAGES: tuple[str, ...] = (
    "aquapose.engine",
    "aquapose.io",
    "aquapose.training",
    "aquapose.evaluation",
    "aquapose.visualization",
    "aquapose.cli",
    "aquapose.cli_utils",
)

# Known, deliberately-not-fixed exemptions: a `core/`-relative module path
# (posix-separated, relative to `src/aquapose/core/`) mapped to the set of
# forbidden packages it is permitted to import. `aquapose.io` must NEVER
# appear in any entry here -- closing that one edge is this phase's own
# deliverable (QA-05 criterion 5), and exempting it would make the phase
# self-defeating. `test_import_boundary_allowlist_has_no_stale_entries`
# below asserts every entry still corresponds to a real import, so this
# allowlist cannot silently outlive the debt it documents.
_KNOWN_EXCEPTIONS: dict[str, frozenset[str]] = {
    # core/reid/cli.py:9 (module-level) imports aquapose.cli_utils for
    # get_project_dir/resolve_run; core/reid/cli.py:16 (TYPE_CHECKING),
    # :267, and :434 (function-local) import aquapose.training.reid_training.
    # 113.1-CONTEXT.md's "only module-level violation" claim (verified
    # 2026-09-02) was found incomplete during Phase 113.1 planning -- both
    # of these were live on the same date. Carried under D-02's scope
    # fence rather than fixed here. Tracked:
    # .planning/todos/pending/2026-09-02-core-reid-import-boundary-exemptions.md
    "reid/cli.py": frozenset({"aquapose.cli_utils", "aquapose.training"}),
    # core/reid/swap_detector.py:323 (function-local) imports
    # aquapose.training.reid_training. Same exemption class and the same
    # tracking todo as reid/cli.py above.
    "reid/swap_detector.py": frozenset({"aquapose.training"}),
    # core/synthetic.py:25 (TYPE_CHECKING) imports aquapose.engine.config
    # for the SyntheticConfig annotation. Pre-existing, already-documented
    # design decision (see tools/import_boundary_checker.py's own
    # _IB003_ALLOWLIST, which independently allowlists the same pair):
    # SyntheticDataStage receives SyntheticConfig from the engine layer as
    # a constructor argument, and config flows strictly downward
    # (engine -> core), never upward. Annotation-only, guarded by
    # TYPE_CHECKING so it never executes at runtime.
    "synthetic.py": frozenset({"aquapose.engine"}),
}


def test_core_does_not_import_io() -> None:
    """No module under ``core/`` may import ``aquapose.io`` or a submodule.

    This is the phase deliverable (QA-05 criterion 5): the
    ``core/types/frame_source.py`` -> ``aquapose.io.discovery`` edge is
    removed by relocating ``discover_camera_videos`` into ``core/`` rather
    than by hiding the import. Unlike the wider boundary test added
    alongside this one, ``aquapose.io`` carries no allowlist exceptions --
    exempting it here would make the phase self-defeating.
    """
    violations: list[str] = []
    for path in _iter_core_python_files():
        rel = path.relative_to(_REPO_ROOT)
        for lineno, module in _collect_imports(path):
            if module == "aquapose.io" or module.startswith("aquapose.io."):
                violations.append(f"{rel}:{lineno} imports {module!r}")
    assert not violations, "core/ must not import aquapose.io:\n" + "\n".join(
        violations
    )


def test_core_does_not_import_upper_layers() -> None:
    """No ``core/`` module may import a forbidden package, allowlist aside.

    Covers every package in ``_FORBIDDEN_PACKAGES``, consulting
    ``_KNOWN_EXCEPTIONS`` for the small number of deliberately-not-fixed
    violations carried out of Phase 113.1 planning. Reports every
    violation in one assertion message so a single run tells the whole
    story.
    """
    violations: list[str] = []
    for path in _iter_core_python_files():
        rel = path.relative_to(_CORE_ROOT).as_posix()
        allowed = _KNOWN_EXCEPTIONS.get(rel, frozenset())
        for lineno, module in _collect_imports(path):
            hit = _matching_forbidden_package(module)
            if hit is None or hit in allowed:
                continue
            violations.append(f"{rel}:{lineno} imports {module!r} (forbidden: {hit})")
    assert not violations, (
        "core/ must not import upper-layer packages "
        "(allowlist exceptions notwithstanding):\n" + "\n".join(violations)
    )


def test_import_boundary_allowlist_has_no_stale_entries() -> None:
    """Every ``_KNOWN_EXCEPTIONS`` entry must correspond to a live import.

    This is what stops the allowlist from quietly outliving the problem
    it documents: once a module under ``core/reid/`` (or ``synthetic.py``)
    stops importing the package it was exempted for -- because a future
    phase fixes it -- this test goes red and names the stale entry,
    forcing the exemption to be removed in the same change.
    """
    stale: list[str] = []
    for rel, allowed_packages in _KNOWN_EXCEPTIONS.items():
        path = _CORE_ROOT / rel
        if not path.is_file():
            stale.append(f"{rel}: allowlisted file no longer exists")
            continue
        found_packages = {
            hit
            for _, module in _collect_imports(path)
            if (hit := _matching_forbidden_package(module)) is not None
        }
        for package in allowed_packages:
            if package not in found_packages:
                stale.append(
                    f"{rel}: allowlisted for {package!r} but no matching "
                    "import was found -- remove this exemption"
                )
    assert not stale, "Stale _KNOWN_EXCEPTIONS entries found:\n" + "\n".join(stale)
