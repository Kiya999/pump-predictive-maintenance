# run_quality_usgs.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../historian-generator')))

import json
from datetime import datetime, timedelta
import dataretrieval.nwis as nwis
from data_quality import assess_quality, format_report
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

SITE = '01646500'
end = datetime.now()
start = end - timedelta(days=365)

print(f"Downloading USGS streamflow ({start.date()} to {end.date()})...")
try:
    df, meta = nwis.get_iv(sites=SITE, start=start.strftime('%Y-%m-%d'),
                            end=end.strftime('%Y-%m-%d'), parameterCd='00060')
    print(f"  Downloaded {len(df)} records")
except Exception as e:
    print(f"Error downloading: {e}")
    sys.exit()

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
    "iqr_multiplier": 1.5,
    "pressure_cols": [],
}

print("Assessing USGS dataset quality...")
report = assess_quality(df_clean, config)
text = format_report(report)

os.makedirs("output/data_quality", exist_ok=True)

with open("output/data_quality/usgs_quality_report.txt", "w") as f:
    f.write(text)

with open("output/data_quality/usgs_quality_report.json", "w") as f:
    json.dump(report, f, indent=2, default=str)

print(text)
