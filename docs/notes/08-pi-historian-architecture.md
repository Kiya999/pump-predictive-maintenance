# PI Historian / AVEVA Architecture

## 1. PI System Overview

PI System is a time-series data infrastructure platform developed by OSIsoft and now owned by AVEVA. Time-series data means measurements recorded over time (e.g., a pressure reading every second, a temperature every minute). The PI System collects, stores, and delivers real-time operations data from industrial assets. A minimal architecture consists of three tiers: data sources (interfaces, adapters, connectors), the PI Server (Data Archive + Asset Framework), and client applications.

### Core Components

| Component | Function |
|-----------|----------|
| PI Interface | Data collection from legacy systems (OPC DA, Modbus, proprietary protocols). Legacy systems are older equipment that may not support modern communication standards. Performs exception filtering before sending data to the Data Archive |
| AVEVA Adapter | Modern data collection for OPC UA, REST, MQTT. These are standard communication protocols for industrial and web-based data exchange. Supports deadband filtering but ignores tag-level exception settings |
| PI Connector | Cloud-to-on-premises data ingestion. Does not perform exception testing |
| PI Data Archive | Storage engine for time-series events. Applies compression via swinging door algorithm |
| PI Asset Framework (AF) | Metadata layer. Metadata means "data about data" — it describes what each tag represents, where it belongs, and how it relates to other tags. Organizes tags into asset hierarchies with attributes, templates, analytics, and event frames |
| PI Buffer Subsystem | Caches data when connection to Data Archive is lost. Can apply compression marking |

Note on protocols: OPC DA (OLE for Process Control - Data Access) is an older Windows-based protocol. OPC UA (Unified Architecture) is its modern platform-independent replacement. Modbus is a simple industrial protocol still widely used on pumps and flow meters. REST and MQTT are web and IoT protocols respectively.

---

## 2. PI Data Archive - Tag Storage

PI Points, also called tags, define the data streams stored in the Data Archive. A tag represents one measurement channel — for example, "Pump 101 Discharge Pressure" would be one tag. Each tag has a set of attributes that control how data is collected, compressed, and stored.

### Key Tag Attributes

| Attribute | Name | Purpose |
|-----------|------|---------|
| Point ID | pointid | Unique numeric identifier, assigned at creation, never changes |
| Point Name | tagname | Human-readable identifier, can be renamed |
| Point Source | source | Identifies the interface or adapter that writes data to the tag |
| Location1, Location2, Location3 | loc | Integer codes for filtering, sorting, grouping tags |
| Unit of Measure | EngUnits | Engineering unit string (e.g., C, gpm, psi) |
| Span | span | Expected range of values (zero and span define 0-100% scale). For example, a pressure transmitter with a 0-100 psi range has Span = 100 |
| Descriptor | descriptor | Text description of the tag |
| Compressing | compress | On/off switch for compression algorithm |
| Compression Deviation | CompDev | Deadband size for swinging door algorithm, in engineering units. Deadband means a tolerance zone: if the value stays within this zone, it is considered unchanged |
| Compression Deviation Percent | CompDevPercent | CompDev as percentage of Span |
| Compression Maximum | CompMax | Maximum time in seconds allowed between archived events |
| Exception Deviation | ExcDev | Deadband size for exception filtering, in engineering units |
| Exception Deviation Percent | ExcDevPercent | ExcDev as percentage of Span |
| Exception Maximum | ExcMax | Maximum time in seconds allowed between events sent to snapshot |
| Point Security | secur | ACL (Access Control List) controlling read/write access |
| Point Data Type | pointtype | Data type: float16, float32, float64, int16, int32, digital. Digital means on/off or discrete states (e.g., pump running = 1, pump stopped = 0) |

---

## 3. Exception and Compression

Two-stage filtering process that reduces data volume while preserving information content. Think of it like deciding which measurements are important enough to keep: exception filtering decides what to send across the network, and compression decides what to permanently store on disk.

| Stage | Location | Algorithm | Effect |
|-------|----------|-----------|--------|
| Exception | PI Interface (or Adapter with deadband) | Simple deadband: if new value differs from previous snapshot by more than ExcDev, send it. If no value exceeds ExcDev within ExcMax seconds, force-send the current value | Filters noise at source. Reduces data sent over network |
| Compression | PI Data Archive snapshot subsystem (the part of the archive that receives new data in real time before deciding whether to store it permanently) | Swinging door: constructs a corridor of width CompDev around data points. If new value falls outside the corridor, the previous point is archived and a new corridor starts. If no value triggers this within CompMax seconds, force-archive | Eliminates redundant stored events. Reduces disk storage and query time |

