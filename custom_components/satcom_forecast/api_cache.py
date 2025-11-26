"""
API Caching Module

This module implements caching for API responses to reduce API calls
and improve performance.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

_LOGGER = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached API response."""

    data: Any
    timestamp: float
    ttl: float  # Time to live in seconds
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)


class APICache:
    """Thread-safe cache for API responses."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300) -> None:
        """
        Initialize the cache.

        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._stats = {"hits": 0, "misses": 0, "evictions": 0, "total_requests": 0}

    def _generate_key(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a cache key for an API request.

        Args:
            endpoint: API endpoint
            params: Request parameters

        Returns:
            Cache key string
        """
        if params:
            # Sort parameters for consistent keys
            sorted_params = sorted(params.items())
            param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
            return f"{endpoint}?{param_str}"
        return endpoint

    def _is_expired(self, entry: CacheEntry) -> bool:
        """
        Check if a cache entry is expired.

        Args:
            entry: Cache entry to check

        Returns:
            True if expired
        """
        return time.time() - entry.timestamp > entry.ttl

    def _evict_lru(self) -> None:
        """Evict least recently used entries."""
        if len(self._cache) < self.max_size:
            return

        # Sort by last accessed time and remove oldest entries
        sorted_entries = sorted(self._cache.items(), key=lambda x: x[1].last_accessed)

        # Remove oldest 10% of entries
        evict_count = max(1, len(sorted_entries) // 10)
        for i in range(evict_count):
            key, _ = sorted_entries[i]
            del self._cache[key]
            self._stats["evictions"] += 1

        _LOGGER.debug(f"Evicted {evict_count} cache entries")

    async def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """
        Get data from cache.

        Args:
            endpoint: API endpoint
            params: Request parameters

        Returns:
            Cached data or None if not found/expired
        """
        async with self._lock:
            key = self._generate_key(endpoint, params)
            self._stats["total_requests"] += 1

            if key not in self._cache:
                self._stats["misses"] += 1
                _LOGGER.debug(f"Cache miss for key: {key}")
                return None

            entry = self._cache[key]

            if self._is_expired(entry):
                del self._cache[key]
                self._stats["misses"] += 1
                _LOGGER.debug(f"Cache entry expired for key: {key}")
                return None

            # Update access statistics
            entry.access_count += 1
            entry.last_accessed = time.time()
            self._stats["hits"] += 1

            _LOGGER.debug(f"Cache hit for key: {key}")
            return entry.data

    async def set(
        self,
        endpoint: str,
        data: Any,
        params: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None,
    ) -> None:
        """
        Store data in cache.

        Args:
            endpoint: API endpoint
            data: Data to cache
            params: Request parameters
            ttl: Time-to-live in seconds (uses default if None)
        """
        async with self._lock:
            key = self._generate_key(endpoint, params)
            ttl = ttl or self.default_ttl

            # Evict LRU entries if cache is full
            if len(self._cache) >= self.max_size:
                self._evict_lru()

            entry = CacheEntry(data=data, timestamp=time.time(), ttl=ttl)

            self._cache[key] = entry
            _LOGGER.debug(f"Cached data for key: {key} (TTL: {ttl}s)")

    async def delete(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Delete data from cache.

        Args:
            endpoint: API endpoint
            params: Request parameters

        Returns:
            True if entry was deleted
        """
        async with self._lock:
            key = self._generate_key(endpoint, params)

            if key in self._cache:
                del self._cache[key]
                _LOGGER.debug(f"Deleted cache entry for key: {key}")
                return True

            return False

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            _LOGGER.info("Cache cleared")

    async def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        async with self._lock:
            expired_keys = []
            current_time = time.time()

            for key, entry in self._cache.items():
                if current_time - entry.timestamp > entry.ttl:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                _LOGGER.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

            return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._stats["total_requests"]
        hit_rate = (
            (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        )

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "hit_rate": round(hit_rate, 2),
            "evictions": self._stats["evictions"],
            "total_requests": total_requests,
        }

    def get_entries_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all cache entries.

        Returns:
            List of entry information dictionaries
        """
        current_time = time.time()
        entries = []

        for key, entry in self._cache.items():
            age = current_time - entry.timestamp
            time_since_access = current_time - entry.last_accessed
            is_expired = self._is_expired(entry)

            entries.append(
                {
                    "key": key,
                    "age_seconds": round(age, 2),
                    "ttl_seconds": entry.ttl,
                    "access_count": entry.access_count,
                    "time_since_access": round(time_since_access, 2),
                    "is_expired": is_expired,
                }
            )

        return entries


class CacheManager:
    """Manages multiple caches for different data types."""

    def __init__(self) -> None:
        self._caches: Dict[str, APICache] = {}
        self._cleanup_task: Optional[asyncio.Task] = None

    def get_cache(
        self, cache_name: str, max_size: int = 1000, default_ttl: int = 300
    ) -> APICache:
        """
        Get or create a cache instance.

        Args:
            cache_name: Name of the cache
            max_size: Maximum cache size
            default_ttl: Default TTL in seconds

        Returns:
            APICache instance
        """
        if cache_name not in self._caches:
            self._caches[cache_name] = APICache(
                max_size=max_size, default_ttl=default_ttl
            )
            _LOGGER.debug(f"Created cache: {cache_name}")

        return self._caches[cache_name]

    async def start_cleanup_task(self, interval: int = 300) -> None:
        """
        Start background cleanup task.

        Args:
            interval: Cleanup interval in seconds
        """
        if self._cleanup_task and not self._cleanup_task.done():
            return

        async def cleanup_loop() -> None:
            while True:
                try:
                    total_cleaned = 0
                    for cache in self._caches.values():
                        cleaned = await cache.cleanup_expired()
                        total_cleaned += cleaned

                    if total_cleaned > 0:
                        _LOGGER.debug(
                            f"Background cleanup removed {total_cleaned} expired entries"
                        )

                    await asyncio.sleep(interval)
                except asyncio.CancelledError:
                    break
                except Exception:
                    _LOGGER.exception("Error in cache cleanup task")
                    await asyncio.sleep(interval)

        self._cleanup_task = asyncio.create_task(cleanup_loop())
        _LOGGER.info(f"Started cache cleanup task (interval: {interval}s)")

    async def stop_cleanup_task(self) -> None:
        """Stop background cleanup task."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            _LOGGER.info("Stopped cache cleanup task")

    async def clear_all_caches(self) -> None:
        """Clear all caches."""
        for cache_name, cache in self._caches.items():
            await cache.clear()
            _LOGGER.debug(f"Cleared cache: {cache_name}")

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all caches.

        Returns:
            Dictionary with cache statistics
        """
        stats = {}
        for cache_name, cache in self._caches.items():
            stats[cache_name] = cache.get_stats()
        return stats


# Global cache manager instance
cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """Get the global cache manager."""
    return cache_manager


def get_gridpoint_cache() -> APICache:
    """Get cache for grid point data (24 hour TTL)."""
    return cache_manager.get_cache("gridpoint", max_size=1000, default_ttl=86400)


def get_forecast_cache() -> APICache:
    """Get cache for forecast data (1 hour TTL)."""
    return cache_manager.get_cache("forecast", max_size=1000, default_ttl=3600)


def get_alerts_cache() -> APICache:
    """Get cache for alerts data (30 minute TTL)."""
    return cache_manager.get_cache("alerts", max_size=100, default_ttl=1800)
