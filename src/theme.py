"""Shared dark chart theme.

The palette matches the companion Power BI dashboard so the Python charts and
the dashboard look like one product. Importing this module applies the theme to
matplotlib/seaborn globally.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

BACKGROUND = "#1b1b1b"
PANEL = "#262626"
BORDER = "#3d3d3d"
GRID = "#333333"
TEXT = "#f2f2f2"
MUTED = "#c9c9c9"
GOLD = "#f2c811"
AMBER = "#e8a33d"
TEAL = "#3fb7c9"
GREEN = "#6fcf97"
RED = "#e4572e"

# Semantic colours reused across charts.
LABEL_COLORS = {
    "Excellent": GREEN,
    "Good": GOLD,
    "Needs Improvement": RED,
}

__all__ = [
    "BACKGROUND",
    "PANEL",
    "BORDER",
    "GRID",
    "TEXT",
    "MUTED",
    "GOLD",
    "AMBER",
    "TEAL",
    "GREEN",
    "RED",
    "LABEL_COLORS",
    "apply_theme",
    "save_figure",
]


def apply_theme() -> None:
    """Apply the dark dashboard theme to the global matplotlib state."""
    sns.set_theme(style="dark")
    plt.rcParams.update(
        {
            "figure.figsize": (11, 5),
            "figure.facecolor": BACKGROUND,
            "savefig.facecolor": BACKGROUND,
            "axes.facecolor": BACKGROUND,
            "axes.edgecolor": BORDER,
            "axes.labelcolor": TEXT,
            "axes.titlecolor": "#ffffff",
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.grid": True,
            "grid.color": GRID,
            "text.color": TEXT,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "legend.facecolor": PANEL,
            "legend.edgecolor": BORDER,
            "font.size": 11,
        }
    )


apply_theme()


def save_figure(fig, filename: str, directory=None) -> Path:
    """Save a figure to the screenshots directory (or ``directory``) as PNG."""
    from .config import SCREENSHOTS_DIR

    target_dir = Path(directory) if directory else SCREENSHOTS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / filename
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BACKGROUND)
    return path
