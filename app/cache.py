"""
Simple In-Memory LRU Cache with TTL and Token Tracking for GadKille.

Provides sub-millisecond responses for repeated queries, tracks token savings,
and prevents duplicate LLM / embedding API calls.
"""

import logging
import threading
import time
from collections import OrderedDict
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def estimate_tokens(text: str) -> int:
    """
    Estimate token count using the standard ~4 chars/token heuristic.
    Works reliably across English, transliterated names, and code.
    """
    if not text:
        return 0
    clean = text.strip()
    if not clean:
        return 0
    # ~4 characters per token + 1 token per 3 words minimum
    word_count = len(clean.split())
    char_tokens = len(clean) // 4
    return max(1, max(char_tokens, int(word_count * 1.3)))


class SimpleQueryCache:
    """Thread-safe in-memory LRU cache with TTL expiration and metrics."""

    def __init__(self, max_size: int = 256, default_ttl_seconds: float = 300.0):
        self.max_size = max_size
        self.default_ttl = default_ttl_seconds
        self._cache: OrderedDict[str, Tuple[Dict[str, Any], float, int]] = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
        self._tokens_saved = 0

    @staticmethod
    def normalize_key(query: str, namespace: str = "chat") -> str:
        """Normalize query to lowercase whitespace-stripped cache key."""
        clean = " ".join(query.strip().lower().split())
        return f"{namespace}:{clean}"

    def get(self, query: str, namespace: str = "chat") -> Optional[Dict[str, Any]]:
        """Retrieve cached response if present and unexpired."""
        key = self.normalize_key(query, namespace=namespace)
        now = time.time()

        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            data, expiry, tokens = self._cache[key]
            if now > expiry:
                # Expired
                del self._cache[key]
                self._misses += 1
                return None

            # Cache hit: mark as most recently used
            self._cache.move_to_end(key)
            self._hits += 1
            self._tokens_saved += tokens
            logger.info(f"Cache HIT for [{key}] | saved ~{tokens} tokens")
            return data.copy()

    def set(
        self,
        query: str,
        value: Dict[str, Any],
        tokens: int = 0,
        namespace: str = "chat",
        ttl_seconds: Optional[float] = None,
    ) -> None:
        """Store response in cache with TTL and token count."""
        key = self.normalize_key(query, namespace=namespace)
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expiry = time.time() + ttl

        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = (value, expiry, tokens)

            # Evict oldest if exceeding max size
            if len(self._cache) > self.max_size:
                evicted_key, _ = self._cache.popitem(last=False)
                logger.debug(f"Evicted oldest cache entry: {evicted_key}")

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()

    def stats(self) -> Dict[str, Any]:
        """Return cache performance statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_ratio = round((self._hits / total) * 100, 2) if total > 0 else 0.0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_ratio_percent": hit_ratio,
                "tokens_saved": self._tokens_saved,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


# Global singleton cache instance
query_cache = SimpleQueryCache(max_size=256, default_ttl_seconds=300.0)
