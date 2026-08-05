# isa_alarm_panel.py
from dash import html
from layout.panel_styles import PANEL_STYLE, PANEL_TITLE_STYLE

def create_isa_alarm_panel():
    return html.Div([
        html.H2("ISA-18.2 Rationalization", style=PANEL_TITLE_STYLE),
        html.Div(id="isa-validation-cards", style={
            "display": "flex", "gap": "6px", "marginBottom": "8px", "flexWrap": "wrap"
        }),
        html.Div(id="isa-daily-rate-summary", style={"fontSize": "12px"}),
    ], style=PANEL_STYLE)