# ISA-18.2 and EEMUA 191 Alarm Management Benchmarks

## 1. Standard Origins and Scope

ISA-18.2 (ANSI/ISA-18.2-2016)
- American National Standard published by the International Society of Automation
- Covers the full alarm management lifecycle (10 phases)
- Applicable to process industries: chemical, refining, oil and gas, power generation, pharmaceutical
- Primary reference in North America
- Basis for international standard IEC 62682

EEMUA 191 (3rd edition, 2013)
- Guide published by the Engineering Equipment and Materials Users Association (UK)
- First document to define quantitative alarm rate targets (1999)
- Applicable to continuous and batch process industries
- Primary reference in Europe and Middle East
- ISA-18.2 adopted its numeric benchmarks with minor adjustments

Relationship between the three standards
- EEMUA 191 defined the quantitative targets first
- ISA-18.2 adopted those targets and added the lifecycle framework
- IEC 62682 harmonizes both into an international standard
- Industry practice uses ISA-18.2 for the process and EEMUA 191 for the numbers

---

## 2. Average Alarm Rate per Operator

| Time Unit | Very Likely Acceptable | Maximum Manageable | Action Required |
|-----------|----------------------|-------------------|-----------------|
| Per day | ~150 | ~300 | >432 |
| Per hour | ~6 | ~12 | >18 |
| Per 10 minutes | ~1 | ~2 | >3 |

Interpretation
- "Very likely acceptable" means the site should target this rate or lower
- "Maximum manageable" means the rate where operator performance degrades
- "Action required" means the alarm system is clearly overloaded
- Rates above 10 per hour consistently trigger mandatory corrective action plans
- These rates assume one operator working one console

---

## 3. Alarm Priority Tiers

Three-tier or four-tier priority systems are used. Four-tier is more common in modern systems.

### Four-Priority System Definitions

| Priority | Label | Target % of Total Alarms | Required Response Time | Consequence of Inaction |
|----------|-------|--------------------------|----------------------|------------------------|
| 1 | Highest | <1% | Seconds | Imminent safety hazard, major environmental release, catastrophic equipment failure |
| 2 | High | ~5% | Minutes | Potential safety issue, equipment damage, process shutdown |
| 3 | Medium | ~15% | Within shift | Process quality or efficiency loss, no immediate safety risk |
| 4 | Low | ~80% | Routine | Maintenance tracking, informational, no operational urgency |

Priority assignment during alarm rationalization considers three factors
- Consequence severity if the operator does not respond
- Available response time before the consequence occurs
- Existence of independent protection layers (other alarms, trips, relief devices)

### Three-Priority System

| Priority | Label | Target % |
|----------|-------|----------|
| 1 | High | ~5% |
| 2 | Medium | ~15% |
| 3 | Low | ~80% |

A site using three tiers typically maps EEMUA 191 benchmarks by treating High as the actionable category and Low as informational.

---

## 4. Problematic Alarm Definitions

### Chattering Alarm

An alarm that repeatedly transitions between alarm state and normal state over a short time period.

| Property | Threshold | Source |
|----------|-----------|--------|
| Activation count | >3 activations | ISA-18.2, EEMUA 191 |
| Time window | Any 5-minute window | Both standards |
| Target | Zero | Both standards |
| Action | Assign owner, create resolution plan, complete within defined timeframe | ISA-18.2 |

Common causes of chattering
- Alarm deadband too narrow for process noise
- Setpoint too close to normal operating range
- Process cycling due to control loop tuning problems
- Instrument signal noise or electrical interference

### Fleeting Alarm

An alarm that activates and clears before the operator can complete the acknowledgment and response cycle.

| Property | Threshold |
|----------|-----------|
| Duration | Typically <30 seconds |
| Target | Zero |
| Impact | Provides no actionable information; adds noise to the alarm system |

Fleeting alarms are detected by computing the time difference between activation and clear for each alarm. Any alarm that consistently clears in under 30 seconds is a candidate for reclassification as a message or for setpoint adjustment.

### Stale Alarm (Standing Alarm)

An alarm that remains continuously active for an extended period.

| Property | Threshold | Source |
|----------|-----------|--------|
| Duration | >24 hours continuously active | ISA-18.2, EEMUA 191 |
| Target count at any time | <5 stale alarms | ISA-18.2 |
| Extended stale threshold | >7 days continuous | Industry practice |

Risks from stale alarms
- Clutter the alarm list and hide new urgent alarms
- Train operators to ignore persistent signals
- Indicate unresolved maintenance issues being masked as alarms
- Increase cognitive load during upset conditions

### Nuisance Alarm

A broad category covering alarms that annunciate excessively, unnecessarily, or do not return to normal after the correct response is taken.

Types of nuisance alarms
- Chattering alarms (frequency-based)
- Fleeting alarms (duration-based)
- Stale alarms (persistence-based)
- Alarms with incorrect setpoints for actual process conditions
- Alarms for conditions the operator cannot influence

