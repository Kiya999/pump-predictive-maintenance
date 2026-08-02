# asset_overview_callbacks.py
from dash import callback, Input, Output, ALL, ctx, no_update, html
import pandas as pd

_engine = None

IQR_MULTIPLIER = 2  # Conservative (higher = fewer false positives, fewer real anomalies caught) 2 is bettter than 1.5


def set_engine(engine):
    global _engine
    _engine = engine


def _health_color(ground_truth_pct, alarm_count):
    if ground_truth_pct > 10.0 or alarm_count >= 15:
        return "#e74c3c", "At Risk"
    if ground_truth_pct > 2.0 or alarm_count >= 5:
        return "#f39c12", "Caution"
    return "#27ae60", "Healthy"


def _compute_iqr_flag_rates(vib_df):
    rates = {}
    for asset_id, group in vib_df.groupby("asset_id"):
        s = group["vibration_mm_s"].dropna()
        if len(s) == 0:
            rates[asset_id] = 0.0
            continue
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr_val = q3 - q1
        lower_fence = q1 - IQR_MULTIPLIER * iqr_val
        upper_fence = q3 + IQR_MULTIPLIER * iqr_val
        flagged = ((s < lower_fence) | (s > upper_fence)).sum()
        rates[asset_id] = 100.0 * flagged / len(s)
    return rates


@callback(
    Output("asset-overview-content", "children"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),
    Input("asset-selector", "value"),
)
def update_asset_overview(start_date, end_date, selected_asset):

    if _engine is None:
        return html.Div("No database connection")

    try:
        query_hist = f"""
        SELECT asset_id,
            COUNT(*) as total_rows,
            SUM(CASE WHEN failure_type != 'none' THEN 1 ELSE 0 END) as ground_truth_count,
            AVG(vibration_mm_s) as avg_vib,
            AVG(motor_temp_c) as avg_temp
        FROM historian_clean
        WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY asset_id
        ORDER BY asset_id
        """
        hist_df = pd.read_sql(query_hist, _engine)

        query_alarms = f"""
        SELECT asset_id, COUNT(*) as alarm_count
        FROM alarm_log_clean
        WHERE timestamp >= datetime('{end_date}', '-1 day')
        AND timestamp <= '{end_date}'
        GROUP BY asset_id
        """
        alarm_df = pd.read_sql(query_alarms, _engine)

        query_recent_failure = f"""
        SELECT asset_id, failure_type FROM (
            SELECT asset_id, failure_type, timestamp,
                ROW_NUMBER() OVER (PARTITION BY asset_id ORDER BY timestamp DESC) as rn
            FROM historian_clean
            WHERE failure_type != 'none'
            AND timestamp BETWEEN '{start_date}' AND '{end_date}'
        ) WHERE rn = 1
        """
        recent_df = pd.read_sql(query_recent_failure, _engine)

        query_vib = f"""
        SELECT asset_id, vibration_mm_s
        FROM historian_clean
        WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'
        """
        vib_df = pd.read_sql(query_vib, _engine)
        iqr_rates = _compute_iqr_flag_rates(vib_df)
        
        merged = hist_df.merge(alarm_df, on="asset_id", how="left")
        merged = merged.merge(recent_df, on="asset_id", how="left", suffixes=("", "_recent"))
        merged["alarm_count"] = merged["alarm_count"].fillna(0).astype(int)
        merged["failure_type"] = merged["failure_type"].fillna("none")

        cards = []
        for _, row in merged.iterrows():
            asset_id = row["asset_id"]
            total_rows = row["total_rows"]
            ground_truth_pct = 100.0 * row["ground_truth_count"] / total_rows if total_rows > 0 else 0
            runtime_hours = total_rows / 60.0
            avg_vib = row["avg_vib"] if pd.notna(row["avg_vib"]) else 0
            avg_temp = row["avg_temp"] if pd.notna(row["avg_temp"]) else 0
            alarm_count = row["alarm_count"]
            recent_flag = row["failure_type"]
            iqr_rate = iqr_rates.get(asset_id, 0.0)

            color, status = _health_color(ground_truth_pct, alarm_count)
            is_selected = asset_id == selected_asset

            card = html.Div(
                id={"type": "asset-card", "index": asset_id},
                n_clicks=0,
                children=[

                    html.Div([
                        html.Span(asset_id, style={"fontWeight": "bold", "fontSize": 15}),
                        html.Span(status, style={
                            "float": "right",
                            "fontSize": 11,
                            "padding": "2px 8px",
                            "borderRadius": 10,
                            "backgroundColor": color,
                            "color": "white",
                        }),
                    ], style={"marginBottom": 8}),

                    html.Div(f"Runtime: {runtime_hours:.0f} h", style={"fontSize": 12}),
                    html.Div(f"Ground truth failure coverage: {ground_truth_pct:.2f}%", style={"fontSize": 12}),
                    html.Div(f"IQR flag rate (vibration): {iqr_rate:.2f}%", style={"fontSize": 12}),                    
                    html.Div(f"Avg vibration: {avg_vib:.4f} mm/s", style={"fontSize": 12}),
                    html.Div(f"Avg temp: {avg_temp:.1f} C", style={"fontSize": 12}),
                    html.Div(f"Alarms (24h): {alarm_count}", style={"fontSize": 12}),
                    html.Div(f"Recent flag: {recent_flag}", style={"fontSize": 12, "color": "#7f8c8d"}),
                ],
                style={
                    "flex": "1 0 100px",
                    "minWidth": 100,
                    "padding": 8,
                    "backgroundColor": "#d0e3f2" if is_selected else "#f9f9f9",
                    "borderRadius": 6,
                    "border": f"4px solid {color}" if is_selected else f"2px solid {color}",
                    "boxShadow": "0 0 6px rgba(52,152,219,0.6)" if is_selected else "none",
                    "cursor": "pointer",
                }

            )
            cards.append(card)

        return html.Div(cards, style={"display": "flex", "gap": 12, "flexWrap": "wrap"})

    except Exception as e:
        return html.Div(f"Error: {str(e)}", style={"color": "red"})


@callback(
    Output("asset-selector", "value"),
    Input({"type": "asset-card", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def select_asset_from_card(n_clicks_list):
    if not any(n_clicks_list):
        return no_update

    triggered = ctx.triggered_id
    if triggered:
        return triggered["index"]
    return no_update
