# validate_synthetic_data.py
"""Validate synthetic pump historian data

Generates diagnostic plots, prints signal statistics, runs physical plausibility checks,
and performs Welch's t-test for weekday/weekend demand reduction.
Reads the CSV produced by historian_generator.py.
"""
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import ttest_ind

SIG_COLS = [
    "flow_m3h", "suction_pressure_bar", "disch_pressure_bar",
    "diff_pressure_bar", "motor_temp_c", "motor_power_kw",
    "vibration_mm_s", "speed_rpm"
]
DOW_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def welch_ttest(a, b):
    n1, n2 = len(a), len(b)
    m1, m2 = a.mean(), b.mean()
    s1, s2 = a.std(ddof=1), b.std(ddof=1)
    diff = m2 - m1
    t_stat, p_value = ttest_ind(a, b, equal_var=False)
    num = (s1**2 / n1 + s2**2 / n2)**2
    den = (s1**2 / n1)**2 / (n1 - 1) + (s2**2 / n2)**2 / (n2 - 1)
    df_welch = num / den if den > 0 else n1 + n2 - 2
    return diff, t_stat, df_welch, p_value, m1, m2, s1, s2, n1, n2


def print_signal_stats(df):
    print("-"*40)
    print("\nSignal Statistics:")
    for col in SIG_COLS:
        s = df[col]
        print(f"{col:25s}  mean={s.mean():10.3f}  min={s.min():10.3f}  max={s.max():10.3f}  std={s.std():10.3f}")


def print_plausibility_checks(df):
    print("-"*40)
    print("\nPhysical Plausibility Checks:")

    failures = []
    for aid in df["asset_id"].unique():
        if aid == "P-0700":
            continue
        sub = df[df["asset_id"] == aid]
        if not (sub["disch_pressure_bar"] > sub["suction_pressure_bar"]).all():
            failures.append(aid)
    if failures:
        print(f"Assets with discharge <= suction: {failures}")
    else:
        print("Discharge > suction pressure across all rows: ok")


    for aid in df["asset_id"].unique():
        sub = df[df["asset_id"] == aid]
        neg_dp = (sub["diff_pressure_bar"] <= 0).sum()
        if neg_dp > 0:
            print(f"  {aid}: {neg_dp} rows with diff_pressure <= 0 (check cavitation spikes)")
        else:
            print(f"  {aid}: differential pressure always positive")


    print()

    corr_f_dp = df["flow_m3h"].corr(df["diff_pressure_bar"])
    corr_f_pw = df["flow_m3h"].corr(df["motor_power_kw"])
    corr_f_v = df["flow_m3h"].corr(df["vibration_mm_s"])
    corr_p_t = df["motor_power_kw"].corr(df["motor_temp_c"])
    print(f"Flow vs dP: {corr_f_dp:.3f} (expected negative -- pump curve)")
    print(f"Flow vs Power: {corr_f_pw:.3f} (expected positive)")
    print(f"Flow vs Vibration: {corr_f_v:.3f} (expected weak linear)")
    print(f"Power vs Temp: {corr_p_t:.3f} (expected positive)")

    t_min, t_max = df["motor_temp_c"].min(), df["motor_temp_c"].max()
    print(f"Motor temp range: {t_min:.1f} to {t_max:.1f} C (expected 15-95 C)")
    v_min, v_max = df["vibration_mm_s"].min(), df["vibration_mm_s"].max()
    print(f"Vibration range: {v_min:.4f} to {v_max:.4f} mm/s (expected 0.01-0.5)")

    s_std = df["speed_rpm"].std()

    nominal_speed = df["speed_rpm"].median()
    pct = s_std / nominal_speed * 100
    print(f"Speed std dev: {s_std:.2f} RPM ({pct:.2f}% of nominal, expected ~0.2%)")


def print_day_night_weekday_weekend(df):
    print("-"*40)
    df["hour"] = df["timestamp"].dt.hour
    day_flow = df[df["hour"].between(8, 20)]["flow_m3h"].mean()
    night_flow = df[df["hour"].between(0, 5)]["flow_m3h"].mean()
    print(f"Day flow mean: {day_flow:.1f}, Night flow mean: {night_flow:.1f} (ratio={day_flow / night_flow:.2f})")

    df["dow"] = df["timestamp"].dt.dayofweek
    weekday_flow = df[df["dow"] < 5]["flow_m3h"].mean()
    weekend_flow = df[df["dow"] >= 5]["flow_m3h"].mean()
    print(f"Weekday flow mean: {weekday_flow:.1f}, Weekend flow mean: {weekend_flow:.1f} (ratio={weekday_flow / weekend_flow:.2f})")


