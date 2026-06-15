# alarm_log_generator.py
import os
import csv
import random
from datetime import datetime, timedelta
from historian_generator import FAILURE_SCENARIOS

FIELDS = [
    "asset_id", "alarm_tag", "alarm_description", "priority", "alarm_type",
    "activation_time", "ack_time", "clear_time", "duration_min",
    "operator_id", "area", "is_test_case"
]

ALARM_TAG_TEMPLATES = {
    "VI_HI":  {"desc": "Pump vibration high",        "priority": 2, "type": "HI", "family": "vibration"},
    "TI_HI":  {"desc": "Motor temperature high",     "priority": 2, "type": "HI", "family": "temperature"},
    "FI_LO":  {"desc": "Discharge flow low",         "priority": 3, "type": "LO", "family": "flow"},
    "PI_HI":  {"desc": "Discharge pressure high",    "priority": 3, "type": "HI", "family": "pressure"},
    "PI_LO":  {"desc": "Suction pressure low",       "priority": 2, "type": "LO", "family": "pressure"},
    "PDI_HI": {"desc": "Differential pressure high", "priority": 3, "type": "HI", "family": "pressure"},
    "II_HI":  {"desc": "Motor current high",         "priority": 2, "type": "HI", "family": "current"},
    "SI_LO":  {"desc": "Speed low",                  "priority": 4, "type": "LO", "family": "speed"},
}

FAILURE_FAMILY_MAP = {
    "bearing":    ["vibration", "temperature"],
    "cavitation": ["flow", "pressure"],
    "insulation": ["current", "temperature"],
}

AREAS = [
    "Raw_Water_Intake", "Chemical_Dosing", "Filtration",
    "Booster_Station_A", "Booster_Station_B", "Wastewater_Lift",
    "Effluent_Distribution", "Irrigation_Supply", "Backwash_System",
    "High_Lift_Station"
]

OPS = ["OP01", "OP02", "OP03", "OP04", "OP05"]

def build_assets(num_assets):
    assets = []
    for i in range(num_assets):
        asset_id = f"P-{(i+1)*100:04d}"
        tag_suffixes = list(ALARM_TAG_TEMPLATES.keys())
        tags = [f"{asset_id}.{sfx}" for sfx in tag_suffixes]
        assets.append({"asset_id": asset_id, "area": AREAS[i % len(AREAS)], "tags": tags,})
    return assets

def make_event(asset, t, tag=None, test=False):
    if tag is None:
        tag = random.choice(asset["tags"])
    suffix = tag.split(".")[-1]
    m = ALARM_TAG_TEMPLATES[suffix]

    # higher priority = shorter duration
    means = {1: 3, 2: 10, 3: 25, 4: 60}
    stds  = {1: 1, 2: 4, 3: 10, 4: 30}
    priority = m["priority"]

    dur = max(0.5, random.gauss(means[priority], stds[priority]))
    ack = random.uniform(0.1, min(5.0, dur))

    desc = m["desc"]
    if test:
        desc = desc + " (test)"

    return {
        "asset_id": asset["asset_id"],
        "alarm_tag": tag,
        "alarm_description": desc,
        "priority": priority,
        "alarm_type": m["type"],
        "activation_time": t.strftime("%Y-%m-%d %H:%M:%S"),
        "ack_time": (t + timedelta(minutes=ack)).strftime("%Y-%m-%d %H:%M:%S"),
        "clear_time": (t + timedelta(minutes=dur)).strftime("%Y-%m-%d %H:%M:%S"),
        "duration_min": round(dur, 1),
        "operator_id": random.choice(OPS),
        "area": asset["area"],
        "is_test_case": "YES" if test else ""
    }

def generate_failure_correlated_alarms(assets_by_id, failure_scenarios, start):
    rows = []
    asset_map = {a["asset_id"]: a for a in assets_by_id}

    for scenario in failure_scenarios:
        asset_id  = scenario["asset_id"]
        sname     = scenario["scenario"]
        start_day = scenario["start_day"]
        ramp_days = scenario["ramp_days"]
        final_sev = scenario["final_severity"]

        if asset_id not in asset_map:
            continue
        asset = asset_map[asset_id]
        target_families = FAILURE_FAMILY_MAP.get(sname, [])
        target_tags = [
            tag for tag in asset["tags"]
            if ALARM_TAG_TEMPLATES[tag.split(".")[-1]]["family"] in target_families
        ]
        if not target_tags:
            continue

        for day_offset in range(ramp_days):
            current_day = start_day + day_offset
            if current_day > 364:
                break
            t_rel = day_offset / ramp_days
            alarms_today = int(2 + (final_sev * 8 - 2) * t_rel)
            for _ in range(alarms_today):
                h = max(0, min(23, int(random.gauss(12, 5))))
                m = random.uniform(0, 59)
                t = start + timedelta(days=current_day, hours=h, minutes=m)
                tag = random.choice(target_tags)
                rows.append(make_event(asset, t, tag=tag))

    return rows

