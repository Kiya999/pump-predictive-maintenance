# header.py
from dash import html, dcc
import pandas as pd
from sqlalchemy import create_engine

from dashboard_config import DB_PATH, DEFAULT_START_DATE, DEFAULT_END_DATE, MAX_WIDTH, BG_COLOR

def get_asset_options():
    """Load asset list from database."""
    engine = create_engine(f"sqlite:///{DB_PATH}")
    try:
        asset_query = "SELECT DISTINCT asset_id FROM historian_clean ORDER BY asset_id"
        assets_df = pd.read_sql(asset_query, engine)
        return [{"label": asset, "value": asset} for asset in assets_df["asset_id"]]
    finally:
        engine.dispose()

ASSET_OPTIONS = get_asset_options()

def create_header():
    return html.Div([
        html.Div([
            html.Div([
                # Logo
                html.Img(
                    src="/assets/logo.png",
                    style={
                        "height": "70px",
                        "marginRight": "20px",
                        "verticalAlign": "middle",
                    }
                ),
                html.Div([
                    html.H1(
                        "Pump and Motor Monitoring Dashboard",
                        style={
                            "margin": "0 0 4px 0",
                            "fontSize": "26px",
                            "fontWeight": "bold",
                            "color": "#ffffff",
                            "lineHeight": "1.1",
                        }
                    ),
                    html.P(
                        "10 assets, 365 days, 1-minute resolution",
                        style={
                            "margin": "0",
                            "fontSize": "12px",
                            "color": "#ecf0f1",
                            "lineHeight": "1",
                        }
                    ),
                ], style={"display": "inline-block", "verticalAlign": "middle"}),
            ], style={
                "display": "flex",
                "alignItems": "center",
                "padding": "12px 15px",
            }),
        ], style={
            "backgroundColor": "#2c3e50",
            "borderBottom": "2px solid #34495e",
        }),

        # Hidden asset selector
        dcc.Dropdown(
            id="asset-selector",
            options=ASSET_OPTIONS,
            value=ASSET_OPTIONS[0]["value"] if ASSET_OPTIONS else None,
            clearable=False,
            style={"display": "none"}
        ),

    ], style={"margin": 0, "padding": 0})