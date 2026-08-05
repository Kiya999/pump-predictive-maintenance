# baseline.py
"""
Baseline calculator: fit and apply three baseline methods (rolling, hourly,
state-based) with configurable control limits.
"""

import pandas as pd
import numpy as np

from analytics_config import SAMPLING_FREQ_MINUTES

class BaselineCalculator:
    """Fit baseline methods (rolling, hourly, state-based) and compute control limits."""
    def __init__(self, training_signal, training_flow, training_timestamps):
        self.training_signal = training_signal.copy()
        self.training_flow = training_flow.copy() if training_flow is not None else None
        self.training_timestamps = training_timestamps

        self.window_periods = None
        self.hourly_stats = None
        self.state_bins = None
        self.state_stats = None

    def fit_rolling(self, window_hours):
        """Store rolling window size in minutes for later application"""
        self.window_periods = int(window_hours * 60 / SAMPLING_FREQ_MINUTES)

    def fit_hourly(self):
        """Compute mean and std for each hour of day from training data"""
        if self.training_timestamps is None:
            raise ValueError("training_timestamps required for hourly baseline")

        if hasattr(self.training_timestamps, 'dt'):
            hour_values = self.training_timestamps.dt.hour.values
        else:
            hour_values = self.training_timestamps.hour.values

        df = pd.DataFrame({
            "signal": self.training_signal.values,
            "hour":   hour_values,
        })
        self.hourly_stats = df.groupby("hour")["signal"].agg(["mean", "std"])

    def fit_state(self):
        """Partition flow into low/mid/high bins and compute signal stats per state"""
        if self.training_flow is None:
            raise ValueError("training_flow required for state baseline")

        q1 = self.training_flow.quantile(0.33)
        q2 = self.training_flow.quantile(0.67)
        self.state_bins = [0, q1, q2, np.inf]

        states = pd.cut(self.training_flow, bins=self.state_bins, labels=["low", "mid", "high"])
        df = pd.DataFrame({"signal": self.training_signal.values, "state": states})
        self.state_stats = df.groupby("state", observed=False)["signal"].agg(["mean", "std"])

    def apply_rolling(self, full_signal, num_std):
        """Apply rolling mean and std to compute baseline and control limits"""
        if self.window_periods is None:
            raise ValueError("fit_rolling() not called")

        baseline = full_signal.rolling(window=self.window_periods, center=False).mean()
        std_vals = full_signal.rolling(window=self.window_periods, center=False).std()

        upper = baseline + num_std * std_vals
        lower = baseline - num_std * std_vals

        return {"baseline": baseline, "upper": upper, "lower": lower}

    def apply_hourly(self, full_timestamps, full_signal, num_std):
        """Map hourly statistics to signal and compute baseline and control limits."""
        if self.hourly_stats is None:
            raise ValueError("fit_hourly() not called")

        if hasattr(full_timestamps, 'dt'):
            hour_arr = full_timestamps.dt.hour.values
        else:
            hour_arr = full_timestamps.hour.values

        mean_map = self.hourly_stats["mean"].to_dict()
        std_map = self.hourly_stats["std"].to_dict()

        all_hours = set(range(24))
        trained_hours = set(mean_map.keys())
        missing_hours = sorted(all_hours - trained_hours)

        if missing_hours:
            print(f"Warning: hourly baseline missing {len(missing_hours)} hours: {missing_hours}")
            print(f"  Baseline will be NaN for these hours (check training data coverage)")

        baseline_vals = [mean_map.get(h, np.nan) for h in hour_arr]
        std_vals = [std_map.get(h, np.nan) for h in hour_arr]

        baseline = pd.Series(baseline_vals, index=full_signal.index)
        stds     = pd.Series(std_vals,      index=full_signal.index)
        upper = baseline + num_std * stds
        lower = baseline - num_std * stds

        return {"baseline": baseline, "upper": upper, "lower": lower}

    def apply_state(self, full_flow, full_signal, num_std):
        """Map flow state to signal statistics and compute baseline and control limits."""
        if self.state_stats is None:
            raise ValueError("fit_state() not called")

        state_labels = ["low", "mid", "high"]
        states = pd.cut(full_flow, bins=self.state_bins, labels=state_labels)

        mean_map = self.state_stats["mean"].to_dict()
        std_map  = self.state_stats["std"].to_dict()

        baseline_vals = states.map(mean_map).astype(float).values
        std_vals      = states.map(std_map).astype(float).values

        baseline = pd.Series(baseline_vals, index=full_signal.index)
        stds     = pd.Series(std_vals,      index=full_signal.index)
        upper = baseline + num_std * stds
        lower = baseline - num_std * stds

        return {"baseline": baseline, "upper": upper, "lower": lower}

    def debug_summary(self, method_name):
        print(f"  === {method_name.upper()} ===")
        if method_name == "rolling":
            print(f"    Window periods: {self.window_periods}")
        elif method_name == "hourly":
            if self.hourly_stats is not None:
                print(f"    Hourly stats computed for {len(self.hourly_stats)} hours")
                sample_hours = [0, 12, 23]
                for hour in sample_hours:
                    if hour in self.hourly_stats.index:
                        mean_val = self.hourly_stats.loc[hour, 'mean']
                        std_val = self.hourly_stats.loc[hour, 'std']
                        print(f"    Hour {hour}: mean={mean_val:.2f}, std={std_val:.4f}")
                    else:
                        print(f"    Hour {hour}: NOT IN TRAINING DATA")
        elif method_name == "state":
            if self.state_stats is not None:
                print(f"    Flow quantile bins: q1={self.state_bins[1]:.2f}, q2={self.state_bins[2]:.2f}")
                for state in ["low", "mid", "high"]:
                    if state in self.state_stats.index:
                        print(f"    State '{state}': mean={self.state_stats.loc[state, 'mean']:.2f}, std={self.state_stats.loc[state, 'std']:.4f}")