if __name__ == "__main__":
    random.seed(42)
    start = datetime(2025, 1, 1, 0, 0, 0)
    ASSETS = build_assets(10)
    rows = []

    # normal events: ~6 alarms per asset per day = 6 * 10 * 365 = 21,900
    for _ in range(21900):
        a = random.choice(ASSETS)
        d = random.randint(0, 364)
        h = max(0, min(23, int(random.gauss(14, 6))))
        m = random.uniform(0, 59)
        t = start + timedelta(days=d, hours=h, minutes=m)
        rows.append(make_event(a, t))

    # chattering: P-0100.VI_HI x7 in ~8 min
    t0 = start + timedelta(days=5, hours=8, minutes=30)
    for i in range(7):
        t = t0 + timedelta(minutes=1.2 * i)
        ev = make_event(ASSETS[0], t, tag="P-0100.VI_HI", test=True)
        ev["duration_min"] = 0.8
        ev["ack_time"] = (t + timedelta(minutes=0.6)).strftime("%Y-%m-%d %H:%M:%S")
        ev["clear_time"] = (t + timedelta(minutes=0.8)).strftime("%Y-%m-%d %H:%M:%S")
        ev["operator_id"] = "OP01"
        rows.append(ev)

    # stale: P-0200.FI_LO never clears
    t0 = start + timedelta(days=10, hours=2)
    ev = make_event(ASSETS[1], t0, tag="P-0200.FI_LO", test=True)
    ev["duration_min"] = 3120.0
    ev["ack_time"] = (t0 + timedelta(minutes=4.5)).strftime("%Y-%m-%d %H:%M:%S")
    ev["clear_time"] = ""
    ev["operator_id"] = "OP04"
    rows.append(ev)

    # correlated batch: P-0300 cascade
    t0 = start + timedelta(days=15, hours=14, minutes=22, seconds=30)
    batch = ["P-0300.PI_LO", "P-0300.FI_LO", "P-0300.VI_HI", "P-0300.PDI_HI", "P-0300.TI_HI"]
    for i, tag in enumerate(batch):
        t = t0 + timedelta(seconds=25 * i)
        dur = random.uniform(3.5, 25.0)
        ev = make_event(ASSETS[2], t, tag=tag, test=True)
        ev["duration_min"] = round(dur, 1)
        ev["ack_time"] = (t + timedelta(minutes=0.8)).strftime("%Y-%m-%d %H:%M:%S")
        ev["clear_time"] = (t + timedelta(minutes=dur)).strftime("%Y-%m-%d %H:%M:%S")
        ev["operator_id"] = "OP05"
        rows.append(ev)

    failure_rows = generate_failure_correlated_alarms(ASSETS, FAILURE_SCENARIOS, start)
    rows.extend(failure_rows)
    print(f"  Failure-correlated alarms added: {len(failure_rows)}")

    rows.sort(key=lambda r: r["activation_time"])

    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)

    csv_path = os.path.join(output_folder, "alarm_log.csv")

    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # quick summary
    print(f"Wrote {len(rows)} records")
    by_asset = {}
    for r in rows:
        by_asset[r["asset_id"]] = by_asset.get(r["asset_id"], 0) + 1
    for a, n in sorted(by_asset.items()):
        print(f"  {a}: {n}")

    pri = {1:0, 2:0, 3:0, 4:0}
    for r in rows:
        pri[r["priority"]] += 1
    print(f"  P 1: {pri[1]}  P 2: {pri[2]}  P 3: {pri[3]}  P 4: {pri[4]}")
    print(f"  Test cases: {sum(1 for r in rows if r['is_test_case'] == 'YES')}")

    # ISA-18.2 check: < 1 alarm per 10 min per asset = 144/asset/day max
    total_asset_days = 10 * 365
    rate = len(rows) / total_asset_days
    print(f"  Mean alarm rate: {rate:.1f} alarms/asset/day")
    if rate > 144:
        print("  WARNING: exceeds ISA-18.2 benchmark")
