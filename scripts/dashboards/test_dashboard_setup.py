# test_dashboard_setup.py
import sys
import os
import pandas as pd
from sqlalchemy import create_engine, inspect
import time

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'analytics-pipeline'))
from environmental_correlation import compute_overlap_correlation

from layout.header import ASSET_OPTIONS
from layout.environmental_panel import create_environmental_panel

from dashboard_config import DB_PATH

passed = 0
failed = 0

def check(name, condition, detail=""):
    global passed, failed
    status = "OK" if condition else "FAIL"
    print(f"{status}: {name}")
    if detail:
        print(f"  {detail}")
    if condition:
        passed += 1
    else:
        failed += 1

print("Dashboard validation tests")
print()

try:
    exists = os.path.exists(DB_PATH)
    check("Database file exists", exists, f"{DB_PATH}")
except Exception as e:
    check("Database file exists", False, str(e))

print()

try:
    engine = create_engine(f"sqlite:///{DB_PATH}")
    conn = engine.connect()
    conn.close()
    check("Database connection", True)
except Exception as e:
    check("Database connection", False, str(e))
    engine = None

print()

try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    required = ["historian_clean", "alarm_log_clean", "environmental_clean", "pipeline_runs"]
    all_exist = all(t in tables for t in required)
    check("Required tables", all_exist, f"Found {len(tables)} tables: {tables}")
except Exception as e:
    check("Required tables", False, str(e))

print()

try:
    count_df = pd.read_sql("SELECT COUNT(*) as cnt FROM historian_clean", engine)
    count = count_df["cnt"].iloc[0]

    assets_df = pd.read_sql("SELECT DISTINCT asset_id FROM historian_clean ORDER BY asset_id", engine)
    num_assets = len(assets_df)

    range_df = pd.read_sql(
        "SELECT MIN(timestamp) as min_ts, MAX(timestamp) as max_ts FROM historian_clean",
        engine, parse_dates=["min_ts", "max_ts"]
    )
    ts_min = range_df["min_ts"].iloc[0]
    ts_max = range_df["max_ts"].iloc[0]

    ok = count > 0 and num_assets == 10
    check("Historian data", ok, f"{count:,} rows, {num_assets} assets, {ts_min} to {ts_max}")
except Exception as e:
    check("Historian data", False, str(e))

print()

try:
    count_df = pd.read_sql("SELECT COUNT(*) as cnt FROM environmental_clean", engine)
    count = count_df["cnt"].iloc[0]

    range_df = pd.read_sql(
        "SELECT MIN(timestamp) as min_ts, MAX(timestamp) as max_ts FROM environmental_clean",
        engine, parse_dates=["min_ts", "max_ts"]
    )
    ts_min = range_df["min_ts"].iloc[0]
    ts_max = range_df["max_ts"].iloc[0]

    ok = count > 0
    check("Environmental data", ok, f"{count:,} rows, {ts_min} to {ts_max}")
except Exception as e:
    check("Environmental data", False, str(e))

print()

try:
    assets_df = pd.read_sql(
        "SELECT DISTINCT asset_id FROM historian_clean ORDER BY asset_id",
        engine
    )
    asset_list = assets_df["asset_id"].tolist()
    expected = ["P-0100", "P-0200", "P-0300", "P-0400", "P-0500",
                "P-0600", "P-0700", "P-0800", "P-0900", "P-1000"]
    all_present = all(a in asset_list for a in expected)
    check("Asset list", all_present, f"{asset_list}")
except Exception as e:
    check("Asset list", False, str(e))

print()

try:
    query = """
        SELECT
            MIN(timestamp) as hist_min, MAX(timestamp) as hist_max,
            (SELECT MIN(timestamp) FROM environmental_clean) as env_min,
            (SELECT MAX(timestamp) FROM environmental_clean) as env_max
        FROM historian_clean
        """

    df = pd.read_sql(query, engine, parse_dates=["hist_min", "hist_max", "env_min", "env_max"])

    hist_min = df["hist_min"].iloc[0]
    hist_max = df["hist_max"].iloc[0]
    env_min = df["env_min"].iloc[0]
    env_max = df["env_max"].iloc[0]

    overlap = (hist_min <= env_max) and (env_min <= hist_max)
    check("Date overlap", overlap, f"Historian {hist_min} to {hist_max}, Environmental {env_min} to {env_max}")