def print_weekly_ttest(df):
    print("-"*40)
    df["dow"] = df["timestamp"].dt.dayofweek
    weekday = df[df["dow"] < 5]["flow_m3h"]
    weekend = df[df["dow"] >= 5]["flow_m3h"]
    diff, t_stat, df_w, p_val, m1, m2, s1, s2, n1, n2 = welch_ttest(weekday, weekend)

    print("\nWeekly Pattern Statistical Test:")
    print(f"Weekday: n={n1}, mean={m1:.2f} m3/h, std={s1:.2f}")
    print(f"Weekend: n={n2}, mean={m2:.2f} m3/h, std={s2:.2f}")
    print(f"Difference (weekend - weekday): {diff:.2f} m3/h ({diff / m1 * 100:.1f}%)")
    print(f"Welch t({df_w:.1f}) = {t_stat:.3f}, p = {p_val:.2e}")
    if p_val < 0.001:
        print("  -> Statistically significant (p < 0.001)")
    elif p_val < 0.05:
        print("  -> Statistically significant (p < 0.05)")
    else:
        print("  -> Not statistically significant (p >= 0.05)")

def print_failures(df):
    print("-"*40)
    if "failure_type" in df.columns:
        print("Failure type column exists")
        for ft in df["failure_type"].unique():
            if ft != "none":
                count = (df["failure_type"] == ft).sum()
                print(f"    {ft}: {count} rows")
    else:
        print("No failure_type column")

def plot_timeseries(df, asset_name, model_name, validation_folder):
    week1 = df[df["timestamp"] < df["timestamp"].iloc[0] + pd.Timedelta(days=7)]
    fig, axes = plt.subplots(4, 2, figsize=(16, 12), sharex=True)
    signals = [
        ("flow_m3h", "Flow Rate (m3/h)", axes[0, 0]),
        ("suction_pressure_bar", "Suction Pressure (bar)", axes[0, 1]),
        ("disch_pressure_bar", "Discharge Pressure (bar)", axes[1, 0]),
        ("diff_pressure_bar", "Differential Pressure (bar)", axes[1, 1]),
        ("motor_temp_c", "Motor Temperature (C)", axes[2, 0]),
        ("motor_power_kw", "Motor Power (kW)", axes[2, 1]),
        ("vibration_mm_s", "Vibration (mm/s)", axes[3, 0]),
        ("speed_rpm", "Pump Speed (RPM)", axes[3, 1]),
    ]
    for col, label, ax in signals:
        ax.plot(week1["timestamp"], week1[col], linewidth=0.5, alpha=0.8)
        ax.set_ylabel(label)
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    fig.suptitle(f"7-Day Time Series -- {asset_name} ({model_name})")
    plt.tight_layout()
    plt.savefig(os.path.join(validation_folder, f"{asset_name}_timeseries.png"), dpi=150)
    plt.close()


def plot_pump_curve(df, asset_name, model_name, validation_folder):
    fig, ax = plt.subplots(figsize=(8, 6))
    sample = df.iloc[::100]
    scatter = ax.scatter(sample["flow_m3h"], sample["diff_pressure_bar"],
                        c=sample["vibration_mm_s"], cmap="viridis",
                        s=10, alpha=0.6)
    ax.set_xlabel("Flow Rate (m3/h)")
    ax.set_ylabel("Differential Pressure (bar)")
    ax.set_title(f"Pump Curve -- {asset_name} ({model_name})")
    plt.colorbar(scatter, label="Vibration (mm/s)")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(validation_folder, f"{asset_name}_pump_curve.png"), dpi=150)
    plt.close()


def plot_correlation_matrix(df, asset_name, validation_folder):
    fig, ax = plt.subplots(figsize=(10, 8))
    corr = df[SIG_COLS].corr()
    mask = np.triu(np.ones_like(corr), k=1)
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
                vmin=-1, vmax=1, center=0, square=True, ax=ax)
    ax.set_title(f"Signal Correlation Matrix -- {asset_name}")
    plt.tight_layout()
    plt.savefig(os.path.join(validation_folder, f"{asset_name}_correlation.png"), dpi=150)
    plt.close()


