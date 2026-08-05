# kpi_header_panel.py
from dash import html
from layout.panel_styles import PANEL_STYLE, PANEL_TITLE_STYLE

def create_kpi_header_panel():
    return html.Div([
        html.H2("KPI Overview", style=PANEL_TITLE_STYLE),
        html.Div(id="kpi-header-content", style={
            "display": "flex", "gap": "8px", "flexWrap": "wrap",
        }),
    ], style=PANEL_STYLE)