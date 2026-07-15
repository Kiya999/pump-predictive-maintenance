# run_quality_usgs.py
"""
Assess data quality of USGS streamflow data for the configured gauge station.
Downloads via dataretrieval if no cached CSV exists, then runs the shared
data_quality module and writes text/JSON reports to output/data_quality/.
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime
import dataretrieval.nwis as nwis
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))
from data_quality import assess_quality, format_report

SITE_ID = '01646500'
START_DATE = '2025-02-01'
END_DATE = '2026-02-01'
RAW_CSV_PATH = "output/usgs_raw.csv"
DATA_QUALITY_SUBDIR_PATH = "output/data_quality"
IQR_MULTIPLIER = 1.5

start = datetime.strptime(START_DATE, '%Y-%m-%d')
end = datetime.strptime(END_DATE, '%Y-%m-%d')

if not os.path.exists(RAW_CSV_PATH):
    print(f"Downloading USGS streamflow ({start.date()} to {end.date()})...")
    try:
        df, meta = nwis.get_iv(sites=SITE_ID, start=start.strftime('%Y-%m-%d'),
                                end=end.strftime('%Y-%m-%d'), parameterCd='00060')
        df[['00060']].to_csv(RAW_CSV_PATH)
        print(f"  Downloaded {len(df)} records, saved to {RAW_CSV_PATH}")
    except Exception as e:
        print(f"Error downloading: {e}")
        sys.exit()
else:
    print(f"Loading cached USGS data from {RAW_CSV_PATH}...")
    df = pd.read_csv(RAW_CSV_PATH, index_col=0, parse_dates=True)

df_clean = df[['00060']].dropna()
df_clean.columns = ['discharge_cfs']
df_clean['timestamp'] = df_clean.index
df_clean = df_clean.reset_index(drop=True)

time_diffs = df_clean['timestamp'].diff().dropna()
time_diffs_min = time_diffs.dt.total_seconds() / 60
median_interval = float(time_diffs_min.median())

print(f"Cleaned to {len(df_clean)} records")
print(f"Median interval: {median_interval:.1f} min")

config = {
    "timestamp_col": "timestamp",
    "asset_col": None,
    "expected_freq_min": median_interval,
    "numeric_cols": ["discharge_cfs"],
    "iqr_multiplier": IQR_MULTIPLIER,
    "pressure_cols": [],
}

print("Assessing USGS dataset quality...")
report = assess_quality(df_clean, config)
text = format_report(report)

os.makedirs(DATA_QUALITY_SUBDIR_PATH, exist_ok=True)

with open(os.path.join(DATA_QUALITY_SUBDIR_PATH, "usgs_quality_report.txt"), "w") as f:
    f.write(text)

with open(os.path.join(DATA_QUALITY_SUBDIR_PATH, "usgs_quality_report.json"), "w") as f:
    json.dump(report, f, indent=2, default=str)

print(text)
