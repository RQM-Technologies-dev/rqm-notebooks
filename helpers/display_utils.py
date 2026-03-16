"""
helpers/display_utils.py
------------------------
Display utility helpers for rqm-notebooks.

Provides convenience wrappers for rendering LaTeX, circuit diagrams, state
summaries, and formatted tables inside Jupyter cells.  All canonical math
objects (Quaternion, Spinor, etc.) come from rqm-core — this module only
formats and displays them.
"""

from __future__ import annotations

from typing import Any

import numpy as np


# ---------------------------------------------------------------------------
# IPython / Jupyter display (graceful fallback outside Jupyter)
# ---------------------------------------------------------------------------

def _display(*args: Any) -> None:
    try:
        from IPython.display import display as _ip_display

        _ip_display(*args)
    except ImportError:
        for obj in args:
            print(obj)


def _html(html: str) -> Any:
    try:
        from IPython.display import HTML

        return HTML(html)
    except ImportError:
        return html


def _latex(src: str) -> Any:
    try:
        from IPython.display import Math

        return Math(src)
    except ImportError:
        return src


def _markdown(src: str) -> Any:
    try:
        from IPython.display import Markdown

        return Markdown(src)
    except ImportError:
        return src


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def show_latex(expr: str) -> None:
    """Render a LaTeX expression inline in a Jupyter cell.

    Parameters
    ----------
    expr:
        Raw LaTeX string (without surrounding ``$``).  Example::

            show_latex(r"H = \\frac{1}{\\sqrt{2}}\\begin{pmatrix}1&1\\\\1&-1\\end{pmatrix}")
    """
    _display(_latex(expr))


def show_matrix(
    matrix: np.ndarray,
    *,
    label: str = "",
    precision: int = 4,
    suppress_small: bool = True,
) -> None:
    """Display a NumPy matrix as a LaTeX pmatrix in Jupyter.

    Parameters
    ----------
    matrix:
        2-D or 1-D NumPy array.
    label:
        Optional LaTeX label prepended to the equals sign, e.g. ``r"H"``.
    precision:
        Number of decimal places.
    suppress_small:
        Replace near-zero entries (< 1e-10) with exact zero before display.
    """
    arr = np.array(matrix, dtype=complex)
    if suppress_small:
        arr = np.where(np.abs(arr) < 1e-10, 0.0 + 0j, arr)

    def _fmt(v: complex) -> str:
        if v.imag == 0:
            return f"{v.real:.{precision}f}"
        if v.real == 0:
            return f"{v.imag:.{precision}f}i"
        sign = "+" if v.imag >= 0 else "-"
        return f"{v.real:.{precision}f}{sign}{abs(v.imag):.{precision}f}i"

    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)

    rows = r" \\ ".join(" & ".join(_fmt(v) for v in row) for row in arr)
    body = r"\begin{pmatrix}" + rows + r"\end{pmatrix}"
    if label:
        body = label + " = " + body
    show_latex(body)


def show_state_vector(
    amplitudes: np.ndarray,
    *,
    basis_labels: list[str] | None = None,
    label: str = r"|\psi\rangle",
    precision: int = 4,
) -> None:
    """Render a state vector as a LaTeX ket expansion.

    Parameters
    ----------
    amplitudes:
        1-D complex array of amplitudes (need not be normalised for display).
    basis_labels:
        Custom ket labels.  Defaults to binary strings (``|0⟩``, ``|1⟩``, …).
    label:
        LHS label.
    precision:
        Decimal places.
    """
    amps = np.asarray(amplitudes, dtype=complex)
    n = len(amps)
    if basis_labels is None:
        bits = int(np.ceil(np.log2(max(n, 2))))
        basis_labels = [f"|{i:0{bits}b}\\rangle" for i in range(n)]

    terms = []
    for amp, ket in zip(amps, basis_labels):
        if abs(amp) < 1e-10:
            continue
        if amp.imag == 0:
            coeff = f"{amp.real:.{precision}f}"
        elif amp.real == 0:
            coeff = f"{amp.imag:.{precision}f}i"
        else:
            sign = "+" if amp.imag >= 0 else "-"
            coeff = f"({amp.real:.{precision}f} {sign} {abs(amp.imag):.{precision}f}i)"
        terms.append(f"{coeff}{ket}")

    rhs = " + ".join(terms) if terms else "0"
    show_latex(label + " = " + rhs)


def show_info_table(rows: list[tuple[str, Any]], *, title: str = "") -> None:
    """Display a two-column HTML table of key→value pairs.

    Parameters
    ----------
    rows:
        List of ``(key, value)`` tuples.
    title:
        Optional table caption.
    """
    header = f"<caption style='font-weight:bold;text-align:left'>{title}</caption>" if title else ""
    body = "".join(
        f"<tr><td style='padding:4px 12px 4px 0;font-weight:600'>{k}</td>"
        f"<td style='padding:4px 0'>{v}</td></tr>"
        for k, v in rows
    )
    html = (
        "<table style='border-collapse:collapse;font-family:monospace;font-size:13px'>"
        + header
        + "<tbody>"
        + body
        + "</tbody></table>"
    )
    _display(_html(html))


