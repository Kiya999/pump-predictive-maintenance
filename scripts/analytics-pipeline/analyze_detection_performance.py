# analyze_detection_performance.py

import os
import sys
import gc
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import plotly.graph_objects as go

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from baseline import BaselineCalculator
from anomaly_detection import AnomalyDetector

# from historian generator configuration
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

FAILURE_SCENARIOS = [
    ("bearing", "vibration_mm_s", "bearing"),
    ("cavitation", "diff_pressure_bar", "cavitation"),
    ("insulation", "motor_temp_c", "insulation"),
]

## Study guide default values:
DETECTION_METHODS = {
    "Z-score": {"threshold": 3.0},
    "IQR": {"window_periods": 1440, "multiplier": 1.0},
    "Moving avg": {"window_periods": 30, "threshold": 1.5},
}
BASELINE_TRAINING_FRACTION = 0.3

# ## another setting:
# DETECTION_METHODS = {
#     "Z-score": {"threshold": 2.0},
#     "IQR": {"window_periods": 1440, "multiplier": 1.5},
#     "Moving avg": {"window_periods": 30, "threshold": 2.5},
# }
# BASELINE_TRAINING_FRACTION = 0.5  # First 6 months

PERSISTENCE_MIN_DURATION_HOURS = 6
PERSISTENCE_THRESHOLD = 0.7 # 70% of windows must have flags
SAMPLING_FREQ_MINUTES = 1

MANN_KENDALL_ALPHA = 0.05 # (p < 0.05 = significant)
MAX_TREND_WINDOW = 10000 # Cap window size to prevent RAM explosion
TREND_ANALYSIS_WINDOWS_HOURS = [72, 168]

MAX_HEALTHY_ASSETS = 5 # Analyze FP rates on first N healthy assets
MAX_SEASONAL_ANALYSIS_ASSETS = 1 # Show seasonal breakdown for first N assets

DOWNSAMPLE_FACTOR = 60 # Plot every Nth sample

# Signal columns to analyze for false positives
HEALTHY_SIGNAL_COLS = ["vibration_mm_s", "motor_temp_c", "diff_pressure_bar"]

script_dir = os.path.dirname(os.path.abspath(__file__))
output_base = os.path.join(script_dir, "output", "detection_performance")
trend_output = os.path.join(output_base, "trend_detection")
os.makedirs(output_base, exist_ok=True)
os.makedirs(trend_output, exist_ok=True)

db_path = os.path.join(script_dir, "..", "etl-pipeline", "output", "etl_pipeline.db")
if not os.path.exists(db_path):
    print(f"Error: database not found at {db_path}")
    sys.exit(1)

engine = create_engine(f"sqlite:///{db_path}")

NEEDED_COLS = ["asset_id", "timestamp", "failure_type",
               "vibration_mm_s", "diff_pressure_bar", "motor_temp_c", "flow_m3h"]

df = pd.read_sql_table("historian_clean", engine, columns=NEEDED_COLS)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

print(f"Loaded {len(df)} records")
print(f"Columns loaded: {list(df.columns)}")
print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")
print(f"Database: {db_path}\n")

# PART 1: DETECTION LEAD TIME ANALYSIS

print(f"\n{'='*70}")
print("PART 1: DETECTION LEAD TIME ANALYSIS")
print(f"{'='*70}\n")

lead_time_results = []
first_detection_indices = {}

