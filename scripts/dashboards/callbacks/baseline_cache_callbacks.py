# baseline_cache_callbacks.py
from dash import callback, Input, Output, State
import pandas as pd

_engine = None

SIGNAL_COLS = ["flow_m3h", "diff_pressure_bar", "motor_temp_c", "vibration_mm_s"]


def set_engine(engine):
    global _engine
    _engine = engine


def _compute_hourly_stats(asset_id):
    select_parts = []
    for col in SIGNAL_COLS:
        select_parts.append(f"AVG({col}) as {col}_mean")
        select_parts.append(f"AVG({col}*{col}) as {col}_sqmean")

    query = f"""
    SELECT CAST(strftime('%H', timestamp) AS INTEGER) as hour, {', '.join(select_parts)}
    FROM historian_clean
    WHERE asset_id = '{asset_id}'
    AND failure_type = 'none'
    GROUP BY hour
    ORDER BY hour
    """

    df = pd.read_sql(query, _engine)

    stats = {}
    for col in SIGNAL_COLS:
        col_stats = {}
        for _, row in df.iterrows():
            hour = int(row["hour"])
            mean = row[f"{col}_mean"]
            sqmean = row[f"{col}_sqmean"]
            variance = max(sqmean - mean * mean, 0)
            std = variance ** 0.5
            col_stats[str(hour)] = [mean, std]
        stats[col] = col_stats

    return stats


@callback(
    Output("baseline-store", "data"),
    Input("asset-selector", "value"),
    State("baseline-store", "data"),
)
def update_baseline_cache(asset_id, store_data):
    if _engine is None or not asset_id:
        return store_data

    if store_data is None:
        store_data = {}

    if asset_id in store_data:
        return store_data

    try:
        store_data[asset_id] = _compute_hourly_stats(asset_id)
    except Exception as e:
        store_data[asset_id] = {"error": str(e)}

    return store_data