### Settings Guidance

| Parameter | Recommendation |
|-----------|---------------|
| CompDev | Set equal to or less than instrument precision for the tag's unit of measure. Instrument precision means the smallest change the sensor can reliably measure (e.g., 0.1 C for a temperature sensor) |
| ExcDev | Set to half of CompDev (ExcDev = CompDev / 2) |
| CompMax, ExcMax | Set based on required update frequency for the tag's process |
| Non-critical analog tags | Enabling compression with CompDev = 0 and CompDevPercent = 0.1 to 2 achieves > 3:1 compression ratio with precision loss below instrument precision. A 3:1 compression ratio means the stored data takes one-third the disk space of the raw data |
| Default values | Defaults are NOT zero. Compressing = 0 (off) is not the same as Compressing = 1 with CompDev = 0 |

---

## 4. Swinging Door Compression Algorithm

The swinging door algorithm determines which events to archive based on a corridor of width CompDev. The name comes from how the upper and lower limits swing open like doors as new data points arrive. Values that fall within the corridor are discarded because they can be approximated later by drawing a straight line between the two archived points that bracket them.

| Step | Action |
|------|--------|
| 1 | Archive the first value (point A). Initialize SMax and SMin slopes from point A through A plus CompDev |
| 2 | For each new value V at time T, calculate the slope from point A to (V plus CompDev) and (V minus CompDev) |
| 3 | If these slopes lie within current SMax and SMin, the corridor has room. Do not archive. Update SMax or SMin to narrow the corridor |
| 4 | If a new value falls outside the corridor, archive the previous value, set point A to that archived value, and start a new corridor |
| 5 | If CompMax seconds elapse without archiving, force-archive the current value |

Values not archived can be recreated by linear interpolation between archived points. Linear interpolation means drawing a straight line between two known points and reading the value at any time along that line. Maximum interpolation error is bounded by CompDev — so you will never be off by more than CompDev from the actual measured value.

---

## 5. PI Asset Framework (AF)

PI AF is a metadata and analytics layer that organizes time-series tags into logical asset hierarchies. It does not store time-series data itself. Instead, it stores relationships and references to PI Data Archive tags. Think of AF as the table of contents and the Data Archive as the books on the shelf.

### AF Components

| Component | Description |
|-----------|-------------|
| Database | Root container for an AF hierarchy. One PI Server can host multiple AF databases |
| Element | Represents an asset (pump, motor, pipeline, valve). Contains attributes |
| Element Template | Reusable definition for similar assets. Defines base attributes, default values, and data references. If you have 50 identical pumps, you define one template and create 50 elements from it |
| Attribute | Property of an element (rated flow, installation date, current vibration reading). Can reference a PI Point for time-series data |
| Category | Tag for grouping elements or attributes (e.g., "Mechanical", "Electrical", "Critical") |
| Notification | Automated alert triggered when an attribute value crosses a defined threshold |
| Analysis | Calculation engine that computes derived attributes (efficiency, health scores, totals) on a schedule. Derived attributes are values calculated from other attributes rather than measured directly |
| Event Frame | Record of an incident or state change with start and end timestamps (e.g., a pump run event, a high vibration alarm) |

### AF Element Hierarchy Example (Water Utility)

```
Plant Database
  +-- Treatment Plant 1
  |     +-- High Lift Station
  |     |     +-- Pump P-101 (Template: Centrifugal Pump)
  |     |     |     +-- Attributes:
  |     |     |           Bearing Temperature DE (ref: PI tag P1_HS_P101_BRG_T_DE)
  |     |     |           Bearing Temperature NDE (ref: PI tag P1_HS_P101_BRG_T_NDE)
  |     |     |           Vibration Velocity (ref: PI tag P1_HS_P101_VIB_RMS)
  |     |     |           Motor Current (ref: PI tag P1_HS_P101_MOT_A)
  |     |     |           Discharge Pressure (ref: PI tag P1_HS_P101_P_DSCH)
  |     |     |           Flow Rate (ref: PI tag P1_HS_P101_F)
  |     |     |           Efficiency (Analysis: power in / hydraulic power)
  |     |     |           Health Score (Analysis: weighted composite of attributes)
  |     |     +-- Pump P-102 (Template: Centrifugal Pump)
  |     +-- Clearwell
  |     +-- Chemical Feed
  +-- Distribution
        +-- Zone 1
        +-- Zone 2
```

