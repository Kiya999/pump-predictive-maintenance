# analyze_bearing_comparison.py
"""
Load synthetic historian P-0100 bearing degradation and PRONOSTIA real bearing 
failure data, normalize and overlay signals, extract quality reports summary.
Outputs comparison plot and dataset statistics.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Paths
HIST_CSV = "../historian-generator/output/synthetic_historian_10x365_1min.csv"
PRONOSTIA_CSV = "output/pronostia_rms_timeseries.csv"
PRONOSTIA_STATS_CSV = "output/pronostia_baseline_stats.csv"
QUALITY_DIR = "../historian-generator/output/data_quality"

os.makedirs("output", exist_ok=True)

for path in [PRONOSTIA_CSV, PRONOSTIA_STATS_CSV, HIST_CSV]:
    if not os.path.exists(path):
        print(f"Error: {path} not found")
        sys.exit(1)

# Load historian data
print("Loading historian dataset...")
df = pd.read_csv(HIST_CSV, parse_dates=["timestamp"])
synth_df = df[df["asset_id"] == "P-0100"].copy().sort_values("timestamp").reset_index(drop=True)

print(f"P-0100: {len(synth_df)} records")
print(f"Vibration: {synth_df['vibration_mm_s'].min():.4f}-{synth_df['vibration_mm_s'].max():.4f} mm/s")

# Find bearing failure window
bearing_mask = synth_df['failure_type'] == 'bearing'
if not bearing_mask.any():
    raise ValueError("No bearing failure events found")

degrade_idx = bearing_mask.idxmax()
degrade_end = synth_df[bearing_mask].index[-1]
print(f"Bearing degradation: record {degrade_idx}-{degrade_end}")
print(f"Duration: {100*degrade_idx/len(synth_df):.1f}% to {100*degrade_end/len(synth_df):.1f}%")

synth_df['time_pct'] = 100.0 * np.arange(len(synth_df)) / len(synth_df)
synth_df[['timestamp', 'time_pct', 'vibration_mm_s', 'failure_type']].to_csv(
    "output/synthetic_bearing_timeseries.csv", index=False)

# Load PRONOSTIA data
print("Loading PRONOSTIA data...")
pron_df = pd.read_csv(PRONOSTIA_CSV)
pron_stats = pd.read_csv(PRONOSTIA_STATS_CSV).iloc[0]

baseline_std = float(pron_stats['baseline_std'])
threshold_accel = float(pron_stats['threshold_accel'])
baseline_end = int(pron_stats['baseline_end_idx'])
accel_start = int(pron_stats['accel_start_idx'])
print(f"Stats: std={baseline_std:.6f}, threshold={threshold_accel:.6f}, baseline_end={baseline_end}")

# Normalize signals to [0, 1]
pron_norm = (pron_df['rms'] - pron_df['rms'].min()) / (pron_df['rms'].max() - pron_df['rms'].min())
synth_norm = (synth_df['vibration_mm_s'] - synth_df['vibration_mm_s'].min()) / \
             (synth_df['vibration_mm_s'].max() - synth_df['vibration_mm_s'].min())

pron_time = 100.0 * np.arange(len(pron_df)) / len(pron_df)
synth_time = synth_df['time_pct'].values

# Phase counts
pron_baseline = baseline_end
pron_gradual = accel_start - baseline_end if accel_start > 0 else 0
pron_accel = len(pron_df) - accel_start if accel_start > 0 else 0

synth_baseline = degrade_idx
synth_degrade = len(synth_df) - degrade_idx
synth_vib_transition = synth_df['vibration_mm_s'].iloc[degrade_idx]

print(f"PRONOSTIA: {len(pron_df)} measurements")
print(f"Synthetic: {len(synth_df)} records")

# Plots
fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(pron_time, pron_norm, marker='o', markersize=3, linewidth=1.5,
        color='steelblue', label='PRONOSTIA')

step = max(1, len(synth_df) // 1000) # downsampled to ~1000 points
synth_time_ds = synth_time[::step]
synth_norm_ds = synth_norm.values[::step]
ax.plot(synth_time_ds, synth_norm_ds, linewidth=1.0, color='crimson',
        alpha=0.7, label='Synthetic P-0100')

ax.axvline(100*baseline_end/len(pron_df), color='blue', linestyle='--', linewidth=1.0, alpha=0.5)
ax.axvline(100*accel_start/len(pron_df), color='blue', linestyle=':', linewidth=1.0, alpha=0.5)
ax.axvline(100*degrade_idx/len(synth_df), color='red', linestyle='--', linewidth=1.0, alpha=0.5)

ax.set_xlabel('Degradation Progress (%)')
ax.set_ylabel('Normalized Signal')
ax.set_title('Bearing Degradation: PRONOSTIA vs Synthetic')
ax.legend(fontsize=11, loc='upper left')
ax.grid(True, alpha=0.3)
ax.set_ylim([-0.05, 1.05])
plt.tight_layout()
plt.savefig("output/bearing_comparison_overlay.png", dpi=150)


# Quality reports
print("\nLoading quality reports...")
reports = {}
for name, path in {
    "historian": os.path.join(QUALITY_DIR, "historian_quality_report.json"),
    "alarm_log": os.path.join(QUALITY_DIR, "alarm_log_quality_report.json"),
    "usgs": "../usgs-weather-analysis/output/data_quality/usgs_quality_report.json",
}.items():
    if os.path.exists(path):
        with open(path) as f:
            reports[name] = json.load(f)
    else:
        print(f"Warning: {name} report not found")

if len(reports) >= 3:
    hist = reports["historian"]
    alarm = reports["alarm_log"]
    usgs = reports["usgs"]

    h_complete = hist['completeness']['overall_completeness_pct']
    h_gaps = hist['gaps'].get('gap_count', 'N/A')
    h_dups = hist['duplicates']['duplicate_timestamp_count']
    h_outliers = sum(v['outlier_count'] for v in hist['outliers'].values())
    print(f"Historian: {hist['row_count']:,} rows, {h_complete:.1f}% complete, {h_gaps} gaps, {h_dups} dups, {h_outliers} outliers")

    a_complete = alarm['completeness']['overall_completeness_pct']
    a_dups = alarm['duplicates']['duplicate_timestamp_count']
    a_outliers = sum(v.get('outlier_count', 0) for v in alarm['outliers'].values())
    print(f"Alarm Log: {alarm['row_count']:,} rows, {a_complete:.1f}% complete, {a_dups} dups, {a_outliers} outliers")

    u_complete = usgs['completeness']['overall_completeness_pct']
    u_gaps = usgs['gaps'].get('gap_count', 'N/A')
    u_outliers = sum(v.get('outlier_count', 0) for v in usgs['outliers'].values())
    print(f"USGS: {usgs['row_count']:,} rows, {u_complete:.1f}% complete, {u_gaps} gaps, {u_outliers} outliers")

    worst = min([("Historian", h_complete), ("Alarm Log", a_complete), ("USGS", u_complete)], key=lambda x: x[1])
    print(f"Worst completeness: {worst[0]} ({worst[1]:.1f}%)")

print("-" * 70)
print("DATASET SUMMARY")
print(f"pronostia_count = {len(pron_df)}")
print(f"synthetic_count = {len(synth_df)}")
print(f"pronostia_rms_range = {pron_df['rms'].min():.6f} to {pron_df['rms'].max():.6f}")
print(f"synthetic_vib_range = {synth_df['vibration_mm_s'].min():.4f} to {synth_df['vibration_mm_s'].max():.4f}")

print("\nPHASES")
print(f"pron_baseline = {pron_baseline}, gradual = {pron_gradual}, accel = {pron_accel}")
print(f"synth_baseline = {synth_baseline}, degrade = {synth_degrade}")

print("\nSYNTHETIC DEGRADATION")
print(f"vib_baseline_mean = {synth_df['vibration_mm_s'].iloc[:synth_baseline].mean():.4f}")
print(f"vib_at_transition = {synth_vib_transition:.4f}")
print(f"vib_peak = {synth_df['vibration_mm_s'].max():.4f}")
print(f"rise_factor = {synth_df['vibration_mm_s'].max() / synth_vib_transition:.2f}")