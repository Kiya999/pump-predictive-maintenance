# motor_monitoring_panel.py
from dash import html

def create_motor_monitoring_panel():
    return html.Div([
        html.H2("Motor Monitoring", style={"marginTop": 0}),
        html.Div([
            html.P("", style={"color": "#7f8c8d"}),
            html.P("Planned indicators:", style={"fontWeight": "bold", "marginBottom": 8}),
            html.Ul([
                html.Li("Current/voltage waveform capture"),
                html.Li("Electrical signature analysis"),
                html.Li("Harmonic distortion detection"),
                html.Li("Phase imbalance detection"),
            ], style={"fontSize": 12, "color": "#7f8c8d"}),
        ], style={
            "padding": 15,
            "backgroundColor": "#f9f9f9",
            "borderRadius": 5,
            "border": "1px dashed #bdc3c7",
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
