# run_quality_historian.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../etl-pipeline')))

import json
import pandas as pd
from data_quality import assess_quality, format_report

csv_path = "output/synthetic_historian_10x365_1min.csv"
if not os.path.exists(csv_path):
    print(f"Error: {csv_path} not found")
    exit(1)

df = pd.read_csv(csv_path, parse_dates=["timestamp"])

config = {
    "timestamp_col": "timestamp",
    "asset_col": "asset_id",
    "expected_freq_min": 1,
    "numeric_cols": [
        "flow_m3h", "suction_pressure_bar", "disch_pressure_bar",
        "diff_pressure_bar", "motor_temp_c", "motor_power_kw",
        "vibration_mm_s", "speed_rpm",
    ],
    "iqr_multiplier": 1.5,
    "pressure_cols": ["suction_pressure_bar", "disch_pressure_bar", "diff_pressure_bar"],
}

report = assess_quality(df, config)
text = format_report(report)

os.makedirs("output/data_quality", exist_ok=True)

with open("output/data_quality/historian_quality_report.txt", "w") as f:
    f.write(text)

with open("output/data_quality/historian_quality_report.json", "w") as f:
    json.dump(report, f, indent=2, default=str)

print(text)
