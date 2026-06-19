# baseline.py
import pandas as pd
import numpy as np

class BaselineCalculator:

    def __init__(self, training_signal, training_flow=None, training_timestamps=None):
        self.training_signal = training_signal.copy()
        self.training_flow = training_flow.copy() if training_flow is not None else None
        self.training_timestamps = training_timestamps

        self.window_periods = None
        self.hourly_stats = None
        self.state_bins = None
        self.state_stats = None

    def fit_rolling(self, window_hours):
        self.window_periods = window_hours * 60

    def fit_hourly(self):
        if self.training_timestamps is None:
            raise ValueError("training_timestamps required for hourly baseline")

        df = pd.DataFrame({
            "signal": self.training_signal.values,
            "hour": self.training_timestamps.dt.hour,
        })
        self.hourly_stats = df.groupby("hour")["signal"].agg(["mean", "std"])

    def fit_state(self):
        if self.training_flow is None:
            raise ValueError("training_flow required for state baseline")

        q1 = self.training_flow.quantile(0.33)
        q2 = self.training_flow.quantile(0.67)
        self.state_bins = [0, q1, q2, np.inf]

        states = pd.cut(self.training_flow, bins=self.state_bins, labels=["low", "mid", "high"])
        df = pd.DataFrame({"signal": self.training_signal.values, "state": states})
        self.state_stats = df.groupby("state", observed=False)["signal"].agg(["mean", "std"])

    def apply_rolling(self, full_signal, num_std=3):
        if self.window_periods is None:
            raise ValueError("fit_rolling() not called")

        baseline = full_signal.rolling(window=self.window_periods, center=False).mean()
        std_vals = full_signal.rolling(window=self.window_periods, center=False).std()

        upper = baseline + num_std * std_vals
        lower = baseline - num_std * std_vals

        return {"baseline": baseline, "upper": upper, "lower": lower,}

    def apply_hourly(self, full_timestamps, full_signal, num_std=3):
        if self.hourly_stats is None:
            raise ValueError("fit_hourly() not called")

        hours = full_timestamps.dt.hour
        baseline = pd.Series(
            [self.hourly_stats.loc[h, "mean"] if h in self.hourly_stats.index else np.nan for h in hours],
            index=full_signal.index
        )
        stds = pd.Series(
            [self.hourly_stats.loc[h, "std"] if h in self.hourly_stats.index else np.nan for h in hours],
            index=full_signal.index
        )

        upper = baseline + num_std * stds
        lower = baseline - num_std * stds

        return {"baseline": baseline, "upper": upper, "lower": lower,}

    def apply_state(self, full_flow, full_signal, num_std=3):
        if self.state_stats is None:
            raise ValueError("fit_state() not called")

        states = pd.cut(full_flow, bins=self.state_bins, labels=["low", "mid", "high"])
        baseline = pd.Series(
            [self.state_stats.loc[s, "mean"] if s in self.state_stats.index else np.nan for s in states],
            index=full_signal.index
        )
        stds = pd.Series(
            [self.state_stats.loc[s, "std"] if s in self.state_stats.index else np.nan for s in states],
            index=full_signal.index
        )

        upper = baseline + num_std * stds
        lower = baseline - num_std * stds

        return {"baseline": baseline, "upper": upper, "lower": lower,}

    def debug_summary(self, method_name):
        print(f"  === {method_name.upper()} ===")
        if method_name == "rolling":
            print(f"    Window periods: {self.window_periods} (24h in 1-min samples)")
        elif method_name == "hourly":
            if self.hourly_stats is not None:
                print(f"    Hourly stats computed for {len(self.hourly_stats)} hours")
                print(f"    Hour 0: mean={self.hourly_stats.loc[0, 'mean']:.2f}, std={self.hourly_stats.loc[0, 'std']:.4f}")
                print(f"    Hour 12: mean={self.hourly_stats.loc[12, 'mean']:.2f}, std={self.hourly_stats.loc[12, 'std']:.4f}")
                print(f"    Hour 23: mean={self.hourly_stats.loc[23, 'mean']:.2f}, std={self.hourly_stats.loc[23, 'std']:.4f}")
        elif method_name == "state":
            if self.state_stats is not None:
                print(f"    Flow quantile bins: q1={self.state_bins[1]:.2f}, q2={self.state_bins[2]:.2f}")
                for state in ["low", "mid", "high"]:
                    if state in self.state_stats.index:
                        print(f"    State '{state}': mean={self.state_stats.loc[state, 'mean']:.2f}, std={self.state_stats.loc[state, 'std']:.4f}")