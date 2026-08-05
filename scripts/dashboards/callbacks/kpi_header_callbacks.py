# kpi_header_callbacks.py
import os
import sys
import json
import pandas as pd
from dash import callback, Input, Output, html

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'analytics-pipeline'))

from analytics_config import DETECTION_PERFORMANCE_DIR, OUTPUT_DIR, OUTPUT_FILES, ANALYSIS_OUTPUT_FILES

_engine = None


def set_engine(engine):
    global _engine
    _engine = engine


def _kpi(label, value):
    return html.Div([
        html.Div(label, style={"fontSize": 11, "color": "#3a3c3d"}),
        html.Div(value, style={"fontSize": 22, "fontWeight": "bold", "color": "black"}),
    ], style={"minWidth": 160})


@callback(
    Output("kpi-header-content", "children"),
    Input("date-range-picker", "start_date"),
)
def update_kpi_header(_start_date):
    """
    Load pre-computed KPIs from static CSVs (lead_times.csv, false_positives_by_asset_signal.csv, etc.).
    NOT reactive to date range or asset selection - these are all-time, all-asset metrics computed offline.
    Used as a summary "dashboard health" header, not live drill-down analytics.
    """
    kpis = []

    # Best lead time (min % of P-F interval among OK statuses)
    pct_path = os.path.join(DETECTION_PERFORMANCE_DIR, ANALYSIS_OUTPUT_FILES["lead_times_percent_pf"])
    hours_path = os.path.join(DETECTION_PERFORMANCE_DIR, ANALYSIS_OUTPUT_FILES["lead_times"])
    if os.path.exists(pct_path) and os.path.exists(hours_path):
        pct_df = pd.read_csv(pct_path, index_col=0)
        hours_df = pd.read_csv(hours_path, index_col=0)
        valid = pct_df.stack().dropna()
        valid = valid[valid <= 100.0]

        if len(valid):
            best_idx = valid.idxmin()
            try:
                best_hours = hours_df.loc[best_idx[0], best_idx[1]]
                kpis.append(_kpi("Best detection lead time", f"{best_hours/24:.0f} days ahead"))
            except Exception:
                kpis.append(_kpi("Best detection lead time", "n/a"))
        else:
            kpis.append(_kpi("Best detection lead time", "n/a"))

    else:
        kpis.append(_kpi("Best detection lead time", "n/a"))

    # Avg FP rate (IQR)
    fp_path = os.path.join(DETECTION_PERFORMANCE_DIR, ANALYSIS_OUTPUT_FILES["false_positives_by_asset_signal"])
    if os.path.exists(fp_path):
        fp_df = pd.read_csv(fp_path)
        avg_fp = fp_df["IQR FP rate (%)"].mean()
        kpis.append(_kpi("Avg false positive rate", f"{avg_fp:.1f}%"))
    else:
        kpis.append(_kpi("Avg false positive rate", "n/a"))

    # ISA validation pass count
    val_path = os.path.join(OUTPUT_DIR, OUTPUT_FILES["isa_validation_results"])
    if os.path.exists(val_path):
        with open(val_path) as f:
            results = json.load(f)
        passed = sum(1 for v in results.values() if v is True)
        total = len(results)
        kpis.append(_kpi("ISA-18.2 test cases passed", f"{passed}/{total}"))
    else:
        kpis.append(_kpi("ISA-18.2 test cases passed", "n/a"))

    # Assets monitored
    if _engine is not None:
        try:
            n_assets = pd.read_sql(
                "SELECT COUNT(DISTINCT asset_id) as n FROM historian_clean", _engine
            )["n"].iloc[0]
            kpis.append(_kpi("Assets monitored", str(n_assets)))
        except Exception:
            kpis.append(_kpi("Assets monitored", "n/a"))

    return kpis
