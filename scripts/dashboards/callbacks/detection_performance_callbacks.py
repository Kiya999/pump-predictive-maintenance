# detection_performance_callbacks.py
import os
import sys
import pandas as pd
from dash import callback, Input, Output, html, dash_table

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'analytics-pipeline'))

from analytics_config import DETECTION_PERFORMANCE_DIR, ANALYSIS_OUTPUT_FILES

ASSET_SCENARIO_MAP = {
    "P-0100": "bearing",
    "P-0500": "insulation",
}

def _load_csv(filename):
    path = os.path.join(DETECTION_PERFORMANCE_DIR, filename)
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


def _status_from_pct(pct):
    if pct is None or pd.isna(pct):
        return "NO"
    return "SUSPECT" if pct > 100.0 else "OK"


def _color_for_status(status):
    return {"OK": "#27ae60", "SUSPECT": "#e74c3c", "NO": "#95a5a6"}.get(status, "#95a5a6")


def _build_lead_time_table():
    hours_df = _load_csv(ANALYSIS_OUTPUT_FILES["lead_times"])
    pct_df = _load_csv(ANALYSIS_OUTPUT_FILES["lead_times_percent_pf"])
    if hours_df is None or pct_df is None:
        error_div = html.Div(
            "lead_times.csv / lead_times_percent_pf.csv not found - "
            "run analyze_detection_performance.py first.",
            style={"color": "#e74c3c"}
        )
        return error_div, None, None

    hours_df = hours_df.set_index(hours_df.columns[0])
    pct_df = pct_df.set_index(pct_df.columns[0])

    rows = []
    for scenario in hours_df.index:
        for method in hours_df.columns:
            hrs = hours_df.loc[scenario, method]
            pct = pct_df.loc[scenario, method] if scenario in pct_df.index else None
            status = _status_from_pct(pct)
            rows.append({
                "Scenario": scenario,
                "Method": method,
                "Lead time (hours)": f"{hrs:.1f}" if pd.notna(hrs) else "-",
                "% of P-F interval": f"{pct:.1f}%" if pd.notna(pct) else "-",
                "Status": status,
            })

    for method in ["Z-score", "IQR", "Moving avg"]:
        rows.append({
            "Scenario": "cavitation",
            "Method": method,
            "Lead time (hours)": "-",
            "% of P-F interval": "-",
            "Status": "NO",
        })

    table = dash_table.DataTable(
        data=rows,
        columns=[{"name": c, "id": c} for c in ["Scenario", "Method", "Lead time (hours)", "% of P-F interval", "Status"]],
        style_cell={"fontSize": 12, "padding": "6px"},
        style_data_conditional=[
            {"if": {"filter_query": '{Status} = "OK"'}, "backgroundColor": "#eafaf1"},
            {"if": {"filter_query": '{Status} = "SUSPECT"'}, "backgroundColor": "#fdedec"},
            {"if": {"filter_query": '{Status} = "NO"'}, "backgroundColor": "#f4f6f6"},
        ],
    )
    return table, hours_df, pct_df


def _build_fp_table():
    fp_df = _load_csv(ANALYSIS_OUTPUT_FILES["false_positives_by_asset_signal"])
    if fp_df is None:
        return html.Div(
            "false_positives_by_asset_signal.csv not found.", style={"color": "#e74c3c"}
        )
    summary = fp_df.groupby("Signal").agg({
        "Z-score FP rate (%)": "mean",
        "IQR FP rate (%)": "mean",
        "Moving avg FP rate (%)": "mean",
    }).round(2).reset_index()

    return dash_table.DataTable(
        data=summary.to_dict("records"),
        columns=[{"name": c, "id": c} for c in summary.columns],
        style_cell={"fontSize": 12, "padding": "6px"},
    )


@callback(
    Output("detection-performance-kpi-row", "children"),
    Output("lead-time-table", "children"),
    Output("fp-rate-table", "children"),
    Output("trend-detection-summary", "children"),
    Output("detection-performance-method-note", "children"),
    Input("date-range-picker", "start_date"),  # trigger on load; these CSVs aren't date-filtered
    Input("asset-selector", "value"),
)
def update_detection_performance(_start_date, selected_asset):
    """
    Load pre-computed detection performance (lead times, false positive rates).
    Aggregated across ALL ASSETS AND TIME - this is offline validation against synthetic failure scenarios.
    Current FP aggregation by Signal only; future enhancement: reactive per-asset FP breakdown on asset-selector change.
    """
    lead_table, hours_df, pct_df = _build_lead_time_table()

    best_pct = None
    if hours_df is not None and pct_df is not None:
        valid_pct = pct_df.replace([float("inf"), float("-inf")], None).stack().dropna()
        valid_pct = valid_pct[valid_pct <= 100.0]
        best_pct = valid_pct.min() if len(valid_pct) else None

    fp_table = _build_fp_table()

    trend_df = _load_csv(ANALYSIS_OUTPUT_FILES["trend_detection_results"])
    if trend_df is None:
        trend_summary = html.Div("trend_detection_results.csv not found.", style={"color": "#e74c3c"})
        avg_fp = None
    else:
        lines = []
        for _, row in trend_df.iterrows():
            sig_col = [c for c in trend_df.columns if c.startswith("Significant")][0]
            sig = "SIGNIFICANT" if row[sig_col] else "not significant"
            lines.append(html.Div(
                f"{row['Window type']} ({row['Window hours']:.0f}h): "
                f"trend={row['Trend direction']}, p={row['P-value']:.6f} - {sig}"
            ))
        trend_summary = html.Div(lines)
        avg_fp = None

    fp_df_raw = _load_csv(ANALYSIS_OUTPUT_FILES["false_positives_by_asset_signal"])
    if fp_df_raw is not None:
        avg_fp = fp_df_raw["IQR FP rate (%)"].mean()

    def _kpi_card(label, value, color="#2980b9"):
        return html.Div([
            html.Div(label, style={"fontSize": 11, "color": "#7f8c8d"}),
            html.Div(value, style={"fontSize": 20, "fontWeight": "bold", "color": color}),
        ], style={
            "padding": "10px 16px", "backgroundColor": "#f9f9f9",
            "borderRadius": 6, "border": "1px solid #ecf0f1", "minWidth": 150,
        })

    kpis = [
        _kpi_card(
            "Best lead time achieved",
            f"{best_pct:.0f}% of P-F interval" if best_pct is not None else "n/a",
            "#27ae60" if best_pct is not None else "#7f8c8d",
        ),
        _kpi_card(
            "Avg IQR false positive rate",
            f"{avg_fp:.2f}%" if avg_fp is not None else "n/a",
            "#e67e22",
        ),
        _kpi_card("Methods compared", "3 (Z-score, IQR, Moving avg)"),
    ]

    note_text = "Showing offline validation results across all assets (fleet-wide, not asset-filtered)."
    return kpis, lead_table, fp_table, trend_summary, note_text
