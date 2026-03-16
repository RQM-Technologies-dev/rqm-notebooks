"""
helpers/notebook_style.py
--------------------------
Notebook styling and display configuration for rqm-notebooks.

Applies consistent matplotlib themes and IPython display settings so every
notebook in the collection looks coherent.  Import this at the top of each
notebook with::

    from helpers.notebook_style import setup_notebook
    setup_notebook()
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Colour palette used across all notebooks
# ---------------------------------------------------------------------------

PALETTE = {
    "primary": "#2563EB",    # blue
    "secondary": "#7C3AED",  # violet
    "accent": "#059669",     # emerald
    "warn": "#D97706",       # amber
    "danger": "#DC2626",     # red
    "neutral": "#6B7280",    # gray
    "bg": "#F9FAFB",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def setup_notebook(
    *,
    style: str = "seaborn-v0_8-whitegrid",
    font_size: int = 12,
    dpi: int = 110,
    inline: bool = True,
) -> None:
    """Apply a consistent style to the current notebook session.

    Parameters
    ----------
    style:
        Matplotlib style name.
    font_size:
        Base font size for all text elements.
    dpi:
        Figure resolution used for inline display.
    inline:
        When *True* (default) the ``%matplotlib inline`` backend is activated
        programmatically if an IPython kernel is running.
    """
    # --- matplotlib style ---
    try:
        plt.style.use(style)
    except OSError:
        plt.style.use("default")

    mpl.rcParams.update(
        {
            "figure.dpi": dpi,
            "font.size": font_size,
            "axes.titlesize": font_size + 1,
            "axes.labelsize": font_size,
            "xtick.labelsize": font_size - 1,
            "ytick.labelsize": font_size - 1,
            "legend.fontsize": font_size - 1,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "lines.linewidth": 1.8,
        }
    )

    # --- IPython inline backend (no-op outside Jupyter) ---
    if inline:
        try:
            from IPython import get_ipython

            ip = get_ipython()
            if ip is not None:
                ip.run_line_magic("matplotlib", "inline")
        except Exception:  # pragma: no cover
            pass


def section_header(title: str, subtitle: str = "") -> None:
    """Print a styled section header as plain text (works in any cell output).

    Parameters
    ----------
    title:
        Main section title.
    subtitle:
        Optional descriptive subtitle shown below the title.
    """
    width = 70
    border = "═" * width
    print(f"\n{border}")
    print(f"  {title}")
    if subtitle:
        print(f"  {subtitle}")
    print(f"{border}\n")
