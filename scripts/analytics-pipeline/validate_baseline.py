# validate_baseline.py
import os
import sys
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from baseline import BaselineCalculator

WINDOW_HOURS = 24
NUM_STD = 3
SIGNAL_COLS = ["flow_m3h", "vibration_mm_s"]

NEEDED_COLS = ["asset_id", "timestamp", "failure_type",
               "flow_m3h", "vibration_mm_s"]
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output", "baseline_validation")
os.makedirs(output_dir, exist_ok=True)

db_path = os.path.join(script_dir, "..", "etl-pipeline", "output", "etl_pipeline.db")

if not os.path.exists(db_path):
    print(f"Error: database not found at {db_path}")
    sys.exit(1)

engine = create_engine(f"sqlite:///{db_path}")
df = pd.read_sql_table("historian_clean", engine, columns=NEEDED_COLS)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

print(f"Loaded {len(df)} records")
print(f"Columns: {list(df.columns)}")
print(f"\nfailure_type unique values: {df['failure_type'].unique()}")
print(f"failure_type value counts:\n{df['failure_type'].value_counts(dropna=False)}")
print(f"Missing in failure_type: {df['failure_type'].isna().sum()}")

healthy_mask = df["failure_type"].isna() | df["failure_type"].isin(["none", "None", "pass", "", "N/A", "NA"])
degrading_mask = ~healthy_mask

print(f"\nHealthy records: {healthy_mask.sum()}")
print(f"Degrading records: {degrading_mask.sum()}")

if not healthy_mask.any():
    print("Error: no healthy assets found")
    sys.exit(1)
if not degrading_mask.any():
    print("Error: no degrading assets found")
    sys.exit(1)

all_healthy_assets = df[healthy_mask]["asset_id"].unique()
all_degrading_assets = df[degrading_mask]["asset_id"].unique()
print(f"\nHealthy asset IDs: {all_healthy_assets}")
print(f"Degrading asset IDs: {all_degrading_assets}")

# Assets completely healthy
pure_healthy_assets = [asset for asset in all_healthy_assets if (df[df["asset_id"] == asset]["failure_type"] == "none").all()]

# Assets that have at least one failure:
any_failure_assets = [asset for asset in all_degrading_assets if not (df[df["asset_id"] == asset]["failure_type"] == "none").all()]

if not pure_healthy_assets:
    print("Error: no asset with entirely normal operation found")
    sys.exit(1)
if not any_failure_assets:
    print("Error: no asset with any failure found")
    sys.exit(1)

# Pick first healthy asset and first degrading asset that is NOT the same
healthy_asset = pure_healthy_assets[0]
degrading_asset = any_failure_assets[0]
if healthy_asset == degrading_asset:
    # If the first ones are the same, take the next degrading asset
    degrading_asset = any_failure_assets[1] if len(any_failure_assets) > 1 else None
    if degrading_asset is None:
        print("Error: could not find a distinct degrading asset")
        sys.exit(1)

# for healthy asset, keep only normal rows
df_healthy = df[(df["asset_id"] == healthy_asset) & (df["failure_type"] == "none")].reset_index(drop=True)

# for degrading asset, keep all rows (including the failure period)
df_degrading = df[df["asset_id"] == degrading_asset].reset_index(drop=True)

# Find first failure index in degrading asset
degrading_failure_mask = df_degrading["failure_type"] != "none"
failure_idx = degrading_failure_mask.idxmax() if degrading_failure_mask.any() else None

if failure_idx is None:
    print(f"Warning: no failure found in degrading asset {degrading_asset}, using last index")
    failure_idx = len(df_degrading) - 1

failure_pct = 100 * failure_idx / len(df_degrading)

print(f"\n{'='*70}")
print("ASSET SELECTION")
print(f"{'='*70}")
print(f"Healthy asset: {healthy_asset} ({len(df_healthy)} rows, all failure_type='none')")
print(f"Degrading asset: {degrading_asset} ({len(df_degrading)} rows total)")
print(f"   Failure onset at index {failure_idx} ({failure_pct:.1f}% into timeline)")
print(f"   Pre-failure rows: {failure_idx}")
print(f"   Post-failure rows: {len(df_degrading) - failure_idx}")

