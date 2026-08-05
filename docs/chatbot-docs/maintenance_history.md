# Maintenance Observations

Period: 2025-01-01 to 2026-01-01 (365 days)

## P-0100 (Raw Water Intake)

Model: Grundfos NK 32-125 (2.5 kW)

Total alarms in period: 6449

**Status: Degradation detected (bearing)**

Onset: 2025-04-11 (Day 100)
Duration: 260 days
Alarms during degradation window: 5813

Top alarm signatures:
- P-0100.TI_HI: 2371 occurrences
- P-0100.VI_HI: 2306 occurrences
- P-0100.FI_LO: 196 occurrences
- P-0100.SI_LO: 195 occurrences
- P-0100.PI_LO: 188 occurrences

**Bearing wear observed.** Vibration and temperature signals show characteristic signatures. Estimated progression over 260 days suggests replacement should be planned by Day 360. Increase monitoring frequency and watch for accelerating degradation.

## P-0200 (Chemical Dosing)

Model: Grundfos NK 40-160 (7.0 kW)

Total alarms in period: 2170

**Status: Healthy**

No major issues detected. Baseline performance within spec. Nominal operation: ~44 m³/h at ~7.0 kW.

## P-0300 (Filtration)

Model: Grundfos NK 50-200 (17.0 kW)

Total alarms in period: 2959

**Status: Degradation detected (cavitation)**

Onset: 2025-07-20 (Day 200)
Duration: 60 days
Alarms during degradation window: 1131

Top alarm signatures:
- P-0300.PDI_HI: 265 occurrences
- P-0300.PI_LO: 229 occurrences
- P-0300.PI_HI: 225 occurrences
- P-0300.FI_LO: 224 occurrences
- P-0300.II_HI: 56 occurrences

**Cavitation detected.** Pressure oscillations and flow instability indicate suction conditions are marginal. Over 60 days, condition worsens predictably. Check inlet strainer and suction line restrictions. Plan corrective action (increase inlet pressure or reduce duty point) before Day 260.

## P-0400 (Booster Station A)

Model: Grundfos NK 65-250 (42.0 kW)

Total alarms in period: 2171

**Status: Healthy**

No major issues detected. Baseline performance within spec. Nominal operation: ~135 m³/h at ~42.0 kW.

## P-0500 (Booster Station B)

Model: Grundfos NK 80-250 (75.0 kW)

Total alarms in period: 3878

**Status: Degradation detected (insulation)**

Onset: 2025-05-31 (Day 150)
Duration: 120 days
Alarms during degradation window: 2402

Top alarm signatures:
- P-0500.TI_HI: 1002 occurrences
- P-0500.II_HI: 927 occurrences
- P-0500.PI_LO: 92 occurrences
- P-0500.SI_LO: 86 occurrences
- P-0500.FI_LO: 82 occurrences

**Motor insulation degradation.** Temperature and power draw trending upward at steady flow. Over 120 days this degrades linearly. Motor rewind or replacement should be scheduled by Day 270. Verify cooling conditions and check for thermal cycling stress.

## P-0600 (Wastewater Lift)

Model: Grundfos NK 80-315 (110.0 kW)

Total alarms in period: 2208

**Status: Healthy**

No major issues detected. Baseline performance within spec. Nominal operation: ~230 m³/h at ~110.0 kW.

## P-0700 (Effluent Distribution)

Model: Grundfos NK 100-200 (8.0 kW)

Total alarms in period: 2216

**Status: Healthy**

No major issues detected. Baseline performance within spec. Nominal operation: ~175 m³/h at ~8.0 kW.

## P-0800 (Irrigation Supply)

Model: Grundfos NK 100-250 (14.0 kW)

Total alarms in period: 2213

**Status: Healthy**

No major issues detected. Baseline performance within spec. Nominal operation: ~175 m³/h at ~14.0 kW.

## P-0900 (Backwash System)

Model: Grundfos NK 125-315 (24.0 kW)

Total alarms in period: 2201

**Status: Healthy**

No major issues detected. Baseline performance within spec. Nominal operation: ~220 m³/h at ~24.0 kW.

## P-1000 (High Lift Station)

Model: Grundfos NK 150-400 (85.0 kW)

Total alarms in period: 2196

**Status: Healthy**

No major issues detected. Baseline performance within spec. Nominal operation: ~500 m³/h at ~85.0 kW.


## Common Failure Modes

### Bearing Wear
Vibration increases, temperature rises (delayed ~60% into ramp). Look for VI_HI and TI_HI alarms clustering.

### Cavitation
Pressure spikes, flow becomes erratic. FI_LO and PDI_HI alarms frequent. Suction strainer or inlet line problem.

### Motor Insulation
Temperature creeps up, power consumption increases at constant flow. TI_HI and II_HI alarms rise. Check motor cooling fan and ambient conditions.
