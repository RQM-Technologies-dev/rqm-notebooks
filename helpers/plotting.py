"""
helpers/plotting.py
-------------------
Lightweight plotting utilities for rqm-notebooks.

All canonical math (quaternions, spinors, Bloch vectors, SU(2) operations)
comes from rqm-core.  This module only provides display/visualisation helpers.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — registers 3D projection
from mpl_toolkits.mplot3d.proj3d import proj_transform


# ---------------------------------------------------------------------------
# Bloch sphere
# ---------------------------------------------------------------------------

class _Arrow3D(FancyArrowPatch):
    """3-D arrow for Bloch-sphere state vectors."""

    def __init__(self, xs, ys, zs, *args, **kwargs):
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def do_3d_projection(self, renderer=None):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj_transform(xs3d, ys3d, zs3d, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        return min(zs)


def draw_bloch_sphere(
    ax: plt.Axes | None = None,
    *,
    vectors: list[tuple[np.ndarray, str, str]] | None = None,
    title: str = "Bloch Sphere",
    alpha: float = 0.08,
) -> plt.Axes:
    """Draw a Bloch sphere with optional state vectors overlaid.

    Parameters
    ----------
    ax:
        Existing 3-D axes to draw on.  A new figure/axes is created when
        ``None`` (default).
    vectors:
        List of ``(xyz, label, colour)`` tuples.  *xyz* is a length-3
        array-like with the Bloch vector components (should be unit length).
    title:
        Axes title.
    alpha:
        Transparency of the sphere surface.

    Returns
    -------
    plt.Axes
        The axes object so callers can further customise the plot.
    """
    if ax is None:
        fig = plt.figure(figsize=(5, 5))
        ax = fig.add_subplot(111, projection="3d")

    # --- sphere surface ---
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 40)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_surface(x, y, z, color="lightblue", alpha=alpha, linewidth=0)

    # --- axes lines ---
    ax.plot([-1.2, 1.2], [0, 0], [0, 0], "k-", lw=0.6, alpha=0.4)
    ax.plot([0, 0], [-1.2, 1.2], [0, 0], "k-", lw=0.6, alpha=0.4)
    ax.plot([0, 0], [0, 0], [-1.3, 1.3], "k-", lw=0.6, alpha=0.4)

    # --- pole labels ---
    ax.text(0, 0, 1.35, r"$|0\rangle$", ha="center", fontsize=11)
    ax.text(0, 0, -1.45, r"$|1\rangle$", ha="center", fontsize=11)
    ax.text(1.35, 0, 0, r"$|+\rangle$", ha="center", fontsize=9, color="gray")
    ax.text(0, 1.35, 0, r"$|+i\rangle$", ha="center", fontsize=9, color="gray")

    # --- state vectors ---
    for xyz, label, colour in (vectors or []):
        xyz = np.asarray(xyz, dtype=float)
        arrow = _Arrow3D(
            [0, xyz[0]], [0, xyz[1]], [0, xyz[2]],
            mutation_scale=15,
            lw=2,
            arrowstyle="-|>",
            color=colour,
        )
        ax.add_artist(arrow)
        offset = xyz * 1.18
        ax.text(*offset, label, color=colour, fontsize=10, ha="center")

    ax.set_title(title, pad=10)
    ax.set_box_aspect([1, 1, 1])
    ax.axis("off")
    return ax


# ---------------------------------------------------------------------------
# Measurement bar chart
# ---------------------------------------------------------------------------

def plot_counts(
    counts: dict[str, int],
    *,
    title: str = "Measurement Results",
    colour: str = "steelblue",
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """Bar chart of Qiskit-style measurement count dictionaries.

    Parameters
    ----------
    counts:
        Mapping of bitstring → count, e.g. ``{"0": 512, "1": 512}``.
    title:
        Plot title.
    colour:
        Bar colour.
    ax:
        Existing axes to draw on.

    Returns
    -------
    plt.Axes
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(max(3, len(counts) * 0.6 + 1), 3))

    labels = sorted(counts.keys())
    values = [counts[k] for k in labels]
    total = sum(values) or 1

    bars = ax.bar(labels, values, color=colour, edgecolor="white", linewidth=0.6)
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + total * 0.01,
            f"{val / total:.1%}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_xlabel("Bitstring", fontsize=10)
    ax.set_ylabel("Counts", fontsize=10)
    ax.set_title(title, fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    return ax


# ---------------------------------------------------------------------------
# Rotation visualisation
# ---------------------------------------------------------------------------

def plot_rotation_path(
    path: np.ndarray,
    *,
    start_colour: str = "green",
    end_colour: str = "red",
    path_colour: str = "cornflowerblue",
    ax: plt.Axes | None = None,
    title: str = "State Rotation on Bloch Sphere",
) -> plt.Axes:
    """Plot a sequence of Bloch vectors showing a rotation path.

    Parameters
    ----------
    path:
        Array of shape ``(N, 3)`` with N Bloch vectors along the rotation.
    start_colour, end_colour, path_colour:
        Colours for the start point, end point, and path line.
    ax:
        Existing 3-D axes.
    title:
        Plot title.

    Returns
    -------
    plt.Axes
    """
    path = np.asarray(path, dtype=float)
    vectors = [
        (path[0], "start", start_colour),
        (path[-1], "end", end_colour),
    ]
    ax = draw_bloch_sphere(ax=ax, vectors=vectors, title=title)
    ax.plot(path[:, 0], path[:, 1], path[:, 2], "-", color=path_colour, lw=1.5, alpha=0.8)
    return ax


# ---------------------------------------------------------------------------
# Quaternion component visualisation
# ---------------------------------------------------------------------------

def plot_quaternion_components(
    quaternions: list[tuple[float, float, float, float]],
    *,
    labels: list[str] | None = None,
    title: str = "Quaternion Components",
    figsize: tuple[float, float] = (9, 3),
) -> plt.Figure:
    """Bar chart showing the (w, x, y, z) components of one or more quaternions.

    Parameters
    ----------
    quaternions:
        List of ``(w, x, y, z)`` tuples.
    labels:
        Display names for each quaternion.  Defaults to ``q0``, ``q1``, …
    title:
        Figure title.
    figsize:
        Figure size in inches.

    Returns
    -------
    plt.Figure
    """
    quaternions = [tuple(float(v) for v in q) for q in quaternions]
    n = len(quaternions)
    if labels is None:
        labels = [f"q{i}" for i in range(n)]

    component_names = ["w (scalar)", "x", "y", "z"]
    colours = ["#2563EB", "#7C3AED", "#059669", "#D97706"]
    x = np.arange(4)
    width = 0.7 / max(n, 1)

    fig, ax = plt.subplots(figsize=figsize)
    for i, (q, label) in enumerate(zip(quaternions, labels)):
        offset = (i - (n - 1) / 2) * width
        bars = ax.bar(x + offset, q, width, label=label, color=colours[i % len(colours)],
                      alpha=0.85, edgecolor="white", linewidth=0.5)
        for bar, val in zip(bars, q):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + (0.02 if val >= 0 else -0.06),
                f"{val:.3f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.axhline(0, color="black", linewidth=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(component_names)
    ax.set_ylabel("Value")
    ax.set_title(title)
    ax.set_ylim(-1.2, 1.4)
    if n > 1:
        ax.legend(loc="upper right", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    return fig


# ---------------------------------------------------------------------------
# Bloch vector display (single-vector shorthand)
# ---------------------------------------------------------------------------

def plot_bloch_like_vector(
    xyz: np.ndarray,
    *,
    label: str = r"$|\psi\rangle$",
    colour: str = "crimson",
    title: str = "Bloch Sphere",
) -> plt.Axes:
    """Plot a single Bloch vector on a standalone sphere.

    This is a convenience shorthand for ``draw_bloch_sphere`` when you only
    need to display one state quickly.

    Parameters
    ----------
    xyz:
        Length-3 array-like with the Bloch vector (should be unit length).
    label:
        Label for the vector.
    colour:
        Arrow colour.
    title:
        Axes title.

    Returns
    -------
    plt.Axes
    """
    fig = plt.figure(figsize=(4, 4))
    ax = fig.add_subplot(111, projection="3d")
    return draw_bloch_sphere(ax=ax, vectors=[(np.asarray(xyz), label, colour)], title=title)