failure_types_in_degrading = df_degrading["failure_type"].value_counts()
print(f"   Failure types in degrading asset:\n{failure_types_in_degrading}")


def debug_baseline_results(method_name, result_dict, signal, failure_idx=None, pre_failure_idx=None):
    baseline = result_dict["baseline"]
    upper = result_dict["upper"]
    lower = result_dict["lower"]

    print(f"\n  {method_name.upper()} BASELINE RESULTS:")
    print(f"   Baseline: min={baseline.min():.4f}, max={baseline.max():.4f}, mean={baseline.mean():.4f}")
    print(f"   Baseline NaN count: {baseline.isna().sum()}")
    print(f"   Upper limit NaN count: {upper.isna().sum()}")
    print(f"   Lower limit NaN count: {lower.isna().sum()}")

    violations = ((signal < lower) | (signal > upper)).sum()
    violation_pct = 100 * violations / len(signal)
    print(f"    Signal violations (outside limits): {violations} ({violation_pct:.2f}%)")

    if failure_idx is not None and pre_failure_idx is not None:
        signal_pre = signal.iloc[:pre_failure_idx]
        baseline_pre = baseline.iloc[:pre_failure_idx]
        upper_pre = upper.iloc[:pre_failure_idx]
        lower_pre = lower.iloc[:pre_failure_idx]
        violations_pre = ((signal_pre < lower_pre) | (signal_pre > upper_pre)).sum()

        # Stats after failure
        signal_post = signal.iloc[pre_failure_idx:]
        baseline_post = baseline.iloc[pre_failure_idx:]
        upper_post = upper.iloc[pre_failure_idx:]
        lower_post = lower.iloc[pre_failure_idx:]
        violations_post = ((signal_post < lower_post) | (signal_post > upper_post)).sum()

        print("    PRE-FAILURE:")
        print(f"      Signal range: {signal_pre.min():.4f} to {signal_pre.max():.4f}")
        print(f"      Baseline mean: {baseline_pre.mean():.4f}")
        print(f"      Violations: {violations_pre} ({100*violations_pre/len(signal_pre):.2f}%)")
        print("    POST-FAILURE:")
        print(f"      Signal range: {signal_post.min():.4f} to {signal_post.max():.4f}")
        print(f"      Baseline mean: {baseline_post.mean():.4f}")
        print(f"      Violations: {violations_post} ({100*violations_post/len(signal_post):.2f}%)")
        print(f"      Violation increase: {violations_post - violations_pre} rows")


