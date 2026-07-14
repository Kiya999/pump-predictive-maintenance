# alarm_analysis_callbacks.py
from dash import callback, Input, Output
import pandas as pd
import plotly.graph_objects as go

_engine = None

def set_engine(engine):
    global _engine
    _engine = engine

@callback(
    Output("alarm-analysis-content", "children"),
    Input("asset-selector", "value"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),
)
def update_alarm_analysis(asset_id, start_date, end_date):
    from dash import html, dcc

    if _engine is None or not asset_id:
        return html.Div("Select asset and date range")

    try:
        query = f"""
        SELECT alarm_tag, COUNT(*) as count, AVG(CAST(priority AS FLOAT)) as avg_priority
        FROM alarm_log_clean
        WHERE asset_id = '{asset_id}'
        AND timestamp BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY alarm_tag
        ORDER BY count DESC
        """
        alarm_df = pd.read_sql(query, _engine)

        if len(alarm_df) == 0:
            return html.Div("No alarms in selected range")

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=alarm_df["alarm_tag"].head(10),
            y=alarm_df["count"].head(10),
            name="Alarm Count",
            marker=dict(color="#3498db")
        ))

        fig.update_layout(
            title="Top 10 Alarms",
            xaxis_title="Alarm Tag",
            yaxis_title="Count",
            template="plotly_white",
            height=450,
        )

        return dcc.Graph(figure=fig)

    except Exception as e:
        return html.Div(f"Error: {str(e)}", style={"color": "red"})
