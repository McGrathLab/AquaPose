"""Sphinx configuration for project documentation."""

import sys
import tomllib
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _package_version
from pathlib import Path

_ROOT = Path(__file__).parent.parent

# Add project source to path for autodoc
sys.path.insert(0, str(_ROOT / "src"))


def _resolve_release() -> str:
    """Return the project version, preferring installed metadata.

    The docs environment is detached (see pyproject.toml), so aquapose is
    usually not installed; fall back to reading pyproject.toml directly.
    """
    try:
        return _package_version("aquapose")
    except PackageNotFoundError:
        pass
    try:
        with (_ROOT / "pyproject.toml").open("rb") as fh:
            return tomllib.load(fh)["project"]["version"]
    except (OSError, KeyError, tomllib.TOMLDecodeError):
        return "0.0.0"


# Project information
project = "Aquapose"
copyright = (
    "2026, Tucker Lancaster and the McGrath Lab at the Georgia Institute of Technology"
)
author = "Tucker Lancaster"
release = _resolve_release()
# `version` must be a string: Sphinx reads module-level names in conf.py as
# config values, so leaving the imported function bound here breaks the
# inventory dump.
version = ".".join(release.split(".")[:2])

# Extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_design",
    "nbsphinx",
    "sphinxcontrib.mermaid",
    "sphinx_click.ext",
]

# Templates and static files
templates_path = []
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

# nbsphinx configuration
nbsphinx_execute = "never"  # Use committed outputs, don't re-execute
nbsphinx_allow_errors = False
nbsphinx_requirejs_path = ""  # Avoid RequireJS conflicts

# HTML output
html_theme = "furo"
html_title = "Aquapose"
html_static_path = []

# Furo theme options
html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
}

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# MyST parser configuration
myst_enable_extensions = [
    "colon_fence",
    "dollarmath",
]

# Napoleon configuration
napoleon_google_docstring = True
napoleon_numpy_docstring = False
# Render "Attributes:" sections as :ivar: fields on the class. Without this,
# napoleon emits standalone attribute directives that collide with the
# dataclass fields picked up by :undoc-members:.
napoleon_use_ivar = True

# Autodoc configuration
autodoc_member_order = "bysource"
autodoc_typehints = "description"
# Suppress cross-reference ambiguity warnings for re-exported symbols.
# Each public package re-exports its submodule symbols in __init__.py, so
# Sphinx finds two valid targets for the same class (one from the __init__
# automodule and one from the submodule automodule). This is the standard
# Sphinx mechanism for exactly this situation and does not relax -W.
suppress_warnings = ["ref.python"]
# Heavy runtime dependencies are not installed in the docs environment; autodoc
# only needs to import the modules, not execute them.
autodoc_mock_imports = [
    "aquacal",
    "boxmot",
    "click",
    "cv2",
    "h5py",
    "igraph",
    "leidenalg",
    "loguru",
    "matplotlib",
    "plotly",
    "PIL",
    "pycocotools",
    "pytorch_metric_learning",
    "scipy",
    "shapely",
    "skimage",
    "sklearn",
    "timm",
    "torch",
    "torchvision",
    "ultralytics",
    "yaml",
]
