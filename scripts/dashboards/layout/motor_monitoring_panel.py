# motor_monitoring_panel.py
from dash import html, dcc

def create_motor_monitoring_panel():
    return html.Div([
        html.H2("Motor Monitoring", style={"marginTop": 0}),
        html.Div([
            html.Span("Note: ", style={"fontWeight": "bold"}),
            html.Span(
                "Uses historian_clean signals (motor_power_kw, motor_temp_c, speed_rpm). "
                "Current derived from power with assumed voltage/power factor.",
                style={"color": "#7f8c8d"}
            ),
        ], style={
            "fontSize": 12,
            "padding": "8px 10px",
            "backgroundColor": "#fdf6e3",
            "borderLeft": "3px solid #f39c12",
            "marginBottom": 15,
        }),

        html.Div(id="motor-metric-cards", style={
            "display": "flex", "gap": 10, "marginBottom": 15, "flexWrap": "wrap"
        }),

        dcc.Graph(id="motor-monitoring-graph"),

        html.Div(id="motor-derived-current-note", style={
            "fontSize": 11, "color": "#7f8c8d", "marginTop": 8
        }),

    ], style={
        "flex": 1,
        "minWidth": 0,
        "padding": 20,
        "backgroundColor": "#ffffff",
        "borderRadius": 8,
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
        "minHeight": 500,
    })
