# asset_overview_callbacks.py
from dash import callback, Input, Output
import pandas as pd

_engine = None

def set_engine(engine):
    global _engine
    _engine = engine

@callback(
    Output("asset-overview-content", "children"),
    Input("asset-selector", "value"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),
)
def update_asset_overview(asset_id, start_date, end_date):
    from dash import html
    
    if _engine is None or not asset_id:
        return html.Div("No data")
    
    try:
        query_hist = f"""
        SELECT 
            COUNT(*) as total_rows,
            SUM(CASE WHEN failure_type = 'none' THEN 1 ELSE 0 END) as normal_count,
            SUM(CASE WHEN failure_type != 'none' THEN 1 ELSE 0 END) as anomaly_count,
            AVG(vibration_mm_s) as avg_vib,
            AVG(motor_temp_c) as avg_temp
        FROM historian_clean
        WHERE asset_id = '{asset_id}'
        AND timestamp BETWEEN '{start_date}' AND '{end_date}'
        """
        hist_df = pd.read_sql(query_hist, _engine)
        
        query_alarms = f"""
        SELECT COUNT(*) as alarm_count
        FROM alarm_log_clean
        WHERE asset_id = '{asset_id}'
        AND timestamp >= datetime('{end_date}', '-1 day')
        """
        alarms_df = pd.read_sql(query_alarms, _engine)
        alarm_count = alarms_df["alarm_count"].iloc[0]
        
        total_rows = hist_df["total_rows"].iloc[0]
        runtime_hours = total_rows / 60.0
        avg_vib = hist_df["avg_vib"].iloc[0]
        avg_temp = hist_df["avg_temp"].iloc[0]
        anomaly_count = hist_df["anomaly_count"].iloc[0]
        
        if avg_vib is None:
            avg_vib = 0
        if avg_temp is None:
            avg_temp = 0
        if anomaly_count is None:
            anomaly_count = 0
        
        anomaly_pct = 100.0 * anomaly_count / total_rows if total_rows > 0 else 0
        
        if anomaly_pct > 10.0:
            health = "#e74c3c"
            status = "At Risk"
        elif anomaly_pct > 2.0:
            health = "#f39c12"
            status = "Caution"
        else:
            health = "#27ae60"
            status = "Healthy"
        
        content = html.Div([
            html.Div([
                html.Div([
                    html.Div(status, style={"fontSize": 18, "fontWeight": "bold"}),
                    html.Div(f"Anomalies: {anomaly_pct:.2f}%", style={"fontSize": 12, "color": "#ecf0f1"}),
                ], style={
                    "padding": 15,
                    "backgroundColor": health,
                    "color": "white",
                    "borderRadius": 5,
                    "marginBottom": 10
                }),
                
                html.Div([
                    html.Span("Runtime: ", style={"fontWeight": "bold"}),
                    html.Span(f"{runtime_hours:.0f} hours"),
                ], style={"marginBottom": 8}),
                
                html.Div([
                    html.Span("Avg Vibration: ", style={"fontWeight": "bold"}),
                    html.Span(f"{avg_vib:.4f} mm/s"),
                ], style={"marginBottom": 8}),
                
                html.Div([
                    html.Span("Avg Temperature: ", style={"fontWeight": "bold"}),
                    html.Span(f"{avg_temp:.1f}°C"),
                ], style={"marginBottom": 8}),
                
                html.Div([
                    html.Span("Alarms (24h): ", style={"fontWeight": "bold"}),
                    html.Span(str(alarm_count)),
                ], style={"marginBottom": 8}),
                
                html.Div([
                    html.Span("Anomalies: ", style={"fontWeight": "bold"}),
                    html.Span(f"{anomaly_pct:.2f}%"),
                ], style={"fontSize": 12, "color": "#7f8c8d"}),
            ], style={"fontSize": 13})
        ])
        
        return content
        
    except Exception as e:
        return html.Div(f"Error: {str(e)}", style={"color": "red"})
