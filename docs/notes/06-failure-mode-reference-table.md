# Failure Mode Reference Table

## Table 

| Failure Mode | Component Affected | Category | Typical Precursor Signals | Estimated P-F Lead Time Range | Historian Tag Types That Could Detect It | ESA Detectability | Data Quality Required |
|---|---|---|---|---|---|---|---|
| Bearing wear (rolling element) | Bearing, shaft, seal | Mechanical | Vibration defect frequencies (BPFI, BPFO), temperature rise 3-10 C above baseline, ultrasound 30-40 kHz, oil analysis wear particles > 50 ppm | 2 to 10 weeks | Vibration velocity (mm/s rms), bearing temperature (C), oil particle count, ultrasound dB level | Partial (indirect via load variation) | High: 1 kHz+ sampling for vibration envelope. Medium for temperature and oil |
| Bearing wear (sleeve / journal) | Bearing babbit, shaft journal | Mechanical | Oil temperature rise 2-5 C, vibration at 1x running speed in radial direction, oil analysis showing tin/lead particles, increased oil consumption | Weeks to months | Oil temperature (C), vibration velocity (mm/s rms), oil pressure (kPa), oil sample lab results | No | Medium: routine vibration at 1x RPM. Medium for oil analysis |
| Mechanical seal failure | Seal faces, elastomer, gland | Mechanical | Visible weepage or mist at gland, seal housing temperature rise, high-frequency vibration at 2x to 10x running speed, reduced seal flush flow | Weeks to months | Seal flush flow rate (gpm or L/min), seal housing temperature (C), vibration velocity (mm/s rms), leak detection (yes/no) | No | High for seal flush flow and temperature. Medium for visual leak detection |
| Shaft misalignment | Coupling, bearing, mechanical seal | Mechanical | Vibration at 1x and 2x running speed dominant in radial direction, high axial vibration at 1x running speed, coupling wear pattern uneven, bearing temperature elevated one side | Weeks to months | Vibration velocity (mm/s rms) at 1x and 2x RPM, bearing temperature (C), coupling inspection (visual), motor current (A) | Partial (indirect via load oscillation at 2x RPM) | High: vibration spectrum analysis with 1x and 2x RPM resolution. Medium for temperature |
| Impeller erosion | Impeller vanes, volute lip, wear rings | Mechanical | Performance degradation: head and flow decrease gradually; increased vibration as impeller balance is disturbed; vane leading edges rounded; surface roughness increases | Months to years | Flow rate (m3/h), discharge pressure (kPa), motor current (A), vibration velocity (mm/s rms), efficiency (percent) | No | Medium: monthly trending of flow, head, and power. High for periodic efficiency calculation and vibration |
| Operating far from BEP | Bearing, seal, impeller, shaft | Hydraulic and mechanical | Bearing temperature 3-10 C above baseline, vibration increase 2-4x, shortened seal life 60-80%, motor current higher than expected for given flow | N/A (accelerates all other failure modes, no unique P-F interval) | Flow rate (m3/h), motor current (A), bearing temperature (C), vibration velocity (mm/s rms), efficiency (percent) | Yes (efficiency drop detectable from current and power signatures) | Medium: flow, head, power trending. High for vibration when flow deviates from BEP |
| Fouling and scaling | Impeller, volute, wear rings | Hydraulic | Motor current increases at same flow, head drops 2-5% from baseline at BEP flow, vibration increases if deposits cause imbalance | Months to years | Motor current (A), flow rate (m3/h), discharge pressure (kPa), efficiency (percent), pump vibration (mm/s rms) | Partial (motor current increase detects it, but cannot distinguish from other causes of increased load) | Medium: daily trending of flow, head, and power. High for efficiency calculation |
| Cavitation | Impeller, casing, wear rings | Hydraulic | Crackling sound, broadband random vibration, ultrasound signature 30-40 kHz, head drop 5-15%, discharge pressure fluctuation | Weeks to months (days if severe) | Discharge pressure (kPa), suction pressure (kPa), flow rate (m3/h), ultrasound dB level, vibration velocity (mm/s rms) | Yes (broadband noise in current PSD) | High: ultrasound > 20 kHz or vibration > 10 kHz. Medium for pressure trend |
| Recirculation (low flow) | Impeller eye, wear rings, shaft | Hydraulic | Surging flow and pressure, intermittent low-frequency pulsation, increased radial vibration at low flow, premature impeller damage on pressure side | Weeks to months | Flow rate (m3/h), discharge pressure (kPa), motor current (A), vibration velocity (mm/s rms) | Partial (detectable via flow and current fluctuation patterns) | Medium: flow and pressure at 1 second or faster. High for vibration |
| Air entrainment | Impeller, bearings, seal | Hydraulic | Random broadband vibration NOT responding to discharge throttling, erratic flow and pressure, rumbling noise, head loss | Immediate damage onset; weeks to functional failure | Flow rate (m3/h), discharge pressure (kPa), suction pressure (kPa), vibration velocity (mm/s rms), motor current (A) | Yes (current signature shows random fluctuations) | High: fast sampling (10 Hz+) for flow and pressure to catch erratic behavior |
| Stator insulation degradation | Motor winding, core | Electrical | Decreasing insulation resistance trend, PI dropping below 2.0, increasing partial discharge activity, tan delta trending upward | Months to years (hours if surge event) | Winding temperature (C), insulation resistance (Mohm), polarization index (dimensionless), partial discharge (pC), motor current (A) | Yes (partial discharge pulses modulate current signature) | High for PD and IR tests (periodic). High for online current if PD measurement needed |
| Rotor bar cracking | Rotor cage, end ring | Electrical | MCSA sideband frequencies at (1 +/- 2s) * f, torque pulsation at slip frequency, vibration at 2 * slip frequency sidebands, increased motor casing temperature | Weeks to months | Motor current (A) at high sampling rate, motor speed (rpm), motor casing temperature (C), vibration velocity (mm/s rms) | Yes (direct detection via MCSA sidebands) | High: current sampling at 2 kHz+ for MCSA analysis. Medium for temperature |
| Winding faults (turn-to-turn, phase-to-ground) | Stator winding, slot insulation, end turns | Electrical | High-frequency current pulses detected by HFCT, neutral current zero-sequence components, negative sequence current increase, PD patterns, increased vibration localized to end-winding region | Months to years (hours if surge event) | Motor current (A) at high sampling rate, neutral current (A), partial discharge (pC), winding temperature (C), vibration velocity (mm/s rms) | Yes (negative sequence current and zero-sequence components detectable in ESA) | High: high-frequency current sampling for HFCT. Medium for vibration and temperature |
| Voltage unbalance | Motor winding, rotor | Electrical | Elevated motor temperature at rated load, audible hum at 2x line frequency, reduced torque capability, unbalanced phase currents | Months to years (gradual thermal degradation) | Phase voltages (V), phase currents (A), motor temperature (C), power factor (dimensionless) | Yes (identifiable via negative sequence current component) | Medium: phase voltage and current at 1 second intervals. High for detailed harmonics |

