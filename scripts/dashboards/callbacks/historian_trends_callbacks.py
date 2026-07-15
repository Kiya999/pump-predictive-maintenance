# historian_trends_callbacks.py

import os
import sys
from dash import html, dcc, callback, Input, Output
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'analytics-pipeline'))

from anomaly_detection import AnomalyDetector

_engine = None

SIGNAL_COLS = ["flow_m3h", "diff_pressure_bar", "motor_temp_c", "vibration_mm_s"]
SIGNAL_LABELS = {
    "flow_m3h": "Flow (m3/h)",
    "diff_pressure_bar": "Diff pressure (bar)",
    "motor_temp_c": "Motor temp (C)",
    "vibration_mm_s": "Vibration (mm/s)",
}


def set_engine(engine):
    global _engine
    _engine = engine


def _apply_hourly_baseline(timestamps, hourly_stats, num_std=3):
    hours = timestamps.dt.hour.astype(str)
    means = hours.map(lambda h: hourly_stats.get(h, [None, None])[0]).astype(float)
    stds = hours.map(lambda h: hourly_stats.get(h, [None, None])[1]).astype(float)

    baseline = pd.Series(means.values, index=timestamps.index)
    stds = pd.Series(stds.values, index=timestamps.index)
    upper = baseline + num_std * stds
    lower = baseline - num_std * stds

    return baseline, upper, lower


@callback(
    Output("historian-trends-content", "children"),
    Input("asset-selector", "value"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),
    Input("subsample-toggle", "value"),
    Input("baseline-store", "data"),
)
def update_historian_trends(asset_id, start_date, end_date, subsample_on, baseline_data):

    if _engine is None or not asset_id:
        return html.Div("Select asset and date range")

    try:
        query = f"""
        SELECT timestamp, flow_m3h, diff_pressure_bar, motor_temp_c, vibration_mm_s, failure_type
        FROM historian_clean
        WHERE asset_id = '{asset_id}'
        AND timestamp BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY timestamp
        """

        df = pd.read_sql(query, _engine, parse_dates=["timestamp"])

        if len(df) == 0:
            return html.Div("No data for selected range")

        asset_stats = (baseline_data or {}).get(asset_id)

        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.12,
            subplot_titles=[SIGNAL_LABELS[c] for c in SIGNAL_COLS],
        )

        resample_rule = "5min" if "on" in subsample_on else None

        for row_idx, col in enumerate(SIGNAL_COLS, start=1):
            signal = df[col]
            timestamps = df["timestamp"]

            has_stats = asset_stats and col in asset_stats and "error" not in asset_stats

            if has_stats:
                baseline, upper, lower = _apply_hourly_baseline(timestamps, asset_stats[col])
                detector = AnomalyDetector({"baseline": baseline, "upper": upper, "lower": lower})
                iqr_result = detector.iqr(signal, window_periods=1440, multiplier=1.0)
                flag = iqr_result["flag"]
            else:
                baseline = upper = lower = None
                flag = pd.Series(False, index=signal.index)

            failure_mask = df["failure_type"] != "none"


            plot_df = pd.DataFrame({
                "timestamp": timestamps,
                "signal": signal,
                "flag": flag,
            })
            if baseline is not None:
                plot_df["baseline"] = baseline
                plot_df["upper"] = upper
                plot_df["lower"] = lower

            failure_periods = df.loc[failure_mask, "timestamp"]
            if len(failure_periods) > 0:
                gaps = failure_periods.diff() > pd.Timedelta(minutes=5)
                group_id = gaps.cumsum()
                for _, group in failure_periods.groupby(group_id):
                    fig.add_vrect(
                        x0=group.iloc[0], x1=group.iloc[-1],
                        fillcolor="#e74c3c", opacity=0.12, line_width=0,
                        row=row_idx, col=1,
                    )

            if resample_rule:
                agg = {"signal": "mean", "flag": "max"}
                if "baseline" in plot_df.columns:
                    agg.update({"baseline": "mean", "upper": "mean", "lower": "mean"})
                plot_df = plot_df.set_index("timestamp").resample(resample_rule).agg(agg).reset_index()
                plot_df["flag"] = plot_df["flag"].astype(bool)

            fig.add_trace(go.Scatter(
                x=plot_df["timestamp"], y=plot_df["signal"],
                mode="lines", name=SIGNAL_LABELS[col],
                line=dict(color="#2c3e50", width=1),
                showlegend=False,
            ), row=row_idx, col=1)

            if "baseline" in plot_df.columns:
                fig.add_trace(go.Scatter(
                    x=plot_df["timestamp"], y=plot_df["baseline"],
                    mode="lines", name="Baseline",
                    line=dict(color="#3498db", width=1, dash="dash"),
                    legendgroup="baseline",
                    showlegend=(row_idx == 1),
                ), row=row_idx, col=1)

                fig.add_trace(go.Scatter(
                    x=plot_df["timestamp"], y=plot_df["upper"],
                    mode="lines", name="Control limit",
                    line=dict(color="#95a5a6", width=1, dash="dot"),
                    legendgroup="control_limit",
                    showlegend=(row_idx == 1),
                ), row=row_idx, col=1)

                fig.add_trace(go.Scatter(
                    x=plot_df["timestamp"], y=plot_df["lower"],
                    mode="lines", name="Control limit",
                    line=dict(color="#95a5a6", width=1, dash="dot"),
                    legendgroup="control_limit",
                    showlegend=False,
                ), row=row_idx, col=1)

            flagged = plot_df[plot_df["flag"]]
            if len(flagged) > 0:
                fig.add_trace(go.Scatter(
                    x=flagged["timestamp"], y=flagged["signal"],
                    mode="markers", name="IQR flag (high false-positive rate)",
                    marker=dict(color="#e74c3c", size=6, symbol="x"),
                    legendgroup="iqr_flag",
                    showlegend=(row_idx == 1),
                ), row=row_idx, col=1)

        subsample_label = "5-min avg" if resample_rule else "1-min raw"

        fig.update_layout(
            title=f"Historian Trends - {asset_id} ({subsample_label})",
            template="plotly_white",
            hovermode="x unified",
            height=450,
        )
        fig.update_xaxes(title_text="Time", row=4, col=1)

        if not asset_stats:
            baseline_note = html.Div(
                "Baseline not yet cached for this asset, computing on next update",
                style={"color": "#e67e22", "fontSize": 12, "marginBottom": 8}
            )
        elif "error" in asset_stats:
            baseline_note = html.Div(
                f"Baseline computation failed: {asset_stats['error']}",
                style={"color": "#c0392b", "fontSize": 12, "marginBottom": 8}
            )
        else:
            baseline_note = html.Div(
                "Note: Red X markers are IQR-based anomaly flags (~1-4% false-positive rate on healthy "
                "assets, higher in summer due to seasonal drift). Cross-check with failure shading before acting.",
                style={"color": "#d68910", "fontSize": 11, "marginBottom": 12, "padding": "10px", "backgroundColor": "#fef5e7", "borderRadius": "4px", "borderLeft": "4px solid #e67e22"}
            )

        return html.Div([baseline_note, dcc.Graph(figure=fig)])

    except Exception as e:
        return html.Div(f"Error: {str(e)}", style={"color": "red"})