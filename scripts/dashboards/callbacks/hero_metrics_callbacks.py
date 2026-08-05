# hero_metrics_callbacks.py
import os
import sys
import pandas as pd
from dash import callback, Input, Output, html

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'analytics-pipeline'))

from analytics_config import DETECTION_PERFORMANCE_DIR, ANALYSIS_OUTPUT_FILES

# Same ground-truth scenario names used by maintenance_comparison_callbacks.py.
# Duplicated intentionally (avoids cross-module coupling)
# if you add a scenario there, add its display name here too.

VALIDATED_SCENARIO_NAMES = ["bearing", "insulation"]

def _load_csv(filename):
    path = os.path.join(DETECTION_PERFORMANCE_DIR, filename)
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


def _card(label, value, sub=None, color="#2c3e50"):
    children = [
        html.Div(label, style={"fontSize": 12, "color": "#7f8c8d"}),
        html.Div(value, style={"fontSize": 28, "fontWeight": "bold", "color": color}),
    ]
    if sub:
        children.append(html.Div(sub, style={"fontSize": 11, "color": "#7f8c8d"}))
    return html.Div(children, style={
        "flex": "1 1 220px",
        "padding": "12px 16px",
        "backgroundColor": "#f9f9f9",
        "border": "1px solid #ecf0f1",
        "borderRadius": "6px",
        "minWidth": "220px",
    })


@callback(
    Output("hero-metrics-content", "children"),
    Input("date-range-picker", "start_date"),
)
def update_hero_metrics(_start_date):
    hours_df = _load_csv(ANALYSIS_OUTPUT_FILES["lead_times"])
    fp_df = _load_csv(ANALYSIS_OUTPUT_FILES["false_positives_by_asset_signal"])

    earliest_days = None
    n_scenarios = None

    if hours_df is not None:
        scenario_col = hours_df.columns[0]
        n_scenarios = hours_df[scenario_col].isin(VALIDATED_SCENARIO_NAMES).sum()

        value_cols = [c for c in hours_df.columns if c != scenario_col]
        vals = pd.to_numeric(hours_df[value_cols].stack(), errors="coerce").dropna()
        if len(vals):
            earliest_days = vals.max() / 24.0

    avg_iqr_fp = None
    if fp_df is not None and "IQR FP rate (%)" in fp_df.columns:
        avg_iqr_fp = fp_df["IQR FP rate (%)"].mean()

    scenario_label = ", ".join(VALIDATED_SCENARIO_NAMES) if n_scenarios else "n/a"

    return [
        _card("Earliest warning", f"{earliest_days:.0f} days", "Best lead time observed", "#27ae60") if earliest_days is not None else _card("Earliest warning", "n/a"),
        _card("Avg IQR false positive rate", f"{avg_iqr_fp:.1f}%", "Healthy assets only", "#e67e22") if avg_iqr_fp is not None else _card("Avg IQR false positive rate", "n/a"),
        _card("Validated sustained-fault scenarios", str(n_scenarios) if n_scenarios is not None else "n/a", scenario_label.capitalize(), "#2980b9"),
    ]