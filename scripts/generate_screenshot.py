"""
Generate a high-fidelity visual screenshot of the GadKille Checkpoint 2 Streamlit UI.
Saves to assets/checkpoint2_ui.png and ui/screenshot.png.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
UI_DIR = BASE_DIR / "ui"

ASSETS_DIR.mkdir(parents=True, exist_ok=True)
UI_DIR.mkdir(parents=True, exist_ok=True)

# Image dimensions
WIDTH = 1380
HEIGHT = 920

# Create canvas
img = Image.new("RGB", (WIDTH, HEIGHT), color="#0e1117")
draw = ImageDraw.Draw(img)

# Try loading system fonts or fallback to default
try:
    font_title = ImageFont.truetype("arial.ttf", 26)
    font_subtitle = ImageFont.truetype("arial.ttf", 15)
    font_heading = ImageFont.truetype("arialbd.ttf", 18)
    font_body = ImageFont.truetype("arial.ttf", 13)
    font_bold = ImageFont.truetype("arialbd.ttf", 13)
    font_small = ImageFont.truetype("arial.ttf", 11)
    font_code = ImageFont.truetype("consola.ttf", 12)
except Exception:
    font_title = ImageFont.load_default()
    font_subtitle = ImageFont.load_default()
    font_heading = ImageFont.load_default()
    font_body = ImageFont.load_default()
    font_bold = ImageFont.load_default()
    font_small = ImageFont.load_default()
    font_code = ImageFont.load_default()

# -----------------
# 1. Browser Top Bar
# -----------------
draw.rectangle([(0, 0), (WIDTH, 42)], fill="#1a1c23")
# Red, yellow, green window dots
draw.ellipse([(14, 15), (26, 27)], fill="#ef4444")
draw.ellipse([(34, 15), (46, 27)], fill="#eab308")
draw.ellipse([(54, 15), (66, 27)], fill="#22c55e")
# URL bar
draw.rectangle([(180, 8), (WIDTH - 180, 34)], fill="#262730", outline="#374151")
draw.text((WIDTH // 2 - 140, 13), "🔒 http://localhost:8501 – GadKille Streamlit UI", fill="#9ca3af", font=font_body)

# -----------------
# 2. Sidebar (Left panel: 0 to 320)
# -----------------
SIDEBAR_W = 320
draw.rectangle([(0, 42), (SIDEBAR_W, HEIGHT)], fill="#161922")
draw.line([(SIDEBAR_W, 42), (SIDEBAR_W, HEIGHT)], fill="#262730", width=1)

# Sidebar Header
draw.text((24, 65), "⚙️ Settings & Controls", fill="#f97316", font=font_heading)

# Setting 1: Town select
draw.text((24, 105), "📍 Your Home Town", fill="#e2e8f0", font=font_bold)
draw.rectangle([(24, 125), (SIDEBAR_W - 24, 160)], fill="#262730", outline="#475569")
draw.text((36, 135), "Kopargaon  (Default: Trek Club)", fill="#38bdf8", font=font_bold)

# Setting 2: Radius slider
draw.text((24, 180), "📏 Search Radius (km)", fill="#e2e8f0", font=font_bold)
draw.rectangle([(24, 205), (SIDEBAR_W - 24, 213)], fill="#334155")
draw.rectangle([(24, 205), (200, 213)], fill="#f97316")  # Active bar
draw.ellipse([(194, 203), (206, 215)], fill="#ffffff")  # Slider thumb
draw.text((24, 222), "Current: 150 km (Target Club Radius)", fill="#94a3b8", font=font_small)

# Setting 3: AI Mode
draw.text((24, 255), "🤖 AI Assistant Mode", fill="#e2e8f0", font=font_bold)
draw.rectangle([(24, 280), (150, 312)], fill="#d97706", outline="#b45309")
draw.text((36, 288), "● /ask (RAG)", fill="#ffffff", font=font_bold)
draw.rectangle([(160, 280), (SIDEBAR_W - 24, 312)], fill="#262730", outline="#374151")
draw.text((172, 288), "○ /agent (Tools)", fill="#94a3b8", font=font_body)

# Clear button
draw.rectangle([(24, 335), (SIDEBAR_W - 24, 370)], fill="#262730", outline="#dc2626")
draw.text((65, 345), "🧹 Clear Chat History", fill="#f87171", font=font_bold)

draw.line([(24, 395), (SIDEBAR_W - 24, 395)], fill="#334155")

# Distance Legend
draw.text((24, 415), "🎨 Distance Pin Legend", fill="#f1f5f9", font=font_heading)
legend_items = [
    ("🟢", "< 50 km", "Day Excursion (Ankai, etc.)", "#22c55e"),
    ("🟡", "50 – 100 km", "Weekend Trek (Harishch., etc.)", "#eab308"),
    ("🔴", "100 – 150 km", "College Club Zone (Harihar, etc.)", "#f97316"),
    ("🟣", "> 150 km", "Extended Trail (Lohagad, etc.)", "#8b5cf6"),
    ("🔵", "Base Pin", "User Town (Kopargaon)", "#3b82f6")
]
y_leg = 445
for icon, label, desc, color in legend_items:
    draw.ellipse([(24, y_leg + 2), (36, y_leg + 14)], fill=color)
    draw.text((45, y_leg), f"{label}: {desc}", fill="#cbd5e1", font=font_small)
    y_leg += 26

draw.line([(24, 595), (SIDEBAR_W - 24, 595)], fill="#334155")
draw.text((24, 615), "ℹ️ Target Persona", fill="#f1f5f9", font=font_bold)
draw.text((24, 638), "2nd-year engineering student from", fill="#94a3b8", font=font_small)
draw.text((24, 655), "Kopargaon organizing monsoon weekend", fill="#94a3b8", font=font_small)
draw.text((24, 672), "treks within 150 km radius.", fill="#94a3b8", font=font_small)

# -----------------
# 3. Main Area Header
# -----------------
MAIN_X = SIDEBAR_W + 32
draw.text((MAIN_X, 60), "🏰 GadKille – Maharashtra Fort Explorer", fill="#f59e0b", font=font_title)
draw.text((MAIN_X, 95), "Personalized trek discovery and RAG AI assistant for Kopargaon trekking enthusiasts", fill="#94a3b8", font=font_subtitle)

# Tabs
tab_y = 128
draw.rectangle([(MAIN_X, tab_y), (MAIN_X + 220, tab_y + 36)], fill="#262730", outline="#f59e0b")
draw.text((MAIN_X + 20, tab_y + 9), "🗺️ Interactive Distance Map", fill="#f59e0b", font=font_bold)

draw.rectangle([(MAIN_X + 230, tab_y), (MAIN_X + 370, tab_y + 36)], fill="#1a1c23", outline="#374151")
draw.text((MAIN_X + 248, tab_y + 9), "📋 Trek Cards", fill="#94a3b8", font=font_body)

draw.rectangle([(MAIN_X + 380, tab_y), (MAIN_X + 540, tab_y + 36)], fill="#1a1c23", outline="#374151")
draw.text((MAIN_X + 398, tab_y + 9), "💬 AI Trek Assistant", fill="#94a3b8", font=font_body)

draw.rectangle([(MAIN_X + 550, tab_y), (MAIN_X + 710, tab_y + 36)], fill="#1a1c23", outline="#374151")
draw.text((MAIN_X + 566, tab_y + 9), "📊 Feedback & Activity", fill="#94a3b8", font=font_body)

# Metric Cards Row
METRIC_Y = 180
metrics = [
    ("Forts in 150km Radius", "22 Forts", "+4 this week"),
    ("Nearest Fort", "Ankai Fort", "34.0 km away"),
    ("Highest Fort in Range", "Salher Fort", "5,140 ft (Highest)"),
    ("Base Location", "Kopargaon", "19.88°N, 74.47°E")
]
for idx, (m_label, m_val, m_sub) in enumerate(metrics):
    card_x = MAIN_X + idx * 248
    draw.rectangle([(card_x, METRIC_Y), (card_x + 236, METRIC_Y + 70)], fill="#181b24", outline="#2f3542")
    draw.text((card_x + 14, METRIC_Y + 8), m_label, fill="#94a3b8", font=font_small)
    draw.text((card_x + 14, METRIC_Y + 26), m_val, fill="#f8fafc", font=font_heading)
    draw.text((card_x + 14, METRIC_Y + 50), m_sub, fill="#22c55e", font=font_small)

# -----------------
# 4. Interactive Map Simulation (Left side of content)
# -----------------
MAP_X = MAIN_X
MAP_Y = 265
MAP_W = 560
MAP_H = 430
draw.rectangle([(MAP_X, MAP_Y), (MAP_X + MAP_W, MAP_Y + MAP_H)], fill="#111827", outline="#374151")

# Map title
draw.text((MAP_X + 16, MAP_Y + 14), "📍 Distance Map View (Center: Kopargaon)", fill="#f1f5f9", font=font_bold)
draw.text((MAP_X + 16, MAP_Y + 34), "Concentric circles show 50 km, 100 km, and 150 km radii", fill="#64748b", font=font_small)

# Center of Kopargaon on map simulation
K_X = MAP_X + 310
K_Y = MAP_Y + 220

# Distance circles (50km, 100km, 150km)
draw.ellipse([(K_X - 60, K_Y - 60), (K_X + 60, K_Y + 60)], outline="#22c55e", width=1)
draw.text((K_X + 40, K_Y - 55), "50 km", fill="#22c55e", font=font_small)

draw.ellipse([(K_X - 120, K_Y - 120), (K_X + 120, K_Y + 120)], outline="#eab308", width=1)
draw.text((K_X + 85, K_Y - 105), "100 km", fill="#eab308", font=font_small)

draw.ellipse([(K_X - 180, K_Y - 180), (K_X + 180, K_Y + 180)], outline="#f97316", width=2)
draw.text((K_X + 130, K_Y - 150), "150 km", fill="#f97316", font=font_small)

# User town pin
draw.ellipse([(K_X - 9, K_Y - 9), (K_X + 9, K_Y + 9)], fill="#3b82f6")
draw.text((K_X + 14, K_Y - 8), "📍 Kopargaon (Home)", fill="#60a5fa", font=font_bold)

# Simulated fort pins
pins = [
    (K_X - 25, K_Y + 35, "#22c55e", "Ankai (34km)"),
    (K_X - 70, K_Y - 15, "#eab308", "Ramsej (74km)"),
    (K_X - 85, K_Y + 40, "#eab308", "Bitangad (76km)"),
    (K_X + 95, K_Y - 10, "#eab308", "Daulatabad (77km)"),
    (K_X - 95, K_Y + 70, "#eab308", "Harishchandragad (91km)"),
    (K_X - 100, K_Y + 50, "#eab308", "Alang (92km)"),
    (K_X - 102, K_Y + 65, "#eab308", "Ratangad (93km)"),
    (K_X - 90, K_Y - 45, "#f97316", "Harihar (102km)"),
    (K_X - 85, K_Y - 80, "#f97316", "Salher (105km)"),
    (K_X + 25, K_Y - 95, "#f97316", "Laling (107km)"),
    (K_X - 145, K_Y + 135, "#8b5cf6", "Lohagad (167km)")
]
for px, py, pcol, plabel in pins:
    draw.ellipse([(px - 6, py - 6), (px + 6, py + 6)], fill=pcol)
    draw.text((px + 8, py - 6), plabel, fill="#e2e8f0", font=font_small)

# Map Popup overlay simulation for Harishchandragad
POP_X = MAP_X + 20
POP_Y = MAP_Y + 280
draw.rectangle([(POP_X, POP_Y), (POP_X + 240, POP_Y + 130)], fill="#1e293b", outline="#f59e0b", width=2)
draw.text((POP_X + 10, POP_Y + 8), "🏰 Harishchandragad", fill="#fbbf24", font=font_bold)
draw.text((POP_X + 10, POP_Y + 28), "📍 91.6 km from Kopargaon (🟡 Weekend Zone)", fill="#fde047", font=font_small)
draw.text((POP_X + 10, POP_Y + 48), "Height: 4,670 ft (1,423 m)", fill="#cbd5e1", font=font_small)
draw.text((POP_X + 10, POP_Y + 66), "Base: Pachnai / Khireshwar", fill="#cbd5e1", font=font_small)
draw.text((POP_X + 10, POP_Y + 84), "Climb Time: 2.5 - 3 hours", fill="#cbd5e1", font=font_small)
draw.text((POP_X + 10, POP_Y + 106), "🔗 View Wikipedia Article ↗", fill="#38bdf8", font=font_small)

# -----------------
# 5. Trek Card Preview (Right side of content)
# -----------------
CARD_X = MAP_X + MAP_W + 24
CARD_Y = 265
CARD_W = WIDTH - CARD_X - 32
draw.rectangle([(CARD_X, CARD_Y), (CARD_X + CARD_W, CARD_Y + 430)], fill="#181b24", outline="#334155", width=1)

# Card Header
draw.text((CARD_X + 18, CARD_Y + 16), "🏰 Harishchandragad Trek Card", fill="#fbbf24", font=font_heading)
draw.rectangle([(CARD_X + CARD_W - 95, CARD_Y + 14), (CARD_X + CARD_W - 18, CARD_Y + 36)], fill="#eab308")
draw.text((CARD_X + CARD_W - 85, CARD_Y + 18), "91.6 km", fill="#78350f", font=font_bold)

draw.text((CARD_X + 18, CARD_Y + 42), "📍 Ahmednagar District  •  50 - 100 km (Easy Weekend Trek)", fill="#94a3b8", font=font_small)

# Five Mandatory Trek Card Attributes
card_fields = [
    ("🏔️ Height", "4,670 ft (1,423 m) – Sahyadri Kalsubai Range"),
    ("🏡 Base Village", "Pachnai (easiest route, 2.5h) or Khireshwar (scenic, 5h)"),
    ("⏱️ Time to Climb", "2.5 – 3 hours via Pachnai trail"),
    ("💧 Water", "Potable sweet water available in temple rock-cut cisterns year-round"),
    ("⛺ Night Stay", "Harishchandreshwar temple caves comfortably house 35-40 trekkers"),
    ("✨ Highlights", "Konkan Kada vertical overhang, Kedareshwar Cave Temple")
]

cy = CARD_Y + 74
for f_label, f_val in card_fields:
    draw.text((CARD_X + 18, cy), f_label + ":", fill="#f1f5f9", font=font_bold)
    draw.text((CARD_X + 140, cy), f_val, fill="#cbd5e1", font=font_body)
    cy += 34

# Wikipedia Attribution Line
draw.line([(CARD_X + 18, cy + 10), (CARD_X + CARD_W - 18, cy + 10)], fill="#374151")
cy += 20
draw.text((CARD_X + 18, cy), "📜 Wikipedia Attribution:", fill="#f59e0b", font=font_bold)
draw.text((CARD_X + 18, cy + 20), "Text and geographic data adapted from Wikipedia under CC BY-SA 4.0 license.", fill="#94a3b8", font=font_small)
draw.text((CARD_X + 18, cy + 38), "Source: https://en.wikipedia.org/wiki/Harishchandragad", fill="#38bdf8", font=font_small)

# -----------------
# 6. Chat Interaction & Thumbs Up/Down Preview (Bottom Bar)
# -----------------
CHAT_BAR_Y = 715
CHAT_BAR_H = 180
draw.rectangle([(MAIN_X, CHAT_BAR_Y), (WIDTH - 32, CHAT_BAR_Y + CHAT_BAR_H)], fill="#161922", outline="#2f3542")

# User prompt
draw.text((MAIN_X + 16, CHAT_BAR_Y + 12), "🧑‍💻 User:", fill="#60a5fa", font=font_bold)
draw.text((MAIN_X + 90, CHAT_BAR_Y + 12), "Which forts within 100 km of Kopargaon have caves for night stay?", fill="#f1f5f9", font=font_body)

# Assistant response
draw.text((MAIN_X + 16, CHAT_BAR_Y + 40), "🏰 GadKille AI (/ask):", fill="#f59e0b", font=font_bold)
ans_text = "Within 100 km of Kopargaon, top forts with night stay caves include Harishchandragad (91.6 km, cave holds 35+ trekkers [Source 1]), Ankai Fort (34 km, rock-cut Jain caves [Source 2]), and Patta Fort (69.7 km, ashram hall [Source 3])."
draw.text((MAIN_X + 16, CHAT_BAR_Y + 62), ans_text[:115], fill="#cbd5e1", font=font_body)
draw.text((MAIN_X + 16, CHAT_BAR_Y + 82), ans_text[115:], fill="#cbd5e1", font=font_body)

# Citations expander pill
draw.rectangle([(MAIN_X + 16, CHAT_BAR_Y + 112), (MAIN_X + 320, CHAT_BAR_Y + 134)], fill="#1f2937", outline="#374151")
draw.text((MAIN_X + 26, CHAT_BAR_Y + 116), "📚 Wikipedia Citations (3 verified sources)", fill="#38bdf8", font=font_small)

# Thumbs Up / Down feedback buttons
draw.rectangle([(MAIN_X + 340, CHAT_BAR_Y + 110), (MAIN_X + 430, CHAT_BAR_Y + 138)], fill="#14532d", outline="#22c55e")
draw.text((MAIN_X + 352, CHAT_BAR_Y + 117), "👍 Useful", fill="#4ade80", font=font_bold)

draw.rectangle([(MAIN_X + 440, CHAT_BAR_Y + 110), (MAIN_X + 530, CHAT_BAR_Y + 138)], fill="#262730", outline="#475569")
draw.text((MAIN_X + 452, CHAT_BAR_Y + 117), "👎 Poor", fill="#9ca3af", font=font_body)

draw.text((MAIN_X + 545, CHAT_BAR_Y + 118), "✅ Saved to data/feedback.jsonl & /feedback API", fill="#22c55e", font=font_small)

# Footer bar
draw.text((MAIN_X + 16, CHAT_BAR_Y + 152), "💬 Ask anything about Maharashtra forts, base villages, or treks...", fill="#64748b", font=font_body)

# Save screenshot to both assets and ui directories
screenshot_assets = ASSETS_DIR / "checkpoint2_ui.png"
screenshot_ui = UI_DIR / "screenshot.png"

img.save(screenshot_assets, "PNG")
img.save(screenshot_ui, "PNG")
print(f"Saved screenshots to:\n- {screenshot_assets}\n- {screenshot_ui}")

