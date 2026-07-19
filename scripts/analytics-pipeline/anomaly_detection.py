# anomaly_detection.py
"""
Anomaly detector class: Z-score, IQR, and moving average methods with
persistence filtering and trend detection (Mann-Kendall test).
"""

import pandas as pd
import numpy as np
import pymannkendall as mk

from analytics_config import BASELINE_NUM_STD

NUMERICAL_EPSILON = 1e-8

class AnomalyDetector:
    """Detect anomalies using configured methods."""
    def __init__(self, baseline_results):
        """Initialize detector from baseline results."""
        self.baseline = baseline_results["baseline"]
        self.upper = baseline_results["upper"]
        self.lower = baseline_results["lower"]
        self.std = (self.upper - self.baseline) / float(BASELINE_NUM_STD)

    def zscore(self, signal, threshold):
        """Flag samples where absolute deviation from baseline exceeds threshold."""
        deviation = (signal - self.baseline) / (self.std + NUMERICAL_EPSILON)
        flag = np.abs(deviation) > threshold

        return {
            "flag": pd.Series(flag, index=signal.index),
            "severity": pd.Series(np.abs(deviation), index=signal.index),
        }

    def iqr(self, signal, window_periods, multiplier):
        """Flag samples outside rolling IQR fences."""
        residual = signal - self.baseline
        q1 = residual.rolling(window=window_periods, center=False).quantile(0.25)
        q3 = residual.rolling(window=window_periods, center=False).quantile(0.75)
        iqr_val = q3 - q1

        lower_fence = q1 - multiplier * iqr_val
        upper_fence = q3 + multiplier * iqr_val

        flag = (residual < lower_fence) | (residual > upper_fence)
        severity = residual.abs() / (self.std + NUMERICAL_EPSILON)

        del q1, q3, iqr_val, lower_fence, upper_fence

        return {
            "flag": pd.Series(flag.values, index=signal.index),
            "severity": pd.Series(severity.values, index=signal.index),
        }


    def moving_average(self, signal, window_periods, threshold):
        """Flag samples where rolling average deviates from baseline by threshold."""
        ma = signal.rolling(window=window_periods, center=False).mean()
        deviation = (ma - self.baseline) / (self.std + NUMERICAL_EPSILON)
        flag = np.abs(deviation) > threshold

        return {
            "flag": pd.Series(flag.values, index=signal.index),
            "severity": pd.Series(np.abs(deviation).values, index=signal.index),
        }

    @staticmethod
    def persistent_detection(flag_series, min_duration_hours, persistence_threshold, sampling_freq_minutes):
        """Find first occurrence of persistent flagging: threshold % of samples flagged over minimum duration."""
        if not isinstance(flag_series, pd.Series):
            flag_series = pd.Series(flag_series)

        window_size = int(min_duration_hours * 60 / sampling_freq_minutes)
        rolling_persistence = flag_series.rolling(window=window_size).mean()
        persistent_positions = np.where(rolling_persistence.values >= persistence_threshold)[0]

        if len(persistent_positions) == 0:
            return None

        first_detection_idx = persistent_positions[0]
        return first_detection_idx

    @staticmethod
    def lead_time_hours(first_flag_idx, failure_idx, sampling_freq_minutes):
        """Compute hours between first detection and failure."""
        if first_flag_idx is None or first_flag_idx >= failure_idx:
            return None

        minutes_before = (failure_idx - first_flag_idx) * sampling_freq_minutes
        hours_before = minutes_before / 60.0
        return hours_before

    @staticmethod
    def detect_trend(signal, window_hours, sampling_freq_minutes, alpha):
        """Apply Mann-Kendall test on recent window; return trend direction and significance."""
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
