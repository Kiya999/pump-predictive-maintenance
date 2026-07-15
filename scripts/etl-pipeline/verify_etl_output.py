# verify_etl_output.py
"""
Verify ETL pipeline output: inspect database tables, row counts, timestamp
ranges, assets, quality flags. Quick sanity check after pipeline run.
"""

import gc
import pandas as pd
from sqlalchemy import create_engine, inspect

from etl_config import CONFIG

db_path = CONFIG["output"]["database_path"]
engine = create_engine(f"sqlite:///{db_path}")

try:
    print("ETL output verification")
    print()

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")
    print()

    for table_name in ["historian_clean", "alarm_log_clean", "environmental_clean", "pipeline_runs"]:
        if table_name not in tables:
            print(f"Warning: {table_name} not found")
            continue

        df = pd.read_sql_table(table_name, engine)
        print(f"{table_name}:")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Memory: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

        if 'timestamp' in df.columns:
            print(f"  Timestamp range: {df['timestamp'].min()} to {df['timestamp'].max()}")

        if table_name == "historian_clean":
            print(f"  Assets: {df['asset_id'].nunique()}")
            print(f"  Failure types: {df['failure_type'].dropna().unique().tolist()}")
            print(f"  Quality flags: {df['quality_flag'].value_counts().to_dict()}")

        if table_name == "alarm_log_clean":
            print(f"  Assets: {df['asset_id'].nunique()}")
            print(f"  Priorities: {sorted(df['priority'].dropna().unique().tolist())}")
            print(f"  Quality flags: {df['quality_flag'].value_counts().to_dict()}")

        if table_name == "environmental_clean":
            print(f"  Quality flags: {df['quality_flag'].value_counts().to_dict()}")

        if table_name == "pipeline_runs":
            print(f"  Latest run: {df['run_timestamp'].max()}")
            print(f"  Status: {df['status'].iloc[-1]}")

        print()
        del df

finally:
    engine.dispose()
    print("Database connection closed")

    gc.collect()