def plot_diurnal_profiles(df, asset_name, model_name, validation_folder):
    # Hourly profiles for flow, power, temp + vibration vs flow.
    df["hour"] = df["timestamp"].dt.hour
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    hourly_flow = df.groupby("hour")["flow_m3h"].agg(["mean", "std"])
    axes[0, 0].plot(hourly_flow.index, hourly_flow["mean"], "b-", linewidth=2)
    axes[0, 0].fill_between(hourly_flow.index,
                           hourly_flow["mean"] - hourly_flow["std"],
                           hourly_flow["mean"] + hourly_flow["std"], alpha=0.2)
    axes[0, 0].set_title("Flow (m3/h) -- Diurnal Profile")
    axes[0, 0].set_xlabel("Hour of Day")
    axes[0, 0].grid(True, alpha=0.3)

    hourly_pwr = df.groupby("hour")["motor_power_kw"].agg(["mean", "std"])
    axes[0, 1].plot(hourly_pwr.index, hourly_pwr["mean"], "r-", linewidth=2)
    axes[0, 1].fill_between(hourly_pwr.index,
                           hourly_pwr["mean"] - hourly_pwr["std"],
                           hourly_pwr["mean"] + hourly_pwr["std"], alpha=0.2)
    axes[0, 1].set_title("Motor Power (kW) -- Diurnal Profile")
    axes[0, 1].set_xlabel("Hour of Day")
    axes[0, 1].grid(True, alpha=0.3)

    hourly_temp = df.groupby("hour")["motor_temp_c"].agg(["mean", "std"])
    axes[1, 0].plot(hourly_temp.index, hourly_temp["mean"], "orange", linewidth=2)
    axes[1, 0].fill_between(hourly_temp.index,
                           hourly_temp["mean"] - hourly_temp["std"],
                           hourly_temp["mean"] + hourly_temp["std"], alpha=0.2)
    axes[1, 0].set_title("Motor Temp (C) -- Diurnal Profile")
    axes[1, 0].set_xlabel("Hour of Day")
    axes[1, 0].grid(True, alpha=0.3)

    # Vibration vs flow -- U-shape expected, minimum at BEP
    df["flow_bin"] = pd.cut(df["flow_m3h"], bins=20)
    vib_by_flow = df.groupby("flow_bin", observed=False)["vibration_mm_s"].mean()
    bin_centers = [(b.left + b.right) / 2 for b in vib_by_flow.index]
    axes[1, 1].plot(bin_centers, vib_by_flow.values, "g.-", linewidth=2)
    axes[1, 1].set_title("Vibration vs Flow (min at BEP)")
    axes[1, 1].set_xlabel("Flow Rate (m3/h)")
    axes[1, 1].set_ylabel("Mean Vibration (mm/s)")
    axes[1, 1].grid(True, alpha=0.3)

    fig.suptitle(f"Signal Profiles -- {asset_name} ({model_name})")
    plt.tight_layout()
    plt.savefig(os.path.join(validation_folder, f"{asset_name}_profiles.png"), dpi=150)
    plt.close()


def plot_weekly_bars(df, asset_name, validation_folder):
    df["dow"] = df["timestamp"].dt.dayofweek
    daily_flow = df.groupby("dow")["flow_m3h"].mean()

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(DOW_LABELS, daily_flow.values, color="steelblue", alpha=0.8)
    ax.set_ylabel("Mean Flow (m3/h)")
    ax.set_title(f"Weekly Flow Profile -- {asset_name}")
    ax.grid(True, alpha=0.3, axis="y")
    for i in [5, 6]:
        bars[i].set_color("coral")
    plt.tight_layout()
    plt.savefig(os.path.join(validation_folder, f"{asset_name}_weekly.png"), dpi=150)
    plt.close()


def run_validation(df, asset_name="P-0100", model_name="NK 32-125"):
    print(f"\n{'=' * 60}")
    print(f"VALIDATION -- {asset_name} ({model_name})")
    print(f"Rows: {len(df):,}   Period: {df['timestamp'].max() - df['timestamp'].min()}")
    print(f"{'=' * 60}")

    validation_folder = "validation"
    os.makedirs(validation_folder, exist_ok=True)

    print_signal_stats(df)
    print_plausibility_checks(df)
    print_day_night_weekday_weekend(df)
    print_weekly_ttest(df)
    print_failures(df)

    plot_timeseries(df, asset_name, model_name, validation_folder)
    plot_pump_curve(df, asset_name, model_name, validation_folder)
    plot_correlation_matrix(df, asset_name, validation_folder)
    plot_diurnal_profiles(df, asset_name, model_name, validation_folder)
    plot_weekly_bars(df, asset_name, validation_folder)
    print("All plots saved.")


if __name__ == "__main__":
    csv_path = "output/synthetic_historian_10x365_1min.csv"

    print(f"Loading CSV: {csv_path}")
    df = pd.read_csv(
        csv_path,
        parse_dates=["timestamp"],
        dtype={"asset_id": "category", "flow_m3h": "float32"}
    )

    # # Validate first asset (P-0100, NK 32-125)
    # asset_df = df[df["asset_id"] == "P-0100"].copy()
    # run_validation(asset_df, asset_name="P-0100", model_name="NK 32-125")

    # Validate all assets
    for asset_id in df["asset_id"].cat.categories:
        asset_df = df[df["asset_id"] == asset_id].copy()
        model_name = asset_df["pump_model"].iloc[0]
        run_validation(asset_df, asset_name=asset_id, model_name=model_name)