# environmental_callbacks.py
import os
import sys
from dash import callback, Input, Output
import pandas as pd
import plotly.graph_objects as go

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'analytics-pipeline'))

from environmental_correlation import compute_overlap_correlation

_engine = None


def set_engine(engine):
    global _engine
    _engine = engine


@callback(
    Output("env-overlay-chart", "figure"),
    Output("env-correlation-stat", "children"),
    Output("env-overlap-message", "children"),
    Output("env-data-alert", "children"),
    Output("env-data-alert", "style"),

    Input("asset-selector", "value"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),
    Input("subsample-toggle", "value"),
)
def update_environmental_chart(asset_id, start_date, end_date, subsample_on):
    if _engine is None:
        fig = go.Figure()
        fig.add_annotation(text="Database not connected")
        return fig, "ERROR", "Database not connected", "Database error", {"display": "none"}

    if not asset_id or not start_date or not end_date:
        fig = go.Figure()
        return fig, "--", "Select asset and date range", "", {"display": "none"}

    try:
        query_hist = f"""
        SELECT timestamp, flow_m3h
        FROM historian_clean
        WHERE asset_id = '{asset_id}'
        AND timestamp BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY timestamp
        """

        hist_df_raw = pd.read_sql(query_hist, _engine, parse_dates=["timestamp"])

        if len(hist_df_raw) == 0:
            fig = go.Figure()
            fig.add_annotation(text=f"No data for {asset_id}")
            return fig, "--", f"No data for {asset_id}", "", {"display": "none"}

        query_env = f"""
        SELECT timestamp, discharge_cfs
        FROM environmental_clean
        WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY timestamp
        """
        env_df_raw = pd.read_sql(query_env, _engine, parse_dates=["timestamp"])

        overlap_info = compute_overlap_correlation(
            hist_df_raw, env_df_raw,
            hist_col="flow_m3h",
            env_col="discharge_cfs"
        )

        if "on" in subsample_on:
            hist_df = hist_df_raw.set_index("timestamp").resample("30min").mean().reset_index()
            env_df = env_df_raw.set_index("timestamp").resample("30min").mean().reset_index()
        else:
            hist_df = hist_df_raw
            env_df = env_df_raw

        corr_str = overlap_info["correlation_str"]
        message = overlap_info["message"]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=hist_df["timestamp"],
            y=hist_df["flow_m3h"],
            mode="lines",
            name="Flow (m3/h)",
            line=dict(color="#3498db", width=2),
            yaxis="y1",
        ))

        if overlap_info["data_available"] and len(env_df) > 0:
            fig.add_trace(go.Scatter(
                x=env_df["timestamp"],
                y=env_df["discharge_cfs"],
                mode="lines",
                name="Discharge (cfs)",
                line=dict(color="#e74c3c", width=2, dash="dash"),
                yaxis="y2",
            ))

            fig.update_layout(
                yaxis2=dict(
                    title=dict(text="Discharge (cfs)", font=dict(color="#e74c3c")),
                    overlaying="y",
                    side="right",
                    tickfont=dict(color="#e74c3c"),
                )
            )

        subsample_label = "(30-min avg)" if "on" in subsample_on else "(1-min raw)"

        fig.update_layout(
            title=f"Environmental Context - {asset_id} {subsample_label}",
            xaxis_title="Timestamp",
            yaxis_title="Flow (m3/h)",
            yaxis=dict(title=dict(text="Flow (m3/h)", font=dict(color="#3498db")), tickfont=dict(color="#3498db"),
            ),
            template="plotly_white",
            hovermode="x unified",
            height=450,
        )

        alert_text = ""
        alert_style = {"display": "none"}

        if not overlap_info["data_available"]:
            alert_text = overlap_info["message"]
            alert_style = {
                "display": "block",
                "padding": 12,
                "marginTop": 15,
                "backgroundColor": "#fdeef4",
                "color": "#c0392b",
                "borderRadius": 5,
                "fontSize": 13
            }

        return fig, corr_str, message, alert_text, alert_style

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Error: {str(e)}")
        alert_style = {
            "display": "block",
            "padding": 12,
            "marginTop": 15,
            "backgroundColor": "#fdeef4",
            "color": "#c0392b",
            "borderRadius": 5,
            "fontSize": 13
        }
        return fig, "ERROR", "Query failed", str(e), alert_style
