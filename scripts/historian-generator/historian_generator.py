# historian_generator.py
"""Generate synthetic pump historian data for predictive maintenance

Outputs a CSV with 10 pump assets x 1 year of 1-min SCADA-like signals
(flow, pressures, temperature, power, vibration, speed). Signal patterns
include diurnal/seasonal demand cycles, weekday/weekend reduction,
pump curve physics, and thermal inertia.

Pump curves from Grundfos NK/NKE databooklet:
https://www.motralec.com/public/fichiers/docs/grundfos-nke-nk-english.pdf
Performance range: 2-2000 m3/h, 2-150 m head, 0.37-315 kW motors

Notes:
1) All pressure values are gauge pressure (relative to 1 atm absolute).
Conversion: discharge_gauge = suction_gauge + (head_m * 0.0981)
NPSHa must be calculated using absolute pressure: P_abs = P_gauge + 1.013

2) Vibration baseline: constant healthy-bearing signal; degradation scenarios inject
bearing wear, cavitation, or insulation faults as multiplicative ramps with increasing noise.
"""

import numpy as np
import pandas as pd
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import sqlite3

from historian_config import (OUTPUT_DIR, CSV_PATH, DB_PATH, FAILURE_SCENARIOS,
                              UNIT_MISMATCH_ASSET, THERMAL_TAU_MIN, PUMP_CURVES,
                              BASE_TIME, NUM_ASSETS, PERIOD_DAYS, FREQ_MIN,
                              NOISE_LEVEL, DRIFT_RATE, SEASON_AMP, SEED,
                              GAP_FRACTION, DUPLICATE_PER_ASSET, AREAS)
@dataclass
class HistorianConfig:
    num_assets: int = NUM_ASSETS
    period_days: int = PERIOD_DAYS
    freq_min: int = FREQ_MIN
    noise_level: float = NOISE_LEVEL
    drift_rate: float = DRIFT_RATE
    season_amp: float = SEASON_AMP
    base_time: datetime = field(default_factory=lambda: BASE_TIME)
    seed: int = SEED
    failure_scenarios: list = field(default_factory=list)
    gap_fraction: float = GAP_FRACTION
    duplicate_per_asset: int = DUPLICATE_PER_ASSET
    unit_mismatch_asset: str = UNIT_MISMATCH_ASSET
    thermal_tau_min: float = THERMAL_TAU_MIN

    def __post_init__(self):
        assert self.num_assets >= 1, "num_assets must be >= 1"
        assert self.period_days >= 1, "period_days must be >= 1"
        assert self.freq_min >= 1, "freq_min must be >= 1"
        assert 0 <= self.noise_level <= 0.5, "noise_level out of range"
        assert 0 <= self.drift_rate <= 0.1, "drift_rate out of range"
        assert 0 <= self.season_amp <= 0.5, "season_amp out of range"
        self.n_samples = self.period_days * 24 * 60 // self.freq_min
        self.time_index = [self.base_time + timedelta(minutes=i * self.freq_min)
                          for i in range(self.n_samples)]


def _daily_pattern(t_hours):
    """Sine wave peaks around 14:00, troughs around 02:00"""
    raw = np.sin(np.pi * (t_hours - 6) / 12)
    raw = np.clip(raw, -1, 1)
    scaled = (raw + 1) / 2
    return scaled


def _weekly_pattern(t_days, base_time):
    """Weekend factor = 0.85 (15% demand reduction Sat-Sun)"""
    offset = base_time.weekday()  # 0=Mon, 1=Tue, ..., 6=Sun
    dow = (t_days + offset) % 7
    return np.where(dow >= 5, 0.85, 1.0)


def _seasonal_pattern(t_days, period_days, amp):
    """Sinusoidal annual cycle: +/-amp% around 0.7 baseline"""
    phase = 2 * np.pi * t_days / period_days
    return 0.7 + amp * np.sin(phase - np.pi / 2)


def _drift(t_days, rate):
    """Linear multiplicative drift per day"""
    return 1.0 + rate * t_days


