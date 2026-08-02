# alarm_analytics.py
"""
Alarm log analytics: detect chattering, stale alarms, clusters, and
compute daily rates vs ISA-18.2 benchmarks. Validates test cases.
"""

import os
import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import json 

from analytics_config import (
    ALARM_TABLE, ALARM_TEST_CASE_VALUE, ALARM_TEST_CASES,
    ISA_CHATTER_MAX_EVENTS, ISA_CHATTER_WINDOW_MIN,
    STALE_ALARM_HOURS, CLUSTER_WINDOW_MIN, ISA_DAILY_RATE_TARGET,
    OUTPUT_DIR, OUTPUT_FILES, ETL_PIPELINE_PATH,
)

class AlarmAnalytics:
    """Load alarm log from database and compute analytics: chattering, stale, clusters, daily rates."""
    def __init__(self, db_path):
        """Load alarm_log_clean table and prepare for analysis."""
        engine = create_engine(f"sqlite:///{db_path}")
        self.df = pd.read_sql_table(ALARM_TABLE, engine)
        engine.dispose()
        self._validate_schema()

        self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])
        self.df["ack_time"] = pd.to_datetime(self.df["ack_time"], errors="coerce")
        self.df["clear_time"] = pd.to_datetime(self.df["clear_time"], errors="coerce")
        self.df = self.df.sort_values("timestamp").reset_index(drop=True)

    def _validate_schema(self):
        """Check for required alarm columns."""
        required = ["asset_id", "alarm_tag", "timestamp", "priority"]
        missing = [c for c in required if c not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def alarm_rate_per_asset_per_day(self):
        """Daily alarm count per asset vs ISA-18.2 target (ISA_DAILY_RATE_TARGET/day)"""
        temp = self.df.copy()
        temp["date"] = temp["timestamp"].dt.date
        rate = temp.groupby(["asset_id", "date"]).size().reset_index(name="alarm_count")
        rate["exceeds_isa_target"] = rate["alarm_count"] > ISA_DAILY_RATE_TARGET
        return rate

    def top_10_alarms(self):
        """Return top 10 alarm tags by frequency with average priority."""
        grouped = self.df.groupby("alarm_tag").agg(
            alarm_description=("alarm_description", "first"),
            avg_priority=("priority", "mean"),
            count=("alarm_tag", "size"),
        ).reset_index()
        return grouped.sort_values("count", ascending=False).head(10)[
            ["alarm_tag", "alarm_description", "count", "avg_priority"]
        ]

    def average_time_to_acknowledge(self, per_asset):
        """Compute mean time from alarm activation to acknowledgment."""
        valid = self.df.dropna(subset=["ack_time"]).copy()
        valid["ack_hours"] = (valid["ack_time"] - valid["timestamp"]).dt.total_seconds() / 3600.0

        if per_asset:
            return valid.groupby("asset_id")["ack_hours"].mean().reset_index(name="avg_hours_to_ack")
        return valid["ack_hours"].mean()

    def detect_stale_alarms(self, hours):
        """Find alarms active longer than threshold or never cleared."""
        df = self.df.copy()
        now_reference = df["timestamp"].max()

        never_cleared = df[df["clear_time"].isna()].copy()
        never_cleared["active_hours"] = (now_reference - never_cleared["timestamp"]).dt.total_seconds() / 3600.0
        never_cleared["stale_reason"] = "never_cleared"

        cleared = df.dropna(subset=["clear_time"]).copy()
        cleared["active_hours"] = (cleared["clear_time"] - cleared["timestamp"]).dt.total_seconds() / 3600.0
        cleared = cleared[cleared["active_hours"] > hours].copy()
        cleared["stale_reason"] = "exceeded_threshold"

        combined = pd.concat([never_cleared, cleared], ignore_index=True)
        if combined.empty:
            return pd.DataFrame(columns=["asset_id", "alarm_tag", "timestamp", "clear_time", "active_hours", "stale_reason"])
        return combined.sort_values("active_hours", ascending=False)[
            ["asset_id", "alarm_tag", "timestamp", "clear_time", "active_hours", "stale_reason"]
        ]

    def detect_chattering(self, window_minutes, max_events):
        """Flag rapid repeated alarms (same asset/tag within window)."""
        results = []
        for (asset, tag), group in self.df.groupby(["asset_id", "alarm_tag"]):
            times = group["timestamp"].sort_values().values
            for i in range(len(times)):
                window_end = times[i] + pd.Timedelta(minutes=window_minutes)
                count = int(np.sum((times >= times[i]) & (times <= window_end)))
                if count > max_events:
                    results.append({
                        "asset_id": asset,
                        "alarm_tag": tag,
                        "window_start": times[i],
                        "window_end": window_end,
                        "event_count": count,
                        "is_chattering": True,
                    })

        if not results:
            return pd.DataFrame(columns=["asset_id", "alarm_tag", "window_start", "window_end", "event_count", "is_chattering"])

        result_df = pd.DataFrame(results).drop_duplicates(subset=["asset_id", "alarm_tag", "window_start"])
        return result_df.sort_values("event_count", ascending=False).reset_index(drop=True)

    def cluster_alarms(self, time_window_minutes):
        """Group distinct alarm tags per asset within time window; flag multi-alarm clusters."""
        results = []
        cluster_id = 0

        for asset in self.df["asset_id"].unique():
            asset_df = self.df[self.df["asset_id"] == asset].sort_values("timestamp")
            current_tags = []
            total_events = 0
            cluster_start = None
            last_time = None

            for _, row in asset_df.iterrows():
                if not current_tags:
                    current_tags = [row["alarm_tag"]]
                    total_events = 1
                    cluster_start = row["timestamp"]
                    last_time = row["timestamp"]
                    continue

                gap_minutes = (row["timestamp"] - last_time).total_seconds() / 60.0
                if gap_minutes <= time_window_minutes:
                    total_events += 1
                    if row["alarm_tag"] not in current_tags:
                        current_tags.append(row["alarm_tag"])
                    last_time = row["timestamp"]
                else:
                    if len(current_tags) > 1:
                        results.append({
                            "cluster_id": cluster_id,
                            "asset_id": asset,
                            "distinct_alarm_count": len(current_tags),
                            "total_events": total_events,
                            "alarms_in_cluster": ",".join(current_tags),
                            "start_time": cluster_start,
                            "end_time": last_time,
                        })
                        cluster_id += 1
                    current_tags = [row["alarm_tag"]]
                    total_events = 1
                    cluster_start = row["timestamp"]
                    last_time = row["timestamp"]

            if len(current_tags) > 1:
                results.append({
                    "cluster_id": cluster_id,
                    "asset_id": asset,
                    "distinct_alarm_count": len(current_tags),
                    "total_events": total_events,
                    "alarms_in_cluster": ",".join(current_tags),
                    "start_time": cluster_start,
                    "end_time": last_time,
                })

        if not results:
            return pd.DataFrame(columns=["cluster_id", "asset_id", "distinct_alarm_count", "total_events", "alarms_in_cluster", "start_time", "end_time"])
        return pd.DataFrame(results)

    def validate_against_known_test_cases(self):
        """Check if synthetic test cases were detected correctly."""
        if "is_test_case" not in self.df.columns:
            print("is_test_case column not found")
            return {"chattering": None, "stale": None, "cluster": None}

        test_rows = self.df[self.df["is_test_case"] == ALARM_TEST_CASE_VALUE]
        print(f"Test case rows: {len(test_rows)}")

        chatter = self.detect_chattering(ISA_CHATTER_WINDOW_MIN, ISA_CHATTER_MAX_EVENTS)
        stale = self.detect_stale_alarms(STALE_ALARM_HOURS)
        clusters = self.cluster_alarms(CLUSTER_WINDOW_MIN)

        chatter_case = ALARM_TEST_CASES["chattering"]
        found_chatter = len(chatter[(chatter["asset_id"] == chatter_case["asset_id"])
                                    & (chatter["alarm_tag"] == chatter_case["alarm_tag"])]) > 0
        print(f"Chattering: {'PASS' if found_chatter else 'FAIL'}")

        stale_case = ALARM_TEST_CASES["stale"]
        found_stale = len(stale[(stale["asset_id"] == stale_case["asset_id"])
                                & (stale["alarm_tag"] == stale_case["alarm_tag"])]) > 0
        print(f"Stale: {'PASS' if found_stale else 'FAIL'}")

        cluster_case = ALARM_TEST_CASES["cluster"]
        found_cluster = len(clusters[clusters["asset_id"] == cluster_case["asset_id"]]) > 0
        print(f"Cluster: {'PASS' if found_cluster else 'FAIL'}")

        return {
            "chattering": found_chatter,
            "stale": found_stale,
            "cluster": found_cluster,
        }
    
if __name__ == "__main__":
    if not os.path.exists(ETL_PIPELINE_PATH):
        print(f"Database not found: {ETL_PIPELINE_PATH}")
        sys.exit(1)

    print("Loading alarm analytics...")
    aa = AlarmAnalytics(ETL_PIPELINE_PATH)
    print(f"Records: {len(aa.df)}\n")

    print("Test case validation:")
    validation_results = aa.validate_against_known_test_cases()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(os.path.join(OUTPUT_DIR, OUTPUT_FILES["isa_validation_results"]), "w") as f:
        json.dump(validation_results, f, indent=2)
        

    print("\nComputing metrics...")
    rate_df = aa.alarm_rate_per_asset_per_day()
    rate_df.to_csv(os.path.join(OUTPUT_DIR, OUTPUT_FILES["alarm_rate_daily"]), index=False)

    top10 = aa.top_10_alarms()
    top10.to_csv(os.path.join(OUTPUT_DIR, OUTPUT_FILES["alarm_frequency_top10"]), index=False)

    avg_ack = aa.average_time_to_acknowledge(per_asset=True)
    avg_ack.to_csv(os.path.join(OUTPUT_DIR, OUTPUT_FILES["alarm_avg_time_to_ack"]), index=False)

    stale = aa.detect_stale_alarms(STALE_ALARM_HOURS)
    stale.to_csv(os.path.join(OUTPUT_DIR, OUTPUT_FILES["alarm_stale_events"]), index=False)

    chatter = aa.detect_chattering(ISA_CHATTER_WINDOW_MIN, ISA_CHATTER_MAX_EVENTS)
    chatter.to_csv(os.path.join(OUTPUT_DIR, OUTPUT_FILES["alarm_chattering_events"]), index=False)

    clusters = aa.cluster_alarms(CLUSTER_WINDOW_MIN)
    clusters.to_csv(os.path.join(OUTPUT_DIR, OUTPUT_FILES["alarm_clusters"]), index=False)

    print(f"Outputs saved to {OUTPUT_DIR}")