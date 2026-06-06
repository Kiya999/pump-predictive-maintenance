# ETL Pipeline Fundamentals for Time Series Data

## 1. ETL Definition

ETL stands for Extract, Transform, Load. It moves data from source systems to a target database or data warehouse.

| Phase | Description |
|---|---|
| Extract | Read raw data from source systems: databases, APIs, flat files, SCADA historians |
| Transform | Clean, validate, aggregate, join, reshape into analysis-ready format |
| Load | Write transformed data to target storage: database, data warehouse, or archive |

## 2. Extract Sources for Sensor Data

| Source | Method |
|---|---|
| CSV export | pandas read_csv |
| SQL database | SQLAlchemy, pyodbc |
| PI Historian | PI Web API, PI ODBC |

## 3. Transform Operations for Sensor Data

| Operation | Description |
|---|---|
| Timestamp normalization | Convert to common timezone and resolution |
| Gap handling | Forward-fill short gaps, interpolate medium gaps, mark remaining as NaN |
| Outlier flagging | Values outside physically plausible ranges |
| Unit conversion | Raw signal to engineering units using instrument range |
| Resampling | Align irregular samples to common time grid using DataFrame.resample |
| Derived signals | diff_pressure = discharge_pressure - suction_pressure |
| Rolling statistics | Rolling mean, std, min, max over configurable window |

## 4. Load Targets

| Target | Method | Use case |
|---|---|---|
| SQLite | pandas to_sql | Prototyping, small datasets |
| PostgreSQL | SQLAlchemy + COPY | Production, concurrent reads |
| Parquet | pandas to_parquet | Columnar storage, fast analytics |
| CSV | pandas to_csv | Universal readability |

## 5. Data Quality Checks in Pipeline

| Check | Method | Action |
|---|---|---|
| Missing timestamp | Verify no null timestamps | Drop row or flag |
| Duplicate timestamps per asset | groupby + duplicated | Keep first, flag duplicates |
| Out-of-range values | Compare against physical thresholds | Cap or flag |
| Monotonicity | Check timestamp order per asset | Sort and flag |
| Stale data | Value unchanged longer than expected window | Flag as frozen sensor |
| Cross-signal consistency | disch_pressure > suction_pressure | Flag violation |

## 6. Common Challenges

| Challenge | Mitigation |
|---|---|
| Missing data in failure periods | Record quality flags per sample |
| Late-arriving data | Buffer window with configurable latency tolerance |
| Sensor drift | Periodic recalibration, drift correction models |
