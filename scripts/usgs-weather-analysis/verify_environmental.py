# verify_environmental.py
"""
Verify USGS environmental correlation outputs. Checks file existence, data structure, nulls, and lag results.
"""

import os
import sys
import pandas as pd

env_output_dir = "output"

print("Verifying environmental correlation outputs\n")

# Check required files
print("Required files:")
required_files = [
    "combined_data.csv",
    "lag_correlation_results.txt",
    "usgs_exploratory_plots.png",
    "usgs_discharge_histogram.png",
    "lag_correlation_plots.png",
    "usgs_data_profile.txt",
]

missing = []
for fname in required_files:
    fpath = os.path.join(env_output_dir, fname)
    if os.path.exists(fpath):
        print(f"  {fname}")
    else:
        missing.append(fname)
        print(f"  {fname} - MISSING")

if missing:
    print(f"\nError: {len(missing)} files missing")
    sys.exit(1)

# Check combined_data.csv
print("\ncombined_data.csv:")
try:
    df = pd.read_csv(os.path.join(env_output_dir, "combined_data.csv"), parse_dates=["datetime"])
    print(f"  Rows: {len(df)}")

    required_cols = ["datetime", "01646500_cfs", "temp_c", "precip_mm"]
    missing_cols = [c for c in required_cols if c not in df.columns]

    if missing_cols:
        print(f"  Error: Missing columns {missing_cols}")
        sys.exit(1)

    min_date = df["datetime"].min()
    max_date = df["datetime"].max()
    print(f"  Date range: {min_date.date()} to {max_date.date()}")

    null_count = df[required_cols].isna().sum().sum()
    if null_count == 0:
        print("  No nulls")
    else:
        print(f"  Nulls: {null_count}")

except Exception as e:
    print(f"  Error: {e}")
    sys.exit(1)

# Check lag correlation results
print("\nlag_correlation_results.txt:")
try:
    with open(os.path.join(env_output_dir, "lag_correlation_results.txt")) as f:
        content = f.read()

    if "Best within" not in content or "Precip:" not in content or "Temp:" not in content:
        print("  Error: Results incomplete")
        sys.exit(1)

    for line in content.split("\n"):
        if "Precip:" in line or "Temp:" in line:
            print(f"  {line.strip()}")

except Exception as e:
    print(f"  Error: {e}")
    sys.exit(1)

# Check source file
print("\nusgs_raw.csv:")
try:
    df_raw = pd.read_csv(os.path.join(env_output_dir, "usgs_raw.csv"))
    print(f"  Rows: {len(df_raw)}")
except Exception as e:
    print(f"  Warning: {e}")

print("\nDone")