In this hierarchy, a "High Lift Station" contains multiple pumps. Each pump element inherits its attribute structure from a Centrifugal Pump template. The template defines which attributes exist, what PI Point each references, and what analyses calculate derived values. Changing the template updates all pump instances at once — you do not need to edit each pump individually.

---

## 6. PI DataLink for Excel

PI DataLink is an Excel add-in (a supplementary program that adds features to Excel) that allows users to pull PI System data directly into spreadsheets without manual copying or exporting.

### Primary Functions

| Function | Description | Use Case |
|----------|-------------|----------|
| PIRef | Returns current snapshot value for a tag or attribute. Snapshot means the most recent value received | Real-time dashboard |
| PICompDat | Returns compressed (archived) values within a time range. Timestamps are irregularly spaced based on when values were archived | Retrieving all historically stored events for a tag |
| PISampDat | Returns evenly-spaced interpolated values at regular time intervals. Interpolated means estimated between two known points | Trending, charting at consistent intervals |
| PITimedDat | Returns values at specific timestamps | Comparing values at defined events |
| PIVTag | Returns the current value of a PI Vision symbol | Linking PI Vision displays to Excel |
| PIFind | Lists PI points matching search criteria | Discovery, tag inventory |
| PIModVal | Writes values back to PI tags | Data correction, manual entries |

### Data Export Format (CSV)

CSV stands for Comma-Separated Values. It is a plain-text file format where each row represents one record and columns are separated by commas. When data is exported from PI Vision or PI DataLink to CSV, the typical structure is:

```
Time,Tag1,Tag2,Tag3
2023-10-15 08:00:00.000,124.5,0.75,88.2
2023-10-15 08:00:01.000,124.6,0.75,88.3
2023-10-15 08:00:02.000,124.4,0.74,88.1
```

Key facts about the timestamp format:

| Parameter | Detail |
|-----------|--------|
| Timestamp format | yyyy-MM-dd HH:mm:ss.ssss (24-hour, up to millisecond or microsecond precision). This is the ISO 8601 standard format |
| Time zone | Local server time zone by default. UTC (Coordinated Universal Time) option available in export settings |
| Decimal separator | Period (e.g., 124.5 not 124,5) |
| Column delimiter | Comma. Semicolon in regional settings where comma is decimal separator |
| Missing data | Empty cell or "No Data" string |
| Compression effect | Timestamps are not evenly spaced if using compressed data export. Time gaps indicate no value was stored during that period because the value did not change enough to trigger compression |
| CSV export limit | PI Vision exports up to 3600 values per data item per export |

### Critical Warning

Do NOT open PI-generated CSV files in Excel by double-clicking. Excel automatically formats the timestamp column, truncating sub-second precision and converting to local time zone. Truncating means cutting off the decimal part — so "08:00:00.123" becomes "08:00:00". Import the CSV using Excel's Data import wizard and specify text format for the timestamp column to preserve the original precision.

---

## 7. PI Web API

API stands for Application Programming Interface. It is a way for software programs to communicate with each other. PI Web API is a RESTful web API (an API that follows REST design principles using standard web HTTP methods like GET and POST) that provides programmatic access to the PI System over HTTP/HTTPS. Programmatic access means you can write code (Python, JavaScript, etc.) to read and write data instead of using a graphical user interface. Clients can read and write data, navigate the AF hierarchy, and trigger analyses without installing PI client software.

### API Capabilities

| Feature | Description |
|---------|-------------|
| Authentication | Kerberos, Basic, Active Directory, or anonymous. These are different methods for verifying the user's identity |
| Data retrieval | Streamed, interpolated, compressed, summary (average, minimum, maximum, count, standard deviation, total) |
| AF navigation | Browse element hierarchy, read attributes, resolve data references |
| Batch requests | Multiple operations in a single HTTP request to reduce round trips. This improves performance when requesting many tags at once |
| Event frames | Query, create, update event frames |
| Output format | JSON by default. JSON (JavaScript Object Notation) is a lightweight text format for structured data, commonly used in web APIs. CSV output option available |
| Rate limits | Configurable on server side to prevent any single client from overloading the system |

### Data Contract

The JSON response for a stream value contains:

| Field | Type | Example |
|-------|------|---------|
| Timestamp | string (ISO 8601) | "2023-10-15T08:00:00.000Z" |
| Value | string, number, or object | 124.5 |
| UnitsAbbreviation | string | "gpm" |
| Good | boolean | true (indicates data quality is acceptable) |
| Annotated | boolean | false (indicates whether a user has added a note to this value) |
| Errors | array | [] (empty if no errors occurred) |

