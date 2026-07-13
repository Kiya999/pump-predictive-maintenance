# alarm_analytics.py
import os
import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

ISA_CHATTER_MAX_EVENTS = 3
ISA_CHATTER_WINDOW_MIN = 5
STALE_ALARM_HOURS = 24
CLUSTER_WINDOW_MIN = 30
ISA_DAILY_RATE_TARGET = 144


class AlarmAnalytics:
    def __init__(self, db_path):
        engine = create_engine(f"sqlite:///{db_path}")
        self.df = pd.read_sql_table("alarm_log_clean", engine)
        self._validate_schema()

        self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])
        self.df["ack_time"] = pd.to_datetime(self.df["ack_time"], errors="coerce")
        self.df["clear_time"] = pd.to_datetime(self.df["clear_time"], errors="coerce")
        self.df = self.df.sort_values("timestamp").reset_index(drop=True)

    def _validate_schema(self):
        required = ["asset_id", "alarm_tag", "timestamp", "priority"]
        missing = [c for c in required if c not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def alarm_rate_per_asset_per_day(self):
        """Daily alarm count per asset vs ISA-18.2 target (144/day)"""
        temp = self.df.copy()
        temp["date"] = temp["timestamp"].dt.date
        rate = temp.groupby(["asset_id", "date"]).size().reset_index(name="alarm_count")
        rate["exceeds_isa_target"] = rate["alarm_count"] > ISA_DAILY_RATE_TARGET
        return rate

    def top_10_alarms(self):
        grouped = self.df.groupby("alarm_tag").agg(
            alarm_description=("alarm_description", "first"),
            avg_priority=("priority", "mean"),
            count=("alarm_tag", "size"),
        ).reset_index()
        return grouped.sort_values("count", ascending=False).head(10)[
            ["alarm_tag", "alarm_description", "count", "avg_priority"]
        ]

    def average_time_to_acknowledge(self, per_asset=True):
        valid = self.df.dropna(subset=["ack_time"]).copy()
        valid["ack_hours"] = (valid["ack_time"] - valid["timestamp"]).dt.total_seconds() / 3600.0

        if per_asset:
            return valid.groupby("asset_id")["ack_hours"].mean().reset_index(name="avg_hours_to_ack")
        return valid["ack_hours"].mean()

    def detect_stale_alarms(self, hours=STALE_ALARM_HOURS):
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

    def detect_chattering(self, window_minutes=ISA_CHATTER_WINDOW_MIN, max_events=ISA_CHATTER_MAX_EVENTS):
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

    def cluster_alarms(self, time_window_minutes=CLUSTER_WINDOW_MIN):
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
        if "is_test_case" not in self.df.columns:
            print("is_test_case column not found")
            return

        test_rows = self.df[self.df["is_test_case"] == "YES"]
        print(f"Test case rows: {len(test_rows)}")

        chatter = self.detect_chattering()
        found_chatter = len(chatter[(chatter["asset_id"] == "P-0100") & (chatter["alarm_tag"] == "P-0100.VI_HI")]) > 0
        print(f"Chattering (P-0100.VI_HI): {'PASS' if found_chatter else 'FAIL'}")

        stale = self.detect_stale_alarms()
        found_stale = len(stale[(stale["asset_id"] == "P-0200") & (stale["alarm_tag"] == "P-0200.FI_LO")]) > 0
        print(f"Stale (P-0200.FI_LO): {'PASS' if found_stale else 'FAIL'}")

        clusters = self.cluster_alarms()
        found_cluster = len(clusters[clusters["asset_id"] == "P-0300"]) > 0
        print(f"Cluster (P-0300): {'PASS' if found_cluster else 'FAIL'}")


if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(__file__), "..", "etl-pipeline", "output", "etl_pipeline.db")
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        sys.exit(1)

    print("Loading alarm analytics...")
    aa = AlarmAnalytics(db_path)
    print(f"Records: {len(aa.df)}\n")

    print("Test case validation:")
    aa.validate_against_known_test_cases()

    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    print("\nComputing metrics...")
    rate_df = aa.alarm_rate_per_asset_per_day()
    rate_df.to_csv(os.path.join(output_dir, "alarm_rate_daily.csv"), index=False)

    top10 = aa.top_10_alarms()
    top10.to_csv(os.path.join(output_dir, "alarm_frequency_top10.csv"), index=False)

    avg_ack = aa.average_time_to_acknowledge(per_asset=True)
    avg_ack.to_csv(os.path.join(output_dir, "alarm_avg_time_to_ack.csv"), index=False)

    stale = aa.detect_stale_alarms()
    stale.to_csv(os.path.join(output_dir, "alarm_stale_events.csv"), index=False)

    chatter = aa.detect_chattering()
    chatter.to_csv(os.path.join(output_dir, "alarm_chattering_events.csv"), index=False)

    clusters = aa.cluster_alarms()
    clusters.to_csv(os.path.join(output_dir, "alarm_clusters.csv"), index=False)

    print(f"Outputs saved to {output_dir}")