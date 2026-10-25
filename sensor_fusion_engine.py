"""
AtomSense: Multi-Modal Sensor Fusion Engine for Atomberg Smart Water Purifiers
Author: Team ElementGuys (IIT Madras)
Event: atomQUEST 2026 - Round 2 Prototype
"""

import numpy as np
import time
from dataclasses import dataclass, asdict

@dataclass
class RawSensorTelemetry:
    """Raw physical and optical telemetry received from the ESP32 Edge Sensing MCU."""
    timestamp: float
    ec_voltage: float            # Electrical Conductivity Probe (V)
    uv254_photodiode_mv: float   # UV-254 nm Photodiode Absorption (mV)
    turbidity_voltage: float     # 90-degree Scattered Light Phototransistor (V)
    ph_voltage: float            # Glass electrode potential (V)
    orp_voltage: float           # Redox probe potential (V)
    dmis_high_freq_imp: float    # High-Freq Impedance @ 100 kHz (Ohms)
    dmis_low_freq_imp: float     # Low-Freq Impedance @ 1 kHz (Ohms)
    feed_pressure_psi: float     # Piezo-resistive pressure sensor at inlet (PSI)
    permeate_pressure_psi: float # Post-RO pressure sensor (PSI)
    flow_rate_lpm: float         # Hall-effect pulse flow sensor (Liters/Min)
    bldc_pump_current_ma: float  # Atomberg BLDC Booster Pump current draw (mA)

@dataclass
class CalibratedWaterProfile:
    """Calibrated physical chemical parameters derived from multi-modal sensor fusion."""
    timestamp: float
    tds_ppm: float               # Bulk Total Dissolved Solids (ppm)
    uv254_absorbance: float      # UV-254 Absorption coefficient (cm^-1)
    toc_ppm: float               # Total Organic Carbon proxy (mg/L)
    turbidity_ntu: float         # Turbidity in Nephelometric Turbidity Units
    ph_level: float              # Calibrated pH (0 - 14)
    orp_mv: float                # Oxidation Reduction Potential (mV)
    mineral_ion_ratio: float     # Ratio of beneficial Ca2+/Mg2+ vs bulk conductivity
    heavy_metal_anomaly: bool    # Differential impedance flag for toxic ionic spike
    delta_pressure_psi: float    # Differential Pressure drop across RO (PSI)
    flow_rate_lpm: float         # Current treated water flow rate
    feed_quality_index: float    # Overall Composite Water Quality Score (0 to 100)
    classification: str          # Categorization of feed source
    safety_verdict: str          # SAFE, WARNING_MINERAL_DEFICIT, WARNING_ORGANIC, DANGER_HAZARD

class AtomSensorFusionEngine:
    """
    Fuses bulk electrical conductivity with optical UV-254 spectrophotometry,
    turbidity scatter, and multi-frequency impedance spectroscopy to decode
    true water safety beyond single-metric TDS.
    """
    def __init__(self):
        # Calibration constants based on lab benchmark curves
        self.ec_slope = 485.0            # ppm per Volt
        self.uv_zero_mv = 980.0          # Baseline photodiode voltage with pure deionized water
        self.turb_clear_v = 4.2          # 0 NTU voltage
        self.turb_slope = -0.75          # V per 10 NTU
        self.ph_neutral_v = 2.50         # pH 7.0 reference voltage
        self.ph_slope = 0.0591           # Nernst slope at 25C (V/pH)

    def process_telemetry(self, raw: RawSensorTelemetry) -> CalibratedWaterProfile:
        # 1. Calibrate Bulk TDS
        tds_ppm = max(5.0, raw.ec_voltage * self.ec_slope)

        # 2. Calibrate UV-254 Optical Absorption (Beer-Lambert Law)
        # Absorbance A = -log10(I / I0)
        norm_intensity = np.clip(raw.uv254_photodiode_mv / self.uv_zero_mv, 0.01, 1.0)
        uv254_abs = -np.log10(norm_intensity)
        # Proxy TOC (Total Organic Carbon) correlation: TOC (mg/L) ~= 42.5 * A254 + 0.8
        toc_ppm = max(0.1, 42.5 * uv254_abs + 0.8)

        # 3. Calibrate Turbidity (NTU)
        turb_diff = max(0.0, self.turb_clear_v - raw.turbidity_voltage)
        turbidity_ntu = max(0.05, turb_diff * 14.5)

        # 4. Calibrate pH and ORP
        ph_level = 7.0 + ((raw.ph_voltage - self.ph_neutral_v) / 0.18)
        ph_level = float(np.clip(ph_level, 3.5, 10.5))
        orp_mv = (raw.orp_voltage - 1.5) * 400.0

        # 5. Differential Multi-Frequency Impedance Spectroscopy (DMIS)
        # Hydrated Ca2+/Mg2+ divalent ions exhibit characteristic relaxation dispersions
        # between 1 kHz and 100 kHz. Heavy metals (Pb2+, As3+) shift the phase angle sharply.
        impedance_ratio = raw.dmis_high_freq_imp / max(1.0, raw.dmis_low_freq_imp)
        mineral_ion_ratio = float(np.clip(impedance_ratio * 1.25, 0.1, 1.0))
        heavy_metal_anomaly = bool(impedance_ratio < 0.35 and tds_ppm < 400)

        # 6. Differential Pressure
        delta_p = max(0.0, raw.feed_pressure_psi - raw.permeate_pressure_psi)

        # 7. Composite Water Quality Index (WQI)
        # Penalizes high organics (UV254), high turbidity, extreme pH, and anomalous heavy ions
        penalty_toc = min(40.0, toc_ppm * 5.0)
        penalty_turb = min(30.0, turbidity_ntu * 4.0)
        penalty_ph = abs(ph_level - 7.4) * 8.0
        penalty_metal = 45.0 if heavy_metal_anomaly else 0.0

        wqi = max(5.0, 100.0 - (penalty_toc + penalty_turb + penalty_ph + penalty_metal))

        # 8. Classification and Safety Verdict
        if heavy_metal_anomaly or toc_ppm > 8.0:
            classification = "Contaminated Runoff / Chemical Spike"
            safety_verdict = "DANGER_HAZARD"
        elif turbidity_ntu > 5.0 or toc_ppm > 4.5:
            classification = "Turbid Surface / Flood Inflow"
            safety_verdict = "WARNING_ORGANIC"
        elif tds_ppm > 800:
            classification = "Deep Borewell Hard Water"
            safety_verdict = "SAFE" if mineral_ion_ratio > 0.6 else "WARNING_MINERAL_DEFICIT"
        elif tds_ppm < 80:
            classification = "Over-Stripped / Low Mineral Supply"
            safety_verdict = "WARNING_MINERAL_DEFICIT"
        else:
            classification = "Standard Municipal Supply"
            safety_verdict = "SAFE"

        return CalibratedWaterProfile(
            timestamp=raw.timestamp,
            tds_ppm=round(float(tds_ppm), 1),
            uv254_absorbance=round(float(uv254_abs), 4),
            toc_ppm=round(float(toc_ppm), 2),
            turbidity_ntu=round(float(turbidity_ntu), 2),
            ph_level=round(float(ph_level), 2),
            orp_mv=round(float(orp_mv), 1),
            mineral_ion_ratio=round(mineral_ion_ratio, 3),
            heavy_metal_anomaly=heavy_metal_anomaly,
            delta_pressure_psi=round(float(delta_p), 1),
            flow_rate_lpm=round(float(raw.flow_rate_lpm), 2),
            feed_quality_index=round(float(wqi), 1),
            classification=classification,
            safety_verdict=safety_verdict
        )

