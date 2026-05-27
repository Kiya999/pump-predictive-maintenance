# P-F Curve Concepts

## 1. P-F Curve Definition

Model that charts an asset's condition decline from normal operation to functional failure. The horizontal axis represents time. The vertical axis represents resistance to failure or functional capacity.

Two critical points on the curve:

| Point | Name | Definition |
|-------|------|------------|
| P | Potential Failure | Earliest moment a developing fault can be detected by inspection or monitoring |
| F | Functional Failure | Asset can no longer perform required function to specified performance standard |

Origin: Introduced by Stan Nowlan and Howard Heap in 1978 (United Airlines RCM document). Popularized by John Moubray in RCM2 (Reliability-Centered Maintenance, 2nd Edition).

The P-F curve applies only to failure modes where onset is followed by a detectable warning period. Not all failure modes follow this pattern.

---

## 2. P Point (Potential Failure)

Point P is not where failure initiation occurs. It is where the fault first becomes detectable. The P point depends on the detection technique. Different technologies place P at different locations on the degradation curve.

| Detection Technology | Typical Signal | Position on Degradation Curve |
|---------------------|---------------|-------------------------------|
| Ultrasound | Friction, impacting, turbulence | Earliest |
| Vibration analysis | Bearing defect frequencies, imbalance | Early |
| Oil analysis | Wear particle concentration, viscosity change | Early to mid |
| Thermography | Temperature rise | Mid |
| Motor current signature analysis | Electrical anomalies | Mid |
| Performance monitoring | Flow drop, pressure drop, power increase | Late |
| Visual or smoke | Visible damage | Latest |

Earlier detection produces a longer usable P-F interval. 

---

## 3. F Point (Functional Failure)

Functional failure = asset can no longer meet its performance standard. This is operationally defined, not mechanically defined.

| Asset | Performance Standard | Functional Failure |
|-------|---------------------|-------------------|
| Centrifugal pump | 120 gpm at required head | Delivers 119 gpm |
| Motor | Rated speed at rated torque | Speed drops below requirement |
| Cooling fan | 5000 cfm airflow | Delivers 4500 cfm |

Point F is not catastrophic destruction. It is the point where the user's requirement is no longer met.

---

## 4. P-F Interval

P-F interval = time between P and F. This is the window available for maintenance intervention after detecting a developing fault.

| Failure Mode | Typical P-F Interval | Detection Method at P |
|-------------|---------------------|----------------------|
| Rolling element bearing wear | 2 to 10 weeks | Ultrasound, vibration analysis |
| Rotating imbalance | Weeks to months | Vibration analysis (1x frequency) |
| Shaft misalignment | Weeks to months | Vibration analysis (2x frequency), thermography |
| Pump cavitation | Weeks | Ultrasound, vibration analysis |
| Electrical insulation degradation | Months to years | Partial discharge testing |
| Electrical arc fault | Milliseconds to seconds | Protection relay |

P-F interval varies by failure mode, operating conditions, load, speed, lubrication quality, and asset design.

---

## 5. Inspection Interval Rule (Half-Interval Rule)

Inspection interval must be less than half the P-F interval.

Formula: I_max = P-F_interval / 2

| P-F Interval | Max Safe Inspection Frequency |
|-------------|------------------------------|
| 8 weeks | 4 weeks |
| 6 weeks | 3 weeks |
| 4 weeks | 2 weeks |
| 2 weeks | 1 week |
| 1 week | 3.5 days |
| 1 day | 12 hours |

If inspection interval exceeds P-F interval / 2, a fault can develop between inspections and reach F before the next inspection detects it.

---

## 6. Example 1: Bearing Failure in Centrifugal Pump

Source: Plant Engineering magazine, "Reduce dreaded pump problems or failures with condition monitoring" (2023)

| Parameter | Detail |
|-----------|--------|
| Asset | Centrifugal pump, rolling element bearing |
| Failure mode | Bearing wear (raceway defect from contamination) |
| Signal monitored at P | Vibration analysis (bearing defect frequencies in vibration spectrum) |
| P-F interval | 2 to 10 weeks (depends on speed, load, lubrication) |
| Action triggered at P | Plan and schedule bearing replacement during next planned outage |
| Consequence | Advanced notice allows repair without unplanned downtime |
| Other detection methods | Ultrasound (earliest), thermography (temperature rise), oil analysis (wear metals) |

