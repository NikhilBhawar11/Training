# GadKille – Engineering Resume Bullets

### Nikhil Bhawar – Full-Stack AI & Backend Engineer
*Project: GadKille – Maharashtra Fort Explorer & Intelligent Trek Advisor*

---

### 💼 High-Impact Resume Bullets

* **Architectural Optimization & Memory Reduction (Python, NumPy, Google Gemini API, Render Free):**
  Architected a lightweight semantic retrieval engine migrating from local PyTorch/SentenceTransformers and ChromaDB to Google Gemini Embedding API with an in-memory normalized NumPy vector matrix, slashing runtime RAM usage by **61% (from >500 MB down to 164 MB)**, eliminating container out-of-memory crashes on Render Free's 512 MB tier, shrinking Docker image size by **1.5 GB**, and accelerating vector similarity retrieval to **< 0.5 ms**.

* **Production AI, RAG & Performance Caching (FastAPI, LangGraph, Groq, LRU Caching):**
  Engineered an autonomous multi-agent trekking assistant featuring LangGraph human-in-the-loop approval workflows, grounded RAG with Wikipedia citation verification, and a thread-safe **LRU TTL query cache** that serves repeat queries in **< 2 ms with zero token consumption**, instrumenting HTTP middleware to monitor real-time latency headers (`X-Response-Time-Ms`) and per-request token usage.

* **Security, Geospatial Clustering & DevOps (Streamlit, Folium, Docker, GitHub Actions, Pytest):**
  Implemented robust prompt-injection defenses isolating untrusted retrieved context with strict grounding directives and tool action allowlists; built an interactive Streamlit GIS mapping interface with Haversine distance-based fort clustering across **203 Maharashtra forts**, maintaining **100% automated CI test pass rate across 35 unit/integration tests** with GitHub Actions and multi-container Docker Compose.

---

### 🛠️ Core Technologies Used
`Python 3.11`, `FastAPI`, `Streamlit`, `Google Gemini API`, `Groq API`, `LangGraph`, `NumPy`, `Scikit-Learn`, `Docker`, `Docker Compose`, `Pytest`, `Ruff`, `Render Cloud`, `Folium`.