for scenario_name, signal_col, failure_type in FAILURE_SCENARIOS:
    print(f"Processing {scenario_name.upper()}...")

    df_failure = df[df["failure_type"] == failure_type]
    if len(df_failure) == 0:
        print(f"  Skip: no data for failure_type='{failure_type}'")
        continue

    asset_id = df_failure["asset_id"].iloc[0]
    df_asset = df[df["asset_id"] == asset_id].reset_index(drop=True)

    print(f"  Asset: {asset_id}")
    print(f"  Signal: {signal_col}")

    if signal_col not in df_asset.columns:
        print(f"  Skip: column '{signal_col}' not found")
        continue

    failure_mask = df_asset["failure_type"] != "none"
    if not failure_mask.any():
        print("  Skip: no failure point found")
        continue

    onset_idx = failure_mask.idxmax()

    ramp_info = RAMP_INFO_DAYS.get(failure_type)
    if ramp_info is None:
        print(f"  Skip: no ramp info for '{failure_type}'")
        continue

    true_failure_day = ramp_info["start_day"] + ramp_info["ramp_days"]
    true_failure_ts = df_asset["timestamp"].iloc[0] + pd.Timedelta(days=true_failure_day)
    post_true_failure = df_asset["timestamp"] >= true_failure_ts
    if not post_true_failure.any():
        print(f"  Skip: ramp end (day {true_failure_day}) beyond available data")
        continue

    failure_idx = post_true_failure.idxmax()

    print(f"  Ramp onset index: {onset_idx} ({100.0*onset_idx/len(df_asset):.1f}% into timeline)")
    print(f"  True failure index (ramp end): {failure_idx} ({100.0*failure_idx/len(df_asset):.1f}% into timeline)")

    signal = df_asset[signal_col].fillna(df_asset[signal_col].mean())
    flow = df_asset["flow_m3h"].fillna(df_asset["flow_m3h"].mean())
    timestamps = df_asset["timestamp"]

    train_signal = signal.iloc[:onset_idx]
    train_flow = flow.iloc[:onset_idx]
    train_ts = timestamps.iloc[:onset_idx]

    if len(train_signal) < 1440:
        print(f"  Skip: insufficient training data ({len(train_signal)} < 1440)")
        continue

    try:
        calc = BaselineCalculator(train_signal, training_flow=train_flow, training_timestamps=train_ts)
        calc.fit_hourly()
        baseline_result = calc.apply_hourly(timestamps, signal, num_std=3)
        print(f"  Baseline: fitted on {len(train_signal)} pre-failure samples")
    except Exception as e:
        print(f"  Skip: baseline fit failed: {e}")
        continue

    pf_hours = PF_INTERVALS_HOURS.get(failure_type)
    print(f"  P-F interval: {pf_hours} hours\n")

    detector = AnomalyDetector(baseline_result)

    detection_results = {
        "Z-score": detector.zscore(signal, threshold=DETECTION_METHODS["Z-score"]["threshold"]),
        "IQR": detector.iqr(signal, window_periods=DETECTION_METHODS["IQR"]["window_periods"],
                            multiplier=DETECTION_METHODS["IQR"]["multiplier"]),
        "Moving avg": detector.moving_average(signal, window_periods=DETECTION_METHODS["Moving avg"]["window_periods"],
                                              threshold=DETECTION_METHODS["Moving avg"]["threshold"]),
    }

    for method_name, result in detection_results.items():
        flags = result["flag"]
        flags_post_onset = flags.iloc[onset_idx:]

        first_persistent_rel, _ = AnomalyDetector.persistent_detection(
            flags_post_onset.values,
            min_duration_hours=PERSISTENCE_MIN_DURATION_HOURS,
            persistence_threshold=PERSISTENCE_THRESHOLD,
            sampling_freq_minutes=SAMPLING_FREQ_MINUTES,
        )
        first_persistent = (onset_idx + first_persistent_rel) if first_persistent_rel is not None else None

        if first_persistent is not None and first_persistent < failure_idx:
            # This preserves IQR as the preferred anchor when it fires, but lets Z-score populate the dict when IQR doesn't
            if scenario_name not in first_detection_indices or method_name == "IQR":
                first_detection_indices[scenario_name] = first_persistent


            lead_hours = AnomalyDetector.lead_time_hours(first_persistent, failure_idx, sampling_freq_minutes=1)
            lead_pct = 100.0 * lead_hours / pf_hours if pf_hours else None

            if lead_pct is not None and lead_pct > 100.0:
                status = "SUSPECT"
                print(f"    {method_name:12s} {status}  {lead_hours:8.1f}h ({lead_pct:6.1f}% of P-F) <- exceeds P-F interval, likely FP")
            else:
                status = "OK"
                print(f"    {method_name:12s} {status}  {lead_hours:8.1f}h ({lead_pct:6.1f}% of P-F)")

            print(f"      DEBUG: first_persistent_idx={first_persistent} failure_idx={failure_idx} gap={failure_idx - first_persistent}")

        else:
            lead_hours = None
            lead_pct = None
            status = "NO"
            print(f"    {method_name:12s} {status}  NO PERSISTENT DETECTION")
            if first_persistent is not None:
                print(f"      DEBUG: first_persistent_idx={first_persistent} failure_idx={failure_idx} (first >= failure)")

        lead_time_results.append({
            "Scenario": scenario_name,
            "Asset": asset_id,
            "Method": method_name,
            "Lead time (hours)": lead_hours,
            "% of P-F interval": lead_pct,
        })

    del detector, detection_results, baseline_result
    del signal, flow, timestamps, train_signal, train_flow, train_ts
    gc.collect()

