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
