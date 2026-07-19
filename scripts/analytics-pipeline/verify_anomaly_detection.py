# verify_anomaly_detection.py
"""
Verify anomaly detection methods on failure scenarios. Generates detailed
plots showing flag locations, severity scores, and detection lead times.
"""

import os
import sys
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from analytics_config import ANOMALY_DETECTION_DIR, DETECTION_METHODS, BASELINE_WINDOW_HOURS, BASELINE_NUM_STD, ETL_PIPELINE_PATH, ANOMALY_DETECTION_NEEDED_COLS, FAILURE_SCENARIOS
from baseline import BaselineCalculator
from anomaly_detection import AnomalyDetector

os.makedirs(ANOMALY_DETECTION_DIR, exist_ok=True)

def debug_anomaly_results(method_name, result_dict, signal, pre_failure_idx, post_failure_idx):
    """Print anomaly detection results: flag counts, severity stats, and lead time."""
    flag = result_dict["flag"]
    severity = result_dict["severity"]
    flag_indices = result_dict.get("flag_indices", np.where(flag.values)[0])

    print(f"\n    {method_name.upper()} METHOD:")

    flags_pre = flag.iloc[:pre_failure_idx].sum()
    flags_post = flag.iloc[post_failure_idx:].sum()
    flags_total = flags_pre + flags_post
    print(f"      Total flags: {flags_total}")

    severity_nonzero = severity[severity > 0]
    if len(severity_nonzero) > 0:
        print(f"      Severity - min: {severity_nonzero.min():.4f}, max: {severity_nonzero.max():.4f}, mean: {severity_nonzero.mean():.4f}")
    else:
        print("      Severity - min: 0.0000, max: 0.0000, mean: 0.0000")

    pct_pre = 100 * flags_pre / pre_failure_idx if pre_failure_idx > 0 else 0
    pct_post = 100 * flags_post / (len(flag) - post_failure_idx) if (len(flag) - post_failure_idx) > 0 else 0

    print(f"      Pre-failure flags: {flags_pre} ({pct_pre:.2f}%)")
    print(f"      Post-failure flags: {flags_post} ({pct_post:.2f}%)")

    if len(flag_indices) > 0:
        first_flag = flag_indices[0]
        if first_flag < pre_failure_idx:
            lead_samples = pre_failure_idx - first_flag
            lead_hours = lead_samples / 60
            lead_days = lead_hours / 24
            if lead_hours < 168:
                print(f"      First flag: {lead_hours:.1f} hours BEFORE failure (index {first_flag})")
            else:
                print(f"      First flag: {lead_days:.1f} days BEFORE failure (index {first_flag})")
        else:
            lag_hours = (first_flag - pre_failure_idx) / 60
            print(f"      First flag: {lag_hours:.1f} hours AFTER failure (index {first_flag})")
    else:
        print("      First flag: no anomalies detected")


