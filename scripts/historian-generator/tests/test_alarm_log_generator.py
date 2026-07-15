# tests/test_alarm_log_generator.py

import sys
import os
from collections import Counter
import pytest
import random
from datetime import datetime, timedelta
from scipy.stats import mannwhitneyu

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from alarm_log_generator import build_assets, ALARM_TAG_TEMPLATES, FAILURE_FAMILY_MAP, make_event, generate_failure_correlated_alarms
from historian_generator import FAILURE_SCENARIOS, SyntheticHistorian, HistorianConfig

START = datetime(2025, 1, 1)


@pytest.fixture(scope="module")
def assets():
    return build_assets(10)


@pytest.fixture(scope="module")
def failure_rows(assets):
    random.seed(42)
    return generate_failure_correlated_alarms(assets, FAILURE_SCENARIOS, START)


@pytest.fixture(scope="module")
def full_rows(assets, failure_rows):
    random.seed(42)
    rows = []
    for _ in range(21900):
        a = random.choice(assets)
        d = random.randint(0, 364)
        h = max(0, min(23, int(random.gauss(14, 6))))
        m = random.uniform(0, 59)
        t = START + timedelta(days=d, hours=h, minutes=m)
        rows.append(make_event(a, t))
    rows.extend(failure_rows)
    return rows


class TestAssetConfig:
    def test_asset_count(self, assets):
        assert len(assets) == 10

    def test_asset_id_format(self, assets):
        expected = [f"P-{(i+1)*100:04d}" for i in range(10)]
        assert [a["asset_id"] for a in assets] == expected

    def test_asset_ids_match_historian(self, assets):
        cfg = HistorianConfig(num_assets=10, period_days=1, freq_min=60)
        h = SyntheticHistorian(cfg)
        historian_ids = [a["asset_id"] for a in h.assets]
        alarm_ids = [a["asset_id"] for a in assets]
        assert alarm_ids == historian_ids

    def test_areas_assigned(self, assets):
        for a in assets:
            assert a["area"] != ""
            assert a["area"] is not None

    def test_tag_format(self, assets):
        for asset in assets:
            for tag in asset["tags"]:
                parts = tag.split(".")
                assert len(parts) == 2, f"malformed tag: {tag}"
                assert parts[0] == asset["asset_id"]
                assert parts[1] in ALARM_TAG_TEMPLATES


class TestMakeEvent:
    def test_required_fields(self, assets):
        random.seed(0)
        t = START + timedelta(days=10, hours=12)
        ev = make_event(assets[0], t)
        expected_keys = [
            "asset_id", "alarm_tag", "alarm_description", "priority", "alarm_type",
            "activation_time", "ack_time", "clear_time", "duration_min",
            "operator_id", "area", "is_test_case"
        ]
        for k in expected_keys:
            assert k in ev, f"missing field: {k}"

    def test_priority_range(self, assets):
        random.seed(1)
        for _ in range(200):
            t = START + timedelta(days=random.randint(0, 364), hours=12)
            ev = make_event(random.choice(assets), t)
            assert ev["priority"] in (1, 2, 3, 4)

    def test_duration_positive(self, assets):
        random.seed(2)
        for _ in range(200):
            t = START + timedelta(days=random.randint(0, 364), hours=12)
            ev = make_event(random.choice(assets), t)
            assert ev["duration_min"] >= 0.5

    def test_ack_before_clear(self, assets):
        random.seed(3)
        fmt = "%Y-%m-%d %H:%M:%S"
        for _ in range(200):
            t = START + timedelta(days=random.randint(0, 364), hours=12)
            ev = make_event(random.choice(assets), t)
            if ev["clear_time"] != "":
                ack = datetime.strptime(ev["ack_time"], fmt)
                clear = datetime.strptime(ev["clear_time"], fmt)
                assert ack <= clear, (
                    f"ack {ev['ack_time']} is after clear {ev['clear_time']} "
                    f"for tag {ev['alarm_tag']} (duration={ev['duration_min']} min)"
                )

    def test_test_flag(self, assets):
        random.seed(4)
        t = START + timedelta(days=5, hours=8)
        ev = make_event(assets[0], t, test=True)
        assert ev["is_test_case"] == "YES"
        assert "(test)" in ev["alarm_description"]

    def test_operator_valid(self, assets):
        random.seed(5)
        valid_ops = {"OP01", "OP02", "OP03", "OP04", "OP05"}
        for _ in range(100):
            t = START + timedelta(days=10, hours=10)
            ev = make_event(random.choice(assets), t)
            assert ev["operator_id"] in valid_ops


