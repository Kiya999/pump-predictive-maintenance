# pf_alignment.py
"""
Generate P-F alignment matrix: failure modes vs detection data sources.
Outputs CSV and formatted Excel workbook with signal strength ratings
and P-F lead time estimates.
"""

import os
import pandas as pd

from analytics_config import OUTPUT_DIR, OUTPUT_FILES


failure_modes = [
    "Bearing wear (rolling element)",
    "Bearing wear (sleeve / journal)",
    "Cavitation",
    "Mechanical seal failure",
    "Shaft misalignment",
    "Impeller erosion",
    "Recirculation (low flow)",
    "Air entrainment",
    "Stator insulation degradation",
    "Rotor bar cracking",
    "Winding faults",
    "Voltage unbalance",
    "Fouling and scaling",
    "Operating far from BEP",
]

data_sources = [
    "Flow Rate",
    "Pressure (Diff)",
    "Motor Temperature",
    "Motor Power",
    "Vibration",
    "Motor ESA",
    "Alarm Log",
    "Environmental (Discharge)",
]

# Reference: 06-failure-mode-reference-table.md and 04/05 electrical/hydraulic documents
# Format: failure_mode -> {data_source: rating}
matrix_data = {
    "Bearing wear (rolling element)": {
        "Flow Rate": "Partial",
        "Pressure (Diff)": "Partial",
        "Motor Temperature": "Strong",
        "Motor Power": "Partial",
        "Vibration": "Strong",
        "Motor ESA": "Partial",
        "Alarm Log": "Unknown",
        "Environmental (Discharge)": "None",
    },
    "Bearing wear (sleeve / journal)": {
        "Flow Rate": "Partial",
        "Pressure (Diff)": "Partial",
        "Motor Temperature": "Strong",
        "Motor Power": "Partial",
        "Vibration": "Partial",
        "Motor ESA": "None",
        "Alarm Log": "Unknown",
        "Environmental (Discharge)": "None",
    },
    "Cavitation": {
        "Flow Rate": "Strong",
        "Pressure (Diff)": "Strong",
        "Motor Temperature": "Partial",
        "Motor Power": "Strong",
        "Vibration": "Strong",
        "Motor ESA": "Partial",
        "Alarm Log": "Unknown",
        "Environmental (Discharge)": "None",
    },
    "Mechanical seal failure": {
        "Flow Rate": "Partial",
        "Pressure (Diff)": "Partial",
        "Motor Temperature": "Strong",
        "Motor Power": "Partial",
        "Vibration": "Partial",
        "Motor ESA": "None",
        "Alarm Log": "Unknown",
        "Environmental (Discharge)": "None",
    },
    "Shaft misalignment": {
        "Flow Rate": "Partial",
        "Pressure (Diff)": "Partial",
        "Motor Temperature": "Partial",
        "Motor Power": "Partial",
        "Vibration": "Strong",
        "Motor ESA": "Partial",
        "Alarm Log": "Unknown",
        "Environmental (Discharge)": "None",
    },
    "Impeller erosion": {
        "Flow Rate": "Strong",
        "Pressure (Diff)": "Strong",
        "Motor Temperature": "Partial",
        "Motor Power": "Strong",
        "Vibration": "Partial",
        "Motor ESA": "None",
        "Alarm Log": "Unknown",
        "Environmental (Discharge)": "None",
    },
    "Recirculation (low flow)": {
        "Flow Rate": "Strong",
        "Pressure (Diff)": "Strong",
        "Motor Temperature": "Partial",
        "Motor Power": "Strong",
        "Vibration": "Partial",
        "Motor ESA": "Partial",
        "Alarm Log": "Unknown",
        "Environmental (Discharge)": "None",
    },
    "Air entrainment": {
        "Flow Rate": "Strong",
        "Pressure (Diff)": "Strong",
        "Motor Temperature": "Partial",
        "Motor Power": "Strong",
        "Vibration": "Strong",
        "Motor ESA": "Partial",
        "Alarm Log": "Unknown",
        "Environmental (Discharge)": "None",
    },
    "Stator insulation degradation": {
        "Flow Rate": "None",
        "Pressure (Diff)": "None",
        "Motor Temperature": "Strong",
        "Motor Power": "Strong",
        "Vibration": "Partial",
        "Motor ESA": "Strong",
        "Alarm Log": "Unknown",
        "Environmental (Discharge)": "None",
    },
    "Rotor bar cracking": {
        "Flow Rate": "None",
        "Pressure (Diff)": "None",
        "Motor Temperature": "Strong",
        "Motor Power": "Strong",
        "Vibration": "Partial",
        "Motor ESA": "Strong",
        "Alarm Log": "Unknown",
        "Environmental (Discharge)": "None",
    },
    "Winding faults": {
        "Flow Rate": "None",
        "Pressure (Diff)": "None",
        "Motor Temperature": "Strong",
        "Motor Power": "Strong",
        "Vibration": "Partial",
        "Motor ESA": "Strong",
        "Alarm Log": "Unknown",
        "Environmental (Discharge)": "None",
    },
    "Voltage unbalance": {
        "Flow Rate": "None",
        "Pressure (Diff)": "None",
        "Motor Temperature": "Strong",
        "Motor Power": "Strong",
        "Vibration": "Partial",
        "Motor ESA": "Partial",
        "Alarm Log": "Unknown",
        "Environmental (Discharge)": "None",
    },
    "Fouling and scaling": {
        "Flow Rate": "Strong",
        "Pressure (Diff)": "Strong",
        "Motor Temperature": "Partial",
        "Motor Power": "Strong",
        "Vibration": "Partial",
        "Motor ESA": "None",
        "Alarm Log": "Unknown",
        "Environmental (Discharge)": "None",
    },
    "Operating far from BEP": {
        "Flow Rate": "Strong",
        "Pressure (Diff)": "Strong",
        "Motor Temperature": "Strong",
        "Motor Power": "Strong",
        "Vibration": "Strong",
        "Motor ESA": "Partial",
        "Alarm Log": "Unknown",
        "Environmental (Discharge)": "None",
    },
}

