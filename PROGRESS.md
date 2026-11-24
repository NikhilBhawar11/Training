# GadKille – Project Progress Tracker

This document tracks all curriculum requirements, milestones, and deliverables for the **GadKille – Maharashtra Fort Explorer** project.

---

## Overall Project Status: 100% Complete (All Items Closed)

| Milestone | Focus Area | Status | Deliverables |
| :--- | :--- | :---: | :--- |
| **Day 01** | Project Setup & CLI Menu | `[x] CLOSED` | `day01_intro.py`, `day01_menu.py`, interactive CLI |
| **Day 02** | Wikipedia Scraping & Data Extraction | `[x] CLOSED` | `app/fetch.py`, `app/article_extractor.py`, article cache |
| **Day 03** | Data Structuring & Schema Design | `[x] CLOSED` | `data/records.json` (203 forts), `app/records.py` |
| **Day 04** | Keyword Search & Evaluation | `[x] CLOSED` | `app/smart_search.py`, search eval set, TF-IDF ranking |
| **Day 05** | Text Chunking Strategies | `[x] CLOSED` | `app/chunking.py`, chunk size & overlap optimization |
| **Day 06** | Vector Storage & Indexing | `[x] CLOSED` | `app/embed.py`, `app/vectorstore.py`, vector embeddings |
| **Day 07** | Semantic Search & Ranking | `[x] CLOSED` | `app/semantic_search.py`, cosine similarity retrieval |
| **Day 08** | Grounded RAG Pipeline & Prompting | `[x] CLOSED` | `app/rag.py`, `app/llm.py`, system prompts, source citations |
| **Day 09** | Autonomous Agent & Spatial Tools | `[x] CLOSED` | `app/agent_loop.py`, `app/graph.py`, `app/tools.py` (Haversine) |
| **Day 10** | Streamlit UI & Interactive Map (CP2) | `[x] CLOSED` | `ui/app.py`, Folium distance rings, trek cards, tag `checkpoint-2` |
| **Day 11** | Test Suite & Containerization | `[x] CLOSED` | `tests/`, `Dockerfile`, `docker-compose.yml`, Ruff linter |
| **Day 12** | CI/CD Pipeline & Render Deployment | `[x] CLOSED` | `.github/workflows/ci.yml`, `render.yaml`, live `/health` |
| **Day 13** | Production Hardening & Marketing | `[x] CLOSED` | `app/cache.py`, latency logging, input limits, `docs/resume.md` |
| **Day 14** | Interview Story, Demo & Final Tag | `[x] CLOSED` | `docs/interview.md`, demo rehearsal, git tag `final` |

---

## Detailed Task Checklist

### Day 01: Project Setup & CLI
- [x] Initialized Git repository and virtual environment (`.venv`).
- [x] Implemented interactive terminal menu in `day01_menu.py`.
- [x] Validated CLI navigation and user feedback loops.

### Day 02: Ingestion & Scraping
- [x] Scraped Wikipedia articles for prominent Maharashtra forts.
- [x] Cached raw Wikipedia HTML to prevent repetitive network requests.
- [x] Extracted clean text while stripping navigational boilerplate.

### Day 03: Data Normalization & Structuring
- [x] Parsed unstructured Wikipedia infoboxes and body content into structured records.
- [x] Normalized elevation units (feet $\leftrightarrow$ meters) with bounds validation ($0\text{--}1,646\text{ m}$).
- [x] Disambiguated duplicate fort entities (e.g. multiple Bhairavgads) using geographic coordinates.
- [x] Persisted 203 structured fort records to `data/records.json`.

### Day 04: Traditional Search & Evaluation
- [x] Built TF-IDF and token-matching engine in `app/smart_search.py`.
- [x] Built evaluation test set and precision/recall scoring benchmark.
- [x] Handled empty queries and edge cases gracefully.

### Day 05: Document Chunking
- [x] Evaluated fixed-size vs sentence-aware vs header-aware chunking.
- [x] Implemented sliding window chunking with configurable overlap in `app/chunking.py`.
- [x] Preserved document IDs, section headers, and metadata tags per chunk.

