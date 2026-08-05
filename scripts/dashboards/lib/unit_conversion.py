# unit_conversion.py
from dashboard_config import UNITS

# Conversion factors (metric → imperial multipliers)
CONVERSIONS = {
    "flow_m3h": {"factor": 4.40287, "metric_unit": "m³/h", "imperial_unit": "GPM"},
    "pressure_bar": {"factor": 14.5038, "metric_unit": "bar", "imperial_unit": "PSI"},
    "temp_c": {"to_f": True, "metric_unit": "°C", "imperial_unit": "°F"},  # special case: (C × 9/5) + 32
    "vibration_mm_s": {"factor": 0.03937, "metric_unit": "mm/s", "imperial_unit": "in/s"},
    "power_kw": {"factor": 1.34102, "metric_unit": "kW", "imperial_unit": "HP"},
    "discharge_cfs": {"is_imperial": True, "metric_unit": "m³/s", "imperial_unit": "cfs"},
    "speed_rpm": {"is_same": True, "metric_unit": "RPM", "imperial_unit": "RPM"},
}


def convert_value(value, key, unit_system=None):

    if unit_system is None:
        unit_system = UNITS

    if unit_system == "metric" or value is None:
        return value

    if key not in CONVERSIONS:
        return value

    spec = CONVERSIONS[key]

    # Already imperial, no conversion needed
    if spec.get("is_imperial") or spec.get("is_same"):
        return value

    # Temperature: special case
    if spec.get("to_f"):
        return (value * 9.0 / 5.0) + 32.0

    # Linear conversion
    if "factor" in spec:
        return value * spec["factor"]

    return value


def unit_label(key, unit_system=None):
    if unit_system is None:
        unit_system = UNITS

    if key not in CONVERSIONS:
        return ""

    spec = CONVERSIONS[key]
    return spec["imperial_unit"] if unit_system == "imperial" else spec["metric_unit"]


def fmt_val(value, key, decimals=1, unit_system=None):
    converted = convert_value(value, key, unit_system)
    label = unit_label(key, unit_system)
    if converted is None:
        return "n/a"
    return f"{converted:.{decimals}f} {label}"