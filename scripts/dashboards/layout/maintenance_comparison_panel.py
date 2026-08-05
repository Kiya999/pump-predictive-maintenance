# maintenance_comparison_panel.py
from dash import html
from layout.panel_styles import PANEL_STYLE, PANEL_TITLE_STYLE, NOTE_STYLE

def create_maintenance_comparison_panel():
    return html.Div([
        html.H2("Maintenance Schedule Comparison", style=PANEL_TITLE_STYLE),
        html.Div(id="maintenance-comparison-content")
    ], style=PANEL_STYLE)