---

## Key Equations Summary

| Quantity | Formula | Units |
|----------|---------|-------|
| Bearing defect frequency BPFO (outer race) | BPFO = (n_b / 2) * (1 - (B_d / P_d) * cos(phi)) * f_s | Hz |
| Bearing defect frequency BPFI (inner race) | BPFI = (n_b / 2) * (1 + (B_d / P_d) * cos(phi)) * f_s | Hz |
| MCSA sideband frequency | f_sb = f_line * (1 +/- 2 * s) | Hz |
| Voltage unbalance (NEMA) | V_unbal = 100 * max_deviation_from_avg / avg_voltage | percent |
| Insulation life factor | Life_factor = 0.5 ^ ((T_actual - T_rated) / 10) | dimensionless |
| Preferred Operating Region | POR = 0.70 * Q_BEP to 1.20 * Q_BEP | m3/h or gpm |
| NPSH margin | NPSH_margin = NPSHa - NPSHr | m |
| Polarization index | PI = IR_10min / IR_1min | dimensionless |
| Erosion rate (comparative) | E ~ V^n (n = 2 to 3) | dimensionless |
| Minimum continuous stable flow | Q_min = 0.20 * Q_BEP to 0.30 * Q_BEP | m3/h or gpm |
| Current unbalance factor (approx.) | I_unbal = 6 to 10 * V_unbal | percent |
| Frequency resolution in FFT | df = 1 / T_recording | Hz |
| Nyquist frequency | f_Nyquist = f_sampling / 2 | Hz |

