# visualize_failure_scenarios.py
import os
import pandas as pd
import matplotlib.pyplot as plt

from historian_config import CSV_PATH, FAILURE_SCENARIOS_DIR, FAILURE_SCENARIOS

def build_scenario_info():
    """Map failure scenarios to signal names and plot labels."""
    SIGNAL_MAP = {
        "bearing": {"signal": "vibration_mm_s", "secondary": "motor_temp_c",
                     "ylabel": "Vibration (mm/s)", "secondary_ylabel": "Motor Temperature (C)"},
        "cavitation": {"signal": "diff_pressure_bar", "secondary": "flow_m3h",
                       "ylabel": "Differential Pressure (bar)", "secondary_ylabel": "Flow (m3/h)"},
        "insulation": {"signal": "motor_temp_c", "secondary": "motor_power_kw",
                       "ylabel": "Motor Temperature (C)", "secondary_ylabel": "Motor Power (kW)"},
    }
    info = {}
    for s in FAILURE_SCENARIOS:
        base = SIGNAL_MAP[s["scenario"]]
        info[s["asset_id"]] = {
            "name": s["scenario"].capitalize(),
            "scenario": s["scenario"],
            "signal": base["signal"],
            "secondary_signal": base["secondary"],
            "ylabel": base["ylabel"],
            "secondary_ylabel": base["secondary_ylabel"],
        }
    return info

def load_data(csv_path):
    """Load historian CSV, parse timestamps."""
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    return df


def get_pf_days(asset_id, full_df):
    """Return P timestamp (start of degradation) and F timestamp (end of ramp)."""
    sub = full_df[full_df["asset_id"] == asset_id]
    if sub.empty:
        return None, None
    failure_rows = sub[sub["failure_type"] != "none"]
    if failure_rows.empty:
        return None, None
    p_timestamp = failure_rows["timestamp"].min()
    for sc in FAILURE_SCENARIOS:
        if sc["asset_id"] == asset_id:
            base = full_df["timestamp"].min()
            p_ts = base + pd.Timedelta(days=sc["start_day"])
            f_ts = p_ts + pd.Timedelta(days=sc["ramp_days"])
            return p_ts, f_ts
    return p_timestamp, None


def annotate_pf(ax, p_ts, f_ts, p_label="Start of degradation (P)", f_label="Functional failure (F)"):
    """Draw vertical lines and labels for P and F events on axis."""
    if p_ts is not None:
        ax.axvline(x=p_ts, color='green', linestyle='--', linewidth=1.5, alpha=0.7)
        x_off = p_ts + pd.Timedelta(days=3) # for better reading of the text

        ax.text(x_off, ax.get_ylim()[1] * 0.95, p_label,
                rotation=90, fontsize=8, color='green',
                verticalalignment='top')
    if f_ts is not None:
        ax.axvline(x=f_ts, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
        x_off = f_ts + pd.Timedelta(days=3) # for better reading of the text
        ax.text(x_off, ax.get_ylim()[1] * 0.95, f_label,
                rotation=90, fontsize=8, color='red',
                verticalalignment='top')


def plot_scenario(df, asset_id, info, output_folder):
    """Create two-panel plot: primary and secondary signals with P-F markers"""
    sub = df[df["asset_id"] == asset_id].copy()
    if sub.empty:
        print(f"No data for asset {asset_id}, skipping.")
        return
    p_ts, f_ts = get_pf_days(asset_id, df)
    if p_ts is None:
        print(f"No P-F data for asset {asset_id}.")

    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    ax = axes[0]
    ax.plot(sub["timestamp"], sub[info["signal"]], linewidth=0.5, color='steelblue')
    ax.set_ylabel(info["ylabel"])
    ax.set_title(f"{info['name']} - {asset_id}")
    ax.grid(True, alpha=0.3)
    ax.relim()
    ax.autoscale_view()
    annotate_pf(ax, p_ts, f_ts)

    ax2 = axes[1]
    ax2.plot(sub["timestamp"], sub[info["secondary_signal"]],
             linewidth=0.5, color='darkorange')
    ax2.set_ylabel(info["secondary_ylabel"])
    ax2.set_xlabel("Time")
    ax2.grid(True, alpha=0.3)
    ax2.relim()
    ax2.autoscale_view()
    annotate_pf(ax2, p_ts, f_ts, p_label="", f_label="")

    fig.autofmt_xdate()
    plt.tight_layout()
    out_path = os.path.join(output_folder, f"{asset_id}_failure_scenario.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"  Saved: {out_path}")


if __name__ == "__main__":
    os.makedirs(FAILURE_SCENARIOS_DIR, exist_ok=True)
    print("Loading data...")
    df = load_data(CSV_PATH)
    scenario_info = build_scenario_info()
    for asset_id, info in scenario_info.items():
        print(f"Plotting {info['name']}...")
        plot_scenario(df, asset_id, info, FAILURE_SCENARIOS_DIR)
    print("Done.")