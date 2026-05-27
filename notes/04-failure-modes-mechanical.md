# Pump Failure Modes - Mechanical

## 1. Bearing Wear - Rolling Element Bearings

Rolling element bearings (ball bearings, cylindrical roller bearings, angular contact ball bearings) support the shaft in most centrifugal pumps. The front bearing (impeller side) handles radial load. The rear bearing handles combined axial and radial load.

Radial load is force perpendicular to the shaft (from the impeller weight and hydraulic forces), while axial load is force along the shaft (from thrust). Understanding this distinction helps in diagnosing which bearing failed and why.

### Root Causes

| Cause | Mechanism |
|-------|-----------|
| Inadequate lubrication | Oil film breaks down, metal-to-metal contact occurs, friction increases |
| Contamination | Particles enter bearing housing through seals or breathers, cause abrasive wear |
| Misalignment | Parallel or angular misalignment of pump and motor shafts induces uneven loading |
| Excessive load | Operating far from BEP increases radial and axial thrust beyond design limits |
| Fatigue | Cyclic stress initiates subsurface cracks that propagate to spalling. Spalling is the flaking or pitting of bearing surfaces, the most common end-of-life mode for properly lubricated bearings |
| Skidding damage | Lightly loaded rolling elements slide instead of roll, caused by insufficient axial preload. Skidding generates heat and wears flat spots on rollers |

### Progression Timeline

| Stage | Condition | Observable Signal |
|-------|-----------|-------------------|
| Early | Microscopic subsurface fatigue cracks | None detectable by conventional vibration |
| Point P | Spall initiation at raceway or rolling element | Vibration spectrum shows bearing defect frequencies (BPFI, BPFO, BSF, FTF). See Key Equations section for formula definitions |
| Mid | Spall growth, particle generation | Increasing vibration amplitude, temperature rise |
| Late | Cage damage, ring fracture, seizure | High broadband vibration, audible noise, smoking |
| Point F | Bearing cannot rotate freely | Pump stops or severe secondary damage occurs |

### Observable Precursor Signals

- Vibration analysis: characteristic defect frequencies in the envelope spectrum. Envelope spectrum is a processed vibration signal that amplifies bearing fault signals by filtering out low-frequency background vibration
- Temperature rise at bearing housing: 3 to 10 C above baseline
- Oil analysis: increased wear particle count, ferrous particles above 50 ppm indicates active wear
- Ultrasound: high-frequency friction signal at 30 to 40 kHz range precedes vibration elevation

### P-F Lead Time

Typical P-F interval for rolling element bearings in centrifugal pumps is 2 to 10 weeks. Higher speeds and heavier loads shorten the interval. Continuous vibration monitoring detects Point P earliest. The P-F interval is the time between Point P (when a fault becomes detectable) and Point F (when functional failure occurs). Understanding this window helps prioritize maintenance scheduling.

---

## 2. Bearing Wear - Sleeve Bearings (Journal Bearings)

Sleeve bearings use an oil film to support the shaft. Common in large vertical pumps and high-power horizontal pumps. Failure is typically gradual. Unlike rolling element bearings, sleeve bearings have no rolling parts; the shaft rides on a pressurized oil wedge that separates metal surfaces.

### Root Causes

| Cause | Mechanism |
|-------|-----------|
| Oil starvation | Insufficient oil supply causes metal-to-metal contact, babbit wiping. Babbit is the soft white metal lining on the bearing shell that provides a low-friction surface |
| Oil degradation | Oxidation, water contamination, or particle contamination reduces film strength |
| Startup without oil | Dry start wipes babbit material from bearing surface |
| Excessive vibration | Shaft orbit becomes unstable, intermittent contact erodes bearing surface |
| Misalignment | Edge loading concentrates pressure on bearing ends |

### Observable Precursor Signals

- Oil temperature rise: consistent increase of 2 to 5 C above baseline
- Vibration at 1x running speed in radial direction with increasing trend
- Oil analysis: high babbit metal (tin, lead) particle count
- Increased oil consumption or leakage

### P-F Lead Time

Sleeve bearing wear is slower than rolling element wear. P-F interval ranges from weeks to months. The oil film provides damping that masks early damage.

---

## 3. Cavitation

Cavitation occurs when local pressure at the impeller eye drops below the fluid vapor pressure. Vapor bubbles form and then implode violently as they move into higher-pressure zones. Implosion generates localized shockwaves of 20,000 to 60,000 psi that erode metal surfaces. It is one of the most common causes of premature impeller failure.

### Root Causes