def generate_flow(asset, t_hours, t_days, config, rng):
    """Combine diurnal, weekly, seasonal patterns with noise and drift"""
    diurnal = _daily_pattern(t_hours)
    weekly = _weekly_pattern(t_days, config.base_time)
    seasonal = _seasonal_pattern(t_days, config.period_days, config.season_amp)
    drift_val = _drift(t_days, config.drift_rate)
    noise = rng.normal(0, config.noise_level, size=len(t_hours))
    base = asset["nominal_flow_m3h"] * 0.8
    variation = 0.3 + 0.4 * diurnal
    flow = base * (0.5 + variation * weekly * seasonal * drift_val + noise)
    flow = np.clip(flow, asset["nominal_flow_m3h"] * 0.1, asset["nominal_flow_m3h"] * 1.1)
    return flow


def generate_suction_pressure(asset, flow, config, rng):
    """Base pressure minus friction losses increasing with flow"""
    base_p = asset["suction_pressure_bar"]
    flow_frac = flow / asset["nominal_flow_m3h"]
    # Friction losses increase slightly with flow
    friction_drop = 0.05 * np.maximum(flow_frac - 0.5, 0.0) # Keeps friction_loss at zero below 50% flow, then ramps linearly
    noise = rng.normal(0, 0.01, size=len(flow))
    p = base_p - friction_drop + noise
    p = np.clip(p, base_p * 0.7, base_p * 1.3)
    return p


def generate_discharge_pressure(asset, flow, config, rng):
    """Head curve physics: head decreases with flow, convert to bar."""
    head_m = asset["nominal_head_m"]
    flow_frac = flow / asset["nominal_flow_m3h"]
    # Head decreases as flow increases (pump curve characteristic)
    head_factor = 1.15 - 0.18 * flow_frac
    head_factor = np.clip(head_factor, 0.75, 1.15)
    head_actual = head_m * head_factor
    p_bar = head_actual * 0.0981 + asset["suction_pressure_bar"]
    noise = rng.normal(0, 0.02, size=len(flow))
    p = p_bar + noise
    p = np.clip(p, asset["suction_pressure_bar"] * 1.1, None)
    return p


def generate_diff_pressure(disch_p, suction_p):
    """Differential pressure: discharge minus suction."""
    return disch_p - suction_p


def generate_motor_power(asset, flow, diff_p, config, rng):
    """Hydraulic power divided by efficiency curve"""
    flow_frac = flow / asset["nominal_flow_m3h"]
    # Quadratic efficiency curve, peaks near 85% of nominal flow
    efficiency = 0.85 - 0.3 * (flow_frac - 0.85)**2
    efficiency = np.clip(efficiency, 0.4, 0.88)
    # Hydraulic power: P_hyd = Q * dP. 1 m3/h * 1 bar = 0.02778 kW
    hyd_power = flow * diff_p * 0.02778
    mech_power = hyd_power / efficiency
    noise = rng.normal(0, 0.02 * asset["motor_power_kw"], size=len(flow))
    power = mech_power + noise
    power = np.clip(power, asset["motor_power_kw"] * 0.05, asset["motor_power_kw"] * 1.1)
    return power


def generate_motor_temp(t_days, power, asset, config, rng):
    """Ambient plus power-dependent temperature rise."""
    ambient = 15 + 10 * _seasonal_pattern(t_days, config.period_days, config.season_amp)
    power_frac = power / asset["motor_power_kw"]
    temp_rise = 30 * power_frac
    temp_raw = ambient + temp_rise
    noise = rng.normal(0, 0.3, size=len(power))
    temp = temp_raw + noise
    temp = np.clip(temp, ambient, 95)
    return temp


def generate_vibration(asset, flow, config, rng):
    """Baseline healthy signal: small constant plus noise"""
    base_vib = 0.04
    noise = rng.normal(0, 0.001, size=len(flow))
    vib = base_vib + noise
    vib = np.clip(vib, 0.01, 0.5)
    return vib


