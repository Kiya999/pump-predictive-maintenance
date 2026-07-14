# header.py
from dash import html, dcc
import pandas as pd
from sqlalchemy import create_engine
import os

db_path = os.path.join(os.path.dirname(__file__), "../..", "etl-pipeline", "output", "etl_pipeline.db")

engine = create_engine(f"sqlite:///{db_path}")

asset_query = "SELECT DISTINCT asset_id FROM historian_clean ORDER BY asset_id"
assets_df = pd.read_sql(asset_query, engine)
ASSET_OPTIONS = [{"label": asset, "value": asset} for asset in assets_df["asset_id"]]

engine.dispose()


def create_header():
    return html.Div([
        html.Div([
            html.H1("Pump and Motor Monitoring Dashboard",
                    style={"textAlign": "center", "marginTop": 0, "marginBottom": 5}),
            html.P("10 assets, 365 days, 1-minute resolution",
                   style={"textAlign": "center", "color": "#7f8c8d", "marginBottom": 15}),

            html.Hr(style={"borderColor": "#bdc3c7"}),

            dcc.Dropdown(
                id="asset-selector",
                options=ASSET_OPTIONS,
                value=ASSET_OPTIONS[0]["value"] if ASSET_OPTIONS else None,
                clearable=False,
                style={"display": "none"}
            ),

            html.Div([

                html.Div([
                    html.Label("Date Range:", style={"fontWeight": "bold"}),
                    dcc.DatePickerRange(
                        id="date-range-picker",
                        start_date="2025-07-21",
                        end_date="2025-07-31",
                        display_format="YYYY-MM-DD"
                    ),
                ], style={"flex": 1, "marginRight": 20}),

                html.Div([
                    dcc.Checklist(
                        id="subsample-toggle",
                        options=[{"label": " Subsample data", "value": "on"}],
                        value=["on"],
                        style={"display": "inline-block"}
                    ),
                ], style={"flex": 1, "marginRight": 0}),

            ], style={
                "display": "flex",
                "gap": 10,
                "padding": "15px",
                "backgroundColor": "#ffffff",
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
            }),

        ], style={
            "maxWidth": 1800,
            "margin": "0 auto",
            "padding": "15px",
        }),

    ], style={"backgroundColor": "#ecf0f1"})