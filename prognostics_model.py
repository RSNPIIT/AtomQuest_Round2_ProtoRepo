"""
AquaPrognos: Physics-Informed 7-Stage Filter Failure Prognostics Engine
Author: Team ElementGuys (IIT Madras)
Event: atomQUEST 2026 - Round 2 Prototype
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class StageHealth:
    stage_id: int
    name: str
    filtration_mechanism: str
    health_pct: float            # 0.0 to 100.0 %
    rul_days: int                # Remaining Useful Life in Days
    rul_liters: int              # Remaining Useful Capacity in Liters
    fouling_factor: float        # Resistance factor (1.0 = clean, >3.0 = heavily fouled)
    status: str                  # OPTIMAL, GOOD, REPLACE_SOON, CRITICAL_EXHAUSTED
    primary_degradation_driver: str

class SevenStagePrognosticsEngine:
    """
    Simulates and predicts filter health across all 7 stages of the Atomberg Purifier:
    1. Sediment Pre-Filter (5 Micron PP)
    2. Pre-Carbon Chemi-Block
    3. High-Recovery Reverse Osmosis (RO) Membrane
    4. Post-Carbon Taste Polisher
    5. UV-C LED Optical Disinfection Chamber
    6. Ultrafiltration (UF) Hollow Fiber
    7. Bio-Alkaliser & Mineraliser Cartridge
    """
    def __init__(self):
        # Baseline rated capacities (Liters under standard municipal feed)
        self.rated_capacity_liters = {
            1: 6000,    # Sediment
            2: 7500,    # Pre-Carbon
            3: 12000,   # RO Membrane
            4: 8000,    # Post-Carbon
            5: 25000,   # UV-C LED (Hours equivalent converted to volume)
            6: 15000,   # UF Hollow Fiber
            7: 5000     # Alkaliser cartridge
        }
        self.stage_names = {
            1: ("Sediment Pre-Filter", "Particulate / Silt Interception"),
            2: ("Pre-Carbon Chemi-Block", "Chlorine / VOC Chemisorption"),
            3: ("High-Recovery RO Membrane", "Nanoscale Hyperfiltration (<0.0001 um)"),
            4: ("Post-Carbon Taste Polisher", "Final Micro-adsorption & Odor Guard"),
            5: ("UV-C LED Disinfection Chamber", "Photolytic 254nm DNA/RNA Inactivation"),
            6: ("Ultrafiltration (UF) Capillary", "Dead-end Colloid & Cyst Barrier"),
            7: ("Bio-Alkaliser & Remineraliser", "Active Mineral Release (Ca2+/Mg2+) & pH Buffer")
        }

    def evaluate_stages(
        self,
        cumulative_liters: float,
        avg_feed_turbidity_ntu: float,
        avg_feed_tds_ppm: float,
        avg_feed_toc_ppm: float,
        delta_p_psi: float,
        uv_power_decay_pct: float = 0.0,
        mineral_dissolution_hours: float = 0.0
    ) -> Dict[int, StageHealth]:
        results = {}

        # 1. Stage 1: Sediment Filter
        # Degradation accelerated heavily by Turbidity
        turbidity_stress = max(1.0, avg_feed_turbidity_ntu / 1.0)
        eff_sed_vol = cumulative_liters * (1.0 + 0.35 * (turbidity_stress - 1.0))
        sed_health = max(0.0, 100.0 * (1.0 - (eff_sed_vol / self.rated_capacity_liters[1])))
        sed_fouling = 1.0 + (2.5 * (1.0 - sed_health / 100.0))

        # 2. Stage 2: Pre-Carbon Block
        # Exhausted by TOC (Total Organic Carbon) & Chlorinated Organics
        toc_stress = max(1.0, avg_feed_toc_ppm / 1.5)
        eff_carb_vol = cumulative_liters * (1.0 + 0.25 * (toc_stress - 1.0))
        carb_health = max(0.0, 100.0 * (1.0 - (eff_carb_vol / self.rated_capacity_liters[2])))
        carb_fouling = 1.0 + (1.8 * (1.0 - carb_health / 100.0))

        # 3. Stage 3: RO Membrane
        # Governed by Hermia Cake Filtration & Resistance-in-Series Model:
        # Flux decline J(t) / J0 = 1 / (1 + Rm_foul)
        # Pressure stress = Delta P / Nominal P (30 PSI)
        pressure_ratio = max(1.0, delta_p_psi / 28.0)
        tds_stress = max(1.0, avg_feed_tds_ppm / 500.0)
        eff_ro_vol = cumulative_liters * (0.6 * pressure_ratio + 0.4 * tds_stress)
        ro_health = max(0.0, 100.0 * (1.0 - (eff_ro_vol / self.rated_capacity_liters[3])))
        ro_fouling = 1.0 + (3.0 * (delta_p_psi / 40.0) * (1.0 - ro_health / 100.0))

        # 4. Stage 4: Post-Carbon
        post_health = max(0.0, 100.0 * (1.0 - (cumulative_liters / self.rated_capacity_liters[4])))
        post_fouling = 1.0 + (1.2 * (1.0 - post_health / 100.0))

        # 5. Stage 5: UV-C LED Chamber
        # Solid-state optical decay over operating hours
        uv_health = max(0.0, 100.0 - uv_power_decay_pct - (cumulative_liters / self.rated_capacity_liters[5]) * 40.0)
        uv_fouling = 1.0 + (0.5 * (1.0 - uv_health / 100.0))

        # 6. Stage 6: UF Capillary Filter
        uf_health = max(0.0, 100.0 * (1.0 - (cumulative_liters / self.rated_capacity_liters[6]) * (1.0 + 0.1 * turbidity_stress)))
        uf_fouling = 1.0 + (1.5 * (1.0 - uf_health / 100.0))

        # 7. Stage 7: Bio-Alkaliser Cartridge
        # Mineral core leaching curve (exponential asymptotic depletion)
        alk_depletion = min(1.0, (cumulative_liters / self.rated_capacity_liters[7]) + (mineral_dissolution_hours / 3000.0))
        alk_health = max(0.0, 100.0 * (1.0 - alk_depletion))
        alk_fouling = 1.0

        raw_healths = [sed_health, carb_health, ro_health, post_health, uv_health, uf_health, alk_health]
        foulings = [sed_fouling, carb_fouling, ro_fouling, post_fouling, uv_fouling, uf_fouling, alk_fouling]
        drivers = [
            f"Colloidal cake buildup (Feed Turbidity: {avg_feed_turbidity_ntu:.1f} NTU)",
            f"Adsorption pore saturation (Feed TOC: {avg_feed_toc_ppm:.1f} mg/L)",
            f"Concentration polarization & scaling (Delta P: {delta_p_psi:.1f} PSI)",
            "Polishing carbon exhaustion",
            "UV-C optical radiometer decay",
            "Capillary hollow fiber cake accumulation",
            "Alkaline mineral core dissolution"
        ]

        # Daily usage assumption for typical Indian household: 15 Liters/Day
        daily_consumption = 15.0

        for sid in range(1, 8):
            h_val = float(raw_healths[sid - 1])
            rated_v = self.rated_capacity_liters[sid]
            rem_liters = max(0, int(rated_v * (h_val / 100.0)))
            rem_days = int(rem_liters / daily_consumption)

            if h_val > 65.0:
                status = "OPTIMAL"
            elif h_val > 35.0:
                status = "GOOD"
            elif h_val > 15.0:
                status = "REPLACE_SOON"
            else:
                status = "CRITICAL_EXHAUSTED"

            name, mech = self.stage_names[sid]
            results[sid] = StageHealth(
                stage_id=sid,
                name=name,
                filtration_mechanism=mech,
                health_pct=round(h_val, 1),
                rul_days=rem_days,
                rul_liters=rem_liters,
                fouling_factor=round(float(foulings[sid - 1]), 2),
                status=status,
                primary_degradation_driver=drivers[sid - 1]
            )

        return results