except Exception as e:
    check("Date overlap", False, str(e))

print()

try:
    hist_sample = pd.read_sql("""
                              SELECT timestamp, flow_m3h FROM historian_clean
                              WHERE asset_id = 'P-0100'
                              AND timestamp >= '2025-06-15'
                              LIMIT 5000
                              """,
        engine, parse_dates=["timestamp"]
    )
    env_sample = pd.read_sql("""
                             SELECT timestamp, discharge_cfs FROM environmental_clean
                             WHERE timestamp >= '2025-06-15'
                             LIMIT 5000
                             """,
        engine, parse_dates=["timestamp"]
    )

    result = compute_overlap_correlation(
        hist_sample, env_sample,
        hist_col="flow_m3h",
        env_col="discharge_cfs",
        hist_ts_col="timestamp",
        env_ts_col="timestamp",
    )

    ok = result["data_available"]
    check("Correlation module", ok, f"Overlap: {result['overlap_count']}, Correlation: {result['correlation_str']}")
except Exception as e:
    check("Correlation module", False, str(e))

print()

try:
    quality_df = pd.read_sql(
        "SELECT quality_flag, COUNT(*) as cnt FROM alarm_log_clean GROUP BY quality_flag",
        engine
    )

    pass_cnt = quality_df[quality_df["quality_flag"] == "pass"]["cnt"].sum() if "pass" in quality_df["quality_flag"].values else 0
    missing_cnt = quality_df[quality_df["quality_flag"] == "missing"]["cnt"].sum() if "missing" in quality_df["quality_flag"].values else 0
    total = quality_df["cnt"].sum()

    pct = 100.0 * missing_cnt / total if total > 0 else 0
    ok = pct < 10.0
    check("Alarm log quality", ok, f"Pass: {pass_cnt:,}, Missing: {missing_cnt:,} ({pct:.1f}%)")
except Exception as e:
    check("Alarm log quality", False, str(e))

print()

try:
    start = time.time()
    df = pd.read_sql("""
                     SELECT timestamp, flow_m3h, motor_temp_c, vibration_mm_s
                     FROM historian_clean
                     WHERE asset_id = 'P-0100'
                     AND timestamp BETWEEN '2025-06-01' AND '2025-06-30'
                     """,
                     engine, parse_dates=["timestamp"]
                     )
    elapsed = time.time() - start
    ok = elapsed < 2.0 and len(df) > 0
    check("Query performance", ok, f"{len(df):,} rows in {elapsed:.3f}s")
except Exception as e:
    check("Query performance", False, str(e))

print()

try:
    hist_df = pd.read_sql("""
                          SELECT timestamp, flow_m3h FROM historian_clean
                          WHERE asset_id = 'P-0100'
                          AND timestamp BETWEEN '2025-06-15' AND '2025-12-31'
                          ORDER BY timestamp
                          """,
                          engine, parse_dates=["timestamp"]
                          )
    env_df = pd.read_sql("""
                         SELECT timestamp, discharge_cfs FROM environmental_clean
                         WHERE timestamp BETWEEN '2025-06-15' AND '2025-12-31'
                         ORDER BY timestamp
                         """,
                         engine, parse_dates=["timestamp"]
                         )

    ok = len(hist_df) > 0 and len(env_df) > 0
    check("Callback data", ok, f"Historian: {len(hist_df):,}, Environmental: {len(env_df):,}")
except Exception as e:
    check("Callback data", False, str(e))

print()

try:
    ok = len(ASSET_OPTIONS) == 10 and ASSET_OPTIONS[0]["value"] == "P-0100"
    check("Header module", ok, f"Loaded {len(ASSET_OPTIONS)} assets")
except Exception as e:
    check("Header module", False, str(e))

print()

try:
    panel = create_environmental_panel()
    ok = panel is not None and hasattr(panel, 'children')
    check("Environmental panel", ok)
except Exception as e:
    check("Environmental panel", False, str(e))

print()

try:
    vib_df = pd.read_sql("""
                         SELECT asset_id, AVG(vibration_mm_s) as avg_vib
                         FROM historian_clean
                         WHERE timestamp BETWEEN '2025-01-01' AND '2025-12-31'
                         GROUP BY asset_id
                         ORDER BY asset_id
                         """,
                         engine
                         )

    max_avg_vib = vib_df["avg_vib"].max()
    ok = len(vib_df) == 10
    check("Asset vibration levels", ok, f"Max avg vibration: {max_avg_vib:.2f} mm/s")
    print("  Breakdown:")
    for _, row in vib_df.iterrows():
        print(f"    {row['asset_id']}: {row['avg_vib']:.2f} mm/s")