---

## 7. Example 2: Cavitation in Centrifugal Pump

Source: Plant Engineering magazine, "Reduce dreaded pump problems or failures with condition monitoring" (2023)

| Parameter | Detail |
|-----------|--------|
| Asset | Centrifugal pump operating below minimum flow |
| Failure mode | Cavitation from blocked suction strainer or insufficient NPSH |
| Signal monitored at P | Ultrasound (crackling signature of bubble collapse) |
| P-F interval | Weeks |
| Action triggered at P | Clear suction strainer, increase suction pressure, correct NPSH conditions |
| Secondary indicators | Vibration analysis detects collapsing bubbles before audible |
| Progression | Cavitation erodes impeller -> flow drops -> functional failure |

---

## 8. How P-F Interval Guides Maintenance Strategy

| P-F Interval Length | Strategy Implication | Monitoring Approach |
|--------------------|--------------------|--------------------|
| Very short (ms to hours) | Condition monitoring not applicable | Protection relays, redundancy, redesign, or run-to-failure |
| Short (hours to days) | Periodic inspection impractical | Continuous automated monitoring required |
| Medium (days to weeks) | Periodic inspection viable | Route-based condition monitoring at half-P-F interval |
| Long (weeks to years) | Flexible scheduling | Periodic inspection or annual testing programs |

If P-F interval is too short to act upon, condition monitoring is not applicable. The team must choose redesign, redundancy, or accept the failure.

---

## 9. Effect of Monitoring Frequency

| Monitoring Type | P-F Interval Usable | Risk Profile |
|----------------|-------------------|-------------|
| No monitoring | 0% of P-F interval | Fault undetected until F |
| Periodic inspection at P-F/2 | Up to 50% of P-F interval | Fault always caught with margin |
| Periodic inspection at P-F | 0% of P-F interval | Fault can initiate and reach F between inspections |
| Continuous monitoring | 100% of P-F interval | Earliest detection, maximum planning time |

Continuous monitoring detects P as soon as it occurs, giving the team the full P-F interval regardless of when the fault initiates.

---

## 10. D-I-P-F Curve Extension (Beyond Basic P-F)

The P-F curve was extended by reliability practitioners to address the full asset lifecycle.

| Point | Domain | Focus |
|-------|--------|-------|
| D | Design | Inherent reliability determined at design stage |
| I | Installation | Quality of installation determines actual reliability |
| P | Potential Failure | First detectable sign of failure |
| F | Functional Failure | Performance standard no longer met |

Proactive maintenance (precision installation, correct lubrication, alignment) extends the I-P interval. The I-P region is the only part of the reliability curve where failures can be prevented.

---

## Key Equations Summary

| Quantity | Formula | Units |
|----------|---------|-------|
| Inspection interval | I_max = P-F_interval / 2 | time (weeks, days, hours) |
| Remaining useful life | RUL = P-F_interval - time_since_P | time |
| Detection lead time | Lead = P-F_interval | time |

---

## Common Mistakes to Avoid

| Mistake | Consequence |
|---------|-------------|
| Using inspection interval longer than P-F interval / 2 | Faults missed between inspections |
| Using P-F curve for age-related failures that follow deterministic wear patterns | Curve was designed for random failure onset |
| Treating Point F as catastrophic destruction | Misses opportunity to intervene before secondary damage |
| Using same inspection frequency for all failure modes | Short P-F modes missed, long P-F modes over-inspected |
| Confusing Point P with failure initiation | P is detection point, not the start of damage |
| Applying condition monitoring to failure modes with zero P-F interval | Wasted resources, no reliability gain |
| Setting inspection intervals based on vendor recommendations without verifying P-F interval | Inspection frequency does not match actual failure behavior |

---

## Terminology Reference

### Reliability and Maintenance Concepts

