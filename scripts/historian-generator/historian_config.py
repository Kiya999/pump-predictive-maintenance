# historian_config.py
"""
Configuration for synthetic historian generation: output paths, default
parameters, failure scenarios, and reference pump data from Grundfos.
"""

import os
from datetime import datetime

## Output Paths
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
CSV_PATH = os.path.join(OUTPUT_DIR, "synthetic_historian_10x365_1min.csv")
DB_PATH = os.path.join(OUTPUT_DIR, "synthetic_historian.db")
FAILURE_SCENARIOS_DIR = os.path.join(OUTPUT_DIR, "failure_scenarios")
HISTORIAN_VALIDATION_DIR = os.path.join(OUTPUT_DIR, "historian_validation")

## Signal Generation Parameters (historian_generator.py)
BASE_TIME = datetime(2025, 1, 1)
NUM_ASSETS = 10
PERIOD_DAYS = 365 # Duration of simulation
FREQ_MIN = 1 # Sampling interval
NOISE_LEVEL = 0.02 # amplitude of random noise (fraction of nominal)
DRIFT_RATE = 0.001 # long-term drift per day (multiplicative)
SEASON_AMP = 0.3
SEED = 42
THERMAL_TAU_MIN = 15 # time constant for motor thermal inertia filter (minutes)

## Data Quality Injection Parameters (historian_generator.py)
GAP_FRACTION = 0.001 # approximate fraction of rows to remove
DUPLICATE_PER_ASSET = 3
UNIT_MISMATCH_ASSET = "P-0700" # asset that gets pressure in kPa instead of bar

## Quality Assessment Parameters (run_quality_historian.py)
IQR_MULTIPLIER = 1.5

## Validation Parameters (verify_historian_output.py)
DAY_HOURS = (8, 20)
NIGHT_HOURS = (0, 5)
PUMP_CURVE_SAMPLE_STRIDE = 100
FLOW_BIN_COUNT = 20

## Signal Definitions
SIGNAL_COLUMNS = [
    "flow_m3h", "suction_pressure_bar", "disch_pressure_bar",
    "diff_pressure_bar", "motor_temp_c", "motor_power_kw",
    "vibration_mm_s", "speed_rpm",
]

PRESSURE_COLUMNS = ["suction_pressure_bar", "disch_pressure_bar", "diff_pressure_bar"]

## Visualization Mappings (visualize_failure_scenarios.py)
FAILURE_SIGNAL_MAP = {
    "bearing": {"signal": "vibration_mm_s", "secondary": "motor_temp_c",
                "ylabel": "Vibration (mm/s)", "secondary_ylabel": "Motor Temperature (C)"},
    "cavitation": {"signal": "diff_pressure_bar", "secondary": "flow_m3h",
                "ylabel": "Differential Pressure (bar)", "secondary_ylabel": "Flow (m3/h)"},
    "insulation": {"signal": "motor_temp_c", "secondary": "motor_power_kw",
                "ylabel": "Motor Temperature (C)", "secondary_ylabel": "Motor Power (kW)"},
}

## Failure Scenarios
FAILURE_SCENARIOS = [
    # Bearing degradation on P-0100, starting day 100, ramp 260 days, severity 4
    {"scenario": "bearing", "asset_id": "P-0100", "start_day": 100, "ramp_days": 260, "final_severity": 4.0},
    # Cavitation on P-0300, starting day 200, ramp 60 days, severity 3
    {"scenario": "cavitation", "asset_id": "P-0300", "start_day": 200, "ramp_days": 60, "final_severity": 3.0},
    # Insulation on P-0500, starting day 150, ramp 120 days, severity 3.5
    {"scenario": "insulation", "asset_id": "P-0500", "start_day": 150, "ramp_days": 120, "final_severity": 3.5},
]

## Operational Areas (historian_generator.py)
AREAS = [
    "Raw_Water_Intake", "Chemical_Dosing", "Filtration",
    "Booster_Station_A", "Booster_Station_B", "Wastewater_Lift",
    "Effluent_Distribution", "Irrigation_Supply", "Backwash_System",
    "High_Lift_Station"
]

## Pump Curve Reference Data (historian_generator.py)
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