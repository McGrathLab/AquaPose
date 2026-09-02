"""Typed h5py narrowing helpers — the canonical entry point for h5py reads.

``h5py.Group.__getitem__`` (and by inheritance ``h5py.File.__getitem__``)
returns the union ``Group | Dataset | Datatype``, so every subscript read
loses static type information about which concrete kind of h5py object was
retrieved. This module provides two narrowing functions that perform an
explicit runtime check and raise a real exception on mismatch, rather than
relying on a bare ``assert`` (stripped under ``python -O``, per the
project's typecheck-backlog decisions).

This module lives under ``core/`` — not ``io/`` or ``evaluation/`` — because
``core/`` may only import stdlib and third-party packages plus other
``core/`` internals (enforced by ``tests/unit/core/test_import_boundary.py``),
which makes it the only placement importable from ``core/``, ``evaluation/``
and ``training/`` alike. It is the canonical entry point for h5py reads
across all three of those layers.
"""

from __future__ import annotations

import h5py

__all__ = ["require_dataset", "require_group"]


def require_group(parent: h5py.Group, key: str) -> h5py.Group:
    """Return ``parent[key]`` narrowed to :class:`h5py.Group`.

    Args:
        parent: An open ``h5py.Group`` (an ``h5py.File`` qualifies, since
            ``File`` subclasses ``Group``) to read from. ``key`` may be a
            slash-separated path, which h5py resolves natively through
            nested groups in a single call.
        key: The key or slash-separated path to resolve within ``parent``.

    Returns:
        The resolved object, narrowed to ``h5py.Group``.

    Raises:
        KeyError: If ``key`` does not exist in ``parent`` — propagated
            unchanged from h5py, not swallowed or rewrapped.
        TypeError: If the object at ``key`` exists but is not a
            ``h5py.Group`` (e.g. it is a ``Dataset`` or ``Datatype``).
    """
    obj = parent[key]
    if not isinstance(obj, h5py.Group):
        raise TypeError(
            f"Expected {key!r} to be an h5py.Group in "
            f"{parent.file.filename!r}, found {type(obj).__name__} instead."
        )
    return obj


def require_dataset(parent: h5py.Group, key: str) -> h5py.Dataset:
    """Return ``parent[key]`` narrowed to :class:`h5py.Dataset`.

    Args:
        parent: An open ``h5py.Group`` (an ``h5py.File`` qualifies, since
            ``File`` subclasses ``Group``) to read from. ``key`` may be a
            slash-separated path, which h5py resolves natively through
            nested groups in a single call.
        key: The key or slash-separated path to resolve within ``parent``.

    Returns:
        The resolved object, narrowed to ``h5py.Dataset``.

    Raises:
        KeyError: If ``key`` does not exist in ``parent`` — propagated
            unchanged from h5py, not swallowed or rewrapped.
        TypeError: If the object at ``key`` exists but is not a
            ``h5py.Dataset`` (e.g. it is a ``Group`` or ``Datatype``).
    """
    obj = parent[key]
    if not isinstance(obj, h5py.Dataset):
        raise TypeError(
            f"Expected {key!r} to be an h5py.Dataset in "
            f"{parent.file.filename!r}, found {type(obj).__name__} instead."
        )
    return obj
