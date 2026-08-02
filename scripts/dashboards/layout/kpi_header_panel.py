# kpi_header_panel.py
from dash import html


def create_kpi_header_panel():
    return html.Div(id="kpi-header-content", style={
        "display": "flex", "gap": 15, "marginBottom": 20, "flexWrap": "wrap",
        "padding": "15px 20px", "backgroundColor": "#2c3e50", "borderRadius": 8,
    })
