# Motor Electrical Signature Analysis (ESA / MCSA)

## 1. ESA vs MCSA - Definitions

Electrical Signature Analysis (ESA) and Motor Current Signature Analysis (MCSA) are related but distinct techniques. ESA measures both voltage and current. MCSA analyzes only the current signal. Both are used to detect faults in electric motors without taking them apart or stopping them.

| Technique | Measurements | Scope |
|-----------|-------------|-------|
| Motor Circuit Analysis (MCA) | Offline impedance, insulation resistance, surge test | Motor as isolated component, tested when not running |
| Motor Current Signature Analysis (MCSA) | Online current waveform only | Electrical and mechanical faults detectable via current modulation. Does not measure voltage |
| Electrical Signature Analysis (ESA) | Online voltage and current simultaneously | Full system: power quality, motor electrical health, drivetrain mechanical health, load conditions |

ESA measures the broadband frequency content of voltage and the corresponding current response. Broadband means across a wide range of frequencies, not just the main 50 or 60 Hz supply frequency. Electrical issues manifest through impedance and field distortions. Mechanical issues appear through airgap and reluctance distortions. Reluctance is the magnetic resistance of the airgap — when the gap changes due to mechanical problems, the magnetic field distorts. In practice these are interlinked: a mechanical problem such as uneven airgap leads to reluctance distortions which cause field distortions that appear as electrical anomalies.

### Historical Origin

MCSA was developed in 1985 at Oak Ridge National Laboratory to non-intrusively monitor motor-operated valves in nuclear power plants. Non-intrusive means the sensors are installed at a safe distance (in the electrical cabinet), not on the equipment itself. ESA evolved from MCSA in the 1990s by adding voltage and power monitoring, expanding to pumps, compressors, and other rotating equipment.

---

## 2. Fundamental Principle

ESA and MCSA operate on the principle that any fault in the motor or driven equipment modulates the airgap magnetic field. "Modulates" means the fault causes small fluctuations (ripples) in the magnetic field as the motor rotates. This modulation appears as sideband frequencies around the fundamental supply frequency in the stator current spectrum. Sideband frequencies are additional frequency peaks that appear next to the main 50 or 60 Hz peak in the frequency plot — think of them as echoes of the fault in the electrical signal.

The Fast Fourier Transform (FFT) converts the time-domain current signal into the frequency domain. Time-domain means the signal plotted as current vs. time. Frequency domain means the signal plotted as amplitude vs. frequency. The FFT is a mathematical algorithm that performs this conversion, revealing hidden frequency patterns that are invisible in the raw time plot.

### Signal Chain

