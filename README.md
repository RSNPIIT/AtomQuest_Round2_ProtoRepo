# 💧 AtomSense™ & AquaPrognos™
### Next-Generation Edge Sensing Beyond TDS & Physics-Informed 7-Stage Filter Prognostics for Atomberg Smart Water Purifiers

**Competition:** atomQUEST 2026 — Round 2: Prototype Submission  
**Track:** Track 3: Smart Water Purifiers  
**Team Name:** ElementGuys  
**Institution:** Indian Institute of Technology (IIT), Madras  
**Team Lead:** Ramrup Satpati  
**Repository:** [RSNPIIT/AtomQuest_Round2_ProtoRepo](https://github.com/RSNPIIT/AtomQuest_Round2_ProtoRepo)

---

## 📌 Executive Summary

Modern residential water purifiers rely almost universally on single-electrode electrical conductivity to measure bulk Total Dissolved Solids (TDS in ppm). As water quality challenges in India escalate, this single metric is dangerously inadequate:
1. **False Positives (Unnecessary Mineral Stripping):** Health-beneficial divalent ions ($\text{Ca}^{2+}$, $\text{Mg}^{2+}$) in deep groundwater trigger high TDS readings, prompting conventional RO purifiers to strip them aggressively.
2. **False Negatives (Unseen Toxic Breakthrough):** Hazardous non-ionic contaminants (dissolved organic carbon, pesticides, industrial solvents, colloids, and microbials) can pass through undetected at dangerous levels under an apparently "normal" TDS reading.

**AtomSense™** transforms Atomberg's water purifier category over the next 5–10 years by replacing blind TDS estimation with a multi-spectral, multi-modal sensing engine and a physics-informed degradation model across all 7 filtration stages.

---

## 🚀 Key Technological Innovations

### 1. Multi-Modal Edge Sensing Array ("Beyond TDS")
- **UV-254 Optical Absorption ($A_{254}$):** Measures aromatic organics, chemical oxygen demand (COD), and proxy Total Organic Carbon (TOC in mg/L) using Beer-Lambert optical transmission through a quartz aperture.
- **Nephelometric Turbidity (NTU):** Uses modulated 850 nm infrared light scattered at $90^\circ$ to detect colloidal silt and suspended solids.
- **Differential Multi-Frequency Impedance Spectroscopy (DMIS):** High/low frequency impedance ratios ($1\text{ kHz}$ vs $100\text{ kHz}$) differentiate hydrated $\text{Ca}^{2+} / \text{Mg}^{2+}$ mineral ions from heavy metal anomalies ($\text{Pb}^{2+}$, $\text{As}^{3+}$).
- **Differential Pressure Drop ($\Delta P$):** Piezo-resistive pressure monitoring across the RO membrane to detect membrane rupture and scaling.

### 2. Physics-Informed 7-Stage Filter Prognostics (AquaPrognos™)
Tracks degradation dynamically across all 7 stages of Atomberg's filtration system:
1. **Sediment Pre-Filter (5 Micron PP):** Cake layer growth kinetics driven by feed turbidity.
2. **Pre-Carbon Block:** Adsorption pore exhaustion curve driven by cumulative organic load.
3. **High-Recovery RO Membrane:** Hermia cake filtration and concentration polarization modeling ($J(t) / J_0$).
4. **Post-Carbon Taste Polisher:** Polishing bed exhaustion tracking.
5. **UV-C LED Chamber:** Solid-state optical radiometer degradation model.
6. **Ultrafiltration (UF) Capillary:** Hollow-fiber colloidal cake resistance.
7. **Bio-Alkaliser & Mineraliser Cartridge:** Exponential mineral dissolution and pH buffer leaching curves.

### 3. Autonomous 3-Tier Hardware Fail-Safe Interlock
- **Tier 1 (Emergency Lockout):** DMIS heavy metal detection, organic spike ($\text{TOC} > 8.0\text{ mg/L}$), $\Delta P$ pressure collapse ($< 6\text{ PSI}$), or UV-C quench triggers an instant shut-off of dual normally-closed inlet solenoids, kills the BLDC pump, isolates the storage tank, and fires an audible and cloud alarm.
- **Tier 2 (Active Mitigation):** Automated backwash flush solenoid cleans sediment when turbidity exceeds 8 NTU. Flow is throttled during high organics to ensure required UV-C disinfection dwell time.
- **Tier 3 (Adaptive Remineralization):** Motorized bypass valve dynamically doses post-RO alkaline minerals to guarantee 150–200 ppm natural healthy minerals.

---

## 📂 Repository Structure

```
AtomQuest_Round2_ProtoRepo/
├── app.py                                 # Interactive Streamlit Digital Twin & IoT Dashboard
├── sensor_fusion_engine.py                # Multi-modal sensor calibration & feed simulation
├── prognostics_model.py                   # 7-stage physics-informed filter degradation & RUL
├── fail_safe_controller.py                # 3-tier hardware fail-safe state machine
├── generate_progress_report.py            # Generates official 2-page PDF progress report
├── generate_charts_pil.py                 # Generates high-res engineering figures
├── progress_charts.png                    # Embedded figures (Figure 1 & Figure 2)
├── atomQUEST2026_ElementGuys_IITMadras_Track3_Report.pdf  # Final PDF Report (Ready to Submit)
├── docs/
│   └── VIDEO_SCRIPT_AND_STORYBOARD.md     # 90-second word-for-word recording script & visual cues
├── LICENSE                                # GPL v3.0
└── README.md
```

---

## 💻 How to Run the Prototype Dashboard

1. **Activate your Python environment:**
   ```bash
   # From your virtual environment
   source .venv/bin/activate
   ```

2. **Launch the Streamlit Digital Twin:**
   ```bash
   streamlit run app.py
   ```

3. **Interact with the Live Scenarios:**
   - Use the sidebar dropdown to switch between:
     - *Clean Municipal Supply*
     - *Deep Borewell Hard Water (High TDS but Safe Minerals)*
     - *Monsoon Turbid Runoff (High Organics, 'Normal' TDS)*
     - *Industrial Chemical Spike (Severe Hazard!)*
     - *RO Membrane Rupture Failure*
   - Observe live actuator reactions: Solenoid shut-off, BLDC pump RPM throttling, and dynamic alkaliser bypass blending.

---

## 📄 Official Submissions

- **Progress Report (PDF, 2 Pages):**  
  [`atomQUEST2026_ElementGuys_IITMadras_Track3_Report.pdf`](./atomQUEST2026_ElementGuys_IITMadras_Track3_Report.pdf)  
  *Adheres strictly to all 7 mandatory sections, naming convention, and budget guidelines.*
- **Video Script & Timing Guide:**  
  [`docs/VIDEO_SCRIPT_AND_STORYBOARD.md`](./docs/VIDEO_SCRIPT_AND_STORYBOARD.md)  
  *Word-for-word voiceover tailored to the 90-second ceiling.*

---

**Team ElementGuys • Indian Institute of Technology (IIT), Madras**  
*Empowering Atomberg with Category-Defining Sensing & Prognostics.*