| Cause | Mechanism |
|-------|-----------|
| Low NPSHa | System provides insufficient suction pressure relative to NPSHr. NPSH stands for Net Positive Suction Head: the absolute pressure at the pump suction minus the fluid vapor pressure. If NPSHa (available) drops below NPSHr (required), cavitation begins |
| High fluid temperature | Fluid vapor pressure increases, reduces NPSH margin |
| Blocked suction strainer | Friction loss increases, available pressure drops |
| Operating below minimum flow | Recirculation at impeller eye creates localized low-pressure zones |
| Pump running past BEP to high flow | NPSHr increases as flow increases past BEP |

### Observable Precursor Signals

- Distinctive noise: sound of gravel or marbles rattling inside pump
- Vibration: broadband random vibration, detectable by ultrasound before audible
- Flow fluctuation: discharge pressure and flow oscillate irregularly
- Performance drop: head decreases 5 to 15% as vapor occupies impeller volume
- Visual: impeller vanes show pitting on the low-pressure (suction) side

### Visual Damage Characteristics

| Damage Feature | Appearance |
|----------------|------------|
| Early cavitation | Small pits on impeller vane leading edges, suction side |
| Moderate cavitation | Sponge-like pitting pattern, material removal from vane surfaces |
| Severe cavitation | Complete loss of vane profile, holes through vane walls |

### P-F Lead Time

Cavitation P-F interval depends on NPSH margin and operating severity. Weeks to months if NPSHa is marginally below NPSHr. Days if NPSHa is far below NPSHr. Detection at Point P by ultrasound allows weeks of lead time for corrective action.

---

## 4. Mechanical Seal Failure

Mechanical seal failure accounts for a large fraction of centrifugal pump failures. Two precision-flat faces (rotating and stationary) slide against each other with a microscopic fluid film. Any disruption to this film causes rapid face wear, heat generation, and leakage. The fluid film between seal faces is typically only 0.5 to 5 microns thick, which explains why even microscopic contamination can cause failure.

### Root Causes

| Cause | Mechanism |
|-------|-----------|
| Dry running | Pump operates without fluid. Seal faces generate friction heat, thermal cracks appear, elastomers melt |
| Improper installation | Seal faces misaligned or damaged during assembly. Contamination from hands or tools |
| Shaft misalignment | Deflection at seal location increases contact force, accelerates face wear |
| Cavitation | Vibration from cavitation shakes seal faces apart, causes sudden leakage |
| Chemical attack | Process fluid incompatible with seal face materials or elastomers |
| Pressure spikes | Faces separate momentarily then slam together, causing cracks and chips |
| Temperature | Elastomers degrade or deform when operating temperature exceeds seal rating |
| Contamination | Abrasive particles enter seal face gap, wear grooves into faces |

### Observable Precursor Signals

- Visible leakage (drips or mist) at seal gland area
- Increased temperature at seal housing (measured by IR thermography or contact probe)
- High-frequency vibration at 2x to 10x running speed
- Changes in pump discharge pressure pattern (seal flush flow disrupted)
- Reduced seal flush flow (if external flush system is present)

### Seal Face Wear Patterns

| Pattern | Root Cause |
|---------|------------|
| Polished, flat wear | Normal operation, long service life |
| Heat cracks (crazing) | Dry running, insufficient cooling. These appear as fine spider-web cracks on the seal face |
| Chipped edges | Pressure spikes, thermal shock |
| Grooves | Contamination in fluid |
| Discoloration (bluing) | Overheating, loss of fluid film. Bluing indicates the seal face reached temperatures high enough to change the material's oxide layer |

### P-F Lead Time

Seal failure P-F interval is short relative to bearing or cavitation failures. Weeks to months depending on operating severity. Point P is detected by seal flush flow decrease, temperature rise, or visual weepage. Once leakage starts, seal life is measured in days to weeks.

---

## 5. Impeller Erosion

Erosion is material loss from impeller surfaces due to abrasive particles suspended in the pumped fluid. Erosion rate follows E ~ V^n where V is particle impact velocity and n typically ranges from 2 to 3 depending on material properties and particle characteristics. This means doubling the impeller speed can increase erosion rate by 4 to 8 times.

### Root Causes

| Cause | Mechanism |
|-------|-----------|
| Suspended solids | Sand, grit, scale particles impact impeller vanes and remove material |
| High tip speed | Higher impeller tip speed increases particle impact energy. Erosion proportional to tip speed raised to exponent n (2 to 3) |
| Recirculation | Particles trapped in secondary flow paths at volute lips and wear ring gaps cause localized wear |
| Wear ring clearance | Particles passing through wear ring annulus erode ring surfaces, increasing clearance and reducing efficiency. Wear rings are replaceable components that form a close-clearance seal between the impeller and casing; as they erode, internal recirculation increases |

### Observable Precursor Signals

- Performance degradation: head and flow decrease gradually as wear ring clearance increases
- Increased vibration as impeller balance is disturbed by uneven material loss
- Visual inspection: vane leading edges rounded, surface roughness increases
- Sound: may be silent until severe, no characteristic noise like cavitation

