# isa_alarm_panel.py
from dash import html


def create_isa_alarm_panel():
    return html.Div([
        html.H2("Alarm Rationalization (ISA-18.2)", style={"marginTop": 0}),
        html.Div(id="isa-validation-cards", style={
            "display": "flex", "gap": 10, "marginBottom": 15, "flexWrap": "wrap"
        }),
        html.Div(id="isa-daily-rate-summary", style={"fontSize": 13}),
    ], style={
        "flex": 1, "minWidth": 0, "padding": 20, "backgroundColor": "#ffffff",
        "borderRadius": 8, "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
    })