def plot_baselines(asset_id, signal_col, data, failure_idx=None, suffix="", is_healthy=False):

    if signal_col not in data.columns or "flow_m3h" not in data.columns:
        print(f"  skip {signal_col}: missing column")
        return

    signal = data[signal_col]
    flow = data["flow_m3h"]
    timestamps = pd.to_datetime(data["timestamp"])

    if signal.isna().all() or flow.isna().all():
        print(f"  skip {signal_col}: all NaN")
        return

    signal = signal.fillna(signal.mean())
    flow = flow.fillna(flow.mean())

    print(f"\n  {signal_col}:")
    print(f"   Full signal: min={signal.min():.4f}, max={signal.max():.4f}, mean={signal.mean():.4f}, std={signal.std():.4f}")

    if failure_idx is not None and not is_healthy:
        train_signal = signal.iloc[:failure_idx]
        train_flow = flow.iloc[:failure_idx]
        train_ts = timestamps.iloc[:failure_idx]
        print(f"   Training (pre-failure): {len(train_signal)} rows")
        print(f"     Signal: min={train_signal.min():.4f}, max={train_signal.max():.4f}, mean={train_signal.mean():.4f}")
    else:
        train_signal = signal
        train_flow = flow
        train_ts = timestamps
        print(f"   Training (entire healthy asset): {len(train_signal)} rows")
        print(f"     Signal: min={train_signal.min():.4f}, max={train_signal.max():.4f}, mean={train_signal.mean():.4f}")

    calc = BaselineCalculator(train_signal, training_flow=train_flow, training_timestamps=train_ts)
    calc.fit_rolling(window_hours=WINDOW_HOURS)
    calc.fit_hourly()
    calc.fit_state()

    calc.debug_summary("rolling")
    calc.debug_summary("hourly")
    calc.debug_summary("state")

    rolling = calc.apply_rolling(signal, num_std=NUM_STD)
    hourly = calc.apply_hourly(timestamps, signal, num_std=NUM_STD)
    state = calc.apply_state(flow, signal, num_std=NUM_STD)

    debug_baseline_results("rolling", rolling, signal, failure_idx=failure_idx, pre_failure_idx=failure_idx if not is_healthy else None)
    debug_baseline_results("hourly", hourly, signal, failure_idx=failure_idx, pre_failure_idx=failure_idx if not is_healthy else None)
    debug_baseline_results("state", state, signal, failure_idx=failure_idx, pre_failure_idx=failure_idx if not is_healthy else None)

    fig = make_subplots(rows=3, cols=1, subplot_titles=("Rolling (24h)", "Hourly adjusted", "State conditioned"), shared_xaxes=True, vertical_spacing=0.1,)

    methods = [("rolling", rolling), ("hourly", hourly),("state", state),]

    for row, (method_name, result) in enumerate(methods, start=1):
        fig.add_trace(
            go.Scatter(x=data["timestamp"], y=signal.values, mode="lines",
                      name="Signal", line=dict(color="steelblue", width=1),
                      showlegend=(row == 1)),
            row=row, col=1
        )

        fig.add_trace(
            go.Scatter(x=data["timestamp"], y=result["baseline"].values, mode="lines",
                      name="Baseline", line=dict(color="red", width=2, dash="dash"),
                      showlegend=(row == 1)),
            row=row, col=1
        )

        fig.add_trace(
            go.Scatter(x=data["timestamp"], y=result["upper"].values, mode="lines",
                      name="Control limits", line=dict(color="orange", width=1, dash="dot"),
                      showlegend=(row == 1)),
            row=row, col=1
        )

        fig.add_trace(
            go.Scatter(x=data["timestamp"], y=result["lower"].values, mode="lines",
                      line=dict(color="orange", width=1, dash="dot"), showlegend=False),
            row=row, col=1
        )

        if failure_idx is not None and not is_healthy:
            failure_timestamp = data["timestamp"].iloc[failure_idx].isoformat()
            fig.add_vline(x=failure_timestamp, line_dash="dash", line_color="red", line_width=2, row=row, col=1)

    fig.update_xaxes(title_text="Time", row=3, col=1)
    fig.update_layout(title=f"{asset_id} - {signal_col}", height=900, hovermode="x unified")

    filename = os.path.join(output_dir, f"{asset_id}_{signal_col}{suffix}.html")
    fig.write_html(filename)
    print(f"   Plot saved: {filename}")


print(f"\n{'='*70}")
print(f"HEALTHY ASSET: {healthy_asset}")
print(f"{'='*70}")
for signal_col in SIGNAL_COLS:
    plot_baselines(healthy_asset, signal_col, df_healthy, suffix="_healthy", is_healthy=True)

print(f"\n{'='*70}")
print(f"DEGRADING ASSET: {degrading_asset} (Failure at index {failure_idx})")
print(f"{'='*70}")
for signal_col in SIGNAL_COLS:
    plot_baselines(degrading_asset, signal_col, df_degrading, failure_idx=failure_idx, suffix="_degrading", is_healthy=False)

print(f"\n{'='*70}")
print("BASELINE VALIDATION COMPLETE")
print(f"{'='*70}")
print(f"Output plots saved to: {output_dir}")