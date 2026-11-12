# GadKille – Checkpoint 1

## 1. FastAPI Execution

Successfully started the GadKille FastAPI application using:

```bash
uvicorn app.main:app --reload
```

## 2. API Documentation

Opened the Swagger UI documentation at:

http://127.0.0.1:8000/docs

Verified the available API endpoints.

## 3. Function Explanation

**Function:** `health_check()`

The health_check function checks whether the GadKille API is running properly. When a client sends a GET request to `/health`, FastAPI executes this function and returns a JSON response indicating that the application is healthy.

## 4. Checkpoint Status

- FastAPI application executed successfully.
- Swagger UI documentation opened.
- Health endpoint tested.
- Function explanation completed.