# data_dictionary.py
"""
Generate data dictionary Excel workbook documenting column definitions,
data types, units, sources, null handling, and value ranges from the
ETL pipeline database.
"""

import os
import pandas as pd
import sqlite3

from analytics_config import OUTPUT_DIR, ETL_PIPELINE_PATH, CLEAN_TABLES, OUTPUT_FILES

os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = sqlite3.connect(ETL_PIPELINE_PATH)

FLAG = "pass | missing | outlier"
SENSOR = "Nulls retained; flagged as missing"
NOTNULL = "Not null"

data_dict_schema = {
    "historian_clean": [
        {"Column": "id", "Data Type": "INTEGER", "Units": "N/A", "Source System": "SQLite",
         "Update Frequency": "Per ETL run", "Null Handling": NOTNULL, "Quality Flag Meaning": ""},
        {"Column": "timestamp", "Data Type": "DATETIME", "Units": "UTC", "Source System": "Historian CSV",
         "Update Frequency": "1-min", "Null Handling": NOTNULL, "Quality Flag Meaning": ""},
        {"Column": "asset_id", "Data Type": "VARCHAR(50)", "Units": "N/A", "Source System": "Historian CSV",
         "Update Frequency": "1-min", "Null Handling": NOTNULL, "Quality Flag Meaning": ""},
        {"Column": "flow_m3h", "Data Type": "FLOAT", "Units": "m3/h", "Source System": "Historian CSV",
         "Update Frequency": "1-min", "Null Handling": SENSOR, "Quality Flag Meaning": FLAG},
        {"Column": "suction_pressure_bar", "Data Type": "FLOAT", "Units": "bar", "Source System": "Historian CSV",
         "Update Frequency": "1-min", "Null Handling": SENSOR, "Quality Flag Meaning": FLAG},
        {"Column": "disch_pressure_bar", "Data Type": "FLOAT", "Units": "bar", "Source System": "Historian CSV",
         "Update Frequency": "1-min", "Null Handling": SENSOR, "Quality Flag Meaning": FLAG},
        {"Column": "diff_pressure_bar", "Data Type": "FLOAT", "Units": "bar", "Source System": "Historian CSV",
         "Update Frequency": "1-min", "Null Handling": SENSOR, "Quality Flag Meaning": FLAG},
        {"Column": "motor_temp_c", "Data Type": "FLOAT", "Units": "C", "Source System": "Historian CSV",
         "Update Frequency": "1-min", "Null Handling": SENSOR, "Quality Flag Meaning": FLAG},
        {"Column": "motor_power_kw", "Data Type": "FLOAT", "Units": "kW", "Source System": "Historian CSV",
         "Update Frequency": "1-min", "Null Handling": SENSOR, "Quality Flag Meaning": FLAG},
        {"Column": "vibration_mm_s", "Data Type": "FLOAT", "Units": "mm/s", "Source System": "Historian CSV",
         "Update Frequency": "1-min", "Null Handling": SENSOR, "Quality Flag Meaning": FLAG},
        {"Column": "speed_rpm", "Data Type": "FLOAT", "Units": "RPM", "Source System": "Historian CSV",
         "Update Frequency": "1-min", "Null Handling": SENSOR, "Quality Flag Meaning": FLAG},
        {"Column": "failure_type", "Data Type": "VARCHAR(50)", "Units": "N/A", "Source System": "Historian CSV",
         "Update Frequency": "Per scenario", "Null Handling": "Nullable (NULL for real-world data)", "Quality Flag Meaning": "none | bearing | cavitation | insulation"},
        {"Column": "quality_flag", "Data Type": "VARCHAR(50)", "Units": "N/A", "Source System": "ETL pipeline",
         "Update Frequency": "Per ETL run", "Null Handling": NOTNULL, "Quality Flag Meaning": FLAG},
    ],

    "alarm_log_clean": [
        {"Column": "id", "Data Type": "INTEGER", "Units": "N/A", "Source System": "SQLite",
         "Update Frequency": "Per ETL run", "Null Handling": NOTNULL, "Quality Flag Meaning": ""},
        {"Column": "timestamp", "Data Type": "DATETIME", "Units": "UTC", "Source System": "Alarm Log CSV",
         "Update Frequency": "Event-driven", "Null Handling": NOTNULL, "Quality Flag Meaning": ""},
        {"Column": "asset_id", "Data Type": "VARCHAR(50)", "Units": "N/A", "Source System": "Alarm Log CSV",
         "Update Frequency": "Event-driven", "Null Handling": NOTNULL, "Quality Flag Meaning": ""},
        {"Column": "alarm_tag", "Data Type": "VARCHAR(100)", "Units": "N/A", "Source System": "Alarm Log CSV",
         "Update Frequency": "Event-driven", "Null Handling": NOTNULL, "Quality Flag Meaning": ""},
        {"Column": "alarm_description", "Data Type": "VARCHAR(256)", "Units": "N/A", "Source System": "Alarm Log CSV",
         "Update Frequency": "Event-driven", "Null Handling": NOTNULL, "Quality Flag Meaning": ""},
        {"Column": "alarm_type", "Data Type": "VARCHAR(20)", "Units": "N/A", "Source System": "Alarm Log CSV",
         "Update Frequency": "Event-driven", "Null Handling": NOTNULL, "Quality Flag Meaning": "HI | LO"},
        {"Column": "priority", "Data Type": "INTEGER", "Units": "N/A", "Source System": "Alarm Log CSV",
         "Update Frequency": "Event-driven", "Null Handling": NOTNULL, "Quality Flag Meaning": "2=high | 3=medium | 4=low"},
        {"Column": "ack_time", "Data Type": "DATETIME", "Units": "UTC", "Source System": "Alarm Log CSV",
         "Update Frequency": "Event-driven", "Null Handling": "Nullable (NULL if not acknowledged)", "Quality Flag Meaning": ""},
        {"Column": "clear_time", "Data Type": "DATETIME", "Units": "UTC", "Source System": "Alarm Log CSV",
         "Update Frequency": "Event-driven", "Null Handling": "Nullable (NULL if still active)", "Quality Flag Meaning": ""},
        {"Column": "duration_min", "Data Type": "FLOAT", "Units": "minutes", "Source System": "Alarm Log CSV",
         "Update Frequency": "Event-driven", "Null Handling": NOTNULL, "Quality Flag Meaning": ""},
        {"Column": "area", "Data Type": "VARCHAR(100)", "Units": "N/A", "Source System": "Alarm Log CSV",
         "Update Frequency": "Event-driven", "Null Handling": NOTNULL, "Quality Flag Meaning": ""},
        {"Column": "operator_id", "Data Type": "VARCHAR(20)", "Units": "N/A", "Source System": "Alarm Log CSV",
         "Update Frequency": "Event-driven", "Null Handling": "Nullable", "Quality Flag Meaning": ""},
        {"Column": "is_test_case", "Data Type": "VARCHAR(10)", "Units": "N/A", "Source System": "Alarm Log CSV",
         "Update Frequency": "Event-driven", "Null Handling": "Nullable", "Quality Flag Meaning": ""},
        {"Column": "quality_flag", "Data Type": "VARCHAR(50)", "Units": "N/A", "Source System": "ETL pipeline",
         "Update Frequency": "Per ETL run", "Null Handling": NOTNULL, "Quality Flag Meaning": FLAG},
    ],

    "environmental_clean": [
        {"Column": "id", "Data Type": "INTEGER", "Units": "N/A", "Source System": "SQLite",
         "Update Frequency": "Per ETL run", "Null Handling": NOTNULL, "Quality Flag Meaning": ""},
        {"Column": "timestamp", "Data Type": "DATETIME", "Units": "UTC", "Source System": "USGS HTTP API",
         "Update Frequency": "5-min", "Null Handling": NOTNULL, "Quality Flag Meaning": ""},
        {"Column": "discharge_cfs", "Data Type": "FLOAT", "Units": "cfs", "Source System": "USGS Stn 01646500",
         "Update Frequency": "5-min", "Null Handling": SENSOR, "Quality Flag Meaning": FLAG},
        {"Column": "quality_flag", "Data Type": "VARCHAR", "Units": "N/A", "Source System": "ETL pipeline",
         "Update Frequency": "Per ETL run", "Null Handling": NOTNULL, "Quality Flag Meaning": FLAG},
    ],
}

