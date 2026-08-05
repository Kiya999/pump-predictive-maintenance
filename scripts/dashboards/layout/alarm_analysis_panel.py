# alarm_analysis_panel.py
from dash import html
from layout.panel_styles import PANEL_STYLE, PANEL_TITLE_STYLE, PANEL_CONTENT_STYLE

def create_alarm_analysis_panel():
    return html.Div([
        html.H2("Alarm Analysis", style=PANEL_TITLE_STYLE),
        html.Div(
            id="alarm-analysis-content",
            children=html.P("", style={"color": "#7f8c8d", "fontSize": "12px"}),
            style=PANEL_CONTENT_STYLE,
        ),
    ], style=PANEL_STYLE)