def detect_on_scenario(scenario_name, signal_col, failure_type, df):
    """Run anomaly detection on a failure scenario and generate comparison plot."""
    print(f"\n  Processing {scenario_name}...")

    all_rows_with_failure_type = df[df["failure_type"] == failure_type]

    if len(all_rows_with_failure_type) == 0:
        print(f"    Skip: no data for failure_type='{failure_type}'")
        return

    asset_id = all_rows_with_failure_type["asset_id"].iloc[0]
    print(f"    Asset ID: {asset_id}")

    df_asset = df[df["asset_id"] == asset_id].reset_index(drop=True)
    print(f"    Total rows for asset: {len(df_asset)}")

    if signal_col not in df_asset.columns:
        print(f"    Skip: column '{signal_col}' not found")
        return

    signal = df_asset[signal_col].fillna(df_asset[signal_col].mean())
    flow = df_asset["flow_m3h"].fillna(df_asset["flow_m3h"].mean())

    timestamps = pd.to_datetime(df_asset["timestamp"])

    print(f"    Signal {signal_col}: min={signal.min():.4f}, max={signal.max():.4f}, mean={signal.mean():.4f}")

    failure_mask = df_asset["failure_type"] != "none"
    if not failure_mask.any():
        print("    Skip: no failure rows (all 'none')")
        return

    failure_idx = failure_mask.idxmax()
    failure_pct = 100 * failure_idx / len(df_asset)

    print(f"    Failure onset at index {failure_idx} ({failure_pct:.1f}% into timeline)")
    print(f"    Pre-failure rows: {failure_idx}")
    print(f"    Post-failure rows: {len(df_asset) - failure_idx}")

    train_signal = signal.iloc[:failure_idx]
    train_flow = flow.iloc[:failure_idx]
    train_ts = timestamps.iloc[:failure_idx]

    if len(train_signal) < 2:
        print(f"    Skip: insufficient training data ({len(train_signal)} rows)")
        return

    print(f"    Training baseline with {len(train_signal)} pre-failure rows")
    print(f"      Signal training - min: {train_signal.min():.4f}, max: {train_signal.max():.4f}, mean: {train_signal.mean():.4f}")

    calc = BaselineCalculator(train_signal, training_flow=train_flow, training_timestamps=train_ts)
    calc.fit_rolling(window_hours=BASELINE_WINDOW_HOURS)
    calc.fit_hourly()
    calc.fit_state()

    baseline_result = calc.apply_hourly(timestamps, signal, num_std=BASELINE_NUM_STD)

    print("    Baseline computed")
    print(f"      Baseline - min: {baseline_result['baseline'].min():.4f}, max: {baseline_result['baseline'].max():.4f}")
    print(f"      Control limits - upper: {baseline_result['upper'].min():.4f} to {baseline_result['upper'].max():.4f}")

    detector = AnomalyDetector(baseline_result)

    print("    Running anomaly detection methods...")
    zscore_result = detector.zscore(signal, threshold=DETECTION_METHODS["Z-score"]["threshold"])
    zscore_result["flag_indices"] = np.where(zscore_result["flag"].values)[0]

    iqr_result = detector.iqr(signal, window_periods=DETECTION_METHODS["IQR"]["window_periods"], multiplier=DETECTION_METHODS["IQR"]["multiplier"])
    iqr_result["flag_indices"] = np.where(iqr_result["flag"].values)[0]

    ma_result = detector.moving_average(signal, window_periods=DETECTION_METHODS["Moving avg"]["window_periods"], threshold=DETECTION_METHODS["Moving avg"]["threshold"])
    ma_result["flag_indices"] = np.where(ma_result["flag"].values)[0]

    debug_anomaly_results("Z-score", zscore_result, signal, failure_idx, failure_idx)
    debug_anomaly_results("IQR", iqr_result, signal, failure_idx, failure_idx)
    debug_anomaly_results("Moving average", ma_result, signal, failure_idx, failure_idx)

    fig = make_subplots(
        rows=4, cols=1,
        subplot_titles=("Signal with baseline", "Z-score method", "IQR method", "Moving average method"),
        shared_xaxes=True,
        vertical_spacing=0.08,
    )

    fig.add_trace(go.Scatter(x=timestamps, y=signal.values, mode="lines",
                  name="Signal", line=dict(color="steelblue", width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=timestamps, y=baseline_result["baseline"].values, mode="lines",
                  name="Baseline", line=dict(color="red", width=2, dash="dash")), row=1, col=1)
    fig.add_trace(go.Scatter(x=timestamps, y=baseline_result["upper"].values, mode="lines",
                  name="Upper limit", line=dict(color="orange", width=1, dash="dot")), row=1, col=1)
    fig.add_trace(go.Scatter(x=timestamps, y=baseline_result["lower"].values, mode="lines",
                  name="Lower limit", line=dict(color="orange", width=1, dash="dot"), showlegend=True), row=1, col=1)

    methods = [
        (2, "Z-score", zscore_result),
        (3, "IQR", iqr_result),
        (4, "Moving average", ma_result),
    ]

    for row, method_name, result in methods:
        flag_indices = result.get("flag_indices", np.where(result["flag"])[0])

        fig.add_trace(go.Scatter(x=timestamps, y=result["severity"], mode="lines",
                      line=dict(color="gray", width=1), name=f"{method_name} severity",
                      showlegend=False), row=row, col=1)

        if len(flag_indices) > 0:
            flagged_x = timestamps.values[flag_indices]
            flagged_y = result["severity"].values[flag_indices]
            fig.add_trace(
                go.Scatter(x=flagged_x, y=flagged_y,
                          mode="markers", name=f"{method_name} anomalies",
                          marker=dict(color="red", size=5, symbol="x"),
                          showlegend=True),
                row=row, col=1
            )

    failure_timestamp = timestamps.iloc[failure_idx].isoformat()
    for row in range(1, 5):
        fig.add_vline(x=failure_timestamp, line_dash="dash", line_color="darkred",
                     line_width=2, row=row, col=1)

    fig.update_xaxes(title_text="Time", row=4, col=1)
    fig.update_yaxes(title_text=signal_col, row=1, col=1)
    fig.update_yaxes(title_text="Z-score", row=2, col=1)
    fig.update_yaxes(title_text="IQR severity", row=3, col=1)
    fig.update_yaxes(title_text="MA severity", row=4, col=1)

    fig.update_layout(
        height=1200,
        hovermode="x unified",
        title=f"{scenario_name}: {asset_id} (failure at index {failure_idx})"
    )

    filename = os.path.join(ANOMALY_DETECTION_DIR, f"{scenario_name}_{asset_id}.html")
    fig.write_html(filename)
    print(f"    Plot saved: {filename}")


# Main block

if not os.path.exists(ETL_PIPELINE_PATH):
    print(f"Error: database not found at {ETL_PIPELINE_PATH}")
    sys.exit(1)

engine = create_engine(f"sqlite:///{ETL_PIPELINE_PATH}")
df = pd.read_sql_table("historian_clean", engine, columns=ANOMALY_DETECTION_NEEDED_COLS)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

print(f"Loaded {len(df)} records")
print(f"Columns: {list(df.columns)}")
print(f"\nfailure_type unique values: {df['failure_type'].unique()}")
print(f"failure_type value counts:\n{df['failure_type'].value_counts(dropna=False)}")

print(f"\n{'='*70}")
print("DATA AVAILABILITY CHECK")
print(f"{'='*70}")
for scenario_name, signal_col, failure_type in FAILURE_SCENARIOS:
    count = len(df[df["failure_type"] == failure_type])
    print(f"{scenario_name}: {count} rows with failure_type='{failure_type}'")

print(f"\n{'='*70}")
print("ANOMALY DETECTION ON FAILURE SCENARIOS")
print(f"{'='*70}")

for scenario_name, signal_col, failure_type in FAILURE_SCENARIOS:
    detect_on_scenario(scenario_name, signal_col, failure_type, df)

print(f"\n{'='*70}")
print("ANOMALY DETECTION VALIDATION COMPLETE")
print(f"{'='*70}")
print(f"Output plots saved to: {ANOMALY_DETECTION_DIR}")
