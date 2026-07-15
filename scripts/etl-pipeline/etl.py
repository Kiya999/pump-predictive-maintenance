# etl.py
"""
ETL pipeline: extract historian/alarm/environmental data from CSV, normalize
timestamps, resample, convert units, apply quality flags, and load to SQLite.
"""

import os
import json
import logging
import gc
from datetime import datetime
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, MetaData, Table, Column, String, Float, Integer, DateTime, Text, inspect

from etl_config import CONFIG

log_path = CONFIG["output"]["log_path"]
os.makedirs(os.path.dirname(log_path) if os.path.dirname(log_path) else ".", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract_historian(path, datetime_cols):
    """Load historian time series from CSV"""
    logger.info(f"Extracting historian from {path}")
    df = pd.read_csv(path, parse_dates=datetime_cols, dayfirst=False)
    logger.info(f"Loaded {len(df)} rows")
    return df

def extract_alarm_log(path, datetime_cols):
    """Load alarm event log from CSV"""
    logger.info(f"Extracting alarm log from {path}")
    df = pd.read_csv(path, parse_dates=datetime_cols)
    logger.info(f"Loaded {len(df)} rows")
    return df

def extract_environmental(path, datetime_cols):
    """Load environmental data from CSV"""
    logger.info(f"Extracting environmental from {path}")
    df = pd.read_csv(path, parse_dates=datetime_cols)
    logger.info(f"Loaded {len(df)} rows")
    return df

def normalize_timestamps(df, col_name, source_tz, target_tz="UTC"):
    """Localize and convert datetime column to target timezone."""
    if col_name not in df.columns:
        logger.warning(f"Column {col_name} not found")
        return df

    df = df.copy()

    if df[col_name].dt.tz is None:
        df[col_name] = df[col_name].dt.tz_localize(source_tz)
        logger.info(f"Localized {col_name} to {source_tz}")
    else:
        logger.info(f"{col_name} already tz-aware: {df[col_name].dt.tz}")

    if str(df[col_name].dt.tz) != target_tz:
        df[col_name] = df[col_name].dt.tz_convert(target_tz)
        logger.info(f"Converted {col_name} to {target_tz}")

    return df

def resample_data(df, timestamp_col, frequency):
    """Resample to specified frequency, keeping per-asset grouping."""
    if frequency is None:
        logger.info("Skipping resample (event data)")
        return df

    df = df.copy().set_index(timestamp_col)

    if "asset_id" in df.columns:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            df_resampled = df.groupby("asset_id")[numeric_cols].resample(frequency).mean()
            non_numeric_cols = [c for c in df.columns if c not in numeric_cols]
            if non_numeric_cols:
                for col in non_numeric_cols:
                    df_resampled[col] = df.groupby("asset_id")[col].resample(frequency).first()
            df_resampled = df_resampled.reset_index()
        else:
            df_resampled = df.groupby("asset_id").resample(frequency).first().reset_index()
    else:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            df_resampled = df[numeric_cols].resample(frequency).mean()
            non_numeric_cols = [c for c in df.columns if c not in numeric_cols]
            if non_numeric_cols:
                for col in non_numeric_cols:
                    df_resampled[col] = df[col].resample(frequency).first()
            df_resampled = df_resampled.reset_index()
        else:
            df_resampled = df.resample(frequency).first().reset_index()

    logger.info(f"Resampled to {frequency}: {len(df)} to {len(df_resampled)} rows")
    return df_resampled

def apply_unit_conversions(df, asset_id_col, conversions_config):
    """Apply per-asset unit conversion factors from config."""
    df = df.copy()

    if asset_id_col not in df.columns:
        logger.warning(f"Column {asset_id_col} not found")
        return df

    for asset_id, col_conversions in conversions_config.items():
        mask = df[asset_id_col] == asset_id
        if not mask.any():
            logger.warning(f"Asset {asset_id} not found")
            continue

        for col_name, conversion_spec in col_conversions.items():
            if col_name not in df.columns:
                logger.warning(f"Column {col_name} not found ({asset_id})")
                continue

            factor = conversion_spec["factor"]
            df.loc[mask, col_name] = df.loc[mask, col_name] * factor
            logger.info(f"Converted {asset_id}/{col_name} by factor {factor}")

    return df

def standardize_columns(df, mapping):
    """Rename columns according to mapping dict"""
    df = df.copy()
    rename_dict = {k: v for k, v in mapping.items() if k in df.columns}
    df = df.rename(columns=rename_dict)
    logger.info(f"Standardized {len(rename_dict)} columns")
    return df

def add_quality_flags(df, quality_report_path):
    """Add quality_flag column based on data quality report JSON."""
    df = df.copy()
    df["quality_flag"] = "pass"

    # Columns that can be NULL without signaling a data quality issue
    OPTIONAL_COLUMNS = {
        "is_test_case", # Metadata: only populated for test alarms
        "ack_time", # Conditional: NULL if alarm not yet acknowledged
        "clear_time", # Conditional: NULL if alarm still active
        "failure_type", # Metadata: only populated when failure injected
        "operator_id", # Metadata: may be NULL for automated alarms
    }

    if not os.path.exists(quality_report_path):
        logger.warning(f"Quality report not found: {quality_report_path}")
        return df

    with open(quality_report_path) as f:
        report = json.load(f)

    for col, col_info in report.get("completeness", {}).get("per_column", {}).items():
        if col in OPTIONAL_COLUMNS:
            logger.debug(f"Skipping quality check for optional column: {col}")
            continue

        if col_info.get("missing_count", 0) > 0 and col in df.columns:
            df.loc[df[col].isna(), "quality_flag"] = "missing"
            logger.info(f"Flagged {df['quality_flag'].eq('missing').sum()} rows as missing in {col}")

    for col in df.select_dtypes(include=[np.number]).columns:
        if col == "quality_flag":
            continue
        if col not in report.get("outliers", {}):
            continue

        col_outlier_info = report["outliers"][col]
        outlier_count = col_outlier_info.get("outlier_count", 0)

        if outlier_count == 0:
            continue

        method = col_outlier_info.get("method", "global IQR")

        if method == "per-asset IQR":
            logger.info(f"Column {col} uses per-asset detection ({outlier_count} outliers total)")
        else:
            lower_fence = col_outlier_info.get("lower_fence")
            upper_fence = col_outlier_info.get("upper_fence")

            if lower_fence is not None and upper_fence is not None:
                outlier_mask = (df[col] < lower_fence) | (df[col] > upper_fence)
                df.loc[outlier_mask, "quality_flag"] = "outlier"
                logger.info(f"Flagged {outlier_mask.sum()} rows as outlier in {col}")

    flag_counts = df["quality_flag"].value_counts().to_dict()
    logger.info(f"Quality flags: {flag_counts}")
    return df

def transform_historian(df_raw, config):
    """Normalize timestamps, resample, convert units, standardize, flag quality."""
    logger.info("Transforming historian")

    source_config = config["sources"]["historian"]
    unit_config = config.get("unit_conversions", {})
    col_mapping = config["column_mappings"]["historian"]
    quality_path = config["quality_report_paths"]["historian"]

    df = df_raw.copy()
    df = normalize_timestamps(df, source_config["timestamp_col"], source_config["tz"], "UTC")

    if source_config["frequency"] != "1min":
        df = resample_data(df, source_config["timestamp_col"], source_config["frequency"])
    else:
        logger.info("Skipping resample for 1-min native frequency")

    df = apply_unit_conversions(df, "asset_id", unit_config)
    df = standardize_columns(df, col_mapping)
    df = add_quality_flags(df, quality_path)

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        if col == 'quality_flag':
            continue
        null_mask = df[col].isna()
        if null_mask.any():
            df.loc[null_mask, 'quality_flag'] = 'missing'
            logger.info(f"Flagged {null_mask.sum()} rows as missing for {col} after resampling")

    logger.info(f"Historian transform complete: {len(df)} rows")
    return df

def transform_alarm_log(df_raw, config):
    """Normalize timestamps, standardize, flag quality."""
    logger.info("Transforming alarm log")

    source_config = config["sources"]["alarm_log"]
    col_mapping = config["column_mappings"]["alarm_log"]
    quality_path = config["quality_report_paths"]["alarm_log"]

    df = df_raw.copy()
    df = normalize_timestamps(df, source_config["timestamp_col"], source_config["tz"], "UTC")
    df = standardize_columns(df, col_mapping)
    df = add_quality_flags(df, quality_path)

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        if col == 'quality_flag':
            continue
        null_mask = df[col].isna()
        if null_mask.any():
            df.loc[null_mask, 'quality_flag'] = 'missing'
            logger.info(f"Flagged {null_mask.sum()} rows as missing for {col} after resampling")

    logger.info(f"Alarm log transform complete: {len(df)} rows")
    return df

def transform_environmental(df_raw, config):
    """Normalize timestamps, resample, standardize, flag quality."""
    logger.info("Transforming environmental")

    source_config = config["sources"]["environmental"]
    col_mapping = config["column_mappings"]["environmental"]
    quality_path = config["quality_report_paths"]["environmental"]

    df = df_raw.copy()
    df = normalize_timestamps(df, source_config["timestamp_col"], source_config["tz"], "UTC")

    if source_config["frequency"]:
        df = resample_data(df, source_config["timestamp_col"], source_config["frequency"])
    else:
        logger.info("Skipping resample (no frequency specified)")

    df = standardize_columns(df, col_mapping)
    df = add_quality_flags(df, quality_path)

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        if col == 'quality_flag':
            continue
        null_mask = df[col].isna()
        if null_mask.any():
            df.loc[null_mask, 'quality_flag'] = 'missing'
            logger.info(f"Flagged {null_mask.sum()} rows as missing for {col} after resampling")

    logger.info(f"Environmental transform complete: {len(df)} rows")
    return df

def create_database_schema(engine):
    """Create historian_clean, alarm_log_clean, environmental_clean, and pipeline_runs tables."""
    metadata = MetaData()

    Table('historian_clean', metadata,
        Column('id', Integer, primary_key=True),
        Column('timestamp', DateTime, nullable=False),
        Column('asset_id', String(50), nullable=False),
        Column('flow_m3h', Float),
        Column('suction_pressure_bar', Float),
        Column('disch_pressure_bar', Float),
        Column('diff_pressure_bar', Float),
        Column('motor_temp_c', Float),
        Column('motor_power_kw', Float),
        Column('vibration_mm_s', Float),
        Column('speed_rpm', Float),
        Column('failure_type', String(50)),
        Column('quality_flag', String(50)),
    )

    Table('alarm_log_clean', metadata,
        Column('id', Integer, primary_key=True),
        Column('timestamp', DateTime, nullable=False),
        Column('asset_id', String(50), nullable=False),
        Column('alarm_tag', String(100)),
        Column('alarm_description', String(256)),
        Column('alarm_type', String(20)),
        Column('priority', Integer),
        Column('ack_time', DateTime),
        Column('clear_time', DateTime),
        Column('duration_min', Float),
        Column('area', String(100)),
        Column('operator_id', String(20)),
        Column('is_test_case', String(10)),
        Column('quality_flag', String(50)),
    )

    Table('environmental_clean', metadata,
        Column('id', Integer, primary_key=True),
        Column('timestamp', DateTime, nullable=False),
        Column('discharge_cfs', Float),
        Column('quality_flag', String(50)),
    )

    Table('pipeline_runs', metadata,
        Column('run_id', Integer, primary_key=True),
        Column('run_timestamp', DateTime, nullable=False),
        Column('historian_input_path', String(256)),
        Column('alarm_log_input_path', String(256)),
        Column('environmental_input_path', String(256)),
        Column('historian_rows_in', Integer),
        Column('historian_rows_out', Integer),
        Column('alarm_log_rows_in', Integer),
        Column('alarm_log_rows_out', Integer),
        Column('environmental_rows_in', Integer),
        Column('environmental_rows_out', Integer),
        Column('quality_summary', Text),
        Column('errors', Text),
        Column('status', String(50)),
    )

    metadata.create_all(engine)
    logger.info("Database schema created")

def load_to_sqlite(dataframes, engine):
    """Insert cleaned dataframes to database tables, matching schema."""
    ts_cols = {"historian": "timestamp", "alarm_log": "timestamp", "environmental": "timestamp"}

    inspector = inspect(engine)

    for name, df in dataframes.items():
        if df is None or len(df) == 0:
            logger.warning(f"Skipping empty: {name}")
            continue

        df = df.copy()

        table_name = f"{name}_clean"
        table_cols = [col['name'] for col in inspector.get_columns(table_name)]

        df = df[[col for col in df.columns if col in table_cols]]

        col = ts_cols.get(name)
        if col and col in df.columns and hasattr(df[col].dt, "tz") and df[col].dt.tz is not None:
            df[col] = df[col].dt.tz_localize(None)

        df.to_sql(table_name, engine, if_exists="append", index=False)
        logger.info(f"Loaded {len(df)} rows to {table_name}")

def log_pipeline_run(engine, run_timestamp, config, df_in_counts, df_out_counts,
                     quality_summaries, errors):
    """Record pipeline run metadata and row counts to pipeline_runs table."""
    quality_summary_str = json.dumps(quality_summaries)
    errors_str = json.dumps(errors) if errors else None
    status = "success" if not errors else "failed"

    run_record = {
        'run_timestamp': run_timestamp,
        'historian_input_path': config["sources"]["historian"]["path"],
        'alarm_log_input_path': config["sources"]["alarm_log"]["path"],
        'environmental_input_path': config["sources"]["environmental"]["path"],
        'historian_rows_in': df_in_counts.get("historian", 0),
        'historian_rows_out': df_out_counts.get("historian", 0),
        'alarm_log_rows_in': df_in_counts.get("alarm_log", 0),
        'alarm_log_rows_out': df_out_counts.get("alarm_log", 0),
        'environmental_rows_in': df_in_counts.get("environmental", 0),
        'environmental_rows_out': df_out_counts.get("environmental", 0),
        'quality_summary': quality_summary_str,
        'errors': errors_str,
        'status': status,
    }

    run_df = pd.DataFrame([run_record])
    run_df.to_sql('pipeline_runs', engine, if_exists='append', index=False)
    logger.info(f"Pipeline run logged: {status}")

def run_pipeline(config=None):
    """Execute full ETL pipeline: extract, transform, load. Returns True on success."""
    if config is None:
        config = CONFIG

    run_timestamp = datetime.utcnow()
    logger.info("ETL Pipeline started")

    df_in_counts = {}
    df_out_counts = {}
    quality_summaries = {}
    errors = {}
    engine = None

    try:
        logger.info("EXTRACT LAYER")
        df_historian_raw = extract_historian(config["sources"]["historian"]["path"],
                                             config["sources"]["historian"]["datetime_cols"])
        df_alarm_log_raw = extract_alarm_log(config["sources"]["alarm_log"]["path"],
                                             config["sources"]["alarm_log"]["datetime_cols"])
        df_environmental_raw = extract_environmental(config["sources"]["environmental"]["path"],
                                                     config["sources"]["environmental"]["datetime_cols"])

        df_in_counts = {
            "historian": len(df_historian_raw),
            "alarm_log": len(df_alarm_log_raw),
            "environmental": len(df_environmental_raw),
        }

        logger.info("TRANSFORM LAYER")
        df_historian = transform_historian(df_historian_raw, config)
        df_alarm_log = transform_alarm_log(df_alarm_log_raw, config)
        df_environmental = transform_environmental(df_environmental_raw, config)

        df_out_counts = {
            "historian": len(df_historian),
            "alarm_log": len(df_alarm_log),
            "environmental": len(df_environmental),
        }

        quality_summaries = {
            "historian": {"in": df_in_counts["historian"], "out": df_out_counts["historian"]},
            "alarm_log": {"in": df_in_counts["alarm_log"], "out": df_out_counts["alarm_log"]},
            "environmental": {"in": df_in_counts["environmental"], "out": df_out_counts["environmental"]},
        }

        logger.info("LOAD LAYER")
        os.makedirs(os.path.dirname(config["output"]["database_path"]) or ".", exist_ok=True)
        engine = create_engine(f"sqlite:///{config['output']['database_path']}")

        try:
            create_database_schema(engine)

            dataframes = {
                "historian": df_historian,
                "alarm_log": df_alarm_log,
                "environmental": df_environmental,
            }
            load_to_sqlite(dataframes, engine)

            log_pipeline_run(engine, run_timestamp, config, df_in_counts, df_out_counts,
                            quality_summaries, errors)

            logger.info("ETL Pipeline completed successfully")
            logger.info(f"Database: {config['output']['database_path']}")

        finally:
            engine.dispose()
            logger.info("Database connections closed")

        return True

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        errors["pipeline"] = str(e)

        try:
            if engine is not None:
                log_pipeline_run(engine, run_timestamp, config, df_in_counts, df_out_counts,
                                quality_summaries, errors)
                engine.dispose()
                logger.info("Database connections closed after error")
        except Exception as cleanup_error:
            logger.error(f"Cleanup failed: {cleanup_error}", exc_info=True)

        raise

    finally:
        for handler in logger.handlers:
            handler.close()

if __name__ == "__main__":
    try:
        success = run_pipeline()
        if success:
            print("Pipeline completed.")
    except Exception as e:
        print(f"Pipeline failed: {e}")
        raise
    finally:
        gc.collect()
