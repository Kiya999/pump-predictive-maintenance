# motor_monitoring_panel.py
from dash import html, dcc
from layout.panel_styles import PANEL_STYLE, PANEL_TITLE_STYLE, NOTE_STYLE

def create_motor_monitoring_panel():
    return html.Div([
        html.H2("Motor Monitoring", style=PANEL_TITLE_STYLE),
        html.Div(id="motor-metric-cards", style={
            "display": "flex", "gap": "8px", "marginBottom": "8px", "flexWrap": "wrap"
        }),
        dcc.Graph(id="motor-monitoring-graph", style={"flex": 1, "minWidth": 0}),
        html.Div(id="motor-derived-current-note", style={
            "fontSize": "11px", "color": "#7f8c8d", "marginTop": "4px"
        }),
    ], style=PANEL_STYLE)