# Preset real-world test scenarios
PRESET_SCENARIOS = {
    "clean_municipal": RawSensorTelemetry(
        timestamp=time.time(),
        ec_voltage=0.38,             # ~185 ppm TDS
        uv254_photodiode_mv=950.0,   # Very clear, negligible organics
        turbidity_voltage=4.15,      # ~0.5 NTU
        ph_voltage=2.54,             # pH ~7.2
        orp_voltage=2.10,            # Good oxidative stability
        dmis_high_freq_imp=820.0,
        dmis_low_freq_imp=910.0,
        feed_pressure_psi=42.0,
        permeate_pressure_psi=12.0,
        flow_rate_lpm=2.2,
        bldc_pump_current_ma=420.0
    ),
    "hard_borewell": RawSensorTelemetry(
        timestamp=time.time(),
        ec_voltage=1.92,             # ~930 ppm TDS (High Mineral)
        uv254_photodiode_mv=920.0,   # Pure groundwater, low organics
        turbidity_voltage=3.95,      # ~1.8 NTU
        ph_voltage=2.68,             # Slightly alkaline pH ~7.8
        orp_voltage=1.85,
        dmis_high_freq_imp=740.0,
        dmis_low_freq_imp=890.0,
        feed_pressure_psi=58.0,
        permeate_pressure_psi=14.0,
        flow_rate_lpm=1.8,
        bldc_pump_current_ma=580.0
    ),
    "monsoon_turbid": RawSensorTelemetry(
        timestamp=time.time(),
        ec_voltage=0.72,             # ~350 ppm TDS (TDS appears 'normal')
        uv254_photodiode_mv=310.0,   # High organic absorption A254 ~0.50!
        turbidity_voltage=2.40,      # >12 NTU (High colloid / muddy runoff)
        ph_voltage=2.32,             # Slightly acidic pH ~6.2
        orp_voltage=1.20,
        dmis_high_freq_imp=510.0,
        dmis_low_freq_imp=780.0,
        feed_pressure_psi=48.0,
        permeate_pressure_psi=9.0,
        flow_rate_lpm=1.5,
        bldc_pump_current_ma=510.0
    ),
    "industrial_chemical_spike": RawSensorTelemetry(
        timestamp=time.time(),
        ec_voltage=0.62,             # ~300 ppm TDS (Deceptive moderate TDS!)
        uv254_photodiode_mv=140.0,   # Extreme organic/chemical absorption!
        turbidity_voltage=3.80,      # Mild turbidity
        ph_voltage=1.90,             # Acidic chemical flux pH ~5.1
        orp_voltage=0.75,            # Reducing toxic potential
        dmis_high_freq_imp=180.0,    # Anomalous phase dispersion (Heavy Metals)
        dmis_low_freq_imp=850.0,
        feed_pressure_psi=45.0,
        permeate_pressure_psi=10.0,
        flow_rate_lpm=1.9,
        bldc_pump_current_ma=480.0
    ),
    "membrane_rupture": RawSensorTelemetry(
        timestamp=time.time(),
        ec_voltage=1.65,             # 800 ppm permeate surge
        uv254_photodiode_mv=480.0,   # Organics leaking into output!
        turbidity_voltage=3.20,
        ph_voltage=2.45,
        orp_voltage=1.40,
        dmis_high_freq_imp=600.0,
        dmis_low_freq_imp=650.0,
        feed_pressure_psi=32.0,      # Sudden pressure collapse across membrane
        permeate_pressure_psi=28.0,  # Delta P collapsed to 4 PSI
        flow_rate_lpm=3.5,           # Unrestricted high flow surge
        bldc_pump_current_ma=290.0
    )
}
