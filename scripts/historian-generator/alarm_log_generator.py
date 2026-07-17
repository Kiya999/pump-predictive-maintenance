# alarm_log_generator.py
"""Generate synthetic alarm log for predictive maintenance testing.

Outputs CSV with 10 pump assets x 1 year of alarm events including normal
background alarms, failure-correlated alarms, and synthetic test cases
(chattering, stale, cascade) for validation of alarm analysis pipeline.

Note: alarm generation depends on historian configuration and must match historian run for consistency
"""

import os
import csv
import random
from datetime import timedelta

from historian_config import (FAILURE_SCENARIOS, AREAS, NUM_ASSETS, PERIOD_DAYS,
                              SEED, BASE_TIME)
from alarm_log_config import (OUTPUT_DIR, CSV_PATH, NORMAL_ALARMS_PER_ASSET_PER_DAY,
                              CHATTERING_EVENTS_COUNT, CHATTERING_INTERVAL_MIN,
                              CHATTERING_DURATION_MIN, STALE_ALARM_DURATION_MIN,
                              CASCADE_INTERVAL_SEC, OPERATORS, ALARM_TAG_TEMPLATES,
                              FAILURE_FAMILY_MAP, PRIORITY_DURATION_MEANS,
                              PRIORITY_DURATION_STDS, CHATTERING_ACK_DELAY_MIN,
                              STALE_ALARM_ACK_DELAY_MIN, CASCADE_DURATION_MIN,
                              CASCADE_DURATION_MAX, CASCADE_ACK_DELAY_MIN,
                              ISA_18_2_ALARMS_PER_ASSET_PER_DAY_MAX)


ALARM_FIELDS = [
    "asset_id", "alarm_tag", "alarm_description", "priority", "alarm_type",
    "activation_time", "ack_time", "clear_time", "duration_min",
    "operator_id", "area", "is_test_case"
]

def build_assets(num_assets):
    """Build asset list with alarm tags from tag templates."""
    assets = []
    for i in range(num_assets):
        asset_id = f"P-{(i+1)*100:04d}"
        tag_suffixes = list(ALARM_TAG_TEMPLATES.keys())
        tags = [f"{asset_id}.{sfx}" for sfx in tag_suffixes]
        assets.append({"asset_id": asset_id, "area": AREAS[i % len(AREAS)], "tags": tags,})
    return assets

def make_event(asset, t, tag=None, test=False):
    """Create alarm event record for asset at timestamp t."""
    if tag is None:
        tag = random.choice(asset["tags"])
    suffix = tag.split(".")[-1]
    m = ALARM_TAG_TEMPLATES[suffix]

    means = PRIORITY_DURATION_MEANS
    stds = PRIORITY_DURATION_STDS

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
        "operator_id": random.choice(OPERATORS),
        "area": asset["area"],
        "is_test_case": "YES" if test else ""
    }

def generate_failure_correlated_alarms(assets_by_id, failure_scenarios, start):
    """Generate alarms correlated with failure scenario timings and signal families"""
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
    random.seed(SEED)
    start = BASE_TIME
    ASSETS = build_assets(NUM_ASSETS)
    rows = []

    normal_events_count = NORMAL_ALARMS_PER_ASSET_PER_DAY * NUM_ASSETS * PERIOD_DAYS # normal events: ~6 alarms per asset per day = 6 * 10 * 365 = 21,900

    for _ in range(normal_events_count):
        a = random.choice(ASSETS)
        d = random.randint(0, 364)
        h = max(0, min(23, int(random.gauss(14, 6))))
        m = random.uniform(0, 59)
        t = start + timedelta(days=d, hours=h, minutes=m)
        rows.append(make_event(a, t))

    # chattering: P-0100.VI_HI x7 in ~8 min
    t0 = start + timedelta(days=5, hours=8, minutes=30)
    for i in range(CHATTERING_EVENTS_COUNT):
        t = t0 + timedelta(minutes=CHATTERING_INTERVAL_MIN * i)
        ev = make_event(ASSETS[0], t, tag="P-0100.VI_HI", test=True)
        ev["duration_min"] = CHATTERING_DURATION_MIN
        ev["ack_time"] = (t + timedelta(minutes=CHATTERING_ACK_DELAY_MIN)).strftime("%Y-%m-%d %H:%M:%S")
        ev["clear_time"] = (t + timedelta(minutes=CHATTERING_DURATION_MIN)).strftime("%Y-%m-%d %H:%M:%S")
        ev["operator_id"] = "OP01"
        rows.append(ev)

    # stale: P-0200.FI_LO never clears
    t0 = start + timedelta(days=10, hours=2)
    ev = make_event(ASSETS[1], t0, tag="P-0200.FI_LO", test=True)
    ev["duration_min"] = STALE_ALARM_DURATION_MIN
    ev["ack_time"] = (t0 + timedelta(minutes=STALE_ALARM_ACK_DELAY_MIN)).strftime("%Y-%m-%d %H:%M:%S")
    ev["clear_time"] = ""
    ev["operator_id"] = "OP04"
    rows.append(ev)

    # correlated batch: P-0300 cascade
    t0 = start + timedelta(days=15, hours=14, minutes=22, seconds=30)
    batch = ["P-0300.PI_LO", "P-0300.FI_LO", "P-0300.VI_HI", "P-0300.PDI_HI", "P-0300.TI_HI"]
    for i, tag in enumerate(batch):
        t = t0 + timedelta(seconds=CASCADE_INTERVAL_SEC * i)
        dur = random.uniform(CASCADE_DURATION_MIN, CASCADE_DURATION_MAX)
        ev = make_event(ASSETS[2], t, tag=tag, test=True)
        ev["duration_min"] = round(dur, 1)
        ev["ack_time"] = (t + timedelta(minutes=CASCADE_ACK_DELAY_MIN)).strftime("%Y-%m-%d %H:%M:%S")
        ev["clear_time"] = (t + timedelta(minutes=dur)).strftime("%Y-%m-%d %H:%M:%S")
        ev["operator_id"] = "OP05"
        rows.append(ev)

    failure_rows = generate_failure_correlated_alarms(ASSETS, FAILURE_SCENARIOS, start)
    rows.extend(failure_rows)
    print(f"  Failure-correlated alarms added: {len(failure_rows)}")

    rows.sort(key=lambda r: r["activation_time"])

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(CSV_PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ALARM_FIELDS)
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
    total_asset_days = NUM_ASSETS * PERIOD_DAYS
    rate = len(rows) / total_asset_days
    print(f"  Mean alarm rate: {rate:.1f} alarms/asset/day")
    if rate > ISA_18_2_ALARMS_PER_ASSET_PER_DAY_MAX:
        print("  WARNING: exceeds ISA-18.2 benchmark")