---

## Common Mistakes to Avoid

| Mistake | Consequence |
|---------|-------------|
| Using the same P-F interval for all instances of the same failure mode | P-F interval varies with speed, load, fluid properties, lubrication condition, and contamination level. Using a fixed number leads to missed detection or wasted inspection |
| Labeling a failure mode as ESA-detectable without confirming the signal-to-noise ratio in the specific pump-motor system | ESA detects current signatures but sensitivity depends on motor size, load variation, VFD harmonics, and electrical noise floor |
| Recording historian tags at too low a sampling rate for transient detection | Cavitation, recirculation, and air entrainment require 1 Hz or faster sampling to capture surging and erratic patterns. Hourly averages mask these signals |
| Confusing correlation with causation when multiple precursors appear simultaneously | Bearing temperature rise can be caused by misalignment, lubrication failure, or operating far from BEP. Each requires different corrective action |
| Treating ESA detectability as a substitute for vibration analysis | ESA detects rotor bar faults and electrical faults directly. Mechanical faults (bearing wear, misalignment) are only indirectly detectable via load modulation effects on current |
| Assuming all failure modes in the table apply to every pump installation | Failure mode applicability depends on pump type, fluid properties, operating conditions, motor type, and control strategy. Select relevant modes per asset |
| Operating pump far from BEP assuming bearings can handle it | Radial thrust increases, bearing skidding damage occurs, cage fractures develop |
| Replacing mechanical seals without checking alignment | New seal fails in the same timeframe as old one |
| Ignoring gradual head loss as normal wear | Impeller erosion destroys vane profile and wear rings, efficiency drops below 60% |
| Ignoring 1% voltage unbalance assuming motor can tolerate it | Current unbalance of 6-10% causes I^2R heating; insulation life halves for each 10 C rise |
| Treating all noise as cavitation without performing discharge throttle test | Air entrainment requires different corrective actions but shares symptoms with cavitation |
| Recording insufficient ESA recording duration for frequency resolution | Short recording produces wide FFT bins; rotor bar sidebands close to fundamental are not resolvable. Resolution = 1 / recording_time |

---

## Terminology Reference

### Vibration and Bearing Analysis

| Term | Definition |
|------|------------|
| **BPFI** (Ball Pass Frequency Inner race) | The calculated frequency at which rolling elements pass over a defect on the bearing inner race. It increases as shaft speed increases. Detected in the vibration envelope spectrum |
| **BPFO** (Ball Pass Frequency Outer race) | The calculated frequency at which rolling elements pass over a defect on the bearing outer race. It is typically the most observable bearing defect frequency because the outer race is stationary and the fault impacts the sensor path consistently |
| **1x, 2x running speed** | Vibration at frequencies equal to one time or two times the rotational speed of the shaft. 1x is commonly caused by imbalance or parallel misalignment. 2x is commonly caused by angular misalignment |
| **Envelope spectrum** | A signal processing technique that extracts bearing fault signals by filtering out low-frequency background vibration and demodulating the high-frequency carrier signal. It reveals bearing defect frequencies that would otherwise be masked by balance and alignment components |
| **Radial direction** | Vibration measured perpendicular to the shaft axis. Distinguish from axial direction (parallel to the shaft). Radial vibration readings are the primary indicator for imbalance, misalignment, and bearing wear |
| **Ultrasound dB level** | A measurement of high-frequency acoustic emissions (typically 20-100 kHz) produced by friction, cavitation, or leakage. Ultrasound detects bearing lubrication loss and early cavitation before they appear in lower-frequency vibration readings |

### Pump Hydraulics