class TestDateRange:
    def test_all_within_year(self, full_rows):
        fmt = "%Y-%m-%d %H:%M:%S"
        year_end = datetime(2025, 12, 31, 23, 59, 59)
        for r in full_rows:
            t = datetime.strptime(r["activation_time"], fmt)
            assert START <= t <= year_end

    def test_covers_full_year(self, full_rows):
        fmt = "%Y-%m-%d %H:%M:%S"
        times = [datetime.strptime(r["activation_time"], fmt) for r in full_rows]
        assert (max(times) - min(times)).days >= 300


class TestFailureCorrelation:
    def test_failure_assets_covered(self, failure_rows):
        ids_in_rows = {r["asset_id"] for r in failure_rows}
        for s in FAILURE_SCENARIOS:
            assert s["asset_id"] in ids_in_rows

    def test_correct_tag_families(self, failure_rows):
        # each failure scenario should only produce alarms from its mapped families
        for scenario in FAILURE_SCENARIOS:
            asset_id = scenario["asset_id"]
            expected_families = set(FAILURE_FAMILY_MAP[scenario["scenario"]])
            for r in failure_rows:
                if r["asset_id"] != asset_id:
                    continue
                suffix = r["alarm_tag"].split(".")[-1]
                family = ALARM_TAG_TEMPLATES[suffix]["family"]
                assert family in expected_families, (f"{asset_id} {scenario['scenario']}: unexpected family '{family}'")

    def test_alarm_rate_higher_on_degrading_asset(self, assets, full_rows):
        # bearing scenario: P-0100, start_day=100, ramp_days=45
        # compare alarm rate during the failure window against a healthy asset
        scenario = next(s for s in FAILURE_SCENARIOS if s["scenario"] == "bearing")
        start_day = scenario["start_day"]
        ramp_days = scenario["ramp_days"]
        failure_asset = scenario["asset_id"]

        failed_ids = {s["asset_id"] for s in FAILURE_SCENARIOS}
        healthy_asset = next(a["asset_id"] for a in assets if a["asset_id"] not in failed_ids)

        fmt = "%Y-%m-%d %H:%M:%S"

        def daily_counts(asset_id):
            c = Counter()
            for r in full_rows:
                if r["asset_id"] != asset_id:
                    continue
                t = datetime.strptime(r["activation_time"], fmt)
                day = (t - START).days
                if start_day <= day < start_day + ramp_days:
                    c[day] += 1
            return [c.get(d, 0) for d in range(start_day, start_day + ramp_days)]

        degrading = daily_counts(failure_asset)
        healthy = daily_counts(healthy_asset)

        stat, p = mannwhitneyu(degrading, healthy, alternative="greater")
        assert p < 0.05, f"alarm rate not significantly higher on {failure_asset} (p={p:.4f})"

    def test_alarms_within_failure_window(self, failure_rows):
        fmt = "%Y-%m-%d %H:%M:%S"
        for scenario in FAILURE_SCENARIOS:
            asset_id = scenario["asset_id"]
            end_day = scenario["start_day"] + scenario["ramp_days"]
            for r in failure_rows:
                if r["asset_id"] != asset_id:
                    continue
                t = datetime.strptime(r["activation_time"], fmt)
                day = (t - START).days
                assert day >= scenario["start_day"], (f"{asset_id}: alarm on day {day} before scenario start {scenario['start_day']}")
                assert day <= min(end_day, 364)


class TestISA182:
    def test_rate_within_benchmark(self, full_rows):
        rate = len(full_rows) / (10 * 365)
        assert rate <= 144, f"alarm rate {rate:.1f}/asset/day exceeds ISA-18.2 max of 144"

    def test_no_asset_dominates(self, full_rows):
        # no single asset should account for more than 3x the average share
        counts = Counter(r["asset_id"] for r in full_rows)
        avg = len(full_rows) / 10
        for asset_id, n in counts.items():
            assert n <= avg * 3, f"{asset_id} has {n} alarms vs avg {avg:.0f}"