# run_quality_alarm_log.py
"""Assess data quality of synthetic alarm log CSV output."""
import sys
import os
import json
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))
from data_quality import assess_quality, format_report

from alarm_log_config import OUTPUT_DIR, CSV_PATH, IQR_MULTIPLIER

if not os.path.exists(CSV_PATH):
    print(f"Error: {CSV_PATH} not found")
    exit(1)

df = pd.read_csv(CSV_PATH, parse_dates=["activation_time", "ack_time", "clear_time"])

config = {
    "timestamp_col": "activation_time",
    "asset_col": "asset_id",
    "expected_freq_min": None,
    "numeric_cols": ["priority", "duration_min"],
    "iqr_multiplier": IQR_MULTIPLIER,
    "pressure_cols": [],
}

report = assess_quality(df, config)
text = format_report(report)

output_path = os.path.join(OUTPUT_DIR, "data_quality")

os.makedirs(output_path, exist_ok=True)

with open(os.path.join(output_path, "alarm_log_quality_report.txt"), "w") as f:
    f.write(text)

with open(os.path.join(output_path, "alarm_log_quality_report.json"), "w") as f:
    json.dump(report, f, indent=2, default=str)

print(text)