| Term | Definition |
|------|------------|
| **Head** | The total pressure rise produced by the pump, expressed as the equivalent height of a fluid column (meters or feet). It is independent of fluid density. A head drop indicates the pump is doing less useful work per unit of fluid |
| **BEP** (Best Efficiency Point) | The flow rate at which the pump achieves its highest hydraulic efficiency. Operating at BEP minimizes radial thrust, vibration, and component wear. The BEP is determined by pump design and is specific to each pump model |
| **NPSH** (Net Positive Suction Head) | NPSHa (available) is the absolute pressure at the pump suction minus the fluid vapor pressure. NPSHr (required) is the minimum suction pressure the pump needs to avoid cavitation. NPSH margin = NPSHa - NPSHr. A positive margin is required for reliable operation |
| **Radial thrust** | The unbalanced hydraulic force acting perpendicular to the shaft, caused by the non-uniform pressure distribution around the impeller. Radial thrust is minimum at BEP and increases significantly when operating away from BEP |
| **Seal flush** | A clean fluid injected at the mechanical seal faces to provide cooling, lubrication, and removal of debris from the seal interface. Reduced flush flow is an early indicator of seal face degradation or blockage in the flush system |

### Electrical and Motor Analysis

| Term | Definition |
|------|------------|
| **Slip (s)** | The difference between synchronous speed (determined by line frequency and number of poles) and actual rotor speed, expressed as a fraction of synchronous speed. Slip increases with load and is required for torque production. It is used to calculate rotor bar fault frequencies |
| **MCSA** (Motor Current Signature Analysis) | A diagnostic technique that analyzes the frequency spectrum of stator current to detect electrical and mechanical faults. It is most effective for rotor bar cracks, eccentricity, and electrical faults. It does not require access to the motor itself, only current measurement at the motor control center |
| **Negative sequence current** | A current component that rotates opposite to the normal positive-sequence magnetic field direction. It is produced by voltage unbalance, phase loss, or winding faults. Even small voltage unbalance (1%) can produce large negative sequence currents (6-10%) due to the motor's low-impedance path |
| **PI** (Polarization Index) | The ratio of insulation resistance measured at 10 minutes to that measured at 1 minute (IR_10min / IR_1min). A PI below 2.0 indicates the presence of moisture, contamination, or insulation degradation. It is more reliable than a single IR reading |
| **Tan delta** (Dissipation Factor) | A measure of dielectric losses in the insulation system. Rising tan delta over time indicates progressive insulation degradation, contamination, or moisture ingress. It is measured during offline testing |
| **Partial discharge (PD)** | Small electrical sparks that occur within insulation voids or at insulation surfaces, which do not fully bridge the gap between conductors. PD erodes insulation over time and precedes complete breakdown. It is detectable online through capacitive couplers or high-frequency current transformers |
| **ESA** (Electrical Signature Analysis) | A technique that measures both voltage and current simultaneously to analyze motor and driven equipment condition. It detects electrical faults (rotor bar, stator, unbalance) directly and mechanical faults (bearing wear, misalignment) indirectly through their effect on current and power |

### Data and Monitoring Concepts

| Term | Definition |
|------|------------|
| **P-F interval** | The time between Point P (when a fault becomes detectable by monitoring) and Point F (when functional failure occurs). Understanding this window determines the required monitoring frequency: longer intervals allow periodic inspection, shorter intervals require continuous monitoring |
| **PSD** (Power Spectral Density) | A signal processing output that shows how power is distributed across frequencies in a signal. Used in ESA to identify fault-specific frequency components in the current spectrum. Broadband noise in the PSD indicates cavitation or air entrainment |
| **Vibration envelope** | A processed vibration signal (also called demodulation or HFD - High Frequency Detection) that amplifies bearing fault signals by removing low-frequency vibration components and rectifying the high-frequency carrier. It is the standard method for rolling element bearing analysis |
| **Historian tag** | A named data stream in a time-series database (such as PI Historian) that stores values for a specific measurement point (temperature, pressure, flow, vibration, current) over time. Historian tags are the data source for trend analysis and predictive maintenance |