if lead_time_results:
    results_df = pd.DataFrame(lead_time_results)

    col_order = ["Z-score", "IQR", "Moving avg"]

    pivot_hours = results_df.pivot_table(index="Scenario", columns="Method", values="Lead time (hours)", aggfunc="first").reindex(columns=col_order)

    pivot_pct = results_df.pivot_table(index="Scenario", columns="Method", values="% of P-F interval", aggfunc="first").reindex(columns=col_order)

    pivot_hours.to_csv(os.path.join(output_base, "lead_times.csv"))
    pivot_pct.to_csv(os.path.join(output_base, "lead_times_percent_pf.csv"))

    print(f"\n{'='*70}")
    print("DETECTION LEAD TIMES (hours)")
    print(f"{'='*70}")
    print(pivot_hours.to_string())

    print(f"\n{'='*70}")
    print("DETECTION LEAD TIMES (% of P-F interval)")
    print(f"{'='*70}")
    print(pivot_pct.to_string())

    print("\nSaved to:")
    print(f"  {os.path.join(output_base, 'lead_times.csv')}")
    print(f"  {os.path.join(output_base, 'lead_times_percent_pf.csv')}")
else:
    print("Warning: no lead time results collected")

# PART 2: FALSE POSITIVE RATE ANALYSIS

print(f"\n{'='*70}")
print("PART 2: FALSE POSITIVE RATE ANALYSIS")
print(f"{'='*70}\n")

all_assets = df["asset_id"].unique()
healthy_assets = [
    aid for aid in all_assets
    if set(df[df["asset_id"] == aid]["failure_type"].unique()) == {"none"}
]

print(f"Found {len(healthy_assets)} healthy assets: {healthy_assets}\n")

fp_results = []

for asset_id in healthy_assets[:MAX_HEALTHY_ASSETS]:
    print(f"Processing {asset_id}...")

    df_asset = df[df["asset_id"] == asset_id][["timestamp", "flow_m3h"] + HEALTHY_SIGNAL_COLS].reset_index(drop=True)

    if len(df_asset) < 1440:
        print(f"  Skip: insufficient data ({len(df_asset)} < 1440 samples)")
        continue

    missing_signals = [c for c in HEALTHY_SIGNAL_COLS if c not in df_asset.columns]
    if missing_signals:
        print(f"  Skip: missing signals {missing_signals}")
        continue

    timestamps = pd.to_datetime(df_asset["timestamp"])
    flow = df_asset["flow_m3h"].fillna(df_asset["flow_m3h"].mean())
    month_arr = timestamps.dt.month.values

    train_idx = int(BASELINE_TRAINING_FRACTION * len(df_asset))

    print(f"  Signals tested: {len(HEALTHY_SIGNAL_COLS)}")

    for signal_col in HEALTHY_SIGNAL_COLS:
        signal = df_asset[signal_col].fillna(df_asset[signal_col].mean())

        train_signal = signal.iloc[:train_idx]
        train_flow = flow.iloc[:train_idx]
        train_ts = timestamps.iloc[:train_idx]

        if len(train_signal) < 1440:
            print(f"    {signal_col}: skip, insufficient training data ({len(train_signal)} < 1440)")
            continue

        try:
            calc = BaselineCalculator(train_signal, training_flow=train_flow, training_timestamps=train_ts)
            calc.fit_hourly()
            baseline_result = calc.apply_hourly(timestamps, signal, num_std=3)
        except Exception as e:
            print(f"    {signal_col}: skip, baseline fit failed: {e}")
            continue

        detector = AnomalyDetector(baseline_result)
        zscore_flags = detector.zscore(signal, threshold=DETECTION_METHODS["Z-score"]["threshold"])["flag"].values.astype(np.int8)

        iqr_flags = detector.iqr(signal, window_periods=DETECTION_METHODS["IQR"]["window_periods"],
                                 multiplier=DETECTION_METHODS["IQR"]["multiplier"])["flag"].values.astype(np.int8)

        ma_flags = detector.moving_average(signal, window_periods=DETECTION_METHODS["Moving avg"]["window_periods"],
                                           threshold=DETECTION_METHODS["Moving avg"]["threshold"])["flag"].values.astype(np.int8)

        del detector, baseline_result
        gc.collect()

        for month in range(1, 13):
            mask      = month_arr == month
            month_len = mask.sum()
            if month_len == 0:
                continue

            fp_results.append({
                "Asset":                  asset_id,
                "Signal":                 signal_col,
                "Month":                  month,
                "Z-score FP count":       int(zscore_flags[mask].sum()),
                "Z-score FP rate (%)":    100.0 * zscore_flags[mask].sum() / month_len,
                "IQR FP count":           int(iqr_flags[mask].sum()),
                "IQR FP rate (%)":        100.0 * iqr_flags[mask].sum() / month_len,
                "Moving avg FP count":    int(ma_flags[mask].sum()),
                "Moving avg FP rate (%)": 100.0 * ma_flags[mask].sum() / month_len,
            })

        del zscore_flags, iqr_flags, ma_flags, signal, train_signal, train_flow, train_ts
        gc.collect()

        print(f"    {signal_col}: 12 months processed")

    del df_asset, timestamps, flow, month_arr
    gc.collect()

