# tests/test_historian_generator.py

import sys
import os
import pytest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from historian_generator import HistorianConfig, SyntheticHistorian
from validate_synthetic_data import welch_ttest


@pytest.fixture(scope="module")
def small_config():
    return HistorianConfig(
        num_assets=2,
        period_days=30,
        freq_min=10,
        noise_level=0.02,
        drift_rate=0.001,
        season_amp=0.3,
        seed=42,
        failure_scenarios=[
            {"scenario": "bearing", "asset_id": "P-0100", "start_day": 10,
             "ramp_days": 15, "final_severity": 3.0},
            {"scenario": "cavitation", "asset_id": "P-0200", "start_day": 15,
             "ramp_days": 10, "final_severity": 2.5},
        ],
        gap_fraction=0.01,
        duplicate_per_asset=2,
        unit_mismatch_asset="P-0200"
    )


@pytest.fixture(scope="module")
def generator(small_config):
    return SyntheticHistorian(small_config)


@pytest.fixture(scope="module")
def df(generator):
    return generator.generate_all()


class TestHistorianConfig:
    def test_default_config(self):
        cfg = HistorianConfig()
        assert cfg.num_assets == 10
        assert cfg.period_days == 365
        assert cfg.freq_min == 1
        assert 0 <= cfg.noise_level <= 0.5

    def test_assertions_fail(self):
        with pytest.raises(AssertionError):
            HistorianConfig(num_assets=0)
        with pytest.raises(AssertionError):
            HistorianConfig(noise_level=0.6)
        with pytest.raises(AssertionError):
            HistorianConfig(drift_rate=0.2)

    def test_time_index_length(self, small_config):
        expected = small_config.period_days * 24 * 60 // small_config.freq_min
        assert len(small_config.time_index) == expected

    def test_asset_assignments(self, generator):
        ids = [a["asset_id"] for a in generator.assets]
        assert ids == ["P-0100", "P-0200"]


class TestOutputStructure:
    def test_columns_exist(self, df):
        expected = ["timestamp", "asset_id", "area", "pump_model",
                    "flow_m3h", "suction_pressure_bar", "disch_pressure_bar",
                    "diff_pressure_bar", "motor_temp_c", "motor_power_kw",
                    "vibration_mm_s", "speed_rpm", "failure_type"]
        for col in expected:
            assert col in df.columns, f"Missing column: {col}"

    def test_row_count_approx(self, df, small_config):
        nominal = small_config.num_assets * small_config.n_samples
        assert len(df) <= nominal * 1.05
        assert len(df) >= nominal * 0.9

    def test_flow_non_negative(self, df):
        assert (df["flow_m3h"] >= 0).all()

    def test_temp_limits(self, df):
        assert df["motor_temp_c"].min() >= 15
        assert df["motor_temp_c"].max() <= 120

    def test_vibration_limits(self, df):
        assert df["vibration_mm_s"].min() >= 0.01
        assert df["vibration_mm_s"].max() <= 2.0

    def test_speed_limits(self, df):
        for aid in df["asset_id"].unique():
            sub = df[df["asset_id"] == aid]
            nominal = sub["speed_rpm"].median()
            assert (sub["speed_rpm"] >= nominal * 0.95).all()
            assert (sub["speed_rpm"] <= nominal * 1.05).all()

    def test_pressure_order(self, df):
        normal = df[df["asset_id"] != "P-0200"]
        assert (normal["disch_pressure_bar"] > normal["suction_pressure_bar"]).all()

    def test_failure_type_column(self, df):
        assert "failure_type" in df.columns
        types = df["failure_type"].unique()
        assert "none" in types
        assert "bearing" in types
        assert "cavitation" in types


class TestFailureScenarios:
    def test_bearing_vibration_increase(self, df):
        asset = df[df["asset_id"] == "P-0100"].copy()
        asset["days"] = (asset["timestamp"] - asset["timestamp"].min()).dt.total_seconds() / 86400
        before = asset[asset["days"] < 10]["vibration_mm_s"]
        after = asset[asset["days"] >= 10]["vibration_mm_s"]
        assert len(before) > 0 and len(after) > 0
        diff, t_stat, df_w, p_val, m1, m2, s1, s2, n1, n2 = welch_ttest(before, after)
        assert m2 > m1
        assert p_val < 0.05

    def test_bearing_temp_delayed_rise(self, df):
        asset = df[df["asset_id"] == "P-0100"].copy()
        asset["days"] = (asset["timestamp"] - asset["timestamp"].min()).dt.total_seconds() / 86400
        baseline = asset[asset["days"] < 10]["motor_temp_c"]
        mean_before = baseline.mean() if len(baseline) > 0 else 0
        early_end = 10 + 0.6 * 15  # day 19
        before_rise = 10 + 5       # day 15
        early = asset[(asset["days"] >= 10) & (asset["days"] < before_rise)]["motor_temp_c"]
        late  = asset[asset["days"] >= early_end]["motor_temp_c"]

        if len(early) > 0 and len(baseline) > 0:
            # Allow +10 for natural variation
            assert early.mean() < mean_before + 10
        if len(late) > 0 and len(baseline) > 0:
            # Temperature should be > baseline after 60% ramp
            assert late.mean() > mean_before + 3

    def test_cavitation_diff_pressure_variance(self, df):
        asset = df[df["asset_id"] == "P-0200"].copy()
        asset["days"] = (asset["timestamp"] - asset["timestamp"].min()).dt.total_seconds() / 86400
        before = asset[asset["days"] < 15]["diff_pressure_bar"]
        after  = asset[asset["days"] >= 15]["diff_pressure_bar"]

        before_mad = np.abs(before - before.median()).max()
        after_mad  = np.abs(after - after.median()).max()
        assert after_mad > before_mad, "Cavitation should produce larger extreme deviations"


class TestDataQuality:
    def test_duplicate_timestamps(self, df, small_config):
        # Shifted timestamps create near-duplicates (per design: 30-120s)
        for aid in df["asset_id"].unique():
            sub = df[df["asset_id"] == aid].sort_values("timestamp")
            time_diff = sub["timestamp"].diff().dt.total_seconds().abs()
            near_dup = (time_diff < 120).sum()
            assert near_dup >= small_config.duplicate_per_asset

    def test_unit_mismatch(self, df):
        asset = df[df["asset_id"] == "P-0200"]
        assert asset["suction_pressure_bar"].median() > 10
        normal = df[df["asset_id"] == "P-0100"]
        assert normal["suction_pressure_bar"].median() < 5


class TestCorrelationSigns:
    def test_flow_vs_dp_negative(self, df):
        sub = df[df["asset_id"] == "P-0100"]
        corr = sub["flow_m3h"].corr(sub["diff_pressure_bar"])
        assert corr < 0

    def test_flow_vs_power_positive(self, df):
        sub = df[df["asset_id"] == "P-0100"]
        corr = sub["flow_m3h"].corr(sub["motor_power_kw"])
        assert corr > 0

    def test_power_vs_temp_positive(self, df):
        sub = df[df["asset_id"] == "P-0100"]
        corr = sub["motor_power_kw"].corr(sub["motor_temp_c"])
        assert corr > 0