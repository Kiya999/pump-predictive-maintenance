# etl_config.py
"""
ETL configuration: data source paths, output locations, timezones, column
mappings, unit conversions, and quality report paths.
"""

CONFIG = {
    "sources": {
        "historian": {
            "path": "../historian-generator/output/synthetic_historian_10x365_1min.csv",
            "frequency": "1min",
            "timestamp_col": "timestamp",
            "tz": "UTC",
            "datetime_cols": ["timestamp"],
        },
        "alarm_log": {
            "path": "../historian-generator/output/alarm_log.csv",
            "frequency": None,
            "timestamp_col": "activation_time",
            "tz": "UTC",
            "datetime_cols": ["activation_time", "ack_time", "clear_time"],
        },
        "environmental": {
            "path": "../usgs-weather-analysis/output/usgs_raw.csv",
            "frequency": "5min",
            "timestamp_col": "datetime",
            "tz": "UTC",
            "datetime_cols": ["datetime"],
        },
    },

    "output": {
        "database_path": "output/etl_pipeline.db",
        "log_path": "output/etl_pipeline.log",
    },

    "unit_conversions": {
        "P-0700": {
            "suction_pressure_bar": {"from_unit": "kPa", "to_unit": "bar", "factor": 0.01},
            "disch_pressure_bar": {"from_unit": "kPa", "to_unit": "bar", "factor": 0.01},
            "diff_pressure_bar": {"from_unit": "kPa", "to_unit": "bar", "factor": 0.01},
        },
    },

    "column_mappings": {
        "historian": {
            "timestamp": "timestamp",
            "asset_id": "asset_id",
            "flow_m3h": "flow_m3h",
            "suction_pressure_bar": "suction_pressure_bar",
            "disch_pressure_bar": "disch_pressure_bar",
            "diff_pressure_bar": "diff_pressure_bar",
            "motor_temp_c": "motor_temp_c",
            "motor_power_kw": "motor_power_kw",
            "vibration_mm_s": "vibration_mm_s",
            "speed_rpm": "speed_rpm",
            "failure_type": "failure_type",
        },
        "alarm_log": {
            "activation_time": "timestamp",
            "ack_time": "ack_time",
            "clear_time": "clear_time",
            "asset_id": "asset_id",
            "alarm_tag": "alarm_tag",
            "alarm_description": "alarm_description",
            "alarm_type": "alarm_type",
            "priority": "priority",
            "duration_min": "duration_min",
            "area": "area",
            "operator_id": "operator_id",
            "is_test_case": "is_test_case",
        },
        "environmental": {
            "datetime": "timestamp",
            "00060": "discharge_cfs",
        },
    },

    "quality_report_paths": {
        "historian": "../historian-generator/output/data_quality/historian_quality_report.json",
        "alarm_log": "../historian-generator/output/data_quality/alarm_log_quality_report.json",
        "environmental": "../usgs-weather-analysis/output/data_quality/usgs_quality_report.json",
    },
}
