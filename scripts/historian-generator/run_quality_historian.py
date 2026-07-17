# run_quality_historian.py
"""Assess data quality of synthetic historian CSV output."""
import sys
import os
import json
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))
from data_quality import assess_quality, format_report

from historian_config import OUTPUT_DIR, CSV_PATH, SIGNAL_COLUMNS, PRESSURE_COLUMNS, IQR_MULTIPLIER, FREQ_MIN

if not os.path.exists(CSV_PATH):
    print(f"Error: {CSV_PATH} not found")
    exit(1)

df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])

config = {
    "timestamp_col": "timestamp",
    "asset_col": "asset_id",
    "expected_freq_min": FREQ_MIN,
    "numeric_cols": SIGNAL_COLUMNS,
    "iqr_multiplier": IQR_MULTIPLIER,
    "pressure_cols": PRESSURE_COLUMNS,
}

report = assess_quality(df, config)
text = format_report(report)

output_path = os.path.join(OUTPUT_DIR, "data_quality")
os.makedirs(output_path, exist_ok=True)

with open(os.path.join(output_path, "historian_quality_report.txt"), "w") as f:
    f.write(text)

with open(os.path.join(output_path, "historian_quality_report.json"), "w") as f:
    json.dump(report, f, indent=2, default=str)

print(text)
