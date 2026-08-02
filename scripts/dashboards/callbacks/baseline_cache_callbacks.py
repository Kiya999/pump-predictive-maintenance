# baseline_cache_callbacks.py
from dash import callback, Input, Output, State
import pandas as pd

_engine = None

SIGNAL_COLS = ["flow_m3h", "diff_pressure_bar", "motor_temp_c", "vibration_mm_s"]

LOOKBACK_DAYS = 180  # rolling window instead of all-time history


def set_engine(engine):
    global _engine
    _engine = engine

def _compute_hourly_stats(asset_id, end_date):
    select_parts = []
    for col in SIGNAL_COLS:
        select_parts.append(f"AVG({col}) as {col}_mean")
        select_parts.append(f"AVG({col}*{col}) as {col}_sqmean")

    query = f"""
    SELECT CAST(strftime('%H', timestamp) AS INTEGER) as hour,
           CASE WHEN CAST(strftime('%w', timestamp) AS INTEGER) IN (0, 6) THEN 1 ELSE 0 END as is_weekend,
           {', '.join(select_parts)}
    FROM historian_clean
    WHERE asset_id = '{asset_id}'
    AND failure_type = 'none'
    AND timestamp >= datetime('{end_date}', '-{LOOKBACK_DAYS} days')
    AND timestamp <= '{end_date}'
    GROUP BY hour, is_weekend
    ORDER BY hour, is_weekend
    """

    df = pd.read_sql(query, _engine)

    stats = {}
    for col in SIGNAL_COLS:
        col_stats = {}
        for _, row in df.iterrows():
            hour = int(row["hour"])
            is_weekend = int(row["is_weekend"])
            mean = row[f"{col}_mean"]
            sqmean = row[f"{col}_sqmean"]
            variance = max(sqmean - mean * mean, 0)
            std = variance ** 0.5
            col_stats[f"{hour}_{is_weekend}"] = [mean, std]
        stats[col] = col_stats

    return stats


@callback(
    Output("baseline-store", "data"),
    Input("asset-selector", "value"),
    Input("date-range-picker", "end_date"),
    State("baseline-store", "data"),
)
def update_baseline_cache(asset_id, end_date, store_data):
    if _engine is None or not asset_id or not end_date:
        return store_data

    if store_data is None:
        store_data = {}

    cache_key = f"{asset_id}_{end_date}"

    if cache_key in store_data:
        return store_data

    try:
        store_data[cache_key] = _compute_hourly_stats(asset_id, end_date)
    except Exception as e:
        store_data[cache_key] = {"error": str(e)}

    return store_data