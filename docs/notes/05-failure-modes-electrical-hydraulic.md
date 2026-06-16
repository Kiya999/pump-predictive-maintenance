# Pump Failure Modes - Electrical and Hydraulic

## 1. Motor Insulation Degradation

Insulation degradation in the stator winding is a common electrical failure mode in induction motors driving pumps. The TEAM factors classify the four stress types that attack winding insulation: Thermal, Electrical, Ambient (environmental), and Mechanical.

### TEAM Factors Detail

| Factor | Stress Type | Mechanism |
|--------|-------------|-----------|
| T - Thermal | Heat | Insulation life halves for each 10 C increase above rated temperature. Sources: thermal aging, overloading, voltage variation, voltage unbalance, high ambient temperature, load cycling, poor ventilation, circulating currents |
| E - Electrical | Voltage | Dielectric aging, transient voltages (lightning, capacitor switching, VFD reflected waves), partial discharge. High dv/dt from VFDs stresses turn-to-turn insulation. dv/dt is the rate of voltage change over time; steep voltage pulses from VFDs can cause arcing between adjacent winding turns |
| A - Ambient | Environmental | Moisture, chemical attack, abrasion from dust, contamination by oil or conductive particles |
| M - Mechanical | Physical forces | Coil movement during startup, vibration loosening windings, thermal expansion cycling, slot wedge loosening |

### Observable Precursor Signals

- Insulation resistance (IR) decreasing trend over successive Megger tests. A Megger test applies a high DC voltage to measure resistance between windings and ground
- Polarization index (PI) dropping below 2.0. PI is the ratio of insulation resistance measured at 10 minutes to that at 1 minute; a low PI indicates moisture or contamination
- Partial discharge activity increasing (detectable by online PD monitoring). Partial discharge is a small electrical spark that does not fully bridge the insulation gap; it erodes insulation over time
- Increased leakage current at rated voltage
- Tan delta / dissipation factor trending upward. Tan delta measures the energy lost as heat in the insulation; rising values indicate degradation

### Failure Progression Timeline

| Stage | Condition | Observable Signal |
|-------|-----------|-------------------|
| Early | Insulation embrittlement, micro-cracks in varnish | None detectable by routine testing |
| Point P | PD inception voltage reached, partial discharge begins | Online PD sensor detects discharge pulses |
| Mid | Crack propagation, moisture ingress, tracking paths form. Tracking is the formation of a conductive carbon path across the insulation surface | IR drops, PI declines, tan delta increases |
| Late | Turn-to-turn or phase-to-ground fault | High fault current, protection relay trips |
| Point F | Winding short circuit, motor stops | Overcurrent or differential relay operation |

### Root Causes by Failure Pattern (EASA)

| Failure Pattern | Associated Root Cause |
|-----------------|----------------------|
| All phases overheated symmetrically | Overload, undervoltage, overvoltage |
| Some phases overheated | Single-phasing, unbalanced voltage |
| Ground at slot exit | Vibration, contaminants, abrasion |
| Phase-to-phase short | Voltage surge, contamination |
| Turn-to-turn short | Voltage surge, VFD ringing, manufacturing defect |

---

## 2. Rotor Bar Cracking (Broken Rotor Bars)

Broken rotor bars in squirrel cage induction motors are caused by thermal and mechanical cyclic stress. Rotor bars expand and contract during each start-stop cycle, eventually cracking at the junction with the end ring. A squirrel cage rotor gets its name from the cage-like structure of bars connected by end rings, resembling a hamster wheel. The end rings complete the electrical circuit between bars; a crack at the bar-to-ring junction increases resistance at that point, which produces detectable sidebands in the current spectrum before the bar breaks completely.

### Root Causes

| Cause | Mechanism |
|-------|-----------|
| Frequent starting | High rotor currents during startup produce thermal stress, bar expansion, and fatigue at bar-to-ring joints |
| Thermal overload | Sustained overcurrent heats rotor bars beyond design limits, weakening aluminum or copper |
| Manufacturing defect | Porosity in cast aluminum rotors, poor brazing in fabricated copper rotors |
| Weak end ring design | Insufficient cross-section at end ring causes localized overheating |
| VFD harmonics | Time harmonics induce additional rotor losses, raising bar temperature |

### Observable Precursor Signals

