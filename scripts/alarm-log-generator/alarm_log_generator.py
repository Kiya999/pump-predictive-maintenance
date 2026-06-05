# alarm_log_generator.py
import csv
import random
from datetime import datetime, timedelta

FIELDS = [
    "asset_id", "alarm_tag", "alarm_description", "priority", "alarm_type",
    "activation_time", "ack_time", "clear_time", "duration_min",
    "operator_id", "area", "is_test_case"
]

ALARM_MASTER = {
    "TK-101.LI_HI":  {"desc": "Tank level high",          "priority": 3, "type": "HI"},
    "TK-101.LI_LO":  {"desc": "Tank level low",           "priority": 4, "type": "LO"},
    "TK-101.TI_HI":  {"desc": "Tank temperature high",    "priority": 3, "type": "HI"},
    "TK-101.PI_HI":  {"desc": "Tank pressure high",       "priority": 2, "type": "HI"},
    "P-201.FI_LO":   {"desc": "Discharge flow low",       "priority": 3, "type": "LO"},
    "P-201.PI_HI":   {"desc": "Discharge pressure high",  "priority": 3, "type": "HI"},
    "P-201.TI_HI":   {"desc": "Motor temperature high",   "priority": 2, "type": "HI"},
    "P-201.VI_HI":   {"desc": "Pump vibration high",      "priority": 2, "type": "HI"},
    "C-301.PI_LO":   {"desc": "Suction pressure low",     "priority": 2, "type": "LO"},
    "C-301.TI_HI":   {"desc": "Discharge temp high",      "priority": 2, "type": "HI"},
    "C-301.VI_HI":   {"desc": "Compressor vibration high","priority": 1, "type": "HI"},
    "C-301.FI_LO":   {"desc": "Lube oil flow low",        "priority": 1, "type": "LO"},
    "C-301.PDI_HI":  {"desc": "Filter delta-P high",      "priority": 4, "type": "HI"},
}

ASSETS = [
    {
        "asset_id": "TK-101",
        "area": "Storage_Tank_Farm",
        "tags": ["TK-101.LI_HI", "TK-101.LI_LO", "TK-101.TI_HI", "TK-101.PI_HI"]
    },
    {
        "asset_id": "P-201",
        "area": "Pumping_Station_A",
        "tags": ["P-201.FI_LO", "P-201.PI_HI", "P-201.TI_HI", "P-201.VI_HI"]
    },
    {
        "asset_id": "C-301",
        "area": "Compressor_Building",
        "tags": ["C-301.PI_LO", "C-301.TI_HI", "C-301.VI_HI", "C-301.FI_LO", "C-301.PDI_HI"]
    }
]

OPS = ["OP01", "OP02", "OP03", "OP04", "OP05"]

def make_event(asset, t, tag=None, test=False):
    if tag is None:
        tag = random.choice(asset["tags"])
    m = ALARM_MASTER[tag]

    # higher priority = shorter duration
    means = {1: 3, 2: 10, 3: 25, 4: 60}
    stds  = {1: 1, 2: 4, 3: 10, 4: 30}
    dur = max(0.5, random.gauss(means[m["priority"]], stds[m["priority"]]))

    ack = random.uniform(0.1, 5.0)

    desc = m["desc"]
    if test:
        desc = desc + " (test)"

    return {
        "asset_id": asset["asset_id"],
        "alarm_tag": tag,
        "alarm_description": desc,
        "priority": m["priority"],
        "alarm_type": m["type"],
        "activation_time": t.strftime("%Y-%m-%d %H:%M:%S"),
        "ack_time": (t + timedelta(minutes=ack)).strftime("%Y-%m-%d %H:%M:%S"),
        "clear_time": (t + timedelta(minutes=dur)).strftime("%Y-%m-%d %H:%M:%S"),
        "duration_min": round(dur, 1),
        "operator_id": random.choice(OPS),
        "area": asset["area"],
        "is_test_case": "YES" if test else ""
    }

if __name__ == "__main__":
    random.seed(42)
    start = datetime(2025, 1, 1, 0, 0, 0)
    rows = []

    # normal events
    for _ in range(250):
        a = random.choice(ASSETS)
        d = random.randint(0, 29)
        h = max(0, min(23, int(random.gauss(14, 6))))
        m = random.uniform(0, 59)
        t = start + timedelta(days=d, hours=h, minutes=m)
        rows.append(make_event(a, t))

    # chattering: TK-101.LI_HI x7 in ~8 min
    t0 = start + timedelta(days=5, hours=8, minutes=30)
    for i in range(7):
        t = t0 + timedelta(minutes=1.2 * i)
        ev = make_event(ASSETS[0], t, tag="TK-101.LI_HI", test=True)
        ev["duration_min"] = 0.8
        ev["ack_time"] = (t + timedelta(minutes=0.6)).strftime("%Y-%m-%d %H:%M:%S")
        ev["clear_time"] = (t + timedelta(minutes=0.8)).strftime("%Y-%m-%d %H:%M:%S")
        ev["operator_id"] = "OP01"
        rows.append(ev)

    # stale: P-201.FI_LO never clears
    t0 = start + timedelta(days=10, hours=2)
    ev = make_event(ASSETS[1], t0, tag="P-201.FI_LO", test=True)
    ev["duration_min"] = 3120.0
    ev["ack_time"] = (t0 + timedelta(minutes=4.5)).strftime("%Y-%m-%d %H:%M:%S")
    ev["clear_time"] = ""
    ev["operator_id"] = "OP04"
    rows.append(ev)

    # correlated batch: C-301 cascade
    t0 = start + timedelta(days=15, hours=14, minutes=22, seconds=30)
    batch = ["C-301.PI_LO", "C-301.TI_HI", "C-301.VI_HI", "C-301.FI_LO", "C-301.PDI_HI"]
    for i, tag in enumerate(batch):
        t = t0 + timedelta(seconds=25 * i)
        dur = random.uniform(3.5, 25.0)
        ev = make_event(ASSETS[2], t, tag=tag, test=True)
        ev["duration_min"] = round(dur, 1)
        ev["ack_time"] = (t + timedelta(minutes=0.8)).strftime("%Y-%m-%d %H:%M:%S")
        ev["clear_time"] = (t + timedelta(minutes=dur)).strftime("%Y-%m-%d %H:%M:%S")
        ev["operator_id"] = "OP05"
        rows.append(ev)

    rows.sort(key=lambda r: r["activation_time"])

    with open("alarm_log.csv", "w", newline="") as f:
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