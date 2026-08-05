# generate_chatbot_docs.py
"""
Generate chatbot knowledge base markdown files from historian/alarm configs.
"""
import os
import csv
from datetime import datetime, timedelta
from collections import defaultdict

from historian_config import PUMP_CURVES, FAILURE_SCENARIOS, AREAS, BASE_TIME, PERIOD_DAYS, NUM_ASSETS

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
ALARM_CSV_PATH = os.path.join(OUTPUT_DIR, "alarm_log.csv")
CHATBOT_DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "chatbot-docs")


def load_alarm_log():
    if not os.path.exists(ALARM_CSV_PATH):
        return {}

    alarms_by_asset = defaultdict(list)
    with open(ALARM_CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            asset_id = row.get("asset_id")
            if asset_id:
                alarms_by_asset[asset_id].append(row)

    return alarms_by_asset


def count_alarms_in_window(alarms, start_date, end_date):
    count = 0
    for alarm in alarms:
        try:
            alarm_time = datetime.strptime(alarm["activation_time"], "%Y-%m-%d %H:%M:%S")
            if start_date <= alarm_time <= end_date:
                count += 1
        except (ValueError, KeyError):
            pass
    return count


def get_top_alarms_in_window(alarms, start_date, end_date, limit=5):
    tags_in_window = defaultdict(int)
    for alarm in alarms:
        try:
            alarm_time = datetime.strptime(alarm["activation_time"], "%Y-%m-%d %H:%M:%S")
            if start_date <= alarm_time <= end_date:
                tag = alarm.get("alarm_tag", "")
                if tag:
                    tags_in_window[tag] += 1
        except (ValueError, KeyError):
            pass

    return sorted(tags_in_window.items(), key=lambda x: x[1], reverse=True)[:limit]


def generate_asset_specs():
    lines = [
        "# Fleet Asset Specifications\n\n",
        f"Data as of: {(BASE_TIME + timedelta(days=PERIOD_DAYS)).strftime('%Y-%m-%d')}\n\n",

    ]

    for i in range(NUM_ASSETS):
        pump_idx = i % len(PUMP_CURVES)
        pump = PUMP_CURVES[pump_idx]
        asset_id = f"P-{(i+1)*100:04d}"
        area = AREAS[i % len(AREAS)]
        commissioned = (BASE_TIME - timedelta(days=1095 + i * 30)).strftime("%Y-%m-%d")

        lines.append(f"## {asset_id}\n")
        lines.append(f"Location: {area.replace('_', ' ')}\n")
        lines.append(f"Model: Grundfos {pump['model']}\n")
        lines.append(f"Commissioned: {commissioned}\n\n")

        lines.append("### Operating Point (BEP)\n")
        lines.append(f"Flow: {pump['nominal_flow_m3h']:.0f} m³/h | ")
        lines.append(f"Head: {pump['nominal_head_m']:.0f} m | ")
        lines.append(f"Power: {pump['motor_power_kw']:.1f} kW\n")
        lines.append(f"Efficiency: {pump['pump_eta']:.1f}% | NPSH: {pump['npsh_m']:.1f} m\n\n")

        lines.append(f"Motor: {pump['speed_rpm']:.0f} RPM | {pump['impeller_diameter_mm']:.0f} mm impeller\n")
        lines.append(f"Suction: {pump['suction_pressure_bar']:.1f} bar (typical range {pump['suction_pressure_bar']*0.7:.2f}–{pump['suction_pressure_bar']*1.3:.2f} bar)\n\n")

    return "".join(lines)


def generate_maintenance_history():
    alarms = load_alarm_log()
    failure_by_asset = {s["asset_id"]: s for s in FAILURE_SCENARIOS}

    lines = [
        "# Maintenance Observations\n\n",
        f"Period: {BASE_TIME.strftime('%Y-%m-%d')} to {(BASE_TIME + timedelta(days=PERIOD_DAYS)).strftime('%Y-%m-%d')} ({PERIOD_DAYS} days)\n\n",
    ]

    for i in range(NUM_ASSETS):
        asset_id = f"P-{(i+1)*100:04d}"
        pump_idx = i % len(PUMP_CURVES)
        pump = PUMP_CURVES[pump_idx]
        area = AREAS[i % len(AREAS)]

        lines.append(f"## {asset_id} ({area.replace('_', ' ')})\n\n")
        lines.append(f"Model: Grundfos {pump['model']} ({pump['motor_power_kw']:.1f} kW)\n\n")

        asset_alarms = alarms.get(asset_id, [])
        total_alarms = len(asset_alarms)
        lines.append(f"Total alarms in period: {total_alarms}\n\n")

        if asset_id not in failure_by_asset:
            lines.append("**Status: Healthy**\n\n")
            lines.append(f"No major issues detected. Baseline performance within spec. ")
            lines.append(f"Nominal operation: ~{pump['nominal_flow_m3h']:.0f} m³/h at ~{pump['motor_power_kw']:.1f} kW.\n\n")
        else:
            scenario = failure_by_asset[asset_id]
            failure_type = scenario["scenario"]
            start_day = scenario["start_day"]
            ramp_days = scenario["ramp_days"]
            end_day = start_day + ramp_days

            start_dt = BASE_TIME + timedelta(days=start_day)
            end_dt = BASE_TIME + timedelta(days=end_day)

            alarms_in_window = count_alarms_in_window(asset_alarms, start_dt, end_dt)
            top_tags = get_top_alarms_in_window(asset_alarms, start_dt, end_dt)

            lines.append(f"**Status: Degradation detected ({failure_type})**\n\n")
            lines.append(f"Onset: {start_dt.strftime('%Y-%m-%d')} (Day {start_day})\n")
            lines.append(f"Duration: {ramp_days} days\n")
            lines.append(f"Alarms during degradation window: {alarms_in_window}\n\n")

            if top_tags:
                lines.append("Top alarm signatures:\n")
                for tag, count in top_tags:
                    lines.append(f"- {tag}: {count} occurrences\n")
                lines.append("\n")

            if failure_type == "bearing":
                lines.append("**Bearing wear observed.** Vibration and temperature signals show characteristic signatures. ")
                lines.append(f"Estimated progression over {ramp_days} days suggests replacement should be planned by Day {end_day}. ")
                lines.append("Increase monitoring frequency and watch for accelerating degradation.\n\n")

            elif failure_type == "cavitation":
                lines.append("**Cavitation detected.** Pressure oscillations and flow instability indicate suction conditions are marginal. ")
                lines.append(f"Over {ramp_days} days, condition worsens predictably. Check inlet strainer and suction line restrictions. ")
                lines.append(f"Plan corrective action (increase inlet pressure or reduce duty point) before Day {end_day}.\n\n")

            elif failure_type == "insulation":
                lines.append("**Motor insulation degradation.** Temperature and power draw trending upward at steady flow. ")
                lines.append(f"Over {ramp_days} days this degrades linearly. Motor rewind or replacement should be scheduled by Day {end_day}. ")
                lines.append("Verify cooling conditions and check for thermal cycling stress.\n\n")

    lines.append("\n## Common Failure Modes\n\n")
    lines.append("### Bearing Wear\n")
    lines.append("Vibration increases, temperature rises (delayed ~60% into ramp). Look for VI_HI and TI_HI alarms clustering.\n\n")

    lines.append("### Cavitation\n")
    lines.append("Pressure spikes, flow becomes erratic. FI_LO and PDI_HI alarms frequent. Suction strainer or inlet line problem.\n\n")

    lines.append("### Motor Insulation\n")
    lines.append("Temperature creeps up, power consumption increases at constant flow. TI_HI and II_HI alarms rise. ")
    lines.append("Check motor cooling fan and ambient conditions.\n")

    return "".join(lines)


if __name__ == "__main__":
    os.makedirs(CHATBOT_DOCS_DIR, exist_ok=True)

    specs = generate_asset_specs()
    hist = generate_maintenance_history()

    specs_file = os.path.join(CHATBOT_DOCS_DIR, "asset_specs.md")
    hist_file = os.path.join(CHATBOT_DOCS_DIR, "maintenance_history.md")

    with open(specs_file, "w", encoding="utf-8") as f:
        f.write(specs)
    print(f"Wrote {specs_file}")

    with open(hist_file, "w", encoding="utf-8") as f:
        f.write(hist)
    print(f"Wrote {hist_file}")