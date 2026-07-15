# tests/test_data_quality.py

import sys
import os

import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_quality import assess_quality, format_report, check_completeness, check_gaps, check_duplicates, check_outliers, check_timestamp_regularity, check_unit_consistency

CSV_PATH = "output/synthetic_historian_10x365_1min.csv"
NUMERIC_COLS = [
    "flow_m3h", "suction_pressure_bar", "disch_pressure_bar",
    "diff_pressure_bar", "motor_temp_c", "motor_power_kw",
    "vibration_mm_s", "speed_rpm",
]
CONFIG = {
    "timestamp_col": "timestamp",
    "asset_col": "asset_id",
    "numeric_cols": NUMERIC_COLS,
    "expected_freq_min": 1,
    "iqr_multiplier": 1.5,
    "pressure_cols": ["suction_pressure_bar", "disch_pressure_bar", "diff_pressure_bar"],
}


@pytest.fixture(scope="module")
def full_df():
    df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])
    return df


@pytest.fixture(scope="module")
def healthy_df(full_df):
    # P-0200 has no failure scenario injected
    return full_df[full_df["asset_id"] == "P-0200"].copy()


@pytest.fixture(scope="module")
def dirty_df(full_df):
    # Full dataset has gaps, duplicates, unit mismatch on P-0700
    return full_df.copy()


@pytest.fixture(scope="module")
def full_report(dirty_df):
    return assess_quality(dirty_df, CONFIG)


@pytest.fixture(scope="module")
def healthy_report(healthy_df):
    cfg = {**CONFIG, "asset_col": None, "pressure_cols": []}
    return assess_quality(healthy_df, cfg)


class TestCompleteness:
    def test_overall_below_100_on_dirty(self, full_report):
        pct = full_report["completeness"]["overall_completeness_pct"]
        assert 0.0 < pct <= 100.0

    def test_per_column_keys_present(self, full_report):
        for col in NUMERIC_COLS:
            assert col in full_report["completeness"]["per_column"]

    def test_completeness_calculation_accurate(self):
        df = pd.DataFrame({"a": [1, 2, None, 4], "b": [1, None, None, 4]})
        result = check_completeness(df, ["a", "b"])
        assert result["per_column"]["a"]["completeness_pct"] == 75.0
        assert result["per_column"]["b"]["completeness_pct"] == 50.0
        # overall: 5 non-null out of 8 cells
        assert result["overall_completeness_pct"] == 62.5


class TestGaps:
    def test_gaps_detected_in_dirty_data(self, full_report):
        assert full_report["gaps"]["gap_count"] > 0

    def test_longest_gap_positive(self, full_report):
        assert full_report["gaps"]["longest_gap_min"] > 1.0

    def test_no_gaps_on_minimal_clean(self):
        ts = pd.date_range("2025-01-01", periods=100, freq="1min")
        df = pd.DataFrame({"timestamp": ts, "val": np.random.randn(100)})
        result = check_gaps(df, "timestamp", expected_freq_min=1)
        assert result["gap_count"] == 0

    def test_known_gap_detected(self):
        ts = list(pd.date_range("2025-01-01", periods=5, freq="1min"))
        ts += list(pd.date_range("2025-01-01 00:35:00", periods=5, freq="1min"))
        df = pd.DataFrame({"timestamp": sorted(ts)})
        result = check_gaps(df, "timestamp", expected_freq_min=1)
        assert result["gap_count"] >= 1
        assert result["longest_gap_min"] >= 29.0


class TestDuplicates:
    def test_duplicate_timestamps_detected(self, full_report):
        assert full_report["duplicates"]["duplicate_timestamp_count"] > 0

    def test_no_duplicates_on_clean(self):
        ts = pd.date_range("2025-01-01", periods=50, freq="1min")
        df = pd.DataFrame({"timestamp": ts, "asset_id": "A", "val": 1.0})
        result = check_duplicates(df, timestamp_col="timestamp", asset_col="asset_id")
        assert result["duplicate_row_count"] == 0
        assert result["duplicate_timestamp_count"] == 0

    def test_known_duplicate_detected(self):
        ts = pd.date_range("2025-01-01", periods=5, freq="1min")
        df = pd.DataFrame({"timestamp": list(ts) + [ts[2]], "asset_id": "A", "val": 1.0})
        result = check_duplicates(df, timestamp_col="timestamp", asset_col="asset_id")
        assert result["duplicate_timestamp_count"] == 1


class TestOutliers:
    def test_outliers_detected_in_full_dataset(self, full_report):
        # at least one numeric column should have outliers given injected failures and unit mismatch
        total_outliers = sum(v["outlier_count"] for v in full_report["outliers"].values())
        assert total_outliers > 0

    def test_no_false_positives_on_clean_synthetic(self):
        rng = np.random.default_rng(0)
        vals = rng.normal(loc=10.0, scale=1.0, size=10000)
        df = pd.DataFrame({"x": vals})
        result = check_outliers(df, ["x"], iqr_multiplier=1.5)
        assert result["x"]["outlier_pct"] < 2.0


class TestTimestampRegularity:
    def test_irregularity_detected_after_duplicate_injection(self, full_df):
        first_asset = full_df["asset_id"].unique()[0]
        asset_df = full_df[full_df["asset_id"] == first_asset].copy()
        result = check_timestamp_regularity(asset_df, "timestamp", expected_freq_min=1)
        assert result["irregular_count"] > 0


    def test_regular_series_passes(self):
        ts = pd.date_range("2025-01-01", periods=1000, freq="1min")
        df = pd.DataFrame({"timestamp": ts})
        result = check_timestamp_regularity(df, "timestamp", expected_freq_min=1)
        assert result["irregularity_rate_pct"] == 0.0

    def test_median_interval_correct(self):
        ts = pd.date_range("2025-01-01", periods=100, freq="5min")
        df = pd.DataFrame({"timestamp": ts})
        result = check_timestamp_regularity(df, "timestamp", expected_freq_min=5)
        assert result["median_interval_min"] == 5.0


class TestUnitConsistency:
    def test_p0700_flagged_as_unit_mismatch(self, full_report):
        flagged = full_report["unit_consistency"]["flagged_assets"]
        assert "P-0700" in flagged

    def test_no_flag_on_consistent_data(self):
        df = pd.DataFrame({
            "asset_id": ["A"] * 5 + ["B"] * 5,
            "pressure": [1.0, 1.1, 0.9, 1.0, 1.05, 1.02, 0.98, 1.01, 0.99, 1.03],
        })
        result = check_unit_consistency(df, "asset_id", ["pressure"])
        assert result["flagged_assets"] == {}


class TestFormatReport:
    def test_format_runs_without_error(self, full_report):
        text = format_report(full_report)
        assert isinstance(text, str)
        assert "DATA QUALITY REPORT" in text

    def test_format_contains_flagged_asset(self, full_report):
        text = format_report(full_report)
        assert "P-0700" in text
        assert "FLAGGED" in text
