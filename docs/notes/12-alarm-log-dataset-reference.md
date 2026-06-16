# Alarm Log Dataset Reference

## 1. Dataset Purpose

Synthetic alarm dataset for testing the downstream alarm analytics module. Contains 260-270 rows covering 3 assets over 30 days. Includes realistic alarm patterns and deliberately inserted edge cases that the analytics module must detect.

---

## 2. Field Definitions

Each row follows ISA-18.2 alarm record field naming conventions.

| Field | Data Type | Description | Example |
|-------|-----------|-------------|---------|
| asset_id | string | Plant equipment identifier per ANSI/ISA-5.1 | TK-101 |
| alarm_tag | string | Unique DCS tag name for the measurement point | TK-101.LI_HI |
| alarm_description | string | Human-readable condition | Tank level high |
| priority | integer | Fixed priority from rationalization, 1=Highest to 4=Low | 3 |
| alarm_type | string | Deviation direction: HI or LO | HI |
| activation_time | datetime | When the alarm condition first occurred | 2024-01-06 08:30:00 |
| ack_time | datetime | When operator acknowledged | 2024-01-06 08:30:36 |
| clear_time | datetime | When condition returned to normal; empty if still active | 2024-01-06 08:30:48 |
| duration_min | float | Minutes from activation to clear | 0.8 |
| operator_id | string | Operator who acknowledged | OP01 |
| area | string | Physical plant area of the asset | Storage_Tank_Farm |
| is_test_case | string | YES for edge cases; empty for normal rows | YES |

---

## 3. Tag Naming Convention

Tags follow ANSI/ISA-5.1 Instrumentation Symbols and Identification.

Structure: ASSET_NUMBER.FUNCTION_CODE_DIRECTION

| Part | Meaning | Example |
|------|---------|---------|
| ASSET_NUMBER | Equipment identifier with unit number | TK-101 |
| FUNCTION_CODE | Measured variable and indicator type | LI |
| DIRECTION | Alarm direction suffix | HI, LO |

Standard function codes used in this dataset

| Code | Stands For | Measures |
|------|------------|----------|
| LI | Level Indicator | Liquid level in a vessel |
| PI | Pressure Indicator | Process pressure |
| TI | Temperature Indicator | Process temperature |
| FI | Flow Indicator | Flow rate |
| VI | Vibration Indicator | Mechanical vibration |
| PDI | Pressure Differential Indicator | Pressure difference across a device |

Alarm direction suffixes

| Suffix | Meaning |
|--------|---------|
| HI | High alarm |
| LO | Low alarm |
| HI_HI | High-High trip (automatic shutdown, not an alarm) |
| LO_LO | Low-Low trip (automatic shutdown, not an alarm) |

The direction suffix is appended to the function code with an underscore to form the full alarm tag. For example, LI with direction HI becomes LI_HI. The alarm_type field stores the direction only (HI or LO), not the function code.

Full tag example breakdown

| Tag Component | Value |
|---------------|-------|
| Asset number | TK-101 |
| Function code | LI |
| Direction | HI |
| Full alarm tag | TK-101.LI_HI |
| Description | Tank level high |

---

## 4. Assets

| Asset ID | Equipment Type | Area |
|----------|---------------|------|
| TK-101 | Storage Tank 101 | Storage_Tank_Farm |
| P-201 | Pump 201 | Pumping_Station_A |
| C-301 | Compressor 301 | Compressor_Building |

Standard equipment abbreviations per ANSI/ISA-5.1

| Abbreviation | Equipment |
|--------------|-----------|
| TK | Tank (atmospheric or low-pressure storage) |
| P | Pump (centrifugal or positive displacement) |
| C | Compressor (centrifugal or reciprocating) |
| T | Tower or column |
| R | Reactor |
| H or E | Heat exchanger |
| F | Furnace or heater |
| V | General pressure vessel |
| D | Drum or knockout drum |

The number in the asset ID (101, 201, 301) represents the plant unit. 100-series is Unit 1, 200-series is Unit 2, 300-series is Unit 3.

---

## 5. Priority Rationale

