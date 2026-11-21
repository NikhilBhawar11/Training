# GadKille Deployment & Project Tracker

## Project Overview
- **Project Name:** GadKille – Maharashtra Fort Explorer
- **Developer:** Nikhil Bhawar
- **Repository:** https://github.com/NikhilBhawar11/Training
- **Target Persona:** Second-year engineering student from Kopargaon organizing monsoon weekend treks within 150 km.

---

## Live Deployment URLs

| Component | Platform | Live URL | Public Status |
| :--- | :--- | :--- | :---: |
| **FastAPI Backend** | Render | https://gadkille-api.onrender.com | 🟢 Active |
| **Health Check Endpoint** | Render | https://gadkille-api.onrender.com/health | 🟢 200 OK |
| **API Documentation (Swagger)** | Render | https://gadkille-api.onrender.com/docs | 🟢 Active |
| **Interactive Streamlit UI** | Render | https://gadkille-ui.onrender.com | 🟢 Active |
| **Streamlit Mirror (Hugging Face)** | HF Spaces | https://huggingface.co/spaces/NikhilBhawar11/GadKille | 🟢 Active |

---

## Health Check Verification

The `/health` endpoint is publicly accessible and returns:

```json
{
  "status": "healthy",
  "project": "GadKille"
}
```

Curl verification command:
```bash
curl -i https://gadkille-api.onrender.com/health
```

Expected HTTP status: `200 OK`

---

## CI/CD Pipeline Tracking

- **Workflow File:** `.github/workflows/ci.yml`
- **Trigger Events:** `push` on `main`, `pull_request` on `main`, `workflow_dispatch`
- **Pipeline Jobs:**
  1. `lint`: Ruff linter (`ruff check .`)
  2. `test`: Pytest test suite (`pytest tests/ -v`, 21 tests)
  3. `docker-build`: Container image build (`docker build -t gadkille:ci .`)
- **CI Status Badge:**
  [![CI](https://github.com/NikhilBhawar11/Training/actions/workflows/ci.yml/badge.svg)](https://github.com/NikhilBhawar11/Training/actions/workflows/ci.yml)
- **Feature Branch PR:** Merged `feature/day-12-ci-cd-deploy` into `main` with green CI.

---

## Deployment Configuration Files

- `render.yaml`: Multi-service Render Blueprint definition for `gadkille-api` and `gadkille-ui`.
- `Dockerfile`: Production Python 3.11-slim container.
- `.dockerignore`: Excluded non-runtime files and secrets.
- `docker-compose.yml`: Local and staging multi-container configuration.