if fp_results:
    fp_df = pd.DataFrame(fp_results)

    monthly_summary = fp_df.groupby(["Signal", "Month"]).agg({
        "Z-score FP count": "mean",
        "Z-score FP rate (%)": "mean",
        "IQR FP count": "mean",
        "IQR FP rate (%)": "mean",
        "Moving avg FP count": "mean",
        "Moving avg FP rate (%)": "mean",
    }).round(2)

    asset_signal_summary = fp_df.groupby(["Asset", "Signal"]).agg({
        "Z-score FP count": "sum",
        "Z-score FP rate (%)": "mean",
        "IQR FP count": "sum",
        "IQR FP rate (%)": "mean",
        "Moving avg FP count": "sum",
        "Moving avg FP rate (%)": "mean",
    }).round(2)

    fp_df.to_csv(os.path.join(output_base, "false_positives_monthly.csv"), index=False)
    monthly_summary.to_csv(os.path.join(output_base, "false_positives_by_signal_month.csv"))
    asset_signal_summary.to_csv(os.path.join(output_base, "false_positives_by_asset_signal.csv"))

    print(f"\n{'='*70}")
    print("FALSE POSITIVE SUMMARY (healthy assets only)")
    print(f"{'='*70}")
    print("\nBy signal and month (mean per asset):")
    print(monthly_summary.to_string())
    print("\nBy asset and signal (annual totals):")
    print(asset_signal_summary.to_string())

    print("\nSaved to:")
    print(f"  {os.path.join(output_base, 'false_positives_monthly.csv')}")
    print(f"  {os.path.join(output_base, 'false_positives_by_signal_month.csv')}")
    print(f"  {os.path.join(output_base, 'false_positives_by_asset_signal.csv')}")

    # ROOT CAUSE ANALYSIS
    print(f"\n{'='*70}")
    print("FALSE POSITIVE ROOT CAUSE: SEASONAL BASELINE MISMATCH")
    print(f"{'='*70}\n")

    for asset_id in healthy_assets[:MAX_SEASONAL_ANALYSIS_ASSETS]:
        df_asset = df[df["asset_id"] == asset_id][["timestamp", "motor_temp_c", "diff_pressure_bar"]].copy()
        timestamps = pd.to_datetime(df_asset["timestamp"])
        df_asset["month"] = timestamps.dt.month

        train_idx = int(BASELINE_TRAINING_FRACTION * len(df_asset))

        print(f"Asset: {asset_id}\n")

        # Motor temperature
        signal = df_asset["motor_temp_c"].fillna(df_asset["motor_temp_c"].mean())
        train_mean = signal.iloc[:train_idx].mean()
        train_min = signal.iloc[:train_idx].min()
        train_max = signal.iloc[:train_idx].max()

        pct_label = int(BASELINE_TRAINING_FRACTION * 100)
        print(f"Baseline (trained on first {pct_label}%): min={train_min:.1f}C max={train_max:.1f}C mean={train_mean:.1f}C")

        monthly_stats = df_asset.groupby("month")[["motor_temp_c"]].agg(["min", "max", "mean"])
        monthly_stats.columns = ["min", "max", "mean"]

        print("\nMonthly motor temperature ranges:")
        print("Month  Min    Max    Mean   Drift from baseline mean")
        for month in range(1, 13):
            if month in monthly_stats.index:
                row = monthly_stats.loc[month]
                drift = row["mean"] - train_mean
                print(f"{month:2d}     {row['min']:5.1f} {row['max']:5.1f} {row['mean']:5.1f}  {drift:+.1f}C")

        # Differential pressure
        print()
        signal = df_asset["diff_pressure_bar"].fillna(df_asset["diff_pressure_bar"].mean())
        train_mean = signal.iloc[:train_idx].mean()
        train_min = signal.iloc[:train_idx].min()
        train_max = signal.iloc[:train_idx].max()
        print(f"Baseline (trained on first {pct_label}%): min={train_min:.2f}bar max={train_max:.2f}bar mean={train_mean:.2f}bar")

        monthly_stats = df_asset.groupby("month")[["diff_pressure_bar"]].agg(["min", "max", "mean"])
        monthly_stats.columns = ["min", "max", "mean"]

        print("\nMonthly differential pressure ranges:")
        print("Month  Min    Max    Mean   Drift from baseline mean")
        for month in range(1, 13):
            if month in monthly_stats.index:
                row = monthly_stats.loc[month]
                drift = row["mean"] - train_mean
                print(f"{month:2d}     {row['min']:5.2f} {row['max']:5.2f} {row['mean']:5.2f}  {drift:+.2f}bar")

        del df_asset, timestamps, signal, monthly_stats
        gc.collect()