Priority is a fixed attribute of each alarm tag, assigned once during alarm rationalization.
Priority is determined by three factors: consequence severity if the operator does not
respond, available response time before the consequence occurs, and existence of independent
protection layers (IPLs).

| Alarm Tag | Fixed Priority | Rationale |
|-----------|----------------|-----------|
| TK-101.LI_HI | 3 | Overflow causes dike-contained environmental release. Operator has 30+ minutes to respond. HI_HI trip provides backup protection. |
| TK-101.LI_LO | 4 | Low level risks downstream pump cavitation only. No safety or environmental consequence. Operator restores level within shift. |
| TK-101.TI_HI | 3 | Temperature high can vaporize contents, raise pressure, or degrade product. Response time is 10 to 30 minutes due to tank thermal mass. |
| TK-101.PI_HI | 2 | Pressure high risks vessel rupture. Immediate operator action required. Relief valve provides backup protection. |
| P-201.FI_LO | 3 | Low flow risks cavitation and pump damage. Minimum flow recirculation line provides backup protection. |
| P-201.PI_HI | 3 | Discharge pressure high from closed downstream valve. Pump can dead-head over 1-5 minutes. Relief valve provides backup protection. |
| P-201.TI_HI | 2 | Motor bearing or winding temperature high. Escalates quickly to failure. Repair cost is high. |
| P-201.VI_HI | 2 | Vibration high indicates bearing wear, imbalance, or cavitation. Condition accelerates rapidly. |
| C-301.PI_LO | 2 | Suction pressure low risks compressor surge. Anti-surge control system provides backup protection. |
| C-301.TI_HI | 2 | Discharge temperature high indicates excessive compression ratio. Internal damage occurs over minutes. |
| C-301.VI_HI | 1 | Vibration high from surge or mechanical rub. Machine destruction in seconds. No automatic shutdown IPL assumed. |
| C-301.FI_LO | 1 | Lube oil flow low causes bearing seizure in seconds. No backup lubrication system assumed. |
| C-301.PDI_HI | 4 | Filter delta-P high is a maintenance advisory. No immediate operational risk. Bypass valve available. |

---

## 6. Edge Cases

Three edge cases test specific detection capabilities. Each is flagged with is_test_case = YES.

### Edge Case 1: Chattering Sequence

| Property | Value |
|----------|-------|
| Asset | TK-101 |
| Alarm tag | TK-101.LI_HI |
| Fixed priority | 3 |
| Activations | 7 |
| Total span | ~8 minutes |
| Date | Day 5 of dataset |

Detection target: ISA-18.2 chattering threshold is >3 activations in any 5-minute window. 7 activations in 8 minutes means multiple 5-minute windows contain 4 or more activations. The analytics module must flag this tag as chattering.

### Edge Case 2: Stale Alarm

| Property | Value |
|----------|-------|
| Asset | P-201 |
| Alarm tag | P-201.FI_LO |
| Fixed priority | 3 |
| Duration | 52 hours |
| Clear time | Empty (still active when dataset ends) |

Detection target: ISA-18.2 stale alarm threshold is >24 hours continuously active. 52 hours exceeds this threshold by a factor of 2. The analytics module must flag this alarm as stale.

### Edge Case 3: Correlated Batch

| Property | Value |
|----------|-------|
| Asset | C-301 |
| Distinct alarm tags | 5 |
| Total span | ~100 seconds (1.7 minutes) |
| Simulated root cause | Compressor surge or trip event |
| Priority mix | Two priority 1, two priority 2, one priority 4 |

| Alarm Tag | Description | Fixed Priority | Activation Time Offset |
|-----------|-------------|----------------|------------------------|
| C-301.PI_LO | Suction pressure low | 2 | 0 seconds |
| C-301.TI_HI | Discharge temperature high | 2 | +25 seconds |
| C-301.VI_HI | Compressor vibration high | 1 | +50 seconds |
| C-301.FI_LO | Lube oil flow low | 1 | +75 seconds |
| C-301.PDI_HI | Filter delta-P high | 4 | +100 seconds |

Detection target: 5 distinct alarm tags on the same asset within 2 minutes is a cascade sequence from a single root cause. The analytics module must group these by asset and time window to detect the correlation. This distinguishes from chattering (same tag repeating) by checking distinct tag count.
