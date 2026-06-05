# historian_generator.py
"""Generate synthetic pump historian data for predictive maintenance

Outputs a CSV with 10 pump assets x 1 year of 1-min SCADA-like signals
(flow, pressures, temperature, power, vibration, speed). Signal patterns
include diurnal/seasonal demand cycles, weekday/weekend reduction,
pump curve physics, and thermal inertia.

Pump curves from Grundfos NK/NKE databooklet:
https://www.motralec.com/public/fichiers/docs/grundfos-nke-nk-english.pdf
Performance range: 2-2000 m3/h, 2-150 m head, 0.37-315 kW motors

All pressure values are gauge pressure (relative to 1 atm absolute).
Conversion: discharge_gauge = suction_gauge + (head_m * 0.0981)
NPSHa must be calculated using absolute pressure: P_abs = P_gauge + 1.013
"""

import numpy as np
import pandas as pd
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class HistorianConfig:
    num_assets: int = 10
    period_days: int = 365
    freq_min: int = 1
    noise_level: float = 0.02
    drift_rate: float = 0.001
    season_amp: float = 0.3
    base_time: datetime = field(default_factory=lambda: datetime(2025, 1, 1, 0, 0, 0))
    seed: int = 42

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


# Nominal operating points from Grundfos NK/NKE databooklet
# Values are approximate BEP duty points from the biggest impleller size curve
PUMP_CURVES = [
    # 2-pole pumps (2900 RPM)
    {
        "model": "NK 32-125",
        "speed_rpm": 2900,
        "impeller_diameter_mm": 142,
        "pump_eta": 77.3,
        "nominal_flow_m3h": 27,
        "nominal_head_m": 25,
        "motor_power_kw": 2.5,
        "npsh_m": 1.8,
        "suction_pressure_bar": 0.5,
    },
    {
        "model": "NK 40-160",
        "speed_rpm": 2900,
        "impeller_diameter_mm": 177,
        "pump_eta": 72.0,
        "nominal_flow_m3h": 44,
        "nominal_head_m": 40,
        "motor_power_kw": 7,
        "npsh_m": 2,
        "suction_pressure_bar": 0.5,
    },
    {
        "model": "NK 50-200",
        "speed_rpm": 2900,
        "impeller_diameter_mm": 219,
        "pump_eta": 79.3,
        "nominal_flow_m3h": 85,
        "nominal_head_m": 60,
        "motor_power_kw": 17,
        "npsh_m": 3,
        "suction_pressure_bar": 0.8,
    },
    {
        "model": "NK 65-250",
        "speed_rpm": 2900,
        "impeller_diameter_mm": 263,
        "pump_eta": 74.4,
        "nominal_flow_m3h": 135,
        "nominal_head_m": 85,
        "motor_power_kw": 42,
        "npsh_m": 6,
        "suction_pressure_bar": 1.0,
    },
    {
        "model": "NK 80-250",
        "speed_rpm": 2900,
        "impeller_diameter_mm": 270,
        "pump_eta": 81.9,
        "nominal_flow_m3h": 235,
        "nominal_head_m": 95,
        "motor_power_kw": 75,
        "npsh_m": 5,
        "suction_pressure_bar": 1.0,
    },
    {
        "model": "NK 80-315",
        "speed_rpm": 2900,
        "impeller_diameter_mm": 330,
        "pump_eta": 71.7,
        "nominal_flow_m3h": 230,
        "nominal_head_m": 125,
        "motor_power_kw": 110,
        "npsh_m": 8.5,
        "suction_pressure_bar": 1.2,
    },
    # 4-pole pumps (1450 RPM)
    {
        "model": "NK 100-200",
        "speed_rpm": 1450,
        "impeller_diameter_mm": 219,
        "pump_eta": 82.9,
        "nominal_flow_m3h": 175,
        "nominal_head_m": 14,
        "motor_power_kw": 8,
        "npsh_m": 2,
        "suction_pressure_bar": 1.5,
    },
    {
        "model": "NK 100-250",
        "speed_rpm": 1450,
        "impeller_diameter_mm": 270,
        "pump_eta": 81.7,
        "nominal_flow_m3h": 175,
        "nominal_head_m": 23.5,
        "motor_power_kw": 14,
        "npsh_m": 1.7,
        "suction_pressure_bar": 1.5,
    },
    {
        "model": "NK 125-315",
        "speed_rpm": 1450,
        "impeller_diameter_mm": 330,
        "pump_eta": 82.3,
        "nominal_flow_m3h": 220,
        "nominal_head_m": 33,
        "motor_power_kw": 24,
        "npsh_m": 2,
        "suction_pressure_bar": 1.5, 
        
    },
    {
        "model": "NK 150-400",
        "speed_rpm": 1450,
        "impeller_diameter_mm": 415,
        "pump_eta": 81.7,
        "nominal_flow_m3h": 500,
        "nominal_head_m": 53,
        "motor_power_kw": 85,
        "npsh_m": 4,
        "suction_pressure_bar": 2,
    },
]


def _daily_pattern(t_hours):
    # Sine wave peaks around 14:00, troughs around 02:00
    raw = np.sin(np.pi * (t_hours - 6) / 12)
    raw = np.clip(raw, -1, 1)
    scaled = (raw + 1) / 2
    return scaled