### Day 06: Vector Database Integration
- [x] Integrated vector embedding generation across document chunks.
- [x] Designed embedding provider abstraction for pluggable local/remote providers.
- [x] Persisted vector representations and chunk metadata.

### Day 07: Semantic Retrieval
- [x] Implemented vector similarity search with cosine similarity scoring.
- [x] Configured dynamic top-$k$ retrieval and minimum similarity thresholds.
- [x] Validated ranking quality on semantic concept queries (e.g. "sea forts built by Shivaji").

### Day 08: Production RAG Pipeline
- [x] Implemented `RAGPipeline` in `app/rag.py` connecting retriever and LLM.
- [x] Integrated multi-provider LLM support (Groq and Google Gemini) in `app/llm.py`.
- [x] Built prompt templates with strict citation attribution.
- [x] Added negative constraint circuit breaker: returns *"This information is not present in the article"* instead of hallucinating missing trek times.

### Day 09: Autonomous Agent & Tools
- [x] Implemented multi-turn ReAct agent loop in `app/agent_loop.py`.
- [x] Implemented deterministic LangGraph state machine workflow in `app/graph.py`.
- [x] Built geospatial proximity tool `forts_within_km` using the Haversine formula in `app/tools.py`.
- [x] Configured Kopargaon ($19.8917^\circ\text{ N}, 74.4789^\circ\text{ E}$) as the default target persona base.

### Day 10: Streamlit Dashboard & Checkpoint 2
- [x] Built full-featured interactive Streamlit frontend in `ui/app.py`.
- [x] Created Folium map with radial distance circles (50 km, 100 km, 150 km) and color-coded fort pins.
- [x] Created standardized Trek Cards for 42 prominent forts in `app/trek_data.py`.
- [x] Added feedback logging (👍 / 👎) with persistence to `data/feedback.jsonl`.
- [x] Tagged repository with `checkpoint-2`.

### Day 11: Testing & Containerization
- [x] Built comprehensive Pytest test suite in `tests/` covering API, RAG, agent tools, and records.
- [x] Configured Ruff linter in `pyproject.toml` with zero tolerated errors.
- [x] Created production `Dockerfile` (Python 3.11-slim) and `.dockerignore`.
- [x] Created `docker-compose.yml` for local multi-container development.

### Day 12: CI/CD & Cloud Deployment
- [x] Implemented GitHub Actions CI pipeline (`.github/workflows/ci.yml`) running lint, tests, and Docker build.
- [x] Deployed live API and UI on Render via `render.yaml` Blueprint.
- [x] Created live health check verification at `https://gadkille-api.onrender.com/health`.
- [x] Set up Hugging Face Spaces frontend mirror.
- [x] Merged feature branch PR into `main` with green CI status badge.

### Day 13: Production Optimization & Marketing
- [x] Resolved Render Free 512 MB OOM issue by replacing PyTorch/ChromaDB with Google Gemini embeddings and a lightweight NumPy vector store (61% memory reduction to 164 MB).
- [x] Implemented thread-safe in-memory `SimpleQueryCache` in `app/cache.py` (sub-2ms warm latency, 0 tokens).
- [x] Added latency logging middleware injecting `X-Response-Time-Ms` and token usage metrics.
- [x] Enforced input length validation caps (max 1,000 characters) against DoS attacks.
- [x] Added prompt injection defense test in `tests/test_day13_production.py`.
- [x] Revamped `README.md` with marketing pitch, Mermaid architecture diagram, demo video, and benchmark table.
- [x] Authored 3 high-impact resume bullet points in `docs/resume.md`.

### Day 14: Interview Story, Rehearsals & Final Release
- [x] Authored 60-second pitch and answers to 10 likely technical questions in `docs/interview.md`.
- [x] Documented the interview story on the hardest problem: handling messy Wikipedia fort data, unit normalization, coordinate deduplication (the two Bhairavgads), and strict hallucination prevention.
- [x] Closed all checklist items across all 14 project milestones in `PROGRESS.md`.
- [x] Rehearsed end-to-end demo twice via automated verification script `scripts/rehearse_demo.py` with 100% pass rate.
- [x] Created Git release tag `final`.