except Exception as e:
    check("Asset vibration levels", False, str(e))

print()

try:
    alarm_df = pd.read_sql("""
                           SELECT asset_id, COUNT(*) as alarm_count
                           FROM alarm_log_clean
                           GROUP BY asset_id
                           ORDER BY asset_id
                           """,
                           engine
                           )

    ok = len(alarm_df) == 10 and alarm_df["alarm_count"].sum() > 0
    check("Asset alarm counts", ok, f"Total alarms: {alarm_df['alarm_count'].sum():,}")
    print("  Breakdown:")
    for _, row in alarm_df.iterrows():
        print(f"    {row['asset_id']}: {row['alarm_count']:,} alarms")
except Exception as e:
    check("Asset alarm counts", False, str(e))

print()

try:
    start = time.time()
    df_full = pd.read_sql("""
                          SELECT timestamp, flow_m3h, vibration_mm_s
                          FROM historian_clean
                          WHERE asset_id = 'P-0100'
                          AND timestamp BETWEEN '2025-01-01' AND '2025-12-31'
                          ORDER BY timestamp
                          """,
                          engine, parse_dates=["timestamp"]
                          )
    elapsed_full = time.time() - start

    start = time.time()
    df_subsampled = df_full.set_index("timestamp").resample("5min").mean().reset_index()
    elapsed_resample = time.time() - start

    ok = elapsed_full < 3.0
    detail = f"Full query: {elapsed_full:.3f}s ({len(df_full):,} rows), resample: {elapsed_resample:.3f}s ({len(df_subsampled):,} rows)"
    check("Historian subsampling performance", ok, detail)
except Exception as e:
    check("Historian subsampling performance", False, str(e))

print()

try:
    hist_df = pd.read_sql("""
                          SELECT timestamp, flow_m3h FROM historian_clean
                          WHERE asset_id = 'P-0100'
                          AND timestamp BETWEEN '2025-06-01' AND '2025-12-31'
                          """, engine, parse_dates=["timestamp"])

    alarm_df = pd.read_sql("""
                           SELECT COUNT(*) as cnt FROM alarm_log_clean
                           WHERE asset_id = 'P-0100'
                           AND timestamp >= datetime('2025-12-31', '-1 day')
                           """, engine)

    env_df = pd.read_sql("""
                         SELECT timestamp, discharge_cfs FROM environmental_clean
                         WHERE timestamp BETWEEN '2025-06-01' AND '2025-12-31'
                         """, engine, parse_dates=["timestamp"])

    ok = len(hist_df) > 0 and len(alarm_df) > 0 and len(env_df) > 0
    detail = f"Historian: {len(hist_df):,}, Alarms: {alarm_df['cnt'].iloc[0]}, Environmental: {len(env_df):,}"
    check("Dashboard callback data integrity", ok, detail)
except Exception as e:
    check("Dashboard callback data integrity", False, str(e))

print()

try:
    anomaly_dist = pd.read_sql("""
                               SELECT asset_id,
                                   SUM(CASE WHEN failure_type != 'none' THEN 1 ELSE 0 END) as anomaly_count,
                                   COUNT(*) as total,
                                   ROUND(100.0 * SUM(CASE WHEN failure_type != 'none' THEN 1 ELSE 0 END) / COUNT(*), 2) as anomaly_pct
                               FROM historian_clean
                               GROUP BY asset_id
                               ORDER BY anomaly_pct DESC
                               """, engine)

    ok = len(anomaly_dist) == 10
    check("Asset anomaly rates", ok, f"Max anomaly rate: {anomaly_dist['anomaly_pct'].max():.2f}%")
    print("  Breakdown:")
    for _, row in anomaly_dist.iterrows():
        print(f"    {row['asset_id']}: {row['anomaly_pct']:.2f}% ({row['anomaly_count']:,}/{row['total']:,})")
except Exception as e:
    check("Asset anomaly rates", False, str(e))

if engine:
    engine.dispose()

print()
print(f"Results: {passed} passed, {failed} failed")

if failed > 0:
    sys.exit(1)
else:
    print("Dashboard test complete")
    sys.exit(0)
