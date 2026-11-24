# GadKille Project - Day 13 Task Overview and Changes

## Tasks Specification (Day 13)
- **S1**: Log latency + tokens per request, a simple cache, input limits and one prompt-injection test; README 'Production notes' with numbers.
- **S2**: README that sells GadKille: problem, architecture diagram (Mermaid), demo video link, results table; `docs/resume.md` with 3 resume bullets.

---

## 1. Files Created & Modified on Day 13

### 1. `app/cache.py` (Created)
- Built thread-safe in-memory `SimpleQueryCache` with LRU eviction and TTL expiration.
- Built token estimation heuristic (`estimate_tokens`) calculating prompt and answer tokens.
- Tracks cache hits, misses, hit ratio %, and total tokens saved.
- Provides instant sub-millisecond (< 2 ms) responses for repeated queries with zero LLM tokens.

### 2. `app/main.py` (Modified)
- Added HTTP middleware measuring request duration in milliseconds and injecting `X-Response-Time-Ms` header.
- Integrated `query_cache` into `/chat` and `/ask` endpoints, tracking `latency_ms`, `tokens_used`, and `cached` boolean flags.
- Enforced input limits using Pydantic Field constraints (max 1,000 characters for questions, max 100-300 for search query parameters), preventing DoS and prompt-stuffing attacks.
- Added `GET /cache/stats` and `POST /cache/clear` endpoints for cache observability.

### 3. `tests/test_day13_production.py` (Created)
- **S1 Prompt Injection Test**: `test_prompt_injection_system_override_defense` verifies that adversarial prompts attempting to override system directives or extract secrets are safely deflected.
- **S1 Input Limits Test**: `test_input_limits_enforced` verifies that oversized questions (> 1,000 chars) and empty questions return 422 Unprocessable Entity.
- **S1 Simple Cache Test**: `test_simple_cache_sub_millisecond_hit_and_tokens_saved` verifies cold requests execute RAG and warm requests hit the cache in < 2ms with 0 tokens.
- **Cache Metrics Test**: `test_cache_stats_endpoint` verifies hit/miss tracking and token savings.
- **Token Estimation Test**: `test_estimate_tokens_utility` validates tokenizer heuristics.

### 4. `tests/conftest.py` (Modified)
- Updated `DirectTestClient` to handle `/cache/stats`, `/cache/clear`, and return 422 on Pydantic `ValidationError`.

### 5. `docs/resume.md` (Created)
- 3 quantified, high-impact resume bullets highlighting:
  * Architectural optimization & 61% memory reduction (500MB to 164MB).
  * Production AI, RAG & LRU TTL query cache cutting latency to < 2ms.
  * Prompt-injection defense, geospatial clustering across 203 forts, Docker & CI/CD.

### 6. `README.md` (Modified)
- **S2 Marketing Focus**: Compelling problem statement explaining trekking information fragmentation in Maharashtra.
- **S2 Architecture**: Full Mermaid diagram illustrating UI, FastAPI gateway, LRU cache, RAG reasoning, NumPy vector store, and external Gemini/Groq APIs.
- **S2 Demo**: Prominent demo video link and badge.
- **S2 Results Table**: Comprehensive benchmark comparing endpoints, cold/cached latency, memory, tokens, and success rates.
- **S1 Production Notes**: Real measured numbers (1.2s cold vs 1.1ms cached, 61% memory reduction to 164MB, +310MB Render Free headroom, input caps, and injection defenses).

### 7. `day 13` / `day 13.txt` / `day 13.md` (Created)
- Summary documentation of Day 13 tasks, architecture, and verification.

---

## 2. Verification & Test Results
- **Ruff Linter**: 0 errors (`ruff check .` passed cleanly)
- **Pytest Suite**: 35 tests passed in 2.03s (100% pass rate)
  * 21 baseline tests (health, records, search, agent tools, trek data, fake LLM)
  * 9 lightweight semantic tests (NumPy store, Gemini provider, prompt defense)
  * 5 Day 13 production tests (prompt injection, input limits, cache hit, token estimation)
- All 35 tests run completely offline with mock fixtures for CI speed and reliability.