The Timestamp field uses ISO 8601 format with UTC time zone by default (trailing Z indicates UTC, which stands for "Zulu time" or Coordinated Universal Time — the same worldwide). Local server time can be requested by specifying a query parameter.

### AVEVA GitHub Repository

GitHub is a platform for hosting and sharing code. AVEVA provides open-source Python client libraries for PI Web API. Open-source means the code is publicly available and free to use. The repository `PI-Web-API-Client-Python` on GitHub (github.com/AVEVA) contains example code for authentication, data retrieval, and AF navigation.

---

## 8. Historian Data Export - What to Expect

When receiving a PI historian data export for analysis, the following characteristics apply:

| Characteristic | Compressed Data (PICompDat) | Sampled Data (PISampDat) |
|----------------|----------------------------|-------------------------|
| Time spacing | Irregular. Gaps where no change occurred | Regular, defined by user interval |
| Number of rows | Variable per tag (each stored event) | Fixed per time range |
| Data fidelity | Actual archived values at time of change | Interpolated values at exact interval boundaries |
| Max interpolation error | Bounded by CompDev | Depends on underlying data pattern |
| Missing data | Gap in rows (no row for that time) | Returns last known value or "No Data" |
| Use case | Root cause analysis, event reconstruction | Trending, averaging, time-based calculations |

### Sample CSV Export - Compressed Data

```
Timestamp,Flow_P101,Pressure_P101
2023-10-15 00:00:00.000,421.5,62.3
2023-10-15 00:02:15.300,421.5,62.4
2023-10-15 00:04:30.100,421.4,62.4
2023-10-15 00:07:00.000,421.5,62.3
2023-10-15 00:10:00.000,421.3,62.2
2023-10-15 00:30:00.000,420.8,62.0
```

Note that timestamps are not evenly spaced. The 20-minute gap between 00:10 and 00:30 means the values did not change enough to trigger compression during that period. The data consumer (the person or program analyzing the data) must handle irregular time spacing in analysis code. If your analysis assumes one data point every minute, it will misinterpret the 20-minute gap as missing data rather than a period of stable operation.

---

## Key Equations Summary

| Quantity | Formula | Units |
|----------|---------|-------|
| Compression Deviation from percent | CompDev = (CompDevPercent * Span) / 100 | engineering units |
| Exception Deviation from percent | ExcDev = (ExcDevPercent * Span) / 100 | engineering units |
| ExcDev recommendation | ExcDev = CompDev / 2 | engineering units |
| Storage per event | Size = timestamp_bytes + value_bytes + status_bytes | bytes |
| Tag count estimate | Tags = point_types * average_points_per_type | count |

---

## Common Mistakes to Avoid

| Mistake | Consequence |
|---------|-------------|
| Requesting compressed data export and assuming timestamps are evenly spaced | Analysis code built for fixed-interval data fails. Linear interpolation assumptions are violated. Time-based aggregations produce incorrect results |
| Opening PI CSV files in Excel by double-clicking | Sub-second timestamp precision lost. Time zone may be auto-converted. Date values may be misinterpreted |
| Setting CompDev to 0 without enabling Compressing = 1 | Compression is not applied. Compressing = 0 (off) is not equivalent to Compressing = 1 with CompDev = 0 |
| Using same exception and compression settings for all tags | Fast-changing tags (flow, pressure) need tighter settings. Slow-changing tags (tank level, temperature) tolerate wider settings. Instrument precision varies by sensor type |
| Not setting ExcMax or CompMax | If process value stays within deadband indefinitely, no data is ever sent or archived. The tag goes silent. Max values force periodic updates |
| Assuming PI AF replaces PI Data Archive tags | AF references PI Data Archive tags. AF is like a card catalog in a library — it points to where the books are. Deleting the PI tag breaks AF references. AF does not store time-series data |
| Using PICompDat for first-time trending without understanding compression effect | Trends appear jagged with flat segments because compression removes intermediate values. PISampDat gives smoother trends for visualization |
| Not accounting for PI Buffer Subsystem during network outages | Buffered data may arrive out of order when the network reconnects. Out-of-order data bypasses compression. Archive may show data spikes or sudden jumps when buffer reconnects |
| Hard-coding PI Point IDs in external applications | PI Point IDs are unique per server and can change if tags are migrated between servers. Always reference tags by name and resolve WebIDs via API at runtime. A WebID is a unique identifier within the PI Web API that the system generates dynamically |
