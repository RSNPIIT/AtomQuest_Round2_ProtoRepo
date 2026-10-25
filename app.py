"""
AtomBerg Smart Purifier - AtomSense & AquaPrognos Digital Twin & IoT Dashboard
Team: ElementGuys (IIT Madras) | atomQUEST 2026 - Round 2 Prototype
"""

import streamlit as st
import numpy as np
import pandas as pd
import time
from sensor_fusion_engine import (
    AtomSensorFusionEngine, RawSensorTelemetry, PRESET_SCENARIOS
)
from prognostics_model import SevenStagePrognosticsEngine
from fail_safe_controller import AtombergFailSafeController, FailSafeState

# Page Configuration
st.set_page_config(
    page_title="Atomberg AtomSense | atomQUEST 2026 Prototype",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Atomberg Modern Slate & Coral Palette)
st.markdown("""
<style>
    .main { background-color: #0b0f19; color: #f8fafc; }
    .stMetric { background-color: #161e2e; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; }
    .stAlert { border-radius: 8px; }
    .atom-badge { background-color: #e11d48; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
    .iit-badge { background-color: #0284c7; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
    .card-box { background-color: #131b2e; border: 1px solid #1e293b; border-radius: 10px; padding: 18px; margin-bottom: 15px; }
    .safe-state { color: #10b981; font-weight: bold; }
    .warn-state { color: #f59e0b; font-weight: bold; }
    .danger-state { color: #ef4444; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Instantiate Engines
@st.cache_resource
def get_engines():
    return AtomSensorFusionEngine(), SevenStagePrognosticsEngine(), AtombergFailSafeController()

fusion_engine, prognostics_engine, failsafe_controller = get_engines()

# Header
col_h1, col_h2 = st.columns([0.7, 0.3])
with col_h1:
    st.markdown("## 💧 **Atomberg AtomSense™ & AquaPrognos™**")
    st.markdown("*Next-Generation Edge Sensing Beyond TDS & Physics-Informed Filter Prognostics*")
with col_h2:
    st.markdown("""
    <div style="text-align: right; padding-top: 10px;">
        <span class="atom-badge">atomQUEST 2026 • Round 2</span><br>
        <span class="iit-badge" style="margin-top: 5px; display: inline-block;">Team ElementGuys • IIT Madras</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Sidebar: Scenario & Telemetry Controls
st.sidebar.markdown("### 🎛️ **Feed Water & Sensor Injection**")
scenario_choice = st.sidebar.selectbox(
    "Choose Test Simulation Scenario:",
    [
        "1. Standard Municipal Supply (Safe Baseline)",
        "2. Deep Borewell Hard Water (High TDS, High Healthy Ca2+/Mg2+)",
        "3. Monsoon Turbid Runoff (High Organics & Sediment, 'Normal' TDS)",
        "4. Industrial Contaminant Spike (Deceptive TDS, Heavy Metal Anomaly)",
        "5. RO Membrane Rupture Failure (Sudden Pressure Drop & Leakage)",
        "Custom Manual Sensor Overrides"
    ]
)

# Load selected preset or allow manual tuning
if scenario_choice.startswith("1"):
    raw = PRESET_SCENARIOS["clean_municipal"]
elif scenario_choice.startswith("2"):
    raw = PRESET_SCENARIOS["hard_borewell"]
elif scenario_choice.startswith("3"):
    raw = PRESET_SCENARIOS["monsoon_turbid"]
elif scenario_choice.startswith("4"):
    raw = PRESET_SCENARIOS["industrial_chemical_spike"]
elif scenario_choice.startswith("5"):
    raw = PRESET_SCENARIOS["membrane_rupture"]
else:
    raw = PRESET_SCENARIOS["clean_municipal"]

# Manual fine tuning in expander
with st.sidebar.expander("🛠️ Fine-Tune Raw Hardware Telemetry"):
    ec_v = st.slider("EC Sensor Voltage (V)", 0.05, 3.5, float(raw.ec_voltage), 0.05)
    uv_mv = st.slider("UV-254 Photodiode (mV)", 50.0, 1000.0, float(raw.uv254_photodiode_mv), 10.0)
    turb_v = st.slider("Turbidity Phototransistor (V)", 1.0, 4.5, float(raw.turbidity_voltage), 0.05)
    dmis_hi = st.slider("DMIS High-Freq Impedance (Ω)", 100.0, 1000.0, float(raw.dmis_high_freq_imp), 10.0)
    dmis_lo = st.slider("DMIS Low-Freq Impedance (Ω)", 100.0, 1000.0, float(raw.dmis_low_freq_imp), 10.0)
    feed_p = st.slider("Feed Inlet Pressure (PSI)", 10.0, 80.0, float(raw.feed_pressure_psi), 1.0)
    perm_p = st.slider("Permeate Pressure (PSI)", 5.0, 40.0, float(raw.permeate_pressure_psi), 1.0)

    raw = RawSensorTelemetry(
        timestamp=time.time(),
        ec_voltage=ec_v,
        uv254_photodiode_mv=uv_mv,
        turbidity_voltage=turb_v,
        ph_voltage=raw.ph_voltage,
        orp_voltage=raw.orp_voltage,
        dmis_high_freq_imp=dmis_hi,
        dmis_low_freq_imp=dmis_lo,
        feed_pressure_psi=feed_p,
        permeate_pressure_psi=perm_p,
        flow_rate_lpm=raw.flow_rate_lpm,
        bldc_pump_current_ma=raw.bldc_pump_current_ma
    )

st.sidebar.markdown("### 📊 **Operational Purifier Age**")
cum_liters = st.sidebar.slider("Cumulative Treated Volume (Liters)", 500, 15000, 3400, 100)

# Process Sensor Fusion
water = fusion_engine.process_telemetry(raw)

# Process Prognostics
stage_health = prognostics_engine.evaluate_stages(
    cumulative_liters=cum_liters,
    avg_feed_turbidity_ntu=water.turbidity_ntu,
    avg_feed_tds_ppm=water.tds_ppm,
    avg_feed_toc_ppm=water.toc_ppm,
    delta_p_psi=water.delta_pressure_psi
)

# Process Fail-Safe State Machine
control = failsafe_controller.evaluate_safety(water, stage_health)

# -----------------------------------------------------------------------------
# MAIN DASHBOARD INTERFACE
# -----------------------------------------------------------------------------

# Top Live Status Banners
if control.fail_safe_state == FailSafeState.EMERGENCY_LOCKOUT:
    st.error(f"🚨 **FAIL-SAFE TRIGGERED: {control.fail_safe_state.value}**\n\n**Reason:** {control.safety_tripped_reason}\n\n**Hardware Action:** Inlet Solenoid CLOSED • Pump KILL SWITCH ACTIVATED • Tank Isolation Valve CLOSED.")
elif control.fail_safe_state == FailSafeState.AUTO_BACKWASH_PURGE:
    st.warning(f"⚡ **ACTIVE MITIGATION: {control.fail_safe_state.value}**\n\n**Action:** {control.safety_tripped_reason}")
elif control.fail_safe_state == FailSafeState.ADAPTIVE_REMINERALIZING:
    st.info(f"🌿 **DYNAMIC MINERAL ENHANCEMENT: {control.fail_safe_state.value}**\n\n**Action:** {control.safety_tripped_reason}")
else:
    st.success(f"✅ **SYSTEM STATUS: {control.fail_safe_state.value}** — Multi-barrier 7-stage filtration running at peak efficiency.")

# Metric Row 1: Water Quality Sensing Beyond TDS
st.markdown("### 1. Multi-Modal Water Quality Sensing: *Beyond Single-Metric TDS*")
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Bulk Feed TDS", f"{water.tds_ppm:.0f} ppm", delta="Bulk EC only" if water.tds_ppm < 500 else "High mineral")
m2.metric("UV-254 Organics (TOC)", f"{water.toc_ppm:.2f} mg/L", delta="SAFE" if water.toc_ppm < 3.0 else "HAZARD!", delta_color="inverse")
m3.metric("Turbidity", f"{water.turbidity_ntu:.2f} NTU", delta="Clear" if water.turbidity_ntu < 1.0 else "Colloidal Mud", delta_color="inverse")
m4.metric("Mineral Retention Index", f"{water.mineral_ion_ratio * 100:.0f}%", delta="Ca2+/Mg2+ intact")
m5.metric("Differential Pressure (ΔP)", f"{water.delta_pressure_psi:.1f} PSI", delta="Normal Drop" if water.delta_pressure_psi > 10 else "RUPTURE WARNING", delta_color="inverse")
m6.metric("Water Quality Index (WQI)", f"{water.feed_quality_index:.0f} / 100", delta=water.classification)

# Section 2: Why Conventional TDS Fails vs AtomSense
col_left, col_right = st.columns([0.55, 0.45])

with col_left:
    st.markdown("#### 🔬 **The 'Blind TDS' Comparison Test**")
    comp_df = pd.DataFrame({
        "Metric Analyzed": [
            "Total Dissolved Solids (TDS)",
            "Dissolved Organic Carbon (TOC)",
            "Colloidal Turbidity (Silt/Mud)",
            "Heavy Metal Anomaly (Pb/As)",
            "Beneficial Mineral Ratio (Ca/Mg)"
        ],
        "Conventional Purifier": [
            f"{water.tds_ppm:.0f} ppm (ONLY metric sensed)",
            "❌ Blind (Cannot detect organics)",
            "❌ Blind (Cannot detect colloids)",
            "❌ Blind (Treats toxic lead same as salt)",
            "❌ Blind (Blindly strips healthy minerals)"
        ],
        "Atomberg AtomSense™": [
            f"{water.tds_ppm:.0f} ppm (Calibrated EC)",
            f"✅ {water.toc_ppm:.2f} mg/L (UV-254 Photodiode)",
            f"✅ {water.turbidity_ntu:.2f} NTU (90° Optical Scatter)",
            f"✅ {'🚨 DETECTED!' if water.heavy_metal_anomaly else 'Clean (Normal)'} (DMIS Spectroscopy)",
            f"✅ {water.mineral_ion_ratio*100:.0f}% Healthy Retention"
        ]
    })
    st.table(comp_df)

with col_right:
    st.markdown("#### ⚙️ **Real-Time Hardware Actuators & Fail-Safe State**")
    act1, act2 = st.columns(2)
    with act1:
        st.write(f"**Inlet Solenoid Valve:** {'🟢 OPEN (Flowing)' if control.inlet_solenoid_open else '🔴 LOCKED SHUT'}")
        st.write(f"**Auto-Drain Solenoid:** {'🟡 OPEN (Purging)' if control.drain_flush_solenoid_open else '⚪ CLOSED'}")
        st.write(f"**BLDC Booster Pump:** `{control.bldc_pump_rpm} RPM`")
    with act2:
        st.write(f"**UV-C Sterilization LED:** `{control.uv_c_led_power_pct}% Power`")
        st.write(f"**Alkaliser Bypass Valve:** `{control.remineralizer_bypass_ratio * 100:.0f}% Mineral Blend`")
        st.write(f"**Emergency Alarm Buzzer:** {'🔔 ACTIVE AUDIBLE' if control.buzzer_alarm_active else '🔕 Silent'}")

    st.info(f"**IoT Telemetry Alert:** {control.iot_cloud_alert}")

st.markdown("---")

# Section 3: 7-Stage Filter Prognostics & Remaining Useful Life (RUL)
st.markdown("### 2. 7-Stage Filter Prognostics (Physics-Informed RUL Prediction)")
st.markdown("*Real-time degradation tracking accounting for feed water stress, sediment fouling, and chemical exhaustion.*")

p_cols = st.columns(7)
for idx, (sid, stage) in enumerate(stage_health.items()):
    with p_cols[idx]:
        st.markdown(f"**Stage {sid}**")
        st.caption(stage.name)
        
        # Color bar based on health
        if stage.health_pct > 65:
            bar_color = "green"
        elif stage.health_pct > 35:
            bar_color = "orange"
        else:
            bar_color = "red"

        st.progress(stage.health_pct / 100.0)
        st.markdown(f"**{stage.health_pct:.0f}%** ({stage.status})")
        st.write(f"📅 **{stage.rul_days} Days**")
        st.write(f"💧 `{stage.rul_liters} L` left")
        st.caption(f"Fouling: `{stage.fouling_factor}x`")

# Detailed Degradation Insight Table
with st.expander("🔍 View In-Depth Stage-by-Stage Physics & Failure Diagnostics"):
    stages_data = []
    for sid, s in stage_health.items():
        stages_data.append({
            "Stage": f"Stage {sid}: {s.name}",
            "Mechanism": s.filtration_mechanism,
            "Health (%)": s.health_pct,
            "RUL (Days)": s.rul_days,
            "RUL (Liters)": s.rul_liters,
            "Fouling Resistance Factor": f"{s.fouling_factor}x",
            "Condition Status": s.status,
            "Primary Degradation Driver": s.primary_degradation_driver
        })
    st.dataframe(pd.DataFrame(stages_data), use_container_width=True)

st.markdown("---")

# Section 4: Architecture & Hardware Circuit Schematic Preview
st.markdown("### 3. Edge-AI Hardware Architecture & Signal Chain")
col_arch1, col_arch2 = st.columns([0.6, 0.4])

with col_arch1:
    st.markdown("""
    ```mermaid
    flowchart LR
        subgraph Inflow["Raw Feed Water"]
            RAW[Feed Inflow]
        end
        
        subgraph Sensing["AtomSense Edge Sensing Array"]
            S_EC[EC Bulk Conductivity]
            S_UV[UV-254 nm Photodiode]
            S_TURB[90° Scatter Turbidity]
            S_DMIS[Multi-Freq Impedance]
            S_P[Piezo Differential ΔP]
        end

        subgraph EdgeMCU["Atomberg Edge Controller (ESP32-S3)"]
            ADC[16-Bit Low-Noise ADC]
            FUSE[Sensor Fusion Engine]
            PHM[7-Stage Prognostics]
            SAFE[Fail-Safe Interlock]
        end

        subgraph Actuators["Hardware Actuators"]
            IN_SOL[Inlet Dual Solenoid]
            PUMP[Atomberg BLDC Pump]
            VALVE[Motorized Bypass Valve]
            UVC[UV-C Sterilization Array]
        end

        RAW --> S_EC & S_UV & S_TURB & S_DMIS & S_P
        Sensing --> ADC --> FUSE --> PHM --> SAFE
        SAFE -->|Emergency Cutoff| IN_SOL
        SAFE -->|Adaptive RPM| PUMP
        SAFE -->|Mineral Balance| VALVE
        SAFE -->|Overdrive 130%| UVC
    ```
    """)

with col_arch2:
    st.markdown("""
    #### **Round 2 Prototype Specifications:**
    - **Edge Microcontroller:** ESP32-S3 Dual-Core Xtensa @ 240 MHz (FreeRTOS)
    - **Spectrophotometric Subsystem:** 254 nm Cold-Cathode / Deep UV-C Photodiode with Quartz optical window
    - **Nephelometric Turbidity:** 850 nm IR Emitter + $90^\circ$ phototransistor detector
    - **Dynamic Remineralization:** Stepper-motor controlled proportional blending orifice
    - **Emergency Interlock:** Dual normally-closed 24V solenoids with magnetic latching
    - **Cloud Connectivity:** MQTT over WiFi / BLE provisioning to Atomberg Home App
    """)

st.caption("Atomberg atomQUEST 2026 Prototype • Team ElementGuys (IIT Madras) • Developed for Round 2 Submission")
