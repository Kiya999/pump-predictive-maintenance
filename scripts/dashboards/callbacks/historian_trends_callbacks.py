# historian_trends_callbacks.py
from dash import callback, Input, Output
import pandas as pd
import plotly.graph_objects as go

_engine = None

def set_engine(engine):
    global _engine
    _engine = engine

@callback(
    Output("historian-trends-content", "children"),
    Input("asset-selector", "value"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),
    Input("subsample-toggle", "value"),
)
def update_historian_trends(asset_id, start_date, end_date, subsample_on):
    from dash import html, dcc
    
    if _engine is None or not asset_id:
        return html.Div("Select asset and date range")
    
    try:
        query = f"""
        SELECT timestamp, flow_m3h, vibration_mm_s
        FROM historian_clean
        WHERE asset_id = '{asset_id}'
        AND timestamp BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY timestamp
        """
        df = pd.read_sql(query, _engine, parse_dates=["timestamp"])
        
        if len(df) == 0:
            return html.Div("No data for selected range")

        if "on" in subsample_on:
            df_plot = df.set_index("timestamp").resample("30min").mean().reset_index()
        else:
            df_plot = df
            
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_plot["timestamp"],
            y=df_plot["flow_m3h"],
            mode="lines",
            name="Flow (m3/h)",
            line=dict(color="#3498db", width=1),
            yaxis="y1"
        ))
        
        fig.add_trace(go.Scatter(
            x=df_plot["timestamp"],
            y=df_plot["vibration_mm_s"],
            mode="lines",
            name="Vibration (mm/s)",
            line=dict(color="#e74c3c", width=1),
            yaxis="y2"
        ))
        
        subsample_label = "(30-min avg)" if "on" in subsample_on else "(1-min raw)"

        fig.update_layout(
            title=f"Historian Trends - {asset_id} {subsample_label}",
            xaxis_title="Time",
            yaxis=dict(
                title=dict(text="Flow (m3/h)", font=dict(color="#3498db")),
                tickfont=dict(color="#3498db")
            ),
            yaxis2=dict(
                title=dict(text="Vibration (mm/s)", font=dict(color="#e74c3c")),
                tickfont=dict(color="#e74c3c"),
                overlaying="y",
                side="right"
            ),
            template="plotly_white",
            hovermode="x unified",
            height=450,
        )
        
        return dcc.Graph(figure=fig)
        
    except Exception as e:
        return html.Div(f"Error: {str(e)}", style={"color": "red"})
