# isa_alarm_callbacks.py
import os
import sys
import json
import pandas as pd
from dash import callback, Input, Output, html

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'analytics-pipeline'))

from analytics_config import OUTPUT_DIR, OUTPUT_FILES, ISA_DAILY_RATE_TARGET


@callback(
    Output("isa-validation-cards", "children"),
    Output("isa-daily-rate-summary", "children"),
    Input("date-range-picker", "start_date"),  # load trigger; not date-filtered
)
def update_isa_alarm_panel(_start_date):

    def _card(label, passed):
        if passed is None:
            text, color = "N/A", "#95a5a6"
        else:
            text, color = ("PASS", "#27ae60") if passed else ("FAIL", "#e74c3c")
        return html.Div([
            html.Div(label, style={"fontSize": 12, "color": "#7f8c8d"}),
            html.Div(text, style={"fontSize": 18, "fontWeight": "bold", "color": color}),
        ], style={
            "padding": "10px 16px", "backgroundColor": "#f9f9f9",
            "borderRadius": 6, "border": "1px solid #ecf0f1", "minWidth": 120,
        })

    val_path = os.path.join(OUTPUT_DIR, OUTPUT_FILES["isa_validation_results"])
    if os.path.exists(val_path):
        with open(val_path) as f:
            results = json.load(f)
    else:
        results = {"chattering": None, "stale": None, "cluster": None}

    cards = [
        _card("Chattering detection", results.get("chattering")),
        _card("Stale alarm detection", results.get("stale")),
        _card("Cluster detection", results.get("cluster")),
    ]

    rate_path = os.path.join(OUTPUT_DIR, OUTPUT_FILES["alarm_rate_daily"])
    if os.path.exists(rate_path):
        rate_df = pd.read_csv(rate_path)
        pct_over = 100.0 * rate_df["exceeds_isa_target"].mean()
        avg_rate = rate_df["alarm_count"].mean()
        summary = html.Div([
            html.Div(f"ISA-18.2 target: ≤ {ISA_DAILY_RATE_TARGET} alarms/asset/day"),
            html.Div(f"Fleet average: {avg_rate:.1f} alarms/asset/day"),
            html.Div(f"{pct_over:.1f}% of asset-days exceeded the ISA target"),
        ])
    else:
        summary = html.Div("alarm_rate_daily.csv not found.", style={"color": "#e74c3c"})

    return cards, summary
