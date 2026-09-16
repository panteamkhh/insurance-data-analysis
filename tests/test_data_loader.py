"""Tests for the raw-data loader."""

import pandas as pd
import pytest

from src.data_loader import REQUIRED_COLUMNS, load_data


def test_load_data_returns_expected_columns(tmp_path):
    path = tmp_path / "data.csv"
    pd.DataFrame({column: [1] for column in REQUIRED_COLUMNS}).to_csv(path, index=False)

    result = load_data(path)

    assert list(result.columns) == REQUIRED_COLUMNS


def test_load_data_ignores_extra_columns(tmp_path):
    path = tmp_path / "data.csv"
    frame = pd.DataFrame({column: [1] for column in REQUIRED_COLUMNS})
    frame["Extra"] = "ignore me"
    frame.to_csv(path, index=False)

    result = load_data(path)

    assert "Extra" not in result.columns


def test_load_data_raises_on_missing_column(tmp_path):
    path = tmp_path / "data.csv"
    pd.DataFrame({"PolicyNumber": ["P1"]}).to_csv(path, index=False)

    with pytest.raises(ValueError, match="Missing required column"):
        load_data(path)


def test_project_data_loads():
    """The bundled dataset must load and satisfy the schema."""
    df = load_data()
    assert len(df) > 0
    assert list(df.columns) == REQUIRED_COLUMNS


def test_load_feedback_returns_expected_columns():
    from src.data_loader import FEEDBACK_COLUMNS, load_feedback

    df = load_feedback()
    assert list(df.columns) == FEEDBACK_COLUMNS
    assert len(df) > 0
    assert df["Feedback"].str.len().gt(0).all()


def test_load_feedback_raises_on_missing_column(tmp_path):
    from src.data_loader import load_feedback

    path = tmp_path / "feedback.csv"
    pd.DataFrame({"Customer Name": ["A"]}).to_csv(path, index=False)

    with pytest.raises(ValueError, match="Missing required column"):
        load_feedback(path)