def _weekly_pattern(t_days, base_time=None):
    # Weekend factor = 0.85 (15% demand reduction Sat-Sun)
    if base_time is not None:
        offset = base_time.weekday()  # 0=Mon, 1=Tue, ..., 6=Sun
    else:
        offset = 0
    dow = (t_days + offset) % 7
    return np.where(dow >= 5, 0.85, 1.0)


def _seasonal_pattern(t_days, period_days=365, amp=0.3):
    # amp controls seasonal amplitude: default 0.3 = +/-30% around 0.7 baseline
    phase = 2 * np.pi * t_days / period_days
    return 0.7 + amp * np.sin(phase - np.pi / 2)


def _drift(t_days, rate):
    return 1.0 + rate * t_days


def generate_flow(asset, t_hours, t_days, config, rng):
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
    base_p = asset["suction_pressure_bar"]
    flow_frac = flow / asset["nominal_flow_m3h"]
    # Friction losses increase slightly with flow
    friction_drop = 0.05 * (flow_frac - 0.5)
    noise = rng.normal(0, 0.01, size=len(flow))
    p = base_p - friction_drop + noise
    p = np.clip(p, base_p * 0.7, base_p * 1.3)
    return p


def generate_discharge_pressure(asset, flow, config, rng):
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
    return disch_p - suction_p


def generate_motor_power(asset, flow, diff_p, config, rng):
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
    # Ambient follows seasonal cycle; temp rise proportional to load
    ambient = 15 + 10 * _seasonal_pattern(t_days, config.period_days, config.season_amp)
    power_frac = power / asset["motor_power_kw"]
    temp_rise = 30 * power_frac
    temp_raw = ambient + temp_rise
    noise = rng.normal(0, 0.3, size=len(power))
    temp = temp_raw + noise
    temp = np.clip(temp, ambient, 95)
    return temp


def generate_vibration(asset, flow, config, rng):
    # Minimum vibration at BEP flow (~90% of nominal), increases away from it
    flow_frac = flow / asset["nominal_flow_m3h"]
    base_vib = 0.04
    off_bep_penalty = 0.15 * (flow_frac - 0.9)**2
    vibration = base_vib + off_bep_penalty
    noise = rng.normal(0, 0.005, size=len(flow))
    vib = vibration + noise
    vib = np.clip(vib, 0.01, 0.5)
    return vib


def generate_speed(asset, t_hours, config, rng):
    base_rpm = asset["speed_rpm"]
    variation = rng.normal(0, base_rpm * 0.002, size=len(t_hours))
    speed = base_rpm + variation
    speed = np.clip(speed, base_rpm * 0.95, base_rpm * 1.05)
    return speed


def apply_thermal_inertia(signal, tau_min=15, dt_min=1):
    # First-order low-pass filter simulating thermal mass
    alpha = 1 - np.exp(-dt_min / tau_min)
    filtered = np.zeros_like(signal)
    filtered[0] = signal[0]
    for i in range(1, len(signal)):
        filtered[i] = filtered[i-1] + alpha * (signal[i] - filtered[i-1])
    return filtered


class SyntheticHistorian:

    def __init__(self, config: HistorianConfig):
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
        areas = ["Raw_Water_Intake", "Chemical_Dosing", "Filtration",
                 "Booster_Station_A", "Booster_Station_B", "Wastewater_Lift",
                 "Effluent_Distribution", "Irrigation_Supply", "Backwash_System",
                 "High_Lift_Station"]
        return areas[idx % len(areas)]

    def generate_asset_data(self, asset):
        flow = generate_flow(asset, self.t_hours, self.t_days, self.config, self.rng)
        suction_p = generate_suction_pressure(asset, flow, self.config, self.rng)
        disch_p = generate_discharge_pressure(asset, flow, self.config, self.rng)
        diff_p = generate_diff_pressure(disch_p, suction_p)
        power = generate_motor_power(asset, flow, diff_p, self.config, self.rng)
        temp_raw = generate_motor_temp(self.t_days, power, asset, self.config, self.rng)
        temp = apply_thermal_inertia(temp_raw, tau_min=15, dt_min=self.config.freq_min)
        vibration = generate_vibration(asset, flow, self.config, self.rng)
        speed = generate_speed(asset, self.t_hours, self.config, self.rng)

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
        return pd.DataFrame(data)

    def generate_all(self):
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
        print(f"  Total rows: {len(result):,}")
        print(f"  Total columns: {len(result.columns)}")
        return result

if __name__ == "__main__":
    config = HistorianConfig(
        num_assets=10,
        period_days=365,
        freq_min=1,
        noise_level=0.02,
        drift_rate=0.001,
        season_amp=0.3,
        seed=42
    )
    print("Configuration:")
    print(f"Assets: {config.num_assets}")
    print(f"Period: {config.period_days} days")
    print(f"Freq: {config.freq_min} min")
    print(f"Samples: {config.n_samples:,} per asset")
    print(f"Total rows: {config.num_assets * config.n_samples:,}")
    print("Outputs: 8 signals per asset (2 ID fields)")

    gen = SyntheticHistorian(config)
    df = gen.generate_all()
    
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "synthetic_historian_10x365_1min.csv")
    df.to_csv(output_path, index=False)
    print("Saved.")
