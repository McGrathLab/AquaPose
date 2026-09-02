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
