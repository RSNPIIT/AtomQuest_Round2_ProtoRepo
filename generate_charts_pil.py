from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1400, 520
img = Image.new("RGB", (W, H), "#ffffff")
draw = ImageDraw.Draw(img)

# Try loading standard font or fallback
try:
    font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
    font_bold = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
    font_main = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13)
    font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
except Exception:
    font_title = font_bold = font_main = font_small = ImageFont.load_default()

# Background panels
draw.rounded_rectangle([20, 20, 670, 490], radius=8, fill="#f8fafc", outline="#cbd5e1", width=1)
draw.rounded_rectangle([710, 20, 1370, 490], radius=8, fill="#f8fafc", outline="#cbd5e1", width=1)

# Panel 1: Blind TDS Dilemma
draw.text((40, 35), "FIGURE 1: THE 'BLIND TDS' DILEMMA VS ATOMSENSE", fill="#0f172a", font=font_title)
draw.text((40, 68), "Why Single-Metric TDS Fails in Real-World Indian Groundwater & Runoff", fill="#64748b", font=font_small)

categories = [
    ("Municipal Tap", 185, 12, "Normal"),
    ("Hard Borewell", 930, 18, "Safe (High Ca/Mg)"),
    ("Monsoon Flood", 350, 78, "HAZARD (Organics)"),
    ("Industrial Spill", 300, 96, "CRITICAL (Metals)"),
    ("RO Rupture", 780, 92, "LEAKAGE BREACH")
]

start_y = 105
for i, (cat, tds, risk, status) in enumerate(categories):
    y = start_y + i * 72
    # Category Label
    draw.text((40, y), cat, fill="#1e293b", font=font_bold)
    draw.text((40, y + 20), f"Status: {status}", fill="#e11d48" if "HAZARD" in status or "CRITICAL" in status or "BREACH" in status else "#0d9488", font=font_small)

    # Bar 1: TDS (Slate)
    w_tds = int((tds / 1000.0) * 220)
    draw.rounded_rectangle([210, y + 2, 210 + w_tds, y + 16], radius=3, fill="#64748b")
    draw.text((220 + w_tds, y + 2), f"{tds} ppm TDS", fill="#334155", font=font_small)

    # Bar 2: True Risk (Coral)
    w_risk = int((risk / 100.0) * 220)
    risk_col = "#e11d48" if risk > 50 else ("#f59e0b" if risk > 25 else "#10b981")
    draw.rounded_rectangle([210, y + 22, 210 + w_risk, y + 36], radius=3, fill=risk_col)
    draw.text((220 + w_risk, y + 22), f"{risk}% Contaminant Hazard", fill=risk_col, font=font_small)

# Panel 2: 7-Stage Filter Prognostics
draw.text((730, 35), "FIGURE 2: 7-STAGE REAL-TIME FILTER HEALTH & RUL", fill="#0f172a", font=font_title)
draw.text((730, 68), "Physics-Informed Remaining Useful Life (RUL) & Membrane Fouling Tracking", fill="#64748b", font=font_small)

stages = [
    ("Stage 1: Sediment Pre-Filter", 48, "68 Days left", "#f59e0b"),
    ("Stage 2: Pre-Carbon Block", 62, "115 Days left", "#10b981"),
    ("Stage 3: High-Recovery RO", 79, "210 Days left", "#10b981"),
    ("Stage 4: Post-Carbon Polisher", 81, "180 Days left", "#10b981"),
    ("Stage 5: UV-C LED Sterilizer", 92, "420 Days left", "#10b981"),
    ("Stage 6: UF Hollow Fiber", 85, "260 Days left", "#10b981"),
    ("Stage 7: Bio-Alkaliser Core", 54, "82 Days left", "#f59e0b")
]

start_y2 = 100
for i, (stg, health, rul, col) in enumerate(stages):
    y = start_y2 + i * 52
    draw.text((730, y), stg, fill="#1e293b", font=font_bold)
    
    # Track background
    draw.rounded_rectangle([1030, y + 2, 1260, y + 16], radius=3, fill="#e2e8f0")
    # Health fill
    w_h = int((health / 100.0) * 230)
    draw.rounded_rectangle([1030, y + 2, 1030 + w_h, y + 16], radius=3, fill=col)
    
    draw.text((1270, y + 1), f"{health}%", fill=col, font=font_bold)
    draw.text((730, y + 20), f"RUL: {rul} • Degradation Model: Active Telemetry", fill="#64748b", font=font_small)

img.save("/Users/ramrupsatpati/Downloads/AtomQuest_Round2_ProtoRepo/progress_charts.png")
print("Saved progress_charts.png using PIL successfully!")
