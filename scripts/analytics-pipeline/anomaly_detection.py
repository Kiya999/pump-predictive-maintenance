# anomaly_detection.py
import pandas as pd
import numpy as np
import pymannkendall as mk


class AnomalyDetector:

    def __init__(self, baseline_results):
        self.baseline = baseline_results["baseline"]
        self.upper = baseline_results["upper"]
        self.lower = baseline_results["lower"]
        self.std = (self.upper - self.baseline) / 3.0

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
        severity = np.abs(signal - self.baseline) / (self.std + 1e-8)

        del q1_baseline, q3_baseline, iqr_baseline, lower_fence, upper_fence

        return {
            "flag": pd.Series(flag.values, index=signal.index),
            "severity": pd.Series(severity.values, index=signal.index),
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
        rolling_persistence = flag_series.rolling(window=window_size).mean()
        persistent_positions = np.where(rolling_persistence.values >= persistence_threshold)[0]

        if len(persistent_positions) == 0:
            return None, []

        first_detection_idx = persistent_positions[0]
        return first_detection_idx, []

    @staticmethod
    def lead_time_hours(first_flag_idx, failure_idx, sampling_freq_minutes=1):
        if first_flag_idx is None or first_flag_idx >= failure_idx:
            return None

        minutes_before = (failure_idx - first_flag_idx) * sampling_freq_minutes
        hours_before = minutes_before / 60.0
        return hours_before

    @staticmethod
    def detect_trend(signal, window_hours=72, sampling_freq_minutes=1, alpha=0.05):
        if not isinstance(signal, pd.Series):
            signal = pd.Series(signal)

        window_size = int(window_hours * 60 / sampling_freq_minutes)

        if len(signal) < window_size:
            return 'insufficient_data', 1.0, None, False

        recent_window = signal.iloc[-window_size:].values

        try:
            result = mk.original_test(recent_window)
        except Exception as e:
            print(f"Warning: Mann-Kendall error: {e}")
            return 'error', None, None, False

        significant = result.p < alpha
        trend_direction = 'stable'
        if significant:
            trend_direction = 'up' if result.slope > 0 else 'down'

        return trend_direction, result.p, result.slope, significant
