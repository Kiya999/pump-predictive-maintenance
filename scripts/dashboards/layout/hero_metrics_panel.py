# hero_metrics_panel.py
from dash import html
from layout.panel_styles import PANEL_STYLE, PANEL_TITLE_STYLE

def create_hero_metrics_panel():
    return html.Div([
        html.Div("Predictive Maintenance Validation Highlights", style={
            **PANEL_TITLE_STYLE,
            "fontSize": "16px",
        }),
        html.Div(id="hero-metrics-content", style={
            "display": "flex",
            "gap": "12px",
            "flexWrap": "wrap",
        }),
    ], style=PANEL_STYLE)
