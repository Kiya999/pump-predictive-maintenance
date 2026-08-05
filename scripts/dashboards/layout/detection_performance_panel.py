# detection_performance_panel.py
from dash import html
from layout.panel_styles import PANEL_STYLE, PANEL_TITLE_STYLE, NOTE_STYLE

def create_detection_performance_panel():
    return html.Div([
        html.H2("Detection Performance", style=PANEL_TITLE_STYLE),

        html.Div(id="detection-performance-method-note", style={
            "fontSize": "11px",
            "color": "#7f8c8d",
            "marginBottom": "8px"
        }),
        html.Div(id="detection-performance-kpi-row", style={
            "display": "flex", "gap": "6px", "marginBottom": "8px", "flexWrap": "wrap"
        }),
        html.H4("Lead time vs P-F interval", style={"fontSize": "13px", "margin": "6px 0"}),
        html.Div(id="lead-time-table", style={"fontSize": "12px"}),
        html.H4("False positive rate", style={"fontSize": "13px", "margin": "6px 0"}),
        html.Div(id="fp-rate-table", style={"fontSize": "12px"}),
        html.H4("Trend significance", style={"fontSize": "13px", "margin": "6px 0"}),
        html.Div(id="trend-detection-summary", style={"fontSize": "12px"}),
    ], style=PANEL_STYLE)