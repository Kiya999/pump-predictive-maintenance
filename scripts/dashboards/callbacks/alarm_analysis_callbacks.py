# alarm_analysis_callbacks.py
from dash import callback, Input, Output, html, dcc
from dash.dash_table import DataTable
import pandas as pd
import plotly.graph_objects as go

_engine = None

def set_engine(engine):
    global _engine
    _engine = engine

@callback(
    Output("alarm-analysis-content", "children"),
    Input("asset-selector", "value"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),
)
def update_alarm_analysis(asset_id, start_date, end_date):

    if _engine is None or not asset_id:
        return html.Div("Select asset and date range")

    try:
        query_top10 = f"""
        SELECT alarm_tag, COUNT(*) as count, AVG(CAST(priority AS FLOAT)) as avg_priority
        FROM alarm_log_clean
        WHERE asset_id = '{asset_id}'
        AND timestamp BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY alarm_tag
        ORDER BY count DESC
        LIMIT 10
        """
        top10_df = pd.read_sql(query_top10, _engine)

        query_priority = f"""
        SELECT
            CASE WHEN priority <= 2 THEN 'Critical' ELSE 'Nuisance' END as severity,
            COUNT(*) as count
        FROM alarm_log_clean
        WHERE asset_id = '{asset_id}'
        AND timestamp BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY severity
        """
        priority_df = pd.read_sql(query_priority, _engine)

        query_daily = f"""
        SELECT DATE(timestamp) as alarm_date, COUNT(*) as daily_count
        FROM alarm_log_clean
        WHERE asset_id = '{asset_id}'
        AND timestamp BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY alarm_date
        ORDER BY alarm_date
        """
        daily_df = pd.read_sql(query_daily, _engine)

        query_events = f"""
        SELECT timestamp, alarm_tag, alarm_description, priority, duration_min
        FROM alarm_log_clean
        WHERE asset_id = '{asset_id}'
        AND timestamp BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY timestamp DESC
        """
        events_df = pd.read_sql(query_events, _engine)

        fig_top10 = go.Figure()
        fig_top10.add_trace(go.Bar(
            x=top10_df["alarm_tag"].head(10),
            y=top10_df["count"].head(10),
            marker=dict(color="#3498db")
        ))
        fig_top10.update_layout(
            title="Top 10 Alarms by Frequency",
            xaxis_title="Alarm Tag",
            yaxis_title="Count",
            template="plotly_white",
            height=450,
        )

        fig_donut = go.Figure()
        if len(priority_df) > 0:
            fig_donut.add_trace(go.Pie(
                labels=priority_df["severity"],
                values=priority_df["count"],
                hole=0.4,
                marker=dict(colors=["#e74c3c", "#f39c12"])
            ))
        fig_donut.update_layout(
            title="Critical vs Nuisance Alarms",
            height=450,
        )

        fig_trend = go.Figure()
        if len(daily_df) > 0:
            fig_trend.add_trace(go.Scatter(
                x=daily_df["alarm_date"],
                y=daily_df["daily_count"],
                mode="lines+markers",
                line=dict(color="#2ecc71", width=2),
                marker=dict(size=6)
            ))
        fig_trend.update_layout(
            title="Daily Alarm Count",
            xaxis_title="Date",
            yaxis_title="Alarm Count",
            template="plotly_white",
            height=300,
        )

        table_data = events_df.to_dict("records")

        return html.Div([
            html.Div([
                html.Div([dcc.Graph(figure=fig_top10)], style={"flex": 1, "minWidth": 0}),
                html.Div([dcc.Graph(figure=fig_donut)], style={"flex": 1, "minWidth": 0}),
            ], style={"display": "flex", "gap": 8, "marginBottom": 15}),

            html.Div([dcc.Graph(figure=fig_trend)], style={"marginBottom": 15}),

            html.Div([
                html.H3("Alarm Events", style={"marginTop": 0}),
                DataTable(
                    data=table_data,
                    columns=[
                        {"name": "Timestamp", "id": "timestamp", "type": "text"},
                        {"name": "Tag", "id": "alarm_tag", "type": "text"},
                        {"name": "Description", "id": "alarm_description", "type": "text"},
                        {"name": "Priority", "id": "priority", "type": "numeric"},
                        {"name": "Duration (min)", "id": "duration_min", "type": "numeric"},
                    ],

                    page_size=20,
                    sort_action="native",
                    filter_action="native",
                    style_cell={"fontSize": 12, "padding": 8},
                    style_header={"backgroundColor": "#f0f0f0", "fontWeight": "bold"},
                    style_data_conditional=[
                        {
                            "if": {"column_id": "priority", "filter_query": "{priority} <= 2"},
                            "backgroundColor": "#fadbd8",
                            "fontWeight": "bold",
                            "color": "#c0392b",
                        },
                        {
                            "if": {"column_id": "priority", "filter_query": "{priority} > 2"},
                            "backgroundColor": "#fdebd0",
                            "color": "#d68910",
                        }
                    ]

                ) if len(table_data) > 0 else html.Div("No events in range", style={"color": "#7f8c8d"}),
            ], style={"marginTop": 15}),
        ])

    except Exception as e:
        return html.Div(f"Error: {str(e)}", style={"color": "red"})
