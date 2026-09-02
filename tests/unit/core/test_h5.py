"""Unit tests for the h5py narrowing helpers require_group / require_dataset."""

from __future__ import annotations

from pathlib import Path

import h5py
import numpy as np
import pytest

from aquapose.core.h5 import require_dataset, require_group


def _make_h5(path: Path) -> Path:
    """Write a small H5 fixture with one nested group and one dataset."""
    with h5py.File(path, "w") as f:
        grp = f.create_group("midlines")
        grp.create_dataset("fish_id", data=np.array([0, 1, 2]))
        nested = grp.create_group("nested")
        nested.create_dataset("value", data=np.array([1.0, 2.0]))
    return path


def test_require_dataset_returns_dataset_identity(tmp_path: Path) -> None:
    """require_dataset on a key that is a Dataset returns it unchanged.

    h5py constructs a fresh Python wrapper object on every ``__getitem__``
    call, so ``is`` identity does not hold between two separate lookups of
    the same key. Equality (which compares the underlying h5py identifier)
    is the correct way to assert "same object, not a copy" here.
    """
    h5_path = _make_h5(tmp_path / "fixture.h5")
    with h5py.File(h5_path, "r") as f:
        grp = f["midlines"]
        assert isinstance(grp, h5py.Group)
        expected = grp["fish_id"]
        result = require_dataset(grp, "fish_id")
        assert result == expected
        assert result.id == expected.id


def test_require_group_returns_group_identity(tmp_path: Path) -> None:
    """require_group on a key that is a Group returns it unchanged.

    See the identity note on ``test_require_dataset_returns_dataset_identity``.
    """
    h5_path = _make_h5(tmp_path / "fixture.h5")
    with h5py.File(h5_path, "r") as f:
        expected = f["midlines"]
        result = require_group(f, "midlines")
        assert result == expected
        assert result.id == expected.id


def test_require_dataset_on_group_raises_type_error(tmp_path: Path) -> None:
    """require_dataset on a key resolving to a Group raises TypeError."""
    h5_path = _make_h5(tmp_path / "fixture.h5")
    with h5py.File(h5_path, "r") as f:
        with pytest.raises(TypeError) as exc_info:
            require_dataset(f, "midlines")
        message = str(exc_info.value)
        assert "midlines" in message
        assert str(h5_path) in message or h5_path.name in message


def test_require_group_on_dataset_raises_type_error(tmp_path: Path) -> None:
    """require_group on a key resolving to a Dataset raises TypeError."""
    h5_path = _make_h5(tmp_path / "fixture.h5")
    with h5py.File(h5_path, "r") as f:
        grp = f["midlines"]
        assert isinstance(grp, h5py.Group)
        with pytest.raises(TypeError) as exc_info:
            require_group(grp, "fish_id")
        message = str(exc_info.value)
        assert "fish_id" in message
        assert str(h5_path) in message or h5_path.name in message


def test_require_dataset_missing_key_raises_key_error(tmp_path: Path) -> None:
    """A missing key propagates h5py's own KeyError, unmodified."""
    h5_path = _make_h5(tmp_path / "fixture.h5")
    with h5py.File(h5_path, "r") as f:
        grp = f["midlines"]
        assert isinstance(grp, h5py.Group)
        with pytest.raises(KeyError):
            require_dataset(grp, "does_not_exist")


def test_require_dataset_resolves_slash_separated_path(tmp_path: Path) -> None:
    """A slash-separated path resolves through nested groups in one call."""
    h5_path = _make_h5(tmp_path / "fixture.h5")
    with h5py.File(h5_path, "r") as f:
        result = require_dataset(f, "midlines/nested/value")
        assert result.shape == (2,)


def test_require_group_resolves_slash_separated_path(tmp_path: Path) -> None:
    """A slash-separated path resolves through nested groups in one call."""
    h5_path = _make_h5(tmp_path / "fixture.h5")
    with h5py.File(h5_path, "r") as f:
        result = require_group(f, "midlines/nested")
        assert isinstance(result, h5py.Group)