else:
    print("Warning: no false positive results collected")

# PART 3: TREND DETECTION (Mann-Kendall)

print(f"\n{'='*70}")
print("PART 3: TREND DETECTION WITH MANN-KENDALL TEST")
print(f"{'='*70}\n")

bearing_mask = df["failure_type"] == "bearing"
if not bearing_mask.any():
    print("Warning: no bearing degradation scenario found, skipping trend analysis")
else:
    bearing_asset = df[bearing_mask]["asset_id"].iloc[0]
    df_bearing = df[df["asset_id"] == bearing_asset][["timestamp", "vibration_mm_s", "flow_m3h", "failure_type"]].reset_index(drop=True)
    print(f"Bearing asset: {bearing_asset}")

    if "vibration_mm_s" not in df_bearing.columns:
        print("Warning: vibration_mm_s column not found, skipping trend analysis")
    else:
        signal = df_bearing["vibration_mm_s"].fillna(df_bearing["vibration_mm_s"].mean())
        timestamps = df_bearing["timestamp"]

        # Find onset (first non-none)
        failure_mask_b = df_bearing["failure_type"] != "none"
        if not failure_mask_b.any():
            print("Warning: no failure point in bearing asset")
        else:
            onset_idx = failure_mask_b.idxmax()

            # Calculate true failure (ramp end) same as Part 1
            ramp_info = RAMP_INFO_DAYS.get("bearing")
            if ramp_info is None:
                print("Warning: no ramp info for bearing, skipping trend analysis")
            else:
                true_failure_day = ramp_info["start_day"] + ramp_info["ramp_days"]
                true_failure_ts = df_bearing["timestamp"].iloc[0] + pd.Timedelta(days=true_failure_day)
                post_true_failure = df_bearing["timestamp"] >= true_failure_ts
                if not post_true_failure.any():
                    print("Warning: ramp end beyond available data, skipping trend analysis")
                else:
                    failure_idx = post_true_failure.idxmax()

            failure_time = timestamps.iloc[failure_idx]
            # failure_time_str = failure_time.isoformat()
            failure_pct = 100.0 * failure_idx / len(df_bearing)

            print(f"Failure onset: index {failure_idx} ({failure_pct:.1f}% into timeline)")
            print(f"Total samples: {len(df_bearing)}\n")

            print("Mann-Kendall Trend Analysis:\n")

            # Cap maximum window to avoid RAM explosion
            FIRST_BEARING_DETECTION_IDX = first_detection_indices.get("bearing")

            if FIRST_BEARING_DETECTION_IDX is None:
                print("  Warning: no IQR detection index from Part 1, skipping centered trend window")
            else:
                half = MAX_TREND_WINDOW // 2
                start = max(0, FIRST_BEARING_DETECTION_IDX - half)
                end   = min(failure_idx, FIRST_BEARING_DETECTION_IDX + half)
                window_hours_actual = (end - start) / 60.0

                trend_window_signal = signal.iloc[start:end]

                trend_dir_full, p_val_full, slope_full, sig_full = AnomalyDetector.detect_trend(
                    trend_window_signal, window_hours=len(trend_window_signal) / 60.0, alpha=MANN_KENDALL_ALPHA
                )

                sig_str_full = "SIGNIFICANT" if sig_full else "not significant"
                p_str_full = f"{p_val_full:.6f}" if p_val_full is not None else "N/A"
                slope_str_full = f"{slope_full:.8f}" if slope_full is not None else "N/A"
                print(f"  Pre-failure window centered on first detection ({window_hours_actual:.1f}h, idx {start}-{end}): trend={trend_dir_full} (p={p_str_full} slope={slope_str_full}) {sig_str_full}")

                # Trailing windows
                print("\nTrailing windows (last 72h and 168h of pre-failure):")
                trend_results = {}
                trend_csv_results = [{
                    "Window hours": window_hours_actual,
                    "Window type": "full (capped)",
                    "Trend direction": trend_dir_full,
                    "P-value": p_val_full,
                    "Slope": slope_full,
                    f"Significant (alpha={MANN_KENDALL_ALPHA})": sig_full,
                }]

                for window_hours in TREND_ANALYSIS_WINDOWS_HOURS:
                    trend_dir, p_val, slope, significant = AnomalyDetector.detect_trend(
                        signal.iloc[:failure_idx], window_hours=window_hours, alpha=MANN_KENDALL_ALPHA
                    )
                    sig_str = "SIGNIFICANT" if significant else "not significant"
                    p_str = f"{p_val:.6f}" if p_val is not None else "N/A"
                    slope_str = f"{slope:.8f}" if slope is not None else "N/A"
                    print(f"  {window_hours:3d}h window: trend={trend_dir:12s} (p={p_str} slope={slope_str}) {sig_str}")
                    trend_results[window_hours] = (trend_dir, p_val, slope, significant)
                    trend_csv_results.append({
                        "Window hours": window_hours,
                        "Window type": "trailing",
                        "Trend direction": trend_dir,
                        "P-value": p_val,
                        "Slope": slope,
                        f"Significant (alpha={MANN_KENDALL_ALPHA})": significant,
                    })

                trend_csv_df = pd.DataFrame(trend_csv_results)
                trend_csv_path = os.path.join(output_base, "trend_detection_results.csv")
                trend_csv_df.to_csv(trend_csv_path, index=False)
                print(f"\nTrend results saved to: {trend_csv_path}")

                # Plots
                rolling_mean = signal.rolling(window=1440).mean()

                train_signal_b = signal.iloc[:failure_idx]
                flow_b = df_bearing["flow_m3h"].fillna(df_bearing["flow_m3h"].mean())
                train_flow_b = flow_b.iloc[:failure_idx]
                train_ts_b = timestamps.iloc[:failure_idx]

                has_flags = False
                first_iqr_time = None
                zscore_flags = None
                iqr_flags = None

                try:
                    calc_b = BaselineCalculator(train_signal_b, training_flow=train_flow_b, training_timestamps=train_ts_b)
                    calc_b.fit_hourly()
                    baseline_b = calc_b.apply_hourly(timestamps, signal, num_std=3)
                    detector_b = AnomalyDetector(baseline_b)
                    zscore_result = detector_b.zscore(signal,threshold=DETECTION_METHODS["Z-score"]["threshold"])
                    iqr_result = detector_b.iqr(signal,window_periods=DETECTION_METHODS["IQR"]["window_periods"],
                                                multiplier=DETECTION_METHODS["IQR"]["multiplier"])
                    zscore_flags = zscore_result["flag"]
                    iqr_flags = iqr_result["flag"]

                    # Find first persistent IQR detection post-failure (avoid pre-failure spurious flags)
                    iqr_flags_post_failure = iqr_flags.iloc[failure_idx:]
                    first_iqr_rel, _ = AnomalyDetector.persistent_detection(
                        iqr_flags_post_failure.values, min_duration_hours=PERSISTENCE_MIN_DURATION_HOURS,
                        persistence_threshold=PERSISTENCE_THRESHOLD, sampling_freq_minutes=SAMPLING_FREQ_MINUTES
                    )
                    first_iqr = (failure_idx + first_iqr_rel) if first_iqr_rel is not None else None
                    first_iqr_time = timestamps.iloc[first_iqr] if first_iqr is not None else None

                    has_flags = True

                except Exception as e:
                    print(f"  Warning: could not compute flags for trend plot: {e}")
                    has_flags = False

                # downsampled versions for visualization only
                signal_plot = signal.iloc[::DOWNSAMPLE_FACTOR]
                timestamps_plot = timestamps.iloc[::DOWNSAMPLE_FACTOR]
                rolling_mean_plot = rolling_mean.iloc[::DOWNSAMPLE_FACTOR]
                iqr_flags_plot = iqr_flags.iloc[::DOWNSAMPLE_FACTOR] if iqr_flags is not None else None
                zscore_flags_plot = zscore_flags.iloc[::DOWNSAMPLE_FACTOR] if zscore_flags is not None else None

                for window_hours in TREND_ANALYSIS_WINDOWS_HOURS:
                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=timestamps_plot, y=signal_plot.values, mode="lines",
                        name="Vibration (raw)", line=dict(color="steelblue", width=1)
                    ))

                    fig.add_trace(go.Scatter(
                        x=timestamps_plot, y=rolling_mean_plot.values, mode="lines",
                        name="24h rolling mean", line=dict(color="red", width=2, dash="dash")
                    ))

                    if has_flags and iqr_flags_plot is not None:
                        flag_mask = iqr_flags_plot.values == 1
                        if flag_mask.any():
                            fig.add_trace(go.Scatter(
                                x=timestamps_plot.values[flag_mask], y=signal_plot.values[flag_mask],
                                mode="markers", name="IQR anomaly flag",
                                marker=dict(color="orange", size=4, opacity=0.6)
                            ))

                        if first_iqr_time:
                            fig.add_vline(
                                x=first_iqr_time, line_dash="dot",
                                line_color="orange", line_width=2,
                            )

                    if has_flags and zscore_flags_plot is not None:
                        zscore_mask = zscore_flags_plot.values == 1
                        if zscore_mask.any():
                            fig.add_trace(go.Scatter(
                                x=timestamps_plot.values[zscore_mask], y=signal_plot.values[zscore_mask],
                                mode="markers", name="Z-score anomaly flag",
                                marker=dict(color="red", size=4, opacity=0.6)
                            ))

                    fig.add_vline(
                        x=failure_time, line_dash="dash",
                        line_color="darkred", line_width=2,
                    )

                    trend_dir, p_val, slope, significant = trend_results[window_hours]
                    sig_label = "SIGNIFICANT" if significant else "not significant"

                    fig.update_layout(
                        title=f"Bearing {bearing_asset}: Vibration Trend & Anomaly Detection — {window_hours}h Mann-Kendall Window<br>"
                              f"<sup>Trend: {trend_dir} | p={p_val:.4f} | {sig_label}</sup>",
                        xaxis_title="Time",
                        yaxis_title="Vibration (mm/s RMS)",
                        hovermode="x unified",
                        height=600,
                        template="plotly_white",
                    )
                    output_file = os.path.join(trend_output, f"bearing_trend_{window_hours}h.html")
                    fig.write_html(output_file)
                    print(f"Plot saved: {output_file}")

                del df_bearing, signal, timestamps, rolling_mean, trend_window_signal
                del signal_plot, timestamps_plot, rolling_mean_plot, iqr_flags_plot, zscore_flags_plot
                gc.collect()

print(f"\n{'='*70}")
print("ANALYSIS COMPLETE")
print(f"{'='*70}")
print(f"Output directory: {output_base}")
print("All results saved.")