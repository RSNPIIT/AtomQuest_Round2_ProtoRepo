"""
AtomSafe: Autonomous Fail-Safe & Adaptive Remineralization Controller
Author: Team ElementGuys (IIT Madras)
Event: atomQUEST 2026 - Round 2 Prototype
"""

from enum import Enum
from dataclasses import dataclass
import time
from sensor_fusion_engine import CalibratedWaterProfile
from prognostics_model import StageHealth

class FailSafeState(Enum):
    STANDBY = "STANDBY"
    NORMAL_PURIFYING = "NORMAL_PURIFYING"
    ADAPTIVE_REMINERALIZING = "ADAPTIVE_REMINERALIZING"
    AUTO_BACKWASH_PURGE = "AUTO_BACKWASH_PURGE"
    SAFETY_THROTTLING = "SAFETY_THROTTLING"
    EMERGENCY_LOCKOUT = "EMERGENCY_LOCKOUT"

@dataclass
class ActuatorControlState:
    inlet_solenoid_open: bool
    drain_flush_solenoid_open: bool
    bldc_pump_rpm: int
    uv_c_led_power_pct: int
    remineralizer_bypass_ratio: float   # 0.0 (Pure RO) to 1.0 (Full Alkaliser blend)
    buzzer_alarm_active: bool
    iot_cloud_alert: str
    fail_safe_state: FailSafeState
    safety_tripped_reason: str

class AtombergFailSafeController:
    """
    Hardware-level state machine governing dual solenoids, Atomberg BLDC booster pump,
    UV-C sterilization array, and motorized proportional mineral bypass valve.
    """
    def __init__(self):
        self.state = FailSafeState.NORMAL_PURIFYING
        self.lockout_reason = ""
        self.last_state_change = time.time()
        self.alert_history = []

    def evaluate_safety(
        self,
        water: CalibratedWaterProfile,
        stage_health: dict
    ) -> ActuatorControlState:
        # Default Normal State
        inlet_sol = True
        drain_sol = False
        pump_rpm = 2800
        uv_power = 100
        bypass_ratio = 0.35
        buzzer = False
        alert = "System Nominal: Purifying safely."
        reason = "None (System Operating within Safe Limits)"

        # -------------------------------------------------------------
        # TIER 1: EMERGENCY AUTO-LOCKOUT CRITICAL CONDITIONS
        # -------------------------------------------------------------
        if water.heavy_metal_anomaly:
            self.state = FailSafeState.EMERGENCY_LOCKOUT
            reason = "CRITICAL HAZARD: Anomalous Heavy Metal Ionic Dispersion Detected by DMIS Sensor!"
            alert = "EMERGENCY SHUTDOWN: Toxic Inflow Intercepted. Inlet valve closed."
            inlet_sol = False
            pump_rpm = 0
            buzzer = True

        elif water.toc_ppm > 8.0:
            self.state = FailSafeState.EMERGENCY_LOCKOUT
            reason = f"CRITICAL HAZARD: Extreme Organic Contaminant Breakthrough (TOC: {water.toc_ppm:.1f} ppm > 8.0 ppm)!"
            alert = "EMERGENCY SHUTDOWN: Severe Chemical / Organic Spillage in Source Water."
            inlet_sol = False
            pump_rpm = 0
            buzzer = True

        elif water.delta_pressure_psi < 6.0 and water.tds_ppm > 400:
            self.state = FailSafeState.EMERGENCY_LOCKOUT
            reason = "CRITICAL FAIL-SAFE: RO Membrane Hydraulic Rupture / Seal Breach (Delta P Collapsed)!"
            alert = "EMERGENCY SHUTDOWN: RO Membrane Integrity Failure. Purified water bypass locked."
            inlet_sol = False
            pump_rpm = 0
            buzzer = True

        elif stage_health[5].health_pct < 5.0: # UV-C LED failure
            self.state = FailSafeState.EMERGENCY_LOCKOUT
            reason = "BIOLOGICAL FAIL-SAFE: UV-C Sterilization LED Array Output Failed / Quenched!"
            alert = "EMERGENCY LOCKOUT: Cannot guarantee 99.9999% microbial eradication without UV-C."
            inlet_sol = False
            pump_rpm = 0
            buzzer = True

        # -------------------------------------------------------------
        # TIER 2: ACTIVE MITIGATION & SAFETY THROTTLING
        # -------------------------------------------------------------
        elif water.turbidity_ntu > 8.0:
            self.state = FailSafeState.AUTO_BACKWASH_PURGE
            reason = f"AUTOMATED FLUSH: Feed Turbidity elevated ({water.turbidity_ntu:.1f} NTU). Activating high-velocity pre-sediment flush."
            alert = "AUTO-FLUSH ACTIVE: Flushing sediment cake to prevent Pre-Carbon clogging."
            inlet_sol = True
            drain_sol = True
            pump_rpm = 3200
            bypass_ratio = 0.0

        elif water.toc_ppm > 3.5 or water.uv254_absorbance > 0.15:
            self.state = FailSafeState.SAFETY_THROTTLING
            reason = f"SAFETY THROTTLING: Elevated organic load (TOC: {water.toc_ppm:.1f} ppm). Slowing pump to maximize UV-C contact time."
            alert = "ELEVATED ORGANICS: Pump throttled, UV-C boosted to 130% over-drive."
            inlet_sol = True
            drain_sol = False
            pump_rpm = 1800
            uv_power = 130
            bypass_ratio = 0.15

        # -------------------------------------------------------------
        # TIER 3: DYNAMIC ADAPTIVE REMINERALIZATION
        # -------------------------------------------------------------
        elif water.mineral_ion_ratio < 0.40 or water.tds_ppm < 120:
            self.state = FailSafeState.ADAPTIVE_REMINERALIZING
            reason = "ADAPTIVE REMINERALIZATION: Low natural mineral quotient. Increasing Alkaliser & Mg2+/Ca2+ core blend ratio."
            alert = "MINERAL ENHANCEMENT: Dynamically adjusting post-filtration mineral infusion to target 180 ppm healthy TDS."
            inlet_sol = True
            pump_rpm = 2600
            uv_power = 100
            bypass_ratio = 0.65 # Boost alkaliser bypass ratio

        else:
            self.state = FailSafeState.NORMAL_PURIFYING
            reason = "Optimal condition: 7-stage multi-barrier purification active."
            alert = "Atomberg Smart Purifier: Optimal mineral retention active."

        return ActuatorControlState(
            inlet_solenoid_open=inlet_sol,
            drain_flush_solenoid_open=drain_sol,
            bldc_pump_rpm=pump_rpm,
            uv_c_led_power_pct=uv_power,
            remineralizer_bypass_ratio=round(bypass_ratio, 2),
            buzzer_alarm_active=buzzer,
            iot_cloud_alert=alert,
            fail_safe_state=self.state,
            safety_tripped_reason=reason
        )
