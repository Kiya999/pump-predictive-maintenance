# analytics_config.py
"""
Configuration for analytics pipeline: detection thresholds, baseline fitting,
alarm analysis, and reference data for failure scenario validation.
"""

import os

## Output Paths
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
DETECTION_PERFORMANCE_DIR = os.path.join(OUTPUT_DIR, "detection_performance")
TREND_OUTPUT_DIR = os.path.join(DETECTION_PERFORMANCE_DIR, "trend_detection")
BASELINE_VALIDATION_DIR = os.path.join(OUTPUT_DIR, "baseline_validation")
ANOMALY_DETECTION_DIR = os.path.join(OUTPUT_DIR, "anomaly_detection")

## Database
ETL_PIPELINE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "etl-pipeline", "output", "etl_pipeline.db")
CLEAN_TABLES = ["historian_clean", "alarm_log_clean", "environmental_clean"]
ALARM_TABLE = "alarm_log_clean"
ANALYSIS_TABLE = "historian_clean"

## Output Files
OUTPUT_FILES = {
    "pf_alignment_csv": "pf_alignment_matrix.csv",
    "pf_alignment_excel": "pf_alignment_matrix.xlsx",
    "data_dictionary_excel": "data_dictionary.xlsx",
    "alarm_rate_daily": "alarm_rate_daily.csv",
    "alarm_frequency_top10": "alarm_frequency_top10.csv",
    "alarm_avg_time_to_ack": "alarm_avg_time_to_ack.csv",
    "alarm_stale_events": "alarm_stale_events.csv",
    "alarm_chattering_events": "alarm_chattering_events.csv",
    "alarm_clusters": "alarm_clusters.csv",
    "isa_validation_results": "isa_validation_results.json",
}

ANALYSIS_OUTPUT_FILES = {
    "lead_times": "lead_times.csv",
    "lead_times_percent_pf": "lead_times_percent_pf.csv",
    "false_positives_monthly": "false_positives_monthly.csv",
    "false_positives_by_signal_month": "false_positives_by_signal_month.csv",
    "false_positives_by_asset_signal": "false_positives_by_asset_signal.csv",
    "trend_detection_results": "trend_detection_results.csv",
}

## Detection Method Parameters (tunable)
DETECTION_METHODS = {
    "Z-score": {"threshold": 3.0},
    "IQR": {"window_periods": 1440, "multiplier": 1.0},
    "Moving avg": {"window_periods": 30, "threshold": 1.5},
}

## Persistence Detection Parameters (tunable)
PERSISTENCE_MIN_DURATION_HOURS = 6
PERSISTENCE_THRESHOLD = 0.7 # 70% of windows must have flags
SAMPLING_FREQ_MINUTES = 1

## Trend Analysis Parameters (tunable)
MANN_KENDALL_ALPHA = 0.05 # (p < 0.05 = significant)
MAX_TREND_WINDOW = 10000 # Cap window size to prevent RAM explosion
TREND_ANALYSIS_WINDOWS_HOURS = [72, 168]
TREND_HTML_TEMPLATE = "bearing_trend_{window_hours}h.html"

## Baseline Fitting Parameters (tunable)
BASELINE_WINDOW_HOURS = 24
BASELINE_NUM_STD = 3
BASELINE_TRAINING_FRACTION = 0.3
MIN_TRAINING_HOURS = 24

## Analysis Limits (tunable)
MAX_HEALTHY_ASSETS = 5 # Analyze FP rates on first N healthy assets
MAX_SEASONAL_ANALYSIS_ASSETS = 1 # Show seasonal breakdown for first N assets
DOWNSAMPLE_FACTOR = 60 # Plot every Nth sample
ANOMALY_ROLLING_PLOT_WINDOW_HOURS = 24

## Alarm Benchmarks (tunable)
ISA_CHATTER_MAX_EVENTS = 3
ISA_CHATTER_WINDOW_MIN = 5
STALE_ALARM_HOURS = 24
CLUSTER_WINDOW_MIN = 30
ISA_DAILY_RATE_TARGET = 144

## Column Definitions
HISTORIAN_NEEDED_COLS_DETECTION = [
    "asset_id", "timestamp", "failure_type",
    "vibration_mm_s", "diff_pressure_bar",
    "motor_temp_c", "flow_m3h"
]

BASELINE_VALIDATION_SIGNAL_COLS = ["flow_m3h", "vibration_mm_s"]
BASELINE_VALIDATION_NEEDED_COLS = [
    "asset_id", "timestamp", "failure_type",
    "flow_m3h", "vibration_mm_s"
]

ANOMALY_DETECTION_NEEDED_COLS = [
    "asset_id", "timestamp", "failure_type",
    "vibration_mm_s", "diff_pressure_bar",
    "motor_temp_c", "flow_m3h"
]

HEALTHY_SIGNAL_COLS = ["vibration_mm_s", "motor_temp_c", "diff_pressure_bar"]

## Alarm Test Cases (synthetic data only)
ALARM_TEST_CASE_VALUE = "YES"

ALARM_TEST_CASES = {
    "chattering": {
        "asset_id": "P-0100",
        "alarm_tag": "P-0100.VI_HI",
    },
    "stale": {
        "asset_id": "P-0200",
        "alarm_tag": "P-0200.FI_LO",
    },
    "cluster": {
        "asset_id": "P-0300",
    },
}

## Failure Scenario Reference (for detection performance testing/validation only)
# Mirror of FAILURE_SCENARIOS from historian_config.py used in performance analysis
FAILURE_SCENARIOS = [
    ("bearing", "vibration_mm_s", "bearing"),
    ("cavitation", "diff_pressure_bar", "cavitation"),
    ("insulation", "motor_temp_c", "insulation"),
]

PF_INTERVALS_HOURS = {
    "bearing": 260 * 24,
    "cavitation": 60 * 24,
    "insulation": 120 * 24,
}

RAMP_INFO_DAYS = {
    "bearing": {"start_day": 100, "ramp_days": 260},
    "cavitation": {"start_day": 200, "ramp_days": 60},
    "insulation": {"start_day": 150, "ramp_days": 120},
}

## Failure Type Definitions
FAILURE_TYPE_HEALTHY = "none"
FAILURE_TYPE_HEALTHY_VARIANTS = ["none", "None", "pass", "", "N/A", "NA"]