- Motor current signature analysis (MCSA): sideband frequencies at (1 +/- 2s) * f appear in stator current spectrum. Slip s is the difference between synchronous speed and actual rotor speed, expressed as a fraction
- Vibration at 2 * slip frequency sidebands around 1x running speed
- Torque pulsation at slip frequency
- Increased motor casing temperature
- Intermittent speed variations under load

### Failure Progression Timeline

| Stage | Condition | Observable Signal |
|-------|-----------|-------------------|
| Early | Hairline crack at bar-to-end-ring junction | None detectable |
| Point P | Crack propagates, increasing resistance at joint | Sideband amplitude rises above noise floor in MCSA |
| Mid | Bar breaks completely but remains in slot | Clear pole-pass frequency sidebands, vibration increase. Pole-pass frequency (2 * s * f) is the modulation frequency caused by the broken bar passing each magnetic pole |
| Late | Broken bar lifts and arcs against laminations | Sparking, localized heating, rotor core damage |
| Point F | Cage fails, motor cannot produce rated torque | Stall, thermal overload trip, motor stops |

---

## 3. Winding Faults

Winding faults include turn-to-turn shorts, coil-to-coil shorts, phase-to-phase shorts, and phase-to-ground faults. Insulation breakdown typically initiates on the first few turns near the line terminal where voltage stress is highest.

### Root Causes

| Cause | Mechanism |
|-------|-----------|
| Voltage surge | Lightning, capacitor switching, VFD reflected wave (dv/dt). Voltage spikes can exceed 3x rated voltage |
| Contamination | Conductive dust, moisture, oil on winding surfaces creates tracking paths. These paths form conductive bridges across insulation surfaces |
| Loose windings | Coil movement abrades insulation where wires exit slots or at coil ends |
| Partial discharge | Corona discharges erode insulation over time, more prevalent in medium-voltage machines. Corona is a visible glow discharge caused by ionization of air around high-voltage conductors; it produces ozone and nitric acid that attack insulation chemically |
| Thermal cycling | Cyclic expansion and contraction causes relative movement between coils, abrasion at contact points |

### Observable Precursor Signals

- High-frequency current pulses detected by high-frequency current transformers (HFCT) on grounding conductor
- Neutral current analysis revealing zero-sequence components. Zero-sequence current is the portion of current that flows through the neutral when phase currents are unbalanced, indicating a ground fault
- Negative sequence current increase in stator current. Negative sequence current is a component that rotates opposite to the normal magnetic field direction, caused by unbalanced voltages or winding faults
- PD patterns on phase-resolved PD analysis
- Increased vibration localized to end-winding region

---

## 4. Voltage Unbalance Effects

Voltage unbalance is the condition where the three phase-to-phase voltages in a three-phase circuit are not equal. NEMA MG-1 requires motors to operate successfully at rated load with up to 1% voltage unbalance. Even small voltage differences between phases can cause significant current imbalance. Derating means operating the motor at less than its nameplate horsepower to keep temperature within safe limits. NEMA provides derating factors for different voltage unbalance levels.

| Parameter | Value |
|-----------|-------|
| NEMA MG-1 maximum allowed without derating | 1% voltage unbalance |
| Current unbalance factor | 6 to 10 times the voltage unbalance percentage. This amplification occurs because the motor's low-impedance path for negative sequence currents |
| Derating at 5% voltage unbalance | Motor derated to 75% of nameplate horsepower |
| Insulation life impact | Each 10 C temperature rise halves insulation life |

### Mechanism

Voltage unbalance creates negative-sequence currents that produce a counter-rotating magnetic field. This field induces rotor currents at twice line frequency, causing additional I^2R heating concentrated in the rotor bars and end rings. The counter-rotating field acts as a brake, reducing motor efficiency and increasing temperature.

### Observable Precursor Signals

- Motor temperature higher than expected for given load
- Audible hum at twice line frequency (120 Hz for 60 Hz systems)
- Vibration at 2x line frequency
- Reduced motor torque capability

---

## 5. Recirculation at Low Flow (Hydraulic)

Internal recirculation occurs when a centrifugal pump operates below its minimum continuous stable flow. Flow separates at the impeller eye or at the impeller discharge, creating localized vortex zones where fluid recirculates rather than moving forward. The impeller eye is the central inlet area of the impeller where fluid enters axially.

### Root Causes

| Cause | Mechanism |
|-------|-----------|
| Operating below minimum flow | Pump flow below manufacturer-specified MCSF causes suction recirculation at impeller eye. MCSF is the Minimum Continuous Stable Flow below which the pump should not operate continuously |
| Oversized pump for system demand | Pump selected for future capacity runs at low flow most of the time |
| Throttled discharge | Valve partially closed, pump pushed left on curve into recirculation zone |