### Areas Most Susceptible

| Area | Damage Pattern |
|------|----------------|
| Impeller vane leading edges | Rounded, thinned profile |
| Volute lip | Grooving at intersection of lip and side wall |
| Wear ring surfaces | Increased clearance diameter, grooved surfaces |
| Casing side wall | Localized erosion from wear ring gap flow |

### P-F Lead Time

Erosion is a gradual process. P-F interval measured in months to years. Point P detected by periodic performance trending showing gradual head and efficiency decline. Action at P: inspect wear ring clearances, apply coatings, reduce tip speed, or replace wear parts.

---

## 6. Shaft Misalignment

Misalignment between motor shaft and pump shaft (parallel offset, angular gap, or combined) is a common cause of pump vibration. It leads to premature failure of bearings, couplings, and mechanical seals. Misalignment is the most common root cause found when investigating repeat mechanical seal failures.

### Root Causes

| Cause | Mechanism |
|-------|-----------|
| Thermal growth | Motor and pump expand differently as they heat up from cold start to operating temperature. A pump aligned cold may become misaligned at running temperature |
| Pipe strain | Piping connected to pump flanges exerts force that shifts pump casing alignment |
| Soft foot | Pump or motor feet not uniformly contacting baseplate, distorting frame when bolted down |
| Foundation settlement | Baseplate shifts over time, breaking initial alignment |
| Improper installation | Coupling aligned to cold tolerance without accounting for thermal growth |

### Observable Precursor Signals

- Vibration at 1x and 2x running speed, dominant in radial direction. In vibration analysis, 1x means frequency equal to rotational speed, 2x means twice rotational speed
- High axial vibration at 1x running speed (angular misalignment)
- Coupling wear pattern: elastomeric element shows uneven compression
- Bearing temperature elevated on one side of the bearing housing
- Mechanical seal fails prematurely with uneven face wear

### Vibration Spectrum Signature

| Misalignment Type | Dominant Frequency | Phase Relationship |
|-------------------|-------------------|-------------------|
| Parallel offset | 1x running speed | 180 degrees out of phase across coupling |
| Angular misalignment | 2x running speed | In phase axially across coupling |
| Combined | 1x and 2x running speed | Mixed phase pattern |

### P-F Lead Time

Misalignment P-F interval is weeks to months. Point P detected when vibration at 2x running speed exceeds baseline by a factor of 2. Progression accelerates as misalignment wears bearings and seals, increasing clearances and further degrading alignment.

---

## Key Equations Summary

| Quantity | Formula | Units |
|----------|---------|-------|
| Erosion rate | E ~ V^n (n = 2 to 3) | dimensionless (comparative) |
| Tip speed | V_tip = pi * D * n / 60 | m/s |
| Bearing defect frequency - BPFO (outer race) | BPFO = (n_b / 2) * (1 - (B_d / P_d) * cos(phi)) * f_s | Hz |
| Bearing defect frequency - BPFI (inner race) | BPFI = (n_b / 2) * (1 + (B_d / P_d) * cos(phi)) * f_s | Hz |
| NPSH margin | NPSH_margin = NPSHa - NPSHr | m |
| Vibration severity zones (ISO 10816-3, Group 2, rigid foundation) | Zone A: < 1.8 mm/s rms (good), Zone B: < 4.5 mm/s rms (acceptable), Zone C: < 11.2 mm/s rms (restricted), Zone D: > 11.2 mm/s rms (danger) | mm/s rms |

**Variable definitions:** n_b = number of rolling elements, B_d = ball diameter, P_d = pitch diameter, phi = contact angle, f_s = shaft rotational frequency in Hz. These formulas calculate the exact vibration frequencies produced by each type of bearing defect, allowing analysts to identify which component is damaged.

---

## Common Mistakes to Avoid

| Mistake | Consequence |
|---------|-------------|
| Operating pump far from BEP assuming bearings can handle it | Radial thrust increases, bearing skidding damage occurs, cage fractures develop |
| Ignoring vibration at 2x running speed, treating it as normal | Misalignment goes uncorrected, mechanical seal wears prematurely, coupling fails |
| Replacing mechanical seals without checking alignment | New seal fails in the same timeframe as old one |
| Ignoring gradual head loss as normal wear | Impeller erosion destroys vane profile and wear rings, efficiency drops below 60% |
| Using the same bearing clearance class for all operating conditions | Clearance optimized for BEP may cause skidding at low-flow conditions |
| Confusing cavitation noise with normal pump operation | Impeller damage progresses until vane failure or catastrophic breakage |
| Assuming oil analysis alone detects all bearing faults | Vibration detects raceway faults earlier; oil analysis detects lubricant degradation earlier |
| Installing seals without cleaning seal faces | Oils, dirt, and grease cause face contamination, premature leakage within days |
