# motor_monitoring_callbacks.py
from dash import callback, Input, Output, html
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_engine = None

ASSUMED_LINE_VOLTAGE_V = 400.0
ASSUMED_POWER_FACTOR = 0.87

SQRT3 = 1.7320508075688772

def set_engine(engine):
    global _engine
    _engine = engine


def _derive_current_amps(power_kw_series):
    """I = P / (sqrt(3) * V_LL * PF), P in watts."""
    power_w = power_kw_series * 1000.0
    return power_w / (SQRT3 * ASSUMED_LINE_VOLTAGE_V * ASSUMED_POWER_FACTOR)


@callback(
    Output("motor-metric-cards", "children"),
    Output("motor-monitoring-graph", "figure"),
    Output("motor-derived-current-note", "children"),
    Input("asset-selector", "value"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),
)
def update_motor_monitoring(selected_asset, start_date, end_date):

    if _engine is None or not selected_asset:
        return [], go.Figure(), ""

    try:
        query = f"""
        SELECT timestamp, motor_power_kw, motor_temp_c, speed_rpm
        FROM historian_clean
        WHERE asset_id = '{selected_asset}'
        AND timestamp BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY timestamp
        """
        df = pd.read_sql(query, _engine, parse_dates=["timestamp"])

        if len(df) == 0:
            empty_fig = go.Figure()
            empty_fig.update_layout(title="No data in selected range")
            return [], empty_fig, ""

        df["current_a_derived"] = _derive_current_amps(df["motor_power_kw"])

        avg_power = df["motor_power_kw"].mean()
        avg_temp = df["motor_temp_c"].mean()
        avg_speed = df["speed_rpm"].mean()
        avg_current = df["current_a_derived"].mean()

        def _card(label, value, unit, sub=None):
            children = [
                html.Div(label, style={"fontSize": 11, "color": "#7f8c8d"}),
                html.Div(f"{value:.1f} {unit}", style={"fontSize": 18, "fontWeight": "bold"}),
            ]
            if sub:
                children.append(html.Div(sub, style={"fontSize": 10, "color": "#e67e22"}))
            return html.Div(children, style={
                "padding": "10px 16px",
                "backgroundColor": "#f9f9f9",
                "borderRadius": 6,
                "border": "1px solid #ecf0f1",
                "minWidth": 130,
            })

        cards = [
            _card("Avg Motor Power", avg_power, "kW"),
            _card("Avg Motor Temp", avg_temp, "C"),
            _card("Avg Speed", avg_speed, "RPM"),
            _card("Avg Current (derived)", avg_current, "A", sub="assumed 400V, PF 0.87"),
        ]

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["motor_power_kw"],
            name="Motor Power (kW)", line=dict(color="#2980b9"),
        ), secondary_y=False)

        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["current_a_derived"],
            name="Derived Current (A)", line=dict(color="#8e44ad", dash="dot"),
        ), secondary_y=False)

        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["motor_temp_c"],
            name="Motor Temp (C)", line=dict(color="#e74c3c"),
        ), secondary_y=True)

        fig.update_layout(
            title=f"{selected_asset}: Motor Power, Derived Current, and Temperature",
            hovermode="x unified",
            legend=dict(orientation="h", y=-0.2),
            margin=dict(t=40, b=40),
        )
        fig.update_yaxes(title_text="Power (kW) / Current (A)", secondary_y=False)
        fig.update_yaxes(title_text="Temp (C)", secondary_y=True)

        note = (
            f"Current trace is derived, not measured: I = P / (√3 × V × PF), "
            f"assuming V={ASSUMED_LINE_VOLTAGE_V:.0f}V line-line, PF={ASSUMED_POWER_FACTOR:.2f}. "
            f"Speed (RPM) omitted from chart to avoid axis clutter; see metric card above."
        )

        return cards, fig, note

    except Exception as e:
        error_fig = go.Figure()
        error_fig.update_layout(title=f"Error: {str(e)}")
        return [], error_fig, ""
