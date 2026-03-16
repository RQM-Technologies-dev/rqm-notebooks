"""
tests/test_notebook_imports.py
-------------------------------
Smoke tests for rqm-notebooks.

These tests verify that:
- key third-party dependencies import correctly
- the helpers package imports correctly
- all notebooks exist and are valid nbformat JSON
"""

from __future__ import annotations

import importlib
import pathlib
import sys

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = REPO_ROOT / "notebooks"
HELPERS_DIR = REPO_ROOT / "helpers"

# Ensure helpers is importable from the repo root
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Dependency import checks
# ---------------------------------------------------------------------------

CORE_DEPS = [
    "numpy",
    "matplotlib",
]

OPTIONAL_DEPS = [
    "qiskit",
    "qiskit_aer",
    "rqm_core",
    "rqm_qiskit",
]


@pytest.mark.parametrize("module_name", CORE_DEPS)
def test_core_dependency_importable(module_name: str) -> None:
    """Core scientific dependencies must be importable."""
    mod = importlib.import_module(module_name)
    assert mod is not None


@pytest.mark.parametrize("module_name", OPTIONAL_DEPS)
def test_optional_dependency_importable(module_name: str) -> None:
    """Optional RQM/Qiskit dependencies: skip gracefully if not installed."""
    pytest.importorskip(module_name)


# ---------------------------------------------------------------------------
# Helpers package
# ---------------------------------------------------------------------------

def test_helpers_plotting_importable() -> None:
    from helpers import plotting  # noqa: F401

    assert hasattr(plotting, "draw_bloch_sphere")
    assert hasattr(plotting, "plot_counts")


def test_helpers_notebook_style_importable() -> None:
    from helpers import notebook_style  # noqa: F401

    assert hasattr(notebook_style, "setup_notebook")
    assert hasattr(notebook_style, "PALETTE")


def test_helpers_display_utils_importable() -> None:
    from helpers import display_utils  # noqa: F401

    assert hasattr(display_utils, "show_matrix")
    assert hasattr(display_utils, "show_state_vector")


def test_helpers_package_importable() -> None:
    import helpers  # noqa: F401

    assert hasattr(helpers, "draw_bloch_sphere")
    assert hasattr(helpers, "setup_notebook")
    assert hasattr(helpers, "show_matrix")


# ---------------------------------------------------------------------------
# Notebook existence and validity
# ---------------------------------------------------------------------------

EXPECTED_NOTEBOOKS = [
    "00_welcome_and_repo_map.ipynb",
    "01_quaternion_intuition.ipynb",
    "02_spinor_to_bloch.ipynb",
    "03_su2_rotations_and_geometry.ipynb",
    "04_rqm_core_as_source_of_truth.ipynb",
    "05_rqm_qiskit_single_qubit_workflows.ipynb",
    "06_simulator_measurements.ipynb",
    "07_state_preparation_and_visual_checks.ipynb",
    "08_gate_composition_as_geometry.ipynb",
    "09_ibm_ready_path.ipynb",
]


@pytest.mark.parametrize("nb_name", EXPECTED_NOTEBOOKS)
def test_notebook_exists(nb_name: str) -> None:
    """Every expected notebook must be present on disk."""
    nb_path = NOTEBOOKS_DIR / nb_name
    assert nb_path.exists(), f"Missing notebook: {nb_path}"


@pytest.mark.parametrize("nb_name", EXPECTED_NOTEBOOKS)
def test_notebook_valid_json(nb_name: str) -> None:
    """Every notebook must be valid JSON and parseable by nbformat."""
    nbformat = pytest.importorskip("nbformat")
    nb_path = NOTEBOOKS_DIR / nb_name
    with nb_path.open("r", encoding="utf-8") as fh:
        nb = nbformat.read(fh, as_version=4)
    assert nb.nbformat == 4
    assert len(nb.cells) > 0, f"Notebook {nb_name} has no cells"


@pytest.mark.parametrize("nb_name", EXPECTED_NOTEBOOKS)
def test_notebook_has_markdown(nb_name: str) -> None:
    """Every notebook should contain at least one markdown cell."""
    nbformat = pytest.importorskip("nbformat")
    nb_path = NOTEBOOKS_DIR / nb_name
    with nb_path.open("r", encoding="utf-8") as fh:
        nb = nbformat.read(fh, as_version=4)
    md_cells = [c for c in nb.cells if c.cell_type == "markdown"]
    assert len(md_cells) >= 1, f"Notebook {nb_name} has no markdown cells"