def generate_speed(asset, t_hours, config, rng):
    """Nominal RPM with small variation"""
    base_rpm = asset["speed_rpm"]
    variation = rng.normal(0, base_rpm * 0.002, size=len(t_hours))
    speed = base_rpm + variation
    speed = np.clip(speed, base_rpm * 0.95, base_rpm * 1.05)
    return speed


def apply_thermal_inertia(signal, tau_min, dt_min):
    """First-order low-pass filter simulating thermal mass"""
    alpha = 1 - np.exp(-dt_min / tau_min)
    filtered = np.zeros_like(signal)
    filtered[0] = signal[0]
    for i in range(1, len(signal)):
        filtered[i] = filtered[i-1] + alpha * (signal[i] - filtered[i-1])
    return filtered


# Failure scenario injection functions
def inject_bearing_degradation(signal_vibration, signal_temp, t_days, start_day, ramp_days, final_severity, rng):
    """Vibration ramp with delayed temperature rise.
    noise only applied during degradation window, proportional to ramp"""

    n = len(t_days)
    ramp = np.ones(n)
    mask = t_days >= start_day
    if not mask.any():
        return signal_vibration, signal_temp

    t_rel = (t_days[mask] - start_day) / ramp_days
    t_rel = np.clip(t_rel, 0, 1)

    # LINEAR RAMP:
    ramp[mask] = 1.0 + (final_severity - 1.0) * t_rel

    # EXPONENTIAL RAMP:
    # ramp[mask] = 1.0 + (final_severity - 1.0) * (np.exp(2 * t_rel) - 1) / (np.exp(2) - 1)

    noise = np.zeros(n)
    noise[mask] = rng.normal(0, 0.002 * ramp[mask], size=mask.sum())
    signal_vibration = signal_vibration * ramp + noise
    signal_vibration = np.clip(signal_vibration, 0.01, 2.0)

    # dalayed effect: temperature rise only after 60% of ramp
    temp_start = start_day + 0.6 * ramp_days
    t_rel_temp = np.clip((t_days - temp_start) / ramp_days, 0, 1)
    temp_drift = 5.0 * final_severity * t_rel_temp
    signal_temp = signal_temp + temp_drift

    signal_temp = np.clip(signal_temp, 15, 120)

    return signal_vibration, signal_temp


def inject_cavitation(signal_flow, signal_diff_p, signal_vibration, t_days, start_day, ramp_days, final_severity, rng):
    """Periodic spikes in differential pressure, flow instability, increasing vibration.
    P-F lead time: weeks to months (days if severe)
    """
    n = len(t_days)
    mask = t_days >= start_day
    if not mask.any():
        return signal_flow, signal_diff_p, signal_vibration

    t_rel = (t_days - start_day) / ramp_days
    t_rel = np.clip(t_rel, 0, 1)

    spike_amp = 0.1 * final_severity * t_rel
    spike_prob = 0.001 * (1 + 5 * t_rel)
    spikes = rng.uniform(0, 1, size=n) < spike_prob

    spike_val = spike_amp * rng.normal(0, 1, size=n) * spikes
    signal_diff_p = signal_diff_p + spike_val

    flow_noise = 0.05 * final_severity * t_rel * signal_flow.std() * rng.normal(0, 1, size=n)
    signal_flow = signal_flow + flow_noise
    signal_flow = np.clip(signal_flow, 0.1, signal_flow.max() * 1.1)

    vib_ramp = 1.0 + (final_severity - 1.0) * t_rel
    noise_vib = rng.normal(0, 0.01 * vib_ramp, size=n)
    signal_vibration = signal_vibration * vib_ramp + noise_vib
    signal_vibration = np.clip(signal_vibration, 0.01, 2.0)

    return signal_flow, signal_diff_p, signal_vibration