try:
    print("Fetching value ranges from database...")
    value_ranges = {}

    for table_name in CLEAN_TABLES:
        try:
            df_temp = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            value_ranges[table_name] = {}

            text_cols = ["timestamp", "asset_id", "alarm_tag", "alarm_description",
                         "alarm_type", "area", "operator_id", "is_test_case",
                         "failure_type", "quality_flag"]

            for col in df_temp.columns:
                if col in text_cols:
                    continue

                try:
                    numeric_col = pd.to_numeric(df_temp[col], errors='coerce')
                    min_val = numeric_col.min()
                    max_val = numeric_col.max()

                    if pd.notna(min_val) and pd.notna(max_val):
                        value_ranges[table_name][col] = f"{min_val:.2f} to {max_val:.2f}"
                    else:
                        value_ranges[table_name][col] = "N/A"
                except Exception:
                    value_ranges[table_name][col] = "N/A"

        except Exception as e:
            print(f"  Warning: Could not read {table_name}: {e}")

    print("Data ranges fetched\n")

    excel_path = os.path.join(OUTPUT_DIR, OUTPUT_FILES["data_dictionary_excel"])

    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        workbook = writer.book

        header_format = workbook.add_format({
            'bold': True, 'font_color': 'white', 'bg_color': '#366092',
            'border': 1, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True,})

        text_format = workbook.add_format({
            'border': 1, 'align': 'left', 'valign': 'top', 'text_wrap': True,})

        for table_name, schema_list in data_dict_schema.items():
            df_dict = pd.DataFrame(schema_list)

            if table_name in value_ranges:
                df_dict["Value Range"] = df_dict["Column"].map(
                    lambda col: value_ranges[table_name].get(col, "N/A")
                )
            else:
                df_dict["Value Range"] = "N/A"

            df_dict.to_excel(writer, sheet_name=table_name, index=False)
            worksheet = writer.sheets[table_name]

            for col_num, col_name in enumerate(df_dict.columns):
                worksheet.write(0, col_num, col_name, header_format)

            for row_num in range(1, len(df_dict) + 1):
                for col_num in range(len(df_dict.columns)):
                    worksheet.write(row_num, col_num, df_dict.iloc[row_num - 1, col_num], text_format)

            worksheet.set_column('A:A', 25)  # Column
            worksheet.set_column('B:B', 15)  # Data Type
            worksheet.set_column('C:C', 15)  # Units
            worksheet.set_column('D:D', 20)  # Source System
            worksheet.set_column('E:E', 20)  # Update Frequency
            worksheet.set_column('F:F', 20)  # Null Handling
            worksheet.set_column('G:G', 20)  # Quality Flag Meaning
            worksheet.set_column('H:H', 30)  # Value Range

    print(f"Data dictionary saved: {excel_path}")

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Tables documented: {len(data_dict_schema)}")
    for table_name, schema_list in data_dict_schema.items():
        print(f"  {table_name:25} {len(schema_list):2d} columns")

finally:
    conn.close()
