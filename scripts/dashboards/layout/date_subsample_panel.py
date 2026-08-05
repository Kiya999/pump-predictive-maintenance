# date_subsample_panel.py
from dash import html, dcc
from dashboard_config import DEFAULT_START_DATE, DEFAULT_END_DATE

def create_date_subsample_panel():
    return html.Div([
        html.Div([
            html.Label("Date Range:", style={
                "fontSize": "12px",
                "fontWeight": "bold",
                "marginBottom": "6px",
                "display": "block",
            }),
            dcc.DatePickerRange(
                id="date-range-picker",
                start_date=DEFAULT_START_DATE,
                end_date=DEFAULT_END_DATE,
                display_format="YYYY-MM-DD",
                style={"fontSize": "12px"},
            ),
        ], style={"marginBottom": "10px"}),

        html.Div([
            dcc.Checklist(
                id="subsample-toggle",
                options=[{"label": " Subsample data", "value": "on"}],
                value=["on"],
                style={"fontSize": "12px"},
                labelStyle={"display": "inline-block", "marginRight": "5px"},
            ),
        ], style={"marginBottom": "0"}),

    ], style={
        "padding": "12px",
        "backgroundColor": "#ffffff",
        "borderBottom": "1px solid #bdc3c7",
        "flex": "0 0 auto",
        "boxSizing": "border-box",
    })