| Term | Definition |
|------|------------|
| **RCM** (Reliability-Centered Maintenance) | A systematic methodology for determining the most effective maintenance strategy for each asset based on its function, failure modes, and consequences of failure. Originated in the airline industry in the 1970s. The P-F curve is a core concept within RCM. RCM2 refers to the second edition of John Moubray's book that popularized the method |
| **Condition monitoring** | The practice of measuring physical parameters (vibration, temperature, current, pressure, oil condition) on operating equipment to detect developing faults before they cause failure. The P-F curve defines the window of opportunity during which condition monitoring is effective. Different monitoring technologies detect faults at different stages along the curve |
| **Protection relay** | An electrical device that monitors parameters such as current, voltage, and frequency, and trips the circuit breaker when values exceed safe thresholds. Protection relays operate in milliseconds and are designed for the shortest P-F intervals where condition monitoring cannot provide useful warning. They are the last line of defense, not a predictive tool |
| **Run-to-failure** | A maintenance strategy where an asset is allowed to operate until it fails, with no proactive intervention. This is appropriate when the P-F interval is too short to act upon, the failure consequences are minor, or the cost of prevention exceeds the cost of repair. It is not the same as neglect; it is a deliberate decision |

### Monitoring Strategies

| Term | Definition |
|------|------------|
| **Periodic inspection** | Data collection at fixed time intervals (daily, weekly, monthly) using portable instruments carried by technicians along a defined route. The inspection interval must be less than half the P-F interval to reliably catch developing faults. Periodic inspection is the most common approach for failure modes with medium-length P-F intervals (days to weeks) |
| **Continuous monitoring** | Permanent sensors installed on the asset that transmit data in real time to a monitoring system. Continuous monitoring detects Point P as soon as it occurs, giving the team the full P-F interval for planning. It is appropriate for failure modes with short P-F intervals (hours to days) or for critical assets where any unplanned downtime is unacceptable |
| **Route-based monitoring** | A periodic inspection approach where a technician follows a predetermined route through the plant, stopping at each asset to collect vibration, temperature, ultrasound, or other measurements using portable instruments. The route is designed to cover all monitored assets within the required inspection interval. This is the most common implementation of periodic condition monitoring in industrial plants |
| **Redundancy** | Having multiple identical assets configured so that if one fails, another automatically takes over its function (e.g., n+1 pump configuration). Redundancy is the appropriate strategy when the P-F interval is too short to act upon and the failure consequences are unacceptable. It does not prevent failures but makes them invisible to the process |

### Failure and Degradation Concepts

| Term | Definition |
|------|------------|
| **Functional capacity** | The asset's ability to perform its required function at a given point in time. On the vertical axis of the P-F curve, functional capacity decreases over time as degradation progresses. Point F is reached when functional capacity drops below the minimum required performance standard, even if the asset is still physically intact and rotating |
| **Secondary damage** | Damage to surrounding components caused by a primary failure that was allowed to progress. For example, a bearing that runs to failure may seize and damage the shaft, then the shaft deflection damages the mechanical seal. A longer P-F interval used for planning maintenance aims to intervene before secondary damage occurs |
| **Age-related failure** | A failure mode where the probability of failure increases with operating time or cycles, following a predictable wear pattern (e.g., erosion of wear rings, contact fatigue in gears). Age-related failures can be managed by time-based replacement. The P-F curve was originally designed for failure modes that are not strongly age-related but develop randomly over time |
| **Random failure onset** | A failure mode where the initiation time is unpredictable and not correlated with operating age. The P-F curve concept was developed specifically for this type of failure: the onset is random, but once initiated, the degradation follows a detectable progression. Rolling element bearing failures, misalignment, and contamination-driven failures are common examples |
| **Deterministic wear pattern** | A predictable, gradual degradation process where the remaining life can be estimated based on operating time and known wear rates (e.g., brake pad wear, pump wear ring erosion). For deterministic patterns, time-based replacement or simple thickness measurements may be more appropriate than P-F curve analysis with condition monitoring |
| **Catastrophic destruction** | Complete, sudden failure of an asset with potential for collateral damage, safety hazards, or environmental release. Point F on the P-F curve is defined as functional failure (unable to meet performance standard), which occurs well before catastrophic destruction in most failure modes. The Common Mistakes section cautions against conflating these two concepts |
| **Inherent reliability** | The maximum reliability level that an asset can achieve under ideal conditions, determined by its design, materials, and manufacturing quality. On the D-I-P-F curve extension, Point D (Design) establishes the inherent reliability. No amount of maintenance can improve reliability beyond the inherent level; maintenance can only preserve it or slow its decay |

---
