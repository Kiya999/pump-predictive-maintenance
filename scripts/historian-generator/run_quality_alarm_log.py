# run_quality_alarm_log.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../etl-pipeline')))

import json
import pandas as pd
from data_quality import assess_quality, format_report

csv_path = "output/alarm_log.csv"
if not os.path.exists(csv_path):
    print(f"Error: {csv_path} not found")
    exit(1)

df = pd.read_csv(csv_path, parse_dates=["activation_time", "ack_time", "clear_time"])

config = {
    "timestamp_col": "activation_time",
    "asset_col": "asset_id",
    "expected_freq_min": None,
    "numeric_cols": [
        "priority", "duration_min"
    ],


    "iqr_multiplier": 1.5,
    "pressure_cols": [],
}

report = assess_quality(df, config)
text = format_report(report)

os.makedirs("output/data_quality", exist_ok=True)

with open("output/data_quality/alarm_log_quality_report.txt", "w") as f:
    f.write(text)

with open("output/data_quality/alarm_log_quality_report.json", "w") as f:
    json.dump(report, f, indent=2, default=str)

print(text)