def inject_insulation_degradation(signal_temp, signal_power, t_days, start_day, ramp_days, final_severity, rng):
    """Slow drift in motor temperature and gradual increase in power draw at same flow.
    P-F lead time: months to years
    """
    n = len(t_days)
    mask = t_days >= start_day
    if not mask.any():
        return signal_temp, signal_power

    t_rel = (t_days - start_day) / ramp_days
    t_rel = np.clip(t_rel, 0, 1)

    temp_drift = 5 * final_severity * t_rel
    signal_temp = signal_temp + temp_drift
    signal_temp = np.clip(signal_temp, 15, 110)

    power_ramp = 1.0 + 0.15 * (final_severity - 1.0) * t_rel
    noise_power = rng.normal(0, 0.01 * power_ramp, size=n)
    signal_power = signal_power * power_ramp + noise_power
    signal_power = np.clip(signal_power, 0, signal_power.max() * 1.2)

    return signal_temp, signal_power

class SyntheticHistorian:
    """Generate synthetic time series signals for all configured pump assets."""
    def __init__(self, config: HistorianConfig):
        """Initialize assets from pump curves, compute time index"""
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        self.assets = []
        for i in range(config.num_assets):
            pump = PUMP_CURVES[i % len(PUMP_CURVES)].copy()
            pump["asset_id"] = f"P-{(i+1)*100:04d}"
            pump["area"] = self._assign_area(i)
            self.assets.append(pump)
        self.t_hours = np.array([(t - config.base_time).total_seconds() / 3600
                                 for t in config.time_index])
        self.t_days = self.t_hours / 24.0
        self.timestamps = config.time_index

    def _assign_area(self, idx):
        """Map asset index to operational area name."""
        return AREAS[idx % len(AREAS)]

    def generate_asset_data(self, asset):
        """Generate all signals for one asset, apply failure scenarios"""
        flow = generate_flow(asset, self.t_hours, self.t_days, self.config, self.rng)
        suction_p = generate_suction_pressure(asset, flow, self.config, self.rng)
        disch_p = generate_discharge_pressure(asset, flow, self.config, self.rng)
        diff_p = generate_diff_pressure(disch_p, suction_p)
        power = generate_motor_power(asset, flow, diff_p, self.config, self.rng)
        temp_raw = generate_motor_temp(self.t_days, power, asset, self.config, self.rng)
        temp = apply_thermal_inertia(temp_raw, tau_min=self.config.thermal_tau_min, dt_min=self.config.freq_min)
        vibration = generate_vibration(asset, flow, self.config, self.rng)
        speed = generate_speed(asset, self.t_hours, self.config, self.rng)

        for scenario in self.config.failure_scenarios:
            if scenario["asset_id"] != asset["asset_id"]:
                continue
            sname = scenario["scenario"]
            start_day = scenario["start_day"]
            ramp_days = scenario["ramp_days"]
            final_severity = scenario["final_severity"]

            if sname == "bearing":
                vibration, temp = inject_bearing_degradation(
                    vibration, temp, self.t_days, start_day, ramp_days, final_severity, self.rng)
            elif sname == "cavitation":
                flow, diff_p, vibration = inject_cavitation(
                    flow, diff_p, vibration, self.t_days, start_day, ramp_days, final_severity, self.rng)
                disch_p = suction_p + diff_p

                # Recalculate motor power and temperature using updated flow and diff_p
                power = generate_motor_power(asset, flow, diff_p, self.config, self.rng)
                temp_raw = generate_motor_temp(self.t_days, power, asset, self.config, self.rng)
                temp = apply_thermal_inertia(temp_raw, tau_min=self.config.thermal_tau_min, dt_min=self.config.freq_min)

            elif sname == "insulation":
                temp, power = inject_insulation_degradation(
                    temp, power, self.t_days, start_day, ramp_days, final_severity, self.rng)

        data = {
            "timestamp": self.timestamps,
            "asset_id": asset["asset_id"],
            "area": asset["area"],
            "pump_model": asset["model"],
            "flow_m3h": np.round(flow, 2),
            "suction_pressure_bar": np.round(suction_p, 3),
            "disch_pressure_bar": np.round(disch_p, 3),
            "diff_pressure_bar": np.round(diff_p, 3),
            "motor_temp_c": np.round(temp, 1),
            "motor_power_kw": np.round(power, 2),
            "vibration_mm_s": np.round(vibration, 4),
            "speed_rpm": np.round(speed, 1),
        }
        df = pd.DataFrame(data)

        df["failure_type"] = "none"
        for scenario in self.config.failure_scenarios:
            if scenario["asset_id"] == asset["asset_id"]:
                df.loc[self.t_days >= scenario["start_day"], "failure_type"] = scenario["scenario"]

        return df

    def generate_all(self):
        """Generate all assets, inject quality issues, sort and return."""
        print(f"Generating {self.config.num_assets} assets x "
              f"{self.config.n_samples} samples "
              f"({self.config.period_days} days @ {self.config.freq_min}min)...")
        all_dfs = []
        for i, asset in enumerate(self.assets):
            if (i + 1) % 5 == 0 or i == 0:
                print(f"  Asset {i+1}/{self.config.num_assets}: {asset['asset_id']} "
                      f"({asset['model']})")
            df = self.generate_asset_data(asset)
            all_dfs.append(df)
        result = pd.concat(all_dfs, ignore_index=True)
        print(f"  Before data quality issues addition: {len(result):,} rows")

        result = self.inject_data_quality_issues(result)

        # Sort by timestamp then asset_id for consistency
        result = result.sort_values(["timestamp", "asset_id"]).reset_index(drop=True)
        print(f"  After data quality issues addition: {len(result):,} rows")
        print(f"  Total columns: {len(result.columns)}")
        return result

    def inject_data_quality_issues(self, df):
        """Remove gaps. Add duplicates. Apply unit mismatch to cfg.unit_mismatch_asset"""
        rng = self.rng
        cfg = self.config

        # Remove random gaps
        gap_indices = []
        for asset_id in df["asset_id"].unique():
            mask = df["asset_id"] == asset_id
            idx = df.index[mask]
            n_remove = max(1, int(len(idx) * cfg.gap_fraction))
            remove = rng.choice(idx, size=n_remove, replace=False)
            gap_indices.extend(remove.tolist())
        df = df.drop(index=gap_indices)

        # Add duplicate timestamps
        for asset_id in df["asset_id"].unique():
            for _ in range(cfg.duplicate_per_asset):
                asset_sub = df[df["asset_id"] == asset_id]
                if len(asset_sub) == 0:
                    continue
                seed_val = int(rng.integers(0, 2**31 - 1))
                row = asset_sub.sample(1, random_state=seed_val).copy()
                # shift timestamp forward by 30-120 seconds (simulate duplicate from buffer)
                row["timestamp"] = row["timestamp"] + pd.Timedelta(seconds=int(rng.integers(30, 120)))
                # Avoid duplicates dated after simulation end:
                row["timestamp"] = row["timestamp"].clip(upper=self.config.base_time + timedelta(days=self.config.period_days - 1/1440))
                df = pd.concat([df, row], ignore_index=True)

        # Unit mismatch: for specified asset, convert pressure from bar to kPa (multiply by 100)
        mism_asset = cfg.unit_mismatch_asset
        if mism_asset in df["asset_id"].unique():
            mask = df["asset_id"] == mism_asset
            for col in ["suction_pressure_bar", "disch_pressure_bar", "diff_pressure_bar"]:
                df.loc[mask, col] = df.loc[mask, col] * 100

        return df

if __name__ == "__main__":
    config = HistorianConfig(failure_scenarios=FAILURE_SCENARIOS)

    print("Configuration:")
    print(f"Assets: {config.num_assets}")
    print(f"Period: {config.period_days} days")
    print(f"Freq: {config.freq_min} min")
    print(f"Samples: {config.n_samples:,} per asset")
    print(f"Total rows: {config.num_assets * config.n_samples:,}")
    print(f"Failure scenarios: {len(FAILURE_SCENARIOS)}")
    print("Outputs: 8 signals per asset (2 ID fields)")

    gen = SyntheticHistorian(config)
    df = gen.generate_all()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df.to_csv(CSV_PATH, index=False)
    print(f"CSV saved: {CSV_PATH}")

    conn = sqlite3.connect(DB_PATH)
    df.to_sql("historian_data", conn, if_exists="replace", index=False)
    conn.close()
    print(f"SQLite saved: {DB_PATH}")
