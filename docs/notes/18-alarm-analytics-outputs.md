# Alarm Analytics Outputs

---

## 1. Purpose

The alarm analytics module processes all alarm events from the database and produces 6 summary CSVs. These outputs support the dashboard panels and form the basis for root cause investigation of asset health degradation.

---

## 2. Output files

File | Purpose | Key insight
--- | --- | ---
alarm_rate_daily.csv | Daily alarm frequency per asset | Detects if daily count exceeds ISA-18.2 target (144/day indicates alarm noise)
alarm_clusters.csv | Groups of co-occurring alarms | Identifies correlated failures within 30-minute windows
alarm_stale_events.csv | Alarms that remain unresolved | Flags maintenance process breakdowns
alarm_chattering_events.csv | Rapid repeated activations | Indicates sensor instability or marginal threshold crossings
alarm_avg_time_to_ack.csv | Response time per asset | Measures operational readiness
alarm_frequency_top10.csv | Most common alarm tags | Reveals systematic weak points across the fleet

---

## 3. Key definitions

Metric | Meaning
--- | ---
chattering | More than 3 activations of the same alarm within 5 minutes
cluster | Two or more distinct alarms on the same asset within 30 minutes
stale | Alarm active longer than 24 hours or never cleared since activation
exceeds_isa_target | Daily alarm count exceeds 144 events

---

## 4. Interpretation

Row counts provide a baseline snapshot for the 10-asset, 365-day dataset:

- alarm_rate_daily: One row per asset-date combination (sparse matrix, most days have few alarms)
- alarm_clusters: Thousands of clusters indicate frequent multi-alarm episodes
- alarm_stale_events: Few rows is healthy; many rows indicate maintenance lag
- alarm_chattering_events: Presence confirms sensor interference or control tuning issues
- alarm_avg_time_to_ack: Values near 0.04 hours reflect operator response
- alarm_frequency_top10: Dominated by motor temperature and vibration alarms

---

## 5. Usage in dashboard

Panel | Consumes
--- | ---
Alarm Analysis | alarm_rate_daily, alarm_frequency_top10, alarm_stale_events
Correlated Events | alarm_clusters, alarm_chattering_events
SLA Metrics | alarm_avg_time_to_ack

---