### Failure Mechanism

Recirculation causes localized low-pressure zones at the impeller eye that induce cavitation-like damage. The recirculating fluid re-enters the impeller with pre-rotation, reducing effective head and causing pressure fluctuations. Pre-rotation means the incoming fluid already has a swirling motion before it enters the impeller vanes.

Differences from cavitation:

| Symptom | Cavitation | Recirculation |
|---------|-----------|---------------|
| Noise | Continuous crackling sound | Intermittent, surging sound |
| Vibration | Broadband random | Low-frequency, flow-dependent |
| NPSH margin | Below required | Usually adequate |
| Effect of throttling discharge | Noise decreases | Noise may increase or shift |

### Observable Precursor Signals

- Surging flow and discharge pressure
- Intermittent low-frequency pulsation
- Increased radial vibration at low flow
- Premature impeller damage at vane inlet on pressure side (opposite of cavitation damage patterns). Cavitation damages the low-pressure (suction) side; recirculation damages the high-pressure (pressure) side

---

## 6. Air Entrainment

Air entrainment occurs when air or gas bubbles enter the pump suction as part of the pumped fluid, unlike cavitation where vapor bubbles form from the fluid itself. The key difference is that entrained air comes from outside the system, while cavitation bubbles form from the fluid boiling at low pressure.

### Root Causes

| Cause | Mechanism |
|-------|-----------|
| Suction vortex | Low submergence in suction tank creates vortex that pulls air into suction pipe. Submergence is the vertical distance from the liquid surface to the suction pipe inlet |
| Leaky suction line | Air drawn through flange gaskets, pipe joints, or valve stem seals at points below atmospheric pressure |
| Free-falling discharge | Discharge flow splashing into a wet well entrains air that recirculates to suction |
| Foaming fluids | Fluids with foaming tendency (paper stock, process chemicals) carry entrained gas |

### Observable Precursor Signals

| Symptom | Characteristic |
|---------|---------------|
| Noise | Similar to cavitation, rumbling, rattling |
| Vibration | Random broadband, does not respond to discharge throttling |
| Flow | Erratic, surging, cycling behavior |
| Head loss | Gradual loss of head as air occupies volume in impeller passages |

### Distinguishing from Cavitation

| Action | Cavitation | Air Entrainment |
|--------|-----------|-----------------|
| Throttle discharge valve | Noise and vibration decrease | Noise and vibration remain same |
| Increase suction pressure | Noise decreases | Noise unchanged |
| Check piping connections | No effect | Leak found and corrected |

---

## 7. Fouling and Scaling

Fouling is the accumulation of deposits on internal pump surfaces. Scaling is a specific type of fouling caused by precipitation of dissolved minerals.

### Root Causes

| Cause | Mechanism |
|-------|-----------|
| Hard water scaling | Calcium carbonate or calcium sulfate precipitation on heated surfaces near wear rings, in volute throat |
| Process deposits | Polymerized substances, biological growth, corrosion products adhering to surfaces |
| Wear ring fouling | Gap closes due to deposits, rotor-to-stator contact, increased power consumption |
| Volute fouling | Rough surfaces increase friction, shift head-capacity curve downward. The head-capacity curve shows the relationship between flow rate and total dynamic head produced by the pump |

### Observable Precursor Signals

- Motor current increases for same flow (higher hydraulic resistance)
- Head decreases at given flow as internal passages narrow
- Discharge pressure oscillations if deposits periodically break loose
- Vibration increases if deposits cause mass imbalance on rotating components

### Failure Progression

| Stage | Condition | Observable Signal |
|-------|-----------|-------------------|
| Early | Thin film on wetted surfaces | None detectable |
| Point P | Measurable reduction in head at BEP flow | Head drops 2-5% from baseline |
| Mid | Wear ring gap reduced by deposits | Motor current increases 5-10%, efficiency drops |
| Late | Deposits break loose, imbalance occurs | Sudden vibration increase, seal leakage |
| Point F | Wear ring binds, seal fails, or impeller seizes | Pump stops, motor overload trip |

---

## 8. Operating Far from BEP