# from 06-failure-mode-reference-table.md
pf_lead_times = {
    "Bearing wear (rolling element)": "2 to 10 weeks",
    "Bearing wear (sleeve / journal)": "Weeks to months",
    "Cavitation": "Weeks to months",
    "Mechanical seal failure": "Weeks to months",
    "Shaft misalignment": "Weeks to months",
    "Impeller erosion": "Months to years",
    "Recirculation (low flow)": "Weeks to months",
    "Air entrainment": "Immediate to weeks",
    "Stator insulation degradation": "Months to years",
    "Rotor bar cracking": "Weeks to months",
    "Winding faults": "Months to years",
    "Voltage unbalance": "Months to years",
    "Fouling and scaling": "Months to years",
    "Operating far from BEP": "N/A (accelerator)",
}

df = pd.DataFrame(index=failure_modes)

for source in data_sources:
    df[source] = [matrix_data[mode][source] for mode in failure_modes]

df["P-F Lead Time"] = [pf_lead_times[mode] for mode in failure_modes]

df = df.reset_index().rename(columns={"index": "Failure Mode"})

os.makedirs(OUTPUT_DIR, exist_ok=True)
csv_path = os.path.join(OUTPUT_DIR, OUTPUT_FILES["pf_alignment_csv"])
excel_path = os.path.join(OUTPUT_DIR, OUTPUT_FILES["pf_alignment_excel"])

df.to_csv(csv_path, index=False)
print(f"CSV saved: {csv_path}")

with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='P-F Alignment Matrix', index=False)

    workbook = writer.book
    worksheet = writer.sheets['P-F Alignment Matrix']

    header_format = workbook.add_format({
        'bold': True, 'font_color': 'white', 'bg_color': 'blue',
        'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,})

    cell_format = workbook.add_format({
        'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,})

    for col_num, col_name in enumerate(df.columns):
        worksheet.write(0, col_num, col_name, header_format)

    for row_num, (_, row) in enumerate(df.iterrows(), start=1):
        for col_num, col_name in enumerate(df.columns):
            value = row[col_name]
            worksheet.write(row_num, col_num, value, cell_format)

    worksheet.set_column('A:A', 30)
    for i, source in enumerate(data_sources, start=1):
        worksheet.set_column(i, i, 15)
    worksheet.set_column(len(data_sources) + 1, len(data_sources) + 1, 20)

print(f"Excel saved: {excel_path}")

print("\n" + "="*70)
print("P-F ALIGNMENT MATRIX SUMMARY")
print("="*70)
print(f"Failure modes: {len(failure_modes)}")
print(f"Data sources: {len(data_sources)}")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print("\nDetection capability distribution:")
for source in data_sources:
    strong = (df[source] == "Strong").sum()
    partial = (df[source] == "Partial").sum()
    none = (df[source] == "None").sum()
    unknown = (df[source] == "Unknown").sum()
    print(f"  {source:25} Strong={strong:2d}  Partial={partial:2d}  None={none:2d}  Unknown={unknown:2d}")