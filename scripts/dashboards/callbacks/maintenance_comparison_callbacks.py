# maintenance_comparison_callbacks.py
import os
import sys
import pandas as pd
from dash import callback, Input, Output, html

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'analytics-pipeline'))

from analytics_config import DETECTION_PERFORMANCE_DIR, ANALYSIS_OUTPUT_FILES

_engine = None


def set_engine(engine):
    global _engine
    _engine = engine


# CONFIGURATION - EDIT HERE IF DATASET / SYNTHETIC SCENARIOS CHANGE

# Ground-truth synthetic fault-injection parameters
# failure day). If that script changes, update this dict to match.
SCENARIO_GROUND_TRUTH = {
    "P-0100": {"scenario": "bearing", "onset_day": 100, "failure_day": 360},
    "P-0500": {"scenario": "insulation", "onset_day": 150, "failure_day": 270},
}

# OEM reference intervals
# SOURCE: Oxmaint, "Electric Motor Maintenance Best Practices" (2024),
BEARING_LUBE_RPM_CONSTANT = 14_000_000        # hours = constant / motor RPM
INSULATION_TEST_INTERVAL_DAYS = 365           # standard-tier annual megger test
VIBRATION_INSPECTION_INTERVAL_DAYS = 30       # standard-tier monthly vibration check


def _event_box(label, value, color="#2c3e50"):
    return html.Div([
        html.Div(label, style={"fontSize": 11, "color": "#7f8c8d"}),
        html.Div(value, style={"fontSize": 18, "fontWeight": "bold", "color": color}),
    ], style={
        "padding": "10px 14px",
        "border": "1px solid #ecf0f1",
        "borderRadius": "6px",
        "backgroundColor": "#f9f9f9",
        "minWidth": "180px",
    })

def _impact_callout(worst_case_days, actual_days):
    return html.Div([
        html.Div([
            html.Div("FIXED SCHEDULE", style={"fontSize": 10, "color": "#7f8c8d", "fontWeight": "bold", "letterSpacing": "0.5px"}),
            html.Div(f"up to {worst_case_days:.0f}d blind gap", style={"fontSize": 19, "fontWeight": "bold", "color": "#c0392b"}),
        ], style={"flex": 1}),
        html.Div("vs", style={"fontSize": 12, "color": "#bdc3c7", "alignSelf": "center", "padding": "0 14px"}),
        html.Div([
            html.Div("THIS PIPELINE", style={"fontSize": 10, "color": "#7f8c8d", "fontWeight": "bold", "letterSpacing": "0.5px"}),
            html.Div(f"caught in {actual_days:.0f}d", style={"fontSize": 19, "fontWeight": "bold", "color": "#27ae60"}),
        ], style={"flex": 1}),
    ], style={
        "display": "flex",
        "alignItems": "center",
        "backgroundColor": "#fdfefe",
        "border": "1px solid #d5dbdb",
        "borderRadius": "8px",
        "padding": "10px 16px",
        "marginBottom": "10px",
    })

def _load_csv(filename):
    path = os.path.join(DETECTION_PERFORMANCE_DIR, filename)
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


def _best_lead_hours(scenario):
    hours_df = _load_csv(ANALYSIS_OUTPUT_FILES["lead_times"])
    pct_df = _load_csv(ANALYSIS_OUTPUT_FILES["lead_times_percent_pf"])
    if hours_df is None or pct_df is None:
        return None, None

    hours_df = hours_df.set_index(hours_df.columns[0])
    pct_df = pct_df.set_index(pct_df.columns[0])

    if scenario not in hours_df.index:
        return None, None

    row_hours = hours_df.loc[scenario]
    row_pct = pct_df.loc[scenario] if scenario in pct_df.index else None

    candidates = []
    for method in row_hours.index:
        hrs = row_hours[method]
        pct = row_pct[method] if row_pct is not None and method in row_pct.index else None
        if pd.notna(hrs) and (pct is None or pd.isna(pct) or pct <= 100.0):
            candidates.append((hrs, method))

    if not candidates:
        return None, None

    best_hours, best_method = max(candidates, key=lambda x: x[0])
    return best_hours, best_method


def _avg_rpm(asset_id):
    if _engine is None:
        return None
    try:
        result = pd.read_sql(
            f"SELECT AVG(speed_rpm) as avg_rpm FROM historian_clean WHERE asset_id = '{asset_id}' AND failure_type = 'none'",
            _engine
        )
        val = result["avg_rpm"].iloc[0]
        return float(val) if pd.notna(val) else None
    except Exception:
        return None

@callback(
    Output("maintenance-comparison-content", "children"),
    Input("asset-selector", "value"),
)
def update_maintenance_comparison(selected_asset):
    if not selected_asset:
        return html.Div("Select an asset to view maintenance comparison.")

    if selected_asset not in SCENARIO_GROUND_TRUTH:
        return html.Div(
            f"{selected_asset}: No validated detection comparison available for this asset.",
            style={"color": "#7f8c8d", "fontSize": "12px"}
        )

    truth = SCENARIO_GROUND_TRUTH[selected_asset]
    scenario = truth["scenario"]
    onset_day = truth["onset_day"]
    failure_day = truth["failure_day"]

    best_hours, best_method = _best_lead_hours(scenario)
    if best_hours is None:
        return html.Div(
            f"{selected_asset}: Lead-time data missing in {ANALYSIS_OUTPUT_FILES['lead_times']} - run analyze_detection_performance.py.",
            style={"color": "#e74c3c", "fontSize": "12px"}
        )

    detect_day = failure_day - (best_hours / 24.0)
    days_after_onset = detect_day - onset_day

    boxes = [
        _event_box("Onset", f"Day {onset_day}", "#2980b9"),
        _event_box("Detection", f"Day {detect_day:.0f}", "#27ae60"),
        _event_box("Failure", f"Day {failure_day}", "#c0392b"),
    ]

    inspection_lines = []
    worst_case_gap_days = None

    if scenario == "bearing":
        rpm = _avg_rpm(selected_asset)
        if rpm and rpm > 0:
            lube_hours = BEARING_LUBE_RPM_CONSTANT / rpm
            lube_days = lube_hours / 24.0
            boxes.append(_event_box(
                "OEM Lube Interval",
                f"{lube_hours:.0f}h (~{lube_days:.0f}d)",
                "#8e44ad"
            ))
            inspection_lines.append(
                f"Lubrication interval based on asset speed ({rpm:.0f} RPM): ~{lube_days:.0f} days "
                f"({BEARING_LUBE_RPM_CONSTANT:,} / RPM). Lubrication is preventive maintenance, "
                f"not fault detection."
            )
        worst_case_gap_days = VIBRATION_INSPECTION_INTERVAL_DAYS
        inspection_lines.append(
            f"Under a monthly vibration cadence, a fault starting on day {onset_day} could go "
            f"unflagged for up to {worst_case_gap_days} days. Continuous monitoring flagged it in {days_after_onset:.0f} days."
        )

    elif scenario == "insulation":
        worst_case_gap_days = INSULATION_TEST_INTERVAL_DAYS
        boxes.append(_event_box(
            "OEM Test Interval",
            f"{INSULATION_TEST_INTERVAL_DAYS}d (Annual)",
            "#8e44ad"
        ))
        inspection_lines.append(
            f"OEM guidance recommends megger testing every ~{INSULATION_TEST_INTERVAL_DAYS} days. "
            f"Fixed schedules leave blind gaps. Continuous monitoring flagged this fault {days_after_onset:.0f} days "
            f"after onset, independent of test calendars."
        )

    summary_line = f"Best lead time ({best_method}): {best_hours:.0f}h (~{best_hours/24:.0f} days) before failure."

    impact_box = (
        _impact_callout(worst_case_gap_days, days_after_onset)
        if worst_case_gap_days is not None else None
    )

    return html.Div([
        html.Div(f"{selected_asset} - {scenario.capitalize()} Scenario", style={
            "fontWeight": "bold", "fontSize": "14px", "marginBottom": "8px"
        }),
        html.Div(boxes, style={"display": "flex", "gap": "8px", "flexWrap": "wrap", "marginBottom": "10px"}),
        impact_box,
        html.Div(summary_line, style={"fontSize": "12px", "color": "#2c3e50", "marginBottom": "6px"}),
        html.Div(inspection_lines, style={
            "fontSize": "11px",
            "color": "#7d6608",
            "backgroundColor": "#fef9e7",
            "borderLeft": "3px solid #d4ac0d",
            "borderRadius": "4px",
            "padding": "8px 10px",
        }),
    ])
