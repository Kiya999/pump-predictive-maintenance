# Synthetic Historian Data - Validation Results

Key observations for failed assets:

- P-0100 (bearing) -- Vibration surges, loss of U-shape (flow-vibration correlation flips from -0.7 to +0.2), temperature drifts.
- P-0300 (cavitation) -- dP spikes, flow-vibration correlation weakens (-0.7 to -0.3), vibration increases at low flows.
- P-0500 (insulation) -- Temperature drift, power climb, flow-power correlation drops (0.98 to 0.75).
- All other assets remain healthy (U-shaped vibration vs flow, flow-power correlation > 0.97).

---

### P-0100 (NK 32-125, 2.5 kW) -- Bearing Failure

<img src="validation/P-0100_timeseries.png" width="180"> <img src="validation/P-0100_pump_curve.png" width="180"> <img src="validation/P-0100_correlation.png" width="180"> <img src="validation/P-0100_profiles.png" width="180"> <img src="validation/P-0100_weekly.png" width="180">

Observation: Vibration increases to approximately 0.37 mm/s, losing the healthy U-shape (vibration vs flow becomes monotonic). Flow-vibration correlation shifts from strong negative (-0.71) to weak positive (+0.16). Temperature drifts upward (max 72.6 degrees C).

---

### P-0200 (NK 40-160, 7 kW) -- Healthy

<img src="validation/P-0200_timeseries.png" width="180"> <img src="validation/P-0200_pump_curve.png" width="180"> <img src="validation/P-0200_correlation.png" width="180"> <img src="validation/P-0200_profiles.png" width="180"> <img src="validation/P-0200_weekly.png" width="180">

Observation: Normal U-shaped vibration, flow-power correlation approximately 0.98, temperatures within 31-51 degrees C.

---

### P-0300 (NK 50-200, 17 kW) -- Cavitation Failure

<img src="validation/P-0300_timeseries.png" width="180"> <img src="validation/P-0300_pump_curve.png" width="180"> <img src="validation/P-0300_correlation.png" width="180"> <img src="validation/P-0300_profiles.png" width="180"> <img src="validation/P-0300_weekly.png" width="180">

Observation: Differential pressure shows random spikes (up to 0.3 bar). Flow-vibration correlation weakens from -0.71 to -0.27; vibration profile becomes nearly monotonic decreasing (higher at low flows). Flow noise increases.

---

### P-0400 (NK 65-250, 42 kW) -- Healthy

<img src="validation/P-0400_timeseries.png" width="180"> <img src="validation/P-0400_pump_curve.png" width="180"> <img src="validation/P-0400_correlation.png" width="180"> <img src="validation/P-0400_profiles.png" width="180"> <img src="validation/P-0400_weekly.png" width="180">

Observation: All signals exhibit standard pump behaviour. U-shaped vibration, flow-power correlation approximately 0.98.

---

### P-0500 (NK 80-250, 75 kW) -- Insulation Failure

<img src="validation/P-0500_timeseries.png" width="180"> <img src="validation/P-0500_pump_curve.png" width="180"> <img src="validation/P-0500_correlation.png" width="180"> <img src="validation/P-0500_profiles.png" width="180"> <img src="validation/P-0500_weekly.png" width="180">

Observation: Motor temperature drifts up to 65.9 degrees C (compared to approximately 55 degrees C in healthy state). Power draw increases (approximately 98 kW max). Flow-power correlation drops to 0.75 (power no longer linear with flow). Vibration unchanged.

---

### P-0600 (NK 80-315, 110 kW) -- Healthy

<img src="validation/P-0600_timeseries.png" width="180"> <img src="validation/P-0600_pump_curve.png" width="180"> <img src="validation/P-0600_correlation.png" width="180"> <img src="validation/P-0600_profiles.png" width="180"> <img src="validation/P-0600_weekly.png" width="180">

Observation: Normal patterns -- flow-power correlation approximately 0.98, vibration minimum near BEP.

---

### P-0700 (NK 100-200, 8 kW) -- Healthy (unit mismatch: pressures in kPa)

<img src="validation/P-0700_timeseries.png" width="180"> <img src="validation/P-0700_pump_curve.png" width="180"> <img src="validation/P-0700_correlation.png" width="180"> <img src="validation/P-0700_profiles.png" width="180"> <img src="validation/P-0700_weekly.png" width="180">

Observation: Values appear 100 times higher due to kPa/bar confusion. Correlations remain valid; flow-power correlation approximately 0.98.

---

### P-0800 (NK 100-250, 14 kW) -- Healthy

<img src="validation/P-0800_timeseries.png" width="180"> <img src="validation/P-0800_pump_curve.png" width="180"> <img src="validation/P-0800_correlation.png" width="180"> <img src="validation/P-0800_profiles.png" width="180"> <img src="validation/P-0800_weekly.png" width="180">

Observation: Standard behaviour -- U-shaped vibration (minimum at approximately 0.9 times nominal flow), flow-power correlation approximately 0.98.

---

### P-0900 (NK 125-315, 24 kW) -- Healthy

<img src="validation/P-0900_timeseries.png" width="180"> <img src="validation/P-0900_pump_curve.png" width="180"> <img src="validation/P-0900_correlation.png" width="180"> <img src="validation/P-0900_profiles.png" width="180"> <img src="validation/P-0900_weekly.png" width="180">

Observation: Healthy pump; correlations match expected values.

---

### P-1000 (NK 150-400, 85 kW) -- Healthy

<img src="validation/P-1000_timeseries.png" width="180"> <img src="validation/P-1000_pump_curve.png" width="180"> <img src="validation/P-1000_correlation.png" width="180"> <img src="validation/P-1000_profiles.png" width="180"> <img src="validation/P-1000_weekly.png" width="180">

Observation: Largest pump; all signals nominal, flow-power correlation > 0.98.