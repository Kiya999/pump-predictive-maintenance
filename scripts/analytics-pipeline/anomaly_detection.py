# anomaly_detection.py
import pandas as pd
import numpy as np


class AnomalyDetector:

    def __init__(self, baseline_results):
        self.baseline = baseline_results["baseline"]
        self.upper = baseline_results["upper"]
        self.lower = baseline_results["lower"]
        self.std = (self.upper - self.baseline) / 3.0 # inherited from baseline (num_std=3)

    def zscore(self, signal, threshold):
        deviation = (signal - self.baseline) / (self.std + 1e-8)
        flag = np.abs(deviation) > threshold

        return {
            "flag": pd.Series(flag, index=signal.index),
            "severity": pd.Series(np.abs(deviation), index=signal.index),
        }

    def iqr(self, signal, window_periods, multiplier):
        q1_baseline = self.baseline.rolling(window=window_periods, center=False).quantile(0.25)
        q3_baseline = self.baseline.rolling(window=window_periods, center=False).quantile(0.75)
        iqr_baseline = q3_baseline - q1_baseline

        lower_fence = q1_baseline - multiplier * iqr_baseline
        upper_fence = q3_baseline + multiplier * iqr_baseline

        flag = (signal < lower_fence) | (signal > upper_fence)

        severity = np.zeros(len(signal))
        for i in range(len(signal)):
            std_val = self.std.iloc[i] if self.std.iloc[i] > 0 else 1.0
            severity[i] = np.abs(signal.iloc[i] - self.baseline.iloc[i]) / (std_val + 1e-8)

        return {
            "flag": pd.Series(flag.values, index=signal.index),
            "severity": pd.Series(severity, index=signal.index),
        }

    def moving_average(self, signal, window_periods, threshold):
        ma = signal.rolling(window=window_periods, center=False).mean()
        deviation = (ma - self.baseline) / (self.std + 1e-8)
        flag = np.abs(deviation) > threshold

        return {
            "flag": pd.Series(flag.values, index=signal.index),
            "severity": pd.Series(np.abs(deviation).values, index=signal.index),
        }

    @staticmethod
    def persistent_detection(flag_series, min_duration_hours=6, persistence_threshold=0.7, sampling_freq_minutes=1):
        if not isinstance(flag_series, pd.Series):
            flag_series = pd.Series(flag_series)

        window_size = int(min_duration_hours * 60 / sampling_freq_minutes)
        if window_size < 1:
            window_size = 1

        if len(flag_series) < window_size:
            return None, []

        persistence_windows = []

        for i in range(len(flag_series) - window_size + 1):
            window = flag_series.iloc[i:i+window_size]
            persistence = window.sum() / len(window)

            if persistence >= persistence_threshold:
                persistence_windows.append((i, i+window_size, float(persistence)))

        if len(persistence_windows) == 0:
            return None, []

        first_persistent_idx = persistence_windows[0][0]
        return first_persistent_idx, persistence_windows

    @staticmethod
    def lead_time_hours(first_flag_idx, failure_idx, sampling_freq_minutes=1):
        if first_flag_idx is None or first_flag_idx >= failure_idx:
            return None

        minutes_before = (failure_idx - first_flag_idx) * sampling_freq_minutes
        hours_before = minutes_before / 60.0
        return hours_before

    @staticmethod
    def detect_trend(signal, window_hours=72, alpha=0.05):
        if mk is None:
            return 'unknown', None, None, False

        if not isinstance(signal, pd.Series):
            signal = pd.Series(signal)

        window_size = int(window_hours * 60)
        if len(signal) < window_size:
            return 'insufficient_data', 1.0, None, False

        recent_window = signal.iloc[-window_size:].values

        try:
            result = mk.original_test(recent_window)
        except Exception as e:
            return 'error', None, None, False

        p_value = result.p
        statistic = result.slope  # [verify] Sen's slope estimator

        significant = p_value < alpha
        trend_direction = 'stable'
        if significant:
            trend_direction = 'up' if statistic > 0 else 'down'

        return trend_direction, p_value, statistic, significant