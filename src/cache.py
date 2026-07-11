"""
In-memory SHA1 cache for HydraRoute Agent.
Avoids redundant API calls for identical or similar instructions.
Thread-safe for concurrent task processing.
"""

import hashlib
import logging
import threading
from typing import Optional

logger = logging.getLogger("hydraroute.cache")


class InMemoryCache:
    """Thread-safe SHA1-keyed in-memory cache for LLM responses."""

    _instance: Optional["InMemoryCache"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "InMemoryCache":
        """Singleton pattern - one cache shared across all threads."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._cache: dict[str, str] = {}
                    instance._cache_lock = threading.Lock()
                    instance._hits = 0
                    instance._misses = 0
                    cls._instance = instance
        return cls._instance

    def _make_key(self, instruction: str) -> str:
        """Generate a SHA1 hash key from the instruction text."""
        return hashlib.sha1(instruction.strip().encode("utf-8")).hexdigest()

    def get(self, instruction: str) -> Optional[str]:
        """Look up a cached answer for the given instruction.

        Args:
            instruction: The task instruction text.

        Returns:
            Cached answer string, or None if not in cache.
        """
        key = self._make_key(instruction)
        with self._cache_lock:
            result = self._cache.get(key)
            if result is not None:
                self._hits += 1
                logger.info("Cache HIT (key=%s...)", key[:8])
                return result
            self._misses += 1
            return None

    def set(self, instruction: str, answer: str) -> None:
        """Store an answer in the cache.

        Args:
            instruction: The task instruction text.
            answer: The answer to cache.
        """
        if not answer or not instruction:
            return
        key = self._make_key(instruction)
        with self._cache_lock:
            self._cache[key] = answer
        logger.debug("Cache SET (key=%s...)", key[:8])

    def stats(self) -> dict:
        """Return cache statistics."""
        with self._cache_lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            return {
                "size": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate_pct": round(hit_rate, 1),
            }

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._cache_lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