def print_section(title: str) -> None:
    """Print a simple text section divider (notebook-friendly).

    Parameters
    ----------
    title:
        Section title to display.
    """
    _display(_markdown(f"### {title}"))


# ---------------------------------------------------------------------------
# Quaternion / complex formatting helpers
# ---------------------------------------------------------------------------

def format_complex_pair(alpha: complex, beta: complex, *, precision: int = 4) -> str:
    """Format a spinor amplitude pair ``(α, β)`` as a readable string.

    Parameters
    ----------
    alpha, beta:
        The two complex amplitudes of a single-qubit state.
    precision:
        Number of decimal places.

    Returns
    -------
    str
        A human-readable string like ``"α = 0.7071, β = 0.7071i"``.

    Example
    -------
    >>> format_complex_pair(1/np.sqrt(2), 1j/np.sqrt(2))
    'α = 0.7071 + 0.0000i,  β = 0.0000 + 0.7071i'
    """

    def _fmt(z: complex) -> str:
        sign = "+" if z.imag >= 0 else "-"
        return f"{z.real:.{precision}f} {sign} {abs(z.imag):.{precision}f}i"

    return f"α = {_fmt(complex(alpha))},  β = {_fmt(complex(beta))}"


def assert_state_close(
    actual: "np.ndarray",
    expected: "np.ndarray",
    *,
    atol: float = 1e-6,
    label: str = "state",
) -> None:
    """Assert that two state vectors are close (up to global phase) and print a summary.

    Compares ``actual`` and ``expected`` up to an overall global phase factor
    so that physically identical states do not raise false failures.

    Parameters
    ----------
    actual:
        The computed state vector (1-D complex array).
    expected:
        The expected state vector (1-D complex array).
    atol:
        Absolute tolerance for each component after phase alignment.
    label:
        Descriptive name used in the printed output.

    Raises
    ------
    AssertionError
        If the states differ by more than ``atol`` after phase alignment.
    """
    actual = np.asarray(actual, dtype=complex)
    expected = np.asarray(expected, dtype=complex)

    if actual.shape != expected.shape:
        raise AssertionError(
            f"{label}: shape mismatch — actual {actual.shape} vs expected {expected.shape}"
        )

    # Align global phase to the component with the largest magnitude
    idx = int(np.argmax(np.abs(expected)))
    if abs(expected[idx]) < 1e-12:
        phase = 1.0 + 0j
    else:
        phase = expected[idx] / actual[idx] if abs(actual[idx]) > 1e-12 else 1.0 + 0j
    aligned = actual * phase

    max_diff = float(np.max(np.abs(aligned - expected)))
    ok = max_diff <= atol
    status = "✓ PASS" if ok else f"✗ FAIL  (max diff = {max_diff:.2e})"
    print(f"{label}: {status}")
    if not ok:
        raise AssertionError(
            f"{label}: states differ by {max_diff:.2e} (tolerance {atol:.2e})"
        )


def show_axis_angle_summary(
    axis: "np.ndarray",
    angle_rad: float,
    *,
    label: str = "",
) -> None:
    """Display an axis-angle rotation summary as a formatted HTML table.

    Parameters
    ----------
    axis:
        Unit rotation axis as a length-3 array-like.
    angle_rad:
        Rotation angle in radians.
    label:
        Optional title for the table (e.g. ``"Hadamard"``).
    """
    axis = np.asarray(axis, dtype=float)
    norm = np.linalg.norm(axis)
    axis_unit = axis / norm if norm > 1e-12 else axis

    import math
    angle_deg = math.degrees(angle_rad)

    half = angle_rad / 2
    w = math.cos(half)
    xyz = math.sin(half) * axis_unit

    rows = [
        ("Axis (nx, ny, nz)", f"({axis_unit[0]:.4f}, {axis_unit[1]:.4f}, {axis_unit[2]:.4f})"),
        ("Angle (radians)", f"{angle_rad:.4f}"),
        ("Angle (degrees)", f"{angle_deg:.2f}°"),
        ("Unit quaternion w", f"{w:.4f}"),
        ("Unit quaternion (x,y,z)", f"({xyz[0]:.4f}, {xyz[1]:.4f}, {xyz[2]:.4f})"),
        ("|q|", f"{math.sqrt(w**2 + float(np.dot(xyz, xyz))):.6f}"),
    ]
    title = f"Axis-Angle Summary{': ' + label if label else ''}"
    show_info_table(rows, title=title)
