# GadKille – Checkpoint 2 Live Demo

## 1. Overview
Checkpoint 2 delivers the full frontend and backend integration for **GadKille**, a Generative AI-powered Maharashtra Fort Explorer tailored for a college trekking club leader from **Kopargaon** seeking weekend treks within **150 km**.

---

## 2. Live Demo Architecture

```
+-----------------------------------------------------------+
|                     Streamlit UI                          |
|                     (ui/app.py)                           |
+-----------------------------+-----------------------------+
                              |
     +------------------------+------------------------+
     | HTTP POST /ask         | HTTP POST /agent       | HTTP POST /feedback
     v                        v                        v
+-----------------------------------------------------------+
|                     FastAPI Backend                       |
|                      (app/main.py)                        |
+-----------------------------+-----------------------------+
     |                        |                        |
     v                        v                        v
+---------------+     +---------------+     +---------------+
|  RAGPipeline  |     | GadKilleAgent |     | Feedback Store|
|  (app/rag.py) |     |(agent_loop.py)|     |(feedback.jsonl|
+---------------+     +---------------+     +---------------+
     |                        |
     +------------+-----------+
                  |
                  v
       +--------------------+
       |  Tools / Distance  |
       |   (app/tools.py)   |
       +--------------------+
                  |
                  v
       +--------------------+
       | Master Trek Cards  |
       | (data/trek_cards)  |
       +--------------------+
```

---

## 3. Key Components Demonstrated

### A. Streamlit Chat Interface (`ui/app.py`)
- **Mode Toggle**: Switches between `/ask` (RAG Q&A with similarity thresholds) and `/agent` (Agent loop orchestrating RAG + distance calculations).
- **Wikipedia Citations**: Explicit citations linked to Wikipedia sources for every claim made by the assistant.
- **Thumbs Up / Down Feedback**: Interactive buttons below each response allowing users to rate utility; recorded persistently in `data/feedback.jsonl` and via `/feedback` endpoint.

### B. Signature Feature: Distance-Colored Map View
- Anchored to the user's home town (**Kopargaon** by default).
- Dynamic Folium Leaflet map with radius circles (50 km, 100 km, 150 km).
- Pins colored by distance:
  - 🟢 `< 50 km`: Day excursion (e.g. Ankai Fort – 34 km)
  - 🟡 `50 – 100 km`: Easy weekend trek (e.g. Patta Fort – 69.7 km, Harishchandragad – 91.6 km)
  - 🔴 `100 – 150 km`: Target club zone (e.g. Harihar Fort – 102 km, Salher – 105 km)
  - 🟣 `> 150 km`: Extended excursion (e.g. Lohagad, Rajgad, Torna)
  - 🔵 `Home Pin`: User reference location (Kopargaon).
- Interactive popup showing fort name, distance, height, base village, and climb time.

### C. Signature Feature: Fort Trek Cards
Each fort features a detailed trek profile with the 5 required parameters:
1. **Height**: e.g., `4,670 ft (1,423 m)`
2. **Base Village**: e.g., `Pachnai / Khireshwar`
3. **Time to Climb**: e.g., `2.5 - 3 hours`
4. **Water Availability**: e.g., `Potable sweet water available in temple cisterns year-round`
5. **Night Stay**: e.g., `Harishchandreshwar temple caves comfortably accommodate 35-40 trekkers`
6. **Wikipedia Attribution Line**:
   > *"Text and geographic data adapted from Wikipedia under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)."*

---

## 4. How to Run the Live Demo

### Step 1: Start Backend API
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```
- Swagger Docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

### Step 2: Start Streamlit Frontend
```powershell
.\.venv\Scripts\Activate.ps1
streamlit run ui/app.py
```
- Application opens at: `http://localhost:8501`

---

## 5. Verification Checklist

| Test Item | Expected Result | Status |
| :--- | :--- | :---: |
| `/health` endpoint | Returns 200 OK with `status: healthy` | ✅ PASS |
| Streamlit launch | UI opens with tabs for Map, Cards, Chat, Stats | ✅ PASS |
| `/ask` Q&A | Returns answer with confidence and Wikipedia sources | ✅ PASS |
| `/agent` Q&A | Reasons, runs distance and/or RAG tools, returns results | ✅ PASS |
| Thumbs Up/Down | Saves rating to `data/feedback.jsonl` and `/feedback` | ✅ PASS |
| Map distance pins | Coloured green, yellow, red, purple by distance from Kopargaon | ✅ PASS |
| Trek Cards | Displays height, base village, climb time, water, stay, and attribution | ✅ PASS |
| UI Screenshot | Embedded in `README.md` and saved to `assets/` and `ui/` | ✅ PASS |
| Git Tag | Tagged `checkpoint-2` on repository | ✅ PASS |
