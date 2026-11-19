# GadKille – Maharashtra Fort Explorer

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.162.0-teal.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.67.0-red.svg)](https://streamlit.io/)
[![Checkpoint 2](https://img.shields.io/badge/Checkpoint-2%20Live%20Demo-brightgreen.svg)]()

## Product
**GadKille** is a Generative AI-powered Maharashtra Fort Explorer and intelligent trek advisor that helps users explore fort history, trekking difficulty, base villages, water sources, night stay options, and accurate distances from their hometown.

## Target User Persona
A second-year engineering student from **Kopargaon** who leads a college trekking club and wants to discover forts within **150 km** for monsoon weekend treks.

![GadKille Streamlit UI](assets/checkpoint2_ui.png)

---

## Day 10 / Checkpoint 2 Features

### 1. Streamlit AI Chat (`ui/app.py`)
- **Dual Query Modes**: Toggle between `/ask` (direct RAG retrieval with confidence scoring) and `/agent` (autonomous tool agent combining RAG and distance search).
- **Wikipedia Citations**: Every AI-generated answer displays verified source citations linking directly to the underlying Wikipedia articles.
- **Thumbs Up / Down Feedback**: Interactive 👍 and 👎 feedback buttons per assistant response that persistently save ratings, timestamps, and queries to `data/feedback.jsonl` and the `/feedback` FastAPI endpoint.

### 2. Signature Feature: Interactive Distance-Colored Fort Map
- **User Hometown Anchoring**: Defaults to **Kopargaon** (with support for Nashik, Pune, Mumbai, Shirdi, Ahmednagar, etc.).
- **Distance-Coded Pins**: Forts across Maharashtra are pinned and colored based on road/geodesic distance from the user's selected town:
  - 🟢 **< 50 km**: Day Excursion (e.g., Ankai Fort – 34 km)
  - 🟡 **50 – 100 km**: Easy Weekend Trek (e.g., Patta Fort – 69.7 km, Harishchandragad – 91.6 km)
  - 🔴 **100 – 150 km**: Target Club Radius (e.g., Harihar Fort – 102 km, Salher – 105 km)
  - 🟣 **> 150 km**: Extended Weekend Trails (e.g., Lohagad, Rajgad, Torna)
  - 🔵 **Home Pin**: User's chosen base town with radial distance rings (50 km, 100 km, 150 km).
- **Interactive Tooltips & Popups**: Click any pin to see distance, elevation, base village, and climb time.

### 3. Signature Feature: Fort Trek Cards
Every fort features a standardized **Trek Card** providing 5 essential trekking attributes:
1. 🏔️ **Height**: Elevation in feet and meters (e.g., `4,670 ft (1,423 m)`).
2. 🏡 **Base Village**: Primary starting hamlet or village (e.g., `Pachnai / Khireshwar`).
3. ⏱️ **Time to Climb**: Ascent duration (e.g., `2.5 - 3 hours`).
4. 💧 **Water Availability**: Potable water sources, rock cisterns, or seasonal warnings.
5. ⛺ **Night Stay**: Cave capacity, temple shelter, or campsite details.
6. 📜 **Wikipedia Attribution Line**:
   > *"Text and geographic data adapted from Wikipedia under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)."*

---

## Problem Statement
Information about Maharashtra forts is scattered across different blogs, forums, and websites. Finding verified fort history, trekking details, base villages, and nearby locations is difficult. 

GadKille provides a unified platform to explore forts, calculate distances, visualize geographic routes, and get accurate answers through an AI-powered assistant.

## Data Sources
1. [List of forts in Maharashtra (Wikipedia)](https://en.wikipedia.org/wiki/List_of_forts_in_Maharashtra)
2. [Template:Forts in Maharashtra (Wikipedia)](https://en.wikipedia.org/wiki/Template:Forts_in_Maharashtra)
3. Direct Wikipedia article extracts under the CC BY-SA 4.0 license.

---

## How to Run GadKille (Checkpoint 2 Live Demo)

### 1. Activate the Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Start the FastAPI Backend Server

```powershell
uvicorn app.main:app --reload --port 8000
```
- API Docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`
- Feedback API: `http://127.0.0.1:8000/feedback`

### 3. Launch the Streamlit Frontend UI

In a separate terminal (with the virtual environment activated):

```powershell
streamlit run ui/app.py
```
The application will open in your browser at `http://localhost:8501`.

---

## Project Structure

```
GadKille/
├── app/
│   ├── main.py                  # FastAPI server (/ask, /agent, /feedback, /records)
│   ├── rag.py                   # RAG Pipeline with ChromaDB vector search & prompt rules
│   ├── agent_loop.py            # Autonomous agent deciding between RAG and distance tools
│   ├── tools.py                 # Haversine distance calculator & forts_within_km
│   ├── trek_data.py             # Trek Card generator & distance provider
│   ├── semantic_search.py       # Semantic vector retrieval engine
│   └── records.py               # Fort record database accessor
├── data/
│   ├── records.json             # 203 fort records with coordinates & trek data
│   ├── trek_cards.json          # Master 42 Trek Cards with height, base, climb, water, stay
│   ├── towns.csv                # Town coordinates (Kopargaon, Nashik, Pune, etc.)
│   ├── feedback.jsonl           # Persistent user thumbs up / down feedback log
│   └── raw/                     # Downloaded Wikipedia articles and raw HTML
├── ui/
│   ├── app.py                   # Streamlit multi-tab Chat, Map, Trek Cards & Feedback UI
│   └── screenshot.png           # Checkpoint 2 UI screenshot
├── assets/
│   └── checkpoint2_ui.png       # UI screenshot preview for README
├── task-docs/
│   ├── checkpoint_1.md          # Checkpoint 1 documentation
│   └── checkpoint_2.md          # Checkpoint 2 live demo walkthrough
├── day 10.md                    # Detailed Day 10 task overview and changelog
└── requirements.txt             # Project dependencies
```
