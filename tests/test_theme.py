"""Tests for the shared chart theme helpers."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from src import theme


def test_apply_theme_sets_dark_background():
    theme.apply_theme()
    assert plt.rcParams["figure.facecolor"] == theme.BACKGROUND
    assert plt.rcParams["axes.facecolor"] == theme.BACKGROUND
    assert plt.rcParams["savefig.facecolor"] == theme.BACKGROUND


def test_label_colors_cover_every_label():
    assert set(theme.LABEL_COLORS) == {"Excellent", "Good", "Needs Improvement"}


def test_save_figure_writes_png(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [1, 0])

    path = theme.save_figure(fig, "chart.png", directory=tmp_path)

    assert path.exists()
    assert path.suffix == ".png"
    assert path.stat().st_size > 0
    plt.close(fig)


def test_save_figure_creates_directory(tmp_path):
    target = tmp_path / "nested" / "dir"
    fig, _ = plt.subplots()

    path = theme.save_figure(fig, "chart.png", directory=target)

    assert target.is_dir()
    assert path.exists()
    plt.close(fig)