Nuisance alarms are the most dangerous category because they train operators to ignore the alarm system. A nuisance alarm is defined by operator behavior: if operators have learned to expect and ignore it, it is a nuisance alarm regardless of its technical classification.

---

## 5. Alarm Flood Criteria

| Metric | Definition | Target | Action Level |
|--------|------------|--------|--------------|
| Flood condition | >=10 alarms in any 10-minute period | <1% of time | >5% of time |
| End of flood | Rate drops below 5 alarms in 10 minutes | Immediate | N/A |
| Maximum alarms in 10-minute period | Peak count during normal operations | <=10 | >10 |
| Hours with >30 alarms | Hours exceeding the flood rate threshold | <1% of hours | >5% of hours |

Flood management procedure
1. Identify the initiating event (first alarm in the sequence)
2. Suppress consequential alarms that provide no additional information
3. Implement state-based alarming to reduce alarm load during known plant states
4. Rationalize alarms that consistently appear in flood sequences

---

## 6. Top 10 Most Frequent Alarms

| Metric | Target | Action Level |
|--------|--------|--------------|
| % of total alarm load from top 10 sources | <1% to 5% | >20% |

Interpretation
- If the top 10 alarm tags account for >20% of all alarms, the site has a nuisance alarm problem
- Each of the top 10 should have an assigned owner and a documented reduction plan
- Target is to redistribute the alarm load so no single tag dominates
- Monitoring this metric monthly tracks progress of rationalization efforts

---

## 7. EEMUA 191 Performance Levels

EEMUA 191 defines five levels based on average alarm rate per 10 minutes and peak alarm rate per 10 minutes.

| Level | Label | Avg Rate (per 10 min) | Peak Rate (per 10 min) | Operator State |
|-------|-------|----------------------|----------------------|----------------|
| 0 | Overloaded | >2 | >1000 | Alarm system overwhelmed; chronic floods; operators cannot distinguish critical from non-critical alarms |
| 1 | Reactive | 1 to 2 | ~100 | Stable during normal operations; floods during process upsets |
| 2 | Stable | <1 | ~10 | Manageable during normal ops and most upsets |
| 3 | Robust | <0.5 | ~5 | Effective during normal operations and moderate upsets |
| 4 | Predictive | <0.1 | ~2 | Proactive; alarms prevented through advanced techniques |

Achieving Level 2 (Stable) is the minimum acceptable target for most process plants. Levels 3 and 4 require continuous improvement programs and advanced techniques such as:
- State-based alarming (alarm configuration changes based on plant operating mode)
- Dynamic alarming (setpoints that adjust with process conditions)
- Alarm shelving (temporary suppression of known nuisance alarms with automatic reinstatement)
- First-out alarming (logical identification of the root cause in a cascade sequence)

---

## 8. Additional EEMUA 191 Metrics

| Metric | Threshold |
|--------|-----------|
| Chattering alarm definition | >3 activations in any 5-minute window |
| Standing alarm definition | Active >24 hours |
| Average alarm rate target | 1 per 10 minutes maximum (target <1) |
| Operator response time expectation | Alarm acknowledgment within 5 minutes |
| Annunciated alarms per shift per operator | <150 |

---

## 9. Key Equations Summary

| Quantity | Formula | Units |
|----------|---------|-------|
| Average alarm rate per 10 min | Total alarms in period / (period in minutes / 10) | alarms per 10 min |
| Average alarm rate per hour | Total alarms in period / (period in hours) | alarms per hour |
| Average alarm rate per day | Total alarms in period / (period in days) | alarms per day |
| % time in flood | (minutes in flood / total minutes) * 100 | percent |
| Top 10 contribution | (alarms from top 10 tags / total alarms) * 100 | percent |
| Chattering detection | count same tag activations in sliding 5-minute window | count per window |
| Stale alarm detection | current time minus activation time | hours |
| Priority distribution | count per priority / total alarms * 100 | percent |
| Flood detection count | count 10-minute windows with >=10 alarms | windows |

---

## 10. Common Mistakes to Avoid

| Mistake | Consequence |
|---------|-------------|
| Treating priority as a variable attribute of each activation | Priority must be fixed per alarm tag; variability undermines rationalization |
| Setting >5% of alarms to Highest priority | Operators cannot distinguish true emergencies; all alarms treated equally |
| Allowing chattering alarms without action plans | Operators learn to ignore alarms |
| Closing stale alarms without root cause investigation | Underlying process or instrument problem remains unresolved |
| Exceeding target alarm rate on paper but accepting it in practice | Operator performance degrades; incident risk increases |
| Using three-tier and four-tier priority systems interchangeably without clear mapping | Confusion during handover and incident investigation |
| Focusing only on average rate while ignoring peak rate | Average may look acceptable but floods still overwhelm operators |
| Not distinguishing between chattering (same tag) and correlated batch (different tags same asset) | Wrong remediation approach: chattering needs deadband fix, correlated batch needs root cause analysis |