Operation away from the Best Efficiency Point increases radial thrust, vibration, temperature, and accelerates wear in bearings, seals, and impellers. BEP is the flow rate at which the pump achieves its highest efficiency, and it is the pump's design operating point. Radial thrust is the net hydraulic force pushing the shaft sideways; it is lowest at BEP and increases sharply away from it. Shaft deflection is the bending of the shaft under radial thrust, which reduces bearing and seal life.

### Effects by Operating Region

| Region | Flow Range | Effects |
|--------|-----------|---------|
| Left of BEP (low flow) | Below 70% of BEP flow | Recirculation, temperature rise, radial thrust, higher NPSHr, vibration, surging |
| Preferred Operating Region (POR) | 70-120% of BEP flow | Minimum radial thrust, optimal efficiency, longest bearing and seal life |
| Right of BEP (high flow) | Above 120% of BEP flow | Increased NPSHr, cavitation risk, higher shaft deflection, reduced bearing life |

### Quantified Effects

| Parameter | At BEP | At 60% BEP flow | At 120% BEP flow |
|-----------|--------|-----------------|-----------------|
| Radial thrust | Minimum | 3-5x higher | 2-3x higher |
| Efficiency | Maximum | 10-20% lower | 5-10% lower |
| Bearing life | Rated | 50-70% of rated | 60-80% of rated |
| NPSH margin | Designed | Reduced margin | Significantly reduced |
| Vibration level | Baseline | 2-4x baseline | 1.5-3x baseline |

### Hydraulic Institute Guidelines (ANSI/HI 9.6.3)

| Term | Definition |
|------|-----------|
| Preferred Operating Region (POR) | 70% to 120% of BEP flow where vibration is acceptable and efficiency is high |
| Allowable Operating Region (AOR) | Extended range beyond POR where pump can operate for limited duration without immediate failure |

### Observable Precursor Signals

- Increased bearing temperature (3-10 C above baseline)
- Vibration increase, particularly at the non-drive end bearing
- Higher motor current for given flow
- Shortened mechanical seal life

---

## Key Equations Summary

| Quantity | Formula | Units |
|----------|---------|-------|
| Voltage unbalance (NEMA) | V_unbal = 100 * max_deviation_from_avg / avg_voltage | percent |
| Insulation life factor per 10 C | Life_factor = 0.5 ^ ((T_actual - T_rated) / 10) | dimensionless |
| Motor winding I^2R loss | P_loss = I^2 * R | W |
| Current unbalance factor (approx.) | I_unbal = 6 to 10 * V_unbal | percent |
| NEMA voltage unbalance limit | V_unbal_max = 1.0 | percent |
| Insulation resistance minimum (IEEE 43) | IR_min = kV + 1 | Mohm |
| Polarization index | PI = IR_10min / IR_1min | dimensionless |
| MCSA sideband frequency | f_sideband = f_line * (1 +/- 2 * s) | Hz |
| Minimum stable flow (typical range) | Q_min = 0.20 * Q_BEP to 0.30 * Q_BEP | m^3/h or gpm |
| Preferred Operating Region | POR = 0.70 * Q_BEP to 1.20 * Q_BEP | m^3/h or gpm |

---

## Common Mistakes to Avoid

| Mistake | Consequence |
|---------|-------------|
| Ignoring 1% voltage unbalance assuming motor can tolerate it | Current unbalance of 6-10% causes I^2R heating; insulation life halves for each 10 C rise |
| Replacing motors that failed from insulation degradation without investigating root cause | Identical failure will repeat if TEAM factors are unchanged |
| Assuming MCSA is not needed because pump runs continuously | Broken rotor bars develop from thermal cycling during starts, not running hours |
| Treating all noise as cavitation without performing discharge throttle test | Air entrainment requires different corrective actions but shares symptoms with cavitation |
| Operating below minimum flow without recirculation line | Recirculation causes impeller damage and pressure fluctuations that destroy seals and bearings. A recirculation line returns excess flow from the discharge back to the suction to keep the pump above minimum flow |
| Selecting pump with duty point at BEP but ignoring system curve changes | As system conditions change, pump drifts away from BEP into high-wear regions. The system curve describes the relationship between flow and the friction head the pump must overcome; changes in piping, valves, or tank levels shift this curve and move the pump's operating point |
| Ignoring gradual motor current increase over months | Indicates fouling or scaling buildup before it causes seizure |
| Relying only on thermal overload protection for single-phasing | Local windings can overheat even when line currents do not exceed the overload setting. Single-phasing occurs when one phase of the three-phase supply is lost, causing the remaining two phases to carry higher current and overheat unevenly |
