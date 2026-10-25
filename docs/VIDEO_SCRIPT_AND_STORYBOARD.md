# atomQUEST 2026: 90-Second Video Demonstration Script & Storyboard

**Project:** AtomSense™ & AquaPrognos™: Edge Sensing Beyond TDS & 7-Stage Filter Prognostics  
**Team Name:** ElementGuys  
**Institution:** Indian Institute of Technology (IIT), Madras  
**Track:** Track 3: Smart Water Purifiers  
**Video File Naming Requirement:** `atomQUEST2026_ElementGuys_IITMadras_Track3_Video.mp4`  
**Max Duration:** 90 Seconds | **Max File Size:** 50 MB

---

## 🎬 Second-by-Second Video Storyboard

| Timestamp | Visual on Screen | Spoken Script (Word-for-Word Voiceover) | Rubric Addressed |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:12**<br/>*(12s)* | **Title Slide / Camera on Ramrup** showing IIT Madras ID / Project Banner: *"Team ElementGuys • Track 3: Smart Water Purifiers"*. | *"Hello, I am Ramrup Satpati representing Team ElementGuys from IIT Madras in atomQUEST 2026. For Track 3, we are demonstrating **AtomSense** and **AquaPrognos**—reimagining Atomberg water purifiers with multi-spectral sensing beyond TDS and physics-informed filter prognostics."* | **Rubric 1:** Team & Track Details |
| **0:12 – 0:28**<br/>*(16s)* | **Switch screen to Dashboard** highlighting the *"Blind TDS Comparison Table"*. | *"Today's purifiers rely exclusively on bulk TDS. But TDS is dangerously blind: it strips healthy calcium and magnesium from hard groundwater, yet completely misses toxic dissolved organics, pesticides, and heavy metal runoffs. We solve this by fusing UV-254 optical absorption, 90-degree turbidity scatter, and multi-frequency impedance spectroscopy directly at the inlet."* | **Rubric 2:** Problem Identified & Solution Approach |
| **0:28 – 0:45**<br/>*(17s)* | **Live Dashboard Demo:** Click preset *"2. Deep Borewell Hard Water"*. Point to the **Mineral Retention Index (85%)** and **Alkaliser Bypass Valve (65%)**. | *"Here is our working prototype. When feed water has high TDS from safe minerals, our algorithm detects high divalent ion dispersion and automatically throttles our motorized alkaliser bypass to preserve healthy minerals, preventing unnecessary water wastage and tasteless acidic water."* | **Rubric 3 & 4:** Prototype Progress & Core Function Demo |
| **0:45 – 1:05**<br/>*(20s)* | **Live Shock Injection:** Select preset *"4. Industrial Chemical Spike"* or *"Monsoon Runoff"*. Show the **Red Emergency Lockout Alert** popping up live! Show **Inlet Solenoid: LOCKED SHUT**, **Pump: 0 RPM**. | *"Now, observe what happens during a severe contaminant spike. While conventional purifiers read a deceptive 300 ppm TDS and continue dispensing, AtomSense detects an immediate UV-254 organic spike and heavy metal anomaly. Within 50 milliseconds, our Tier-1 Autonomous Fail-Safe trips: the dual inlet solenoid snaps shut, the BLDC booster pump is killed, and an emergency cloud alert is dispatched."* | **Rubric 4 & 5:** Fail-Safe & Safety Mechanism Status |
| **1:05 – 1:20**<br/>*(15s)* | **Scroll to Section 2:** Show the **7-Stage Health & RUL Progress Bars** (Sediment 48%, RO 79%, UV-C 92%). | *"Simultaneously, our physics-informed prognostics engine tracks degradation across all 7 stages—from sediment cake resistance to UV-C LED radiometer decay—predicting exact Remaining Useful Life in days and liters, eliminating surprise failures and premature cartridge replacements."* | **Rubric 3:** Working Analytics & PHM Core Module |
| **1:20 – 1:30**<br/>*(10s)* | **Camera on Ramrup / System Architecture Summary**: Display hardware schematic on screen. | *"All edge algorithms, IoT telemetry, and safety state machines are complete and validated. In Round 3, we will consolidate this onto our custom ESP32-S3 PCB and bench-test with Atomberg mentors. Thank you!"* | **Rubric 5:** What is done & Next steps |

---

## 💡 Quick Tips for Recording:
1. **Screen Recording:** Open `http://localhost:8501` (run `streamlit run app.py`) in full screen.
2. **Audio:** Speak clearly with confidence. A smartphone microphone or headset is more than enough.
3. **Pacing:** Practice once with a stopwatch—90 seconds is approximately 220 words.
4. **File Format:** Export as MP4 (H.264), 1080p or 720p. The final file will be around 15–25 MB (well under the 50 MB limit).