| Stage | Description |
|-------|-------------|
| Sensor | Current clamps, Rogowski coils, or CTs (Current Transformers) installed in the Motor Control Cabinet (MCC — the metal enclosure housing the motor's circuit breaker, contactor, and overload protection). Voltage probes connected directly for low voltage (up to 1 kV) or via measurement transformers for high voltage (above 1 kV). 1 kV = 1000 volts |
| Data acquisition | Analog-to-digital converter (ADC — a device that converts real-world analog signals into digital numbers a computer can process) with sufficient sampling rate and anti-aliasing filter |
| Signal processing | FFT, spectral analysis, power quality analysis |
| Interpretation | Comparison of frequency spectrum against baseline. Baseline means a reference measurement taken when the motor was known to be healthy. Identification of fault-specific sidebands |
| Diagnosis | Classification of fault type, severity estimation, remaining useful life projection |

---

## 3. Fault-Specific Frequency Patterns

Each fault type produces characteristic frequency components in the current spectrum. These frequencies are like fingerprints — each fault has a unique pattern that can be identified.

### Broken Rotor Bars

Rotor bars are conducting bars embedded in the rotor (the rotating part of the motor). In an induction motor, current flows through these bars to create the magnetic field that drives rotation. A broken bar reduces the motor's ability to produce torque.

| Parameter | Detail |
|-----------|--------|
| Sideband frequencies | f_sb = f_line * (1 +/- 2 * s) where f_line is supply frequency (typically 50 or 60 Hz) and s is slip |
| Frequency spacing | 2 * s * f_line (pole pass frequency F_p) |
| For 50 Hz motor with 2% slip | Sidebands at 48 Hz and 52 Hz |
| Amplitude indicator | Ratio of sideband amplitude to fundamental amplitude. Single broken bar produces sideband approximately 40-45 dB below fundamental. Decibels (dB) is a logarithmic scale — 40 dB below means the sideband is 100 times smaller in amplitude than the fundamental |
| Severity progression | As crack propagates (grows), sideband amplitude increases. Frequency pattern shifts if bars break asymmetrically |

The lower sideband (1 - 2s) * f_line and upper sideband (1 + 2s) * f_line appear around the fundamental. A broken rotor bar causes an asymmetry in rotor resistance (one side of the rotor conducts differently than the other), which modulates the stator current at twice slip frequency.

**What is slip?** In an induction motor, the rotor always rotates slightly slower than the magnetic field created by the stator. Slip (s) is the difference between the magnetic field speed (synchronous speed) and actual rotor speed, expressed as a fraction. For example, a motor with 2% slip rotates at 98% of synchronous speed. Slip increases under heavier load.

### Air Gap Eccentricity

The air gap is the small physical gap between the rotor (rotating part) and the stator (stationary part). Eccentricity means the gap is not uniform — the rotor is not perfectly centered.

| Type | Frequency | Cause |
|------|-----------|-------|
| Static eccentricity | f_ecc = f_line * (1 +/- k / p) | Rotor centerline offset from stator centerline but rotor rotates around its own center (like a lopsided wheel spinning on its own axle) |
| Dynamic eccentricity | f_ecc = f_line * (1 +/- k * (1 - s) / p) | Rotor centerline offset from stator centerline and rotor rotates around stator center (like a bent shaft wobbling) |
| Mixed eccentricity | Both patterns present | Most common in-field condition |

k is integer (1, 2, 3...), p is number of pole pairs (magnetic north-south pairs in the motor), s is slip. Static eccentricity is caused by stator core ovality (the stator frame is not perfectly round) or incorrect bearing fit. Dynamic eccentricity is caused by bent shaft, bearing wear, or imbalance.

### Bearing Defects

Bearing fault frequencies modulate the current at characteristic frequencies determined by bearing geometry. Bearings have rolling elements (balls or rollers) held in a cage between an inner race (attached to the shaft) and an outer race (attached to the housing). The same defect frequencies used in vibration analysis (BPFO, BPFI, BSF, FTF) appear in the current spectrum as sidebands around the supply frequency.

| Frequency | Formula | Description |
|-----------|---------|-------------|
| BPFO (outer race) | (n_b / 2) * (1 - (B_d / P_d) * cos(phi)) * f_r | Ball pass frequency outer race — how often a rolling element passes a defect on the outer race |
| BPFI (inner race) | (n_b / 2) * (1 + (B_d / P_d) * cos(phi)) * f_r | Ball pass frequency inner race — how often a rolling element passes a defect on the inner race |
| BSF (ball spin) | (P_d / (2 * B_d)) * (1 - (B_d^2 / P_d^2) * cos^2(phi)) * f_r | Ball spin frequency — how fast a defective rolling element spins |
| FTF (cage) | (1 / 2) * (1 - (B_d / P_d) * cos(phi)) * f_r | Fundamental train (cage) frequency — how fast the cage holding the rolling elements rotates |

Where n_b = number of rolling elements, B_d = ball diameter, P_d = pitch diameter (diameter of the circle through the center of all rolling elements), phi = contact angle (angle at which the ball contacts the race), f_r = rotational speed of the shaft in Hz. These mechanical frequencies appear in the current spectrum as sidebands around the supply frequency at f_line +/- k * f_bearing. Detection sensitivity depends on load. Higher load improves signal-to-noise ratio for bearing detection in current.

### Stator Winding Faults

The stator contains copper wire windings that create the magnetic field. Faults in these windings (shorts between turns or to ground) alter the electrical balance of the motor.

| Fault Type | Frequency Signature |
|------------|-------------------|
| Turn-to-turn short | Negative sequence current increase. Negative sequence means current components that rotate opposite to the normal direction. Sidebands at (1 +/- 2k * s) * f_line |
| Phase-to-ground fault | Zero-sequence current. Zero-sequence means current flowing equally in all three phases (instead of normally cancelling out). Harmonics not present in healthy motor |
| Inter-turn short circuit | Third harmonic component in residual current. Negative sequence impedance change |

Turn-to-turn faults are difficult to detect via MCSA alone at incipient (early) stage. ESA using both voltage and current provides better detection via negative sequence impedance calculation.

### Load Fluctuations and Mechanical Faults

Any load-side mechanical fault (cavitation, misalignment, gear damage) that produces torque oscillation (the load alternately speeds up and slows down) modulates the current at the oscillation frequency. In a centrifugal pump, cavitation (formation and collapse of vapor bubbles in the fluid due to low pressure) produces broadband noise in the current power spectral density. Broadband noise means energy spread across many frequencies rather than concentrated at a few specific ones.

---

## 4. Sampling Requirements

Sampling rate is how many times per second the data acquisition system measures the current signal. Higher sampling rates capture more detail but produce more data. Bit depth (resolution) determines how precisely each measurement is recorded — 16-bit can distinguish 65,536 levels, 24-bit can distinguish 16.7 million levels.

| Parameter | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| Sampling rate | 2 kHz (2000 measurements per second) | 5-10 kHz | For rotor bar detection, minimum 2 kHz to capture sidebands. For bearing detection and high-frequency components, 10 kHz or higher |
| Resolution | 16-bit | 24-bit | Higher bit depth improves dynamic range for detecting low-amplitude sidebands |
| Anti-aliasing filter | Required | Hardware filter preferred | Prevents frequency aliasing from corrupting the spectrum |
| Recording duration | 10 seconds | 30-60 seconds | Longer recording improves frequency resolution in FFT. Resolution = 1 / recording_time |
| Nyquist frequency | f_line * 20 | f_line * 50 | Must cover fault frequencies up to at least 20x supply frequency for bearing detection |

**What is aliasing?** If you sample a signal too slowly, high-frequency components can masquerade as lower-frequency ones in the digital data, creating false fault signatures. An anti-aliasing filter removes frequencies above half the sampling rate before digitization to prevent this.

**What is Nyquist frequency?** The Nyquist frequency is half the sampling rate. It is the highest frequency that can be reliably measured. For example, at 10 kHz sampling, the Nyquist frequency is 5 kHz. Any signal above 5 kHz will be aliased.

### Practical Considerations

| Condition | Sampling Strategy |
|-----------|------------------|
| Direct online (DOL) motor (started directly from the power supply, no speed control) | Standard 10 kHz, 16-bit. 60-second recording for 0.017 Hz frequency resolution |
| VFD-fed motor (Variable Frequency Drive controls motor speed) | Higher sampling rate may be needed. VFD switching noise can mask fault signals. Analysis may require filtering to remove VFD artifacts |
| Steady load | Single recording sufficient for baseline |
| Varying load | Multiple recordings or continuous monitoring needed. Load variation modulates fault sideband amplitude |
| High slip motors (motors under heavy load or with high-resistance rotors) | Lower sampling rate acceptable for rotor bar detection because sidebands are wider apart |
| Low slip motors (large motors running near synchronous speed) | Higher frequency resolution needed. Longer recording time required |

---

## 5. ESA vs Vibration Analysis - Comparison

ESA and vibration analysis are complementary, not competing, techniques. Each detects faults the other misses, so using both together gives the most complete picture.

| Parameter | ESA / MCSA | Vibration Analysis |
|-----------|-----------|-------------------|
| Sensor location | Motor control cabinet (MCC), remote from equipment | On bearing housing, directly on equipment |
| Installation | No equipment access needed. Sensors safe from process hazards | Requires physical access to rotating equipment. Sensors exposed to heat, moisture, vibration |
| Hazardous areas | No restriction. MCC is non-hazardous | Requires ATEX-rated (explosion-proof certified) sensors for hazardous zone installation |
| Electrical faults (rotor bar, stator, eccentricity) | Direct detection via current spectrum | Indirect detection via vibration at pole-pass frequencies. Lower sensitivity |
| Bearing faults | Detectable via current modulation (f_line +/- k * f_bearing) | Direct detection via accelerometer on bearing housing. Higher sensitivity for early stage |
| Misalignment | Detectable via load oscillation | Direct detection via 1x and 2x RPM components |
| Cavitation | Detectable via broadband current noise | Detectable via broadband vibration noise |
| Submerged pumps | ESA is the only practical method | Vibration sensors cannot be installed on submerged rotating parts |
| Remote / inaccessible motors | ESA is preferred | Requires sensor installation at the motor |
| Detection timing | Earlier for electrical faults | Earlier for mechanical faults |
| Scalability | High. Multiple motors monitored from one MCC | Moderate. Each motor requires separate sensor installation |

Combining vibration analysis and MCSA delivers 94%+ fault type detection coverage versus 55-65% for either method alone, as reported in industry literature.

---

## 6. ESA vs Thermal Imaging

| Parameter | ESA | Thermal Imaging |
|-----------|-----|----------------|
| Measurement principle | Electrical current and voltage analysis | Surface temperature measurement |
| Installation | Permanent sensors in MCC | Handheld camera or fixed IR (infrared) sensors with line-of-sight to the equipment |
| Detection timing | Early (predictive) | Late (fault already developing significant heat before becoming visible on thermal camera) |
| Fault types detected | Electrical and mechanical | Overheating, insulation breakdown, thermal imbalances |
| Suitability for remote assets | High | Low. Requires direct visual access |
| Scalability | High across assets | Low. Manual inspections required |

---

## 7. ESA Workflow - Practical Procedure

### Phase 1: On-Site Data Collection

| Step | Action |
|------|--------|
| 1 | Visual inspection of equipment for visible defects |
| 2 | Gather nameplate data, drawings, maintenance history |
| 3 | Brief operator on procedure, confirm process conditions are stable |
| 4 | Install current clamps and voltage probes in MCC |
| 5 | Record data at stable operating point (30-60 seconds minimum) |
| 6 | Optionally record at multiple load conditions |
| 7 | Validate data quality immediately (check for clipping — waveform hitting the maximum measurable level, which distorts the signal; noise; and saturation — when the sensor is overloaded) |

### Phase 2: Analysis

| Step | Action |
|------|--------|
| 1 | Time-waveform analysis to detect anomalies, DC offset (constant shift in the signal), clipping |
| 2 | Power quality analysis: crest factor (ratio of peak to RMS value), form factor, RMS (Root Mean Square — the effective value of an AC signal), power, THD (Total Harmonic Distortion — how much the waveform deviates from a pure sine wave), power factor |
| 3 | Detailed spectral analysis with FFT and optional advanced transforms |
| 4 | Compare against baseline measurement at identical operating conditions |
| 5 | Identify sideband frequencies matching known fault patterns |
| 6 | Trend characteristic frequencies across multiple measurement campaigns |

### Phase 3: Diagnosis and Reporting

| Step | Action |
|------|--------|
| 1 | Classify fault type based on frequency pattern |
| 2 | Estimate severity based on sideband amplitude relative to fundamental |
| 3 | Estimate remaining useful life when P-F data is available. P-F interval is the time between when a potential fault (Point P) first becomes detectable and when it becomes a functional failure (Point F) |
| 4 | Merge with FMECA (Failure Mode, Effects, and Criticality Analysis — a systematic method for ranking asset failure modes by risk) for criticality ranking |
| 5 | Report findings to maintenance team with recommended actions |
| 6 | Confirm diagnosis during subsequent inspection or repair |

---

## 8. Limitations and Challenges

| Limitation | Description |
|------------|-------------|
| Varying load conditions | Sideband amplitude changes with load. Low load reduces signal-to-noise ratio for rotor bar and bearing detection. Load variation can mask or mimic fault signatures |
| VFD-fed motors | VFD switching noise injects harmonics (integer multiples of the switching frequency) into the current spectrum. Fault sidebands may be masked. Analysis algorithms must filter or compensate for VFD artifacts |
| Low signal-to-noise ratio | Early-stage faults produce very small sideband amplitudes. Detection requires high-resolution sampling, long recording times, and advanced signal processing (wavelet transform — analyzing the signal at multiple frequency scales simultaneously; autoregressive modeling — predicting future signal behavior based on past patterns) |
| Multiple faults | Multiple simultaneous faults produce overlapping frequency patterns. Separating individual fault contributions requires multi-dimensional analysis |
| Baseline requirement | Trend-based detection requires a reliable baseline measurement at the same operating conditions. Baseline must be captured when the motor is confirmed healthy |
| Transformer effects | Motors fed through long cables or step-down transformers (which reduce voltage) attenuate (weaken) and distort the current signal. ESA sensors should be as close to the motor terminals as practical |
| Slip estimation accuracy | Rotor bar sideband frequencies depend on slip. Inaccurate slip estimation causes incorrect frequency identification. Slip varies with load and temperature |
| Bearing detection sensitivity | Bearing fault detection via current is less sensitive than vibration analysis. Load must be above 50% for reliable bearing detection via current |

---

## Key Equations Summary

| Quantity | Formula | Units |
|----------|---------|-------|
| Broken rotor bar sidebands | f_sb = f_line * (1 +/- 2 * s) | Hz |
| Pole pass frequency | F_p = 2 * s * f_line | Hz |
| Static eccentricity frequency | f_ecc = f_line * (1 +/- k / p) | Hz |
| Dynamic eccentricity frequency | f_ecc = f_line * (1 +/- k * (1 - s) / p) | Hz |
| Bearing BPFO (outer race) | BPFO = (n_b / 2) * (1 - (B_d / P_d) * cos(phi)) * f_r | Hz |
| Bearing BPFI (inner race) | BPFI = (n_b / 2) * (1 + (B_d / P_d) * cos(phi)) * f_r | Hz |
| Bearing BSF (ball spin) | BSF = (P_d / (2 * B_d)) * (1 - (B_d^2 / P_d^2) * cos^2(phi)) * f_r | Hz |
| Bearing FTF (cage) | FTF = (1 / 2) * (1 - (B_d / P_d) * cos(phi)) * f_r | Hz |
| Negative sequence current | I_neg = (I_a + a^2 * I_b + a * I_c) / 3 where a = e^(j * 2 * pi / 3). This is a complex rotation operator that shifts phases by 120 degrees | A |
| Voltage unbalance (NEMA) | V_unbal = 100 * max_deviation_from_avg / avg_voltage | percent |
| ESA sideband amplitude ratio | Amp_ratio = 20 * log10(A_sideband / A_fundamental). The factor 20 converts the ratio to decibels | dB |
| Frequency resolution in FFT | df = 1 / T_recording. Longer recording time gives finer resolution | Hz |
| Nyquist frequency | f_Nyquist = f_sampling / 2. This is the highest frequency that can be measured without aliasing | Hz |

---

## Common Mistakes to Avoid

| Mistake | Consequence |
|---------|-------------|
| Using MCSA alone without voltage measurement for comprehensive diagnosis | Cannot distinguish between supply-side issues (voltage imbalance, harmonics) and motor-side problems (rotor bar, stator faults). Both produce current sidebands |
| Setting sampling rate too low for bearing detection | Bearing defect frequencies in current are modulated around supply frequency. Low sampling rate limits Nyquist frequency, missing high-frequency bearing sidebands |
| Recording insufficient duration for frequency resolution | Short recording produces wide FFT bins. Rotor bar sidebands close to fundamental are not resolvable. Resolution = 1 / recording_time. A 10-second recording gives 0.1 Hz resolution — meaning two frequencies must be at least 0.1 Hz apart to be distinguished |
| Not collecting baseline at same load condition | Load changes shift slip frequency, alter fault sideband amplitudes, change current magnitude. Comparison against baseline at different load produces false positives or missed detections |
| Assuming ESA detects all faults vibration can detect | ESA detects electrical faults earlier but bearing detection sensitivity is lower. Vibration analysis is more sensitive for early stage bearing faults |
| Installing current clamps on energized MCC without verifying CT ratings | Current transformer saturation (magnetic overload of the CT core) above rated current clips the waveform, introducing harmonics that mimic fault signatures |
| Not using anti-aliasing filter | High-frequency noise above Nyquist frequency folds back into the analysis band, creating false frequency peaks indistinguishable from real fault signatures. This folded noise appears at unexpected frequencies and can be mistaken for actual faults |
| Assuming digital output from VFD represents actual motor current | VFD output may include switching artifacts and filtering. Measure actual motor current with external CT at motor terminals or output side of VFD |
| Interpreting frequency components without slip verification | Broken rotor bar sideband frequency depends on slip. Estimating slip from nameplate RPM is inaccurate under load because nameplate RPM is measured at full load only. Slip must be measured during the recording |
