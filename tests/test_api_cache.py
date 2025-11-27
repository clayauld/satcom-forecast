"""Test the API Cache."""

import asyncio

import pytest

from custom_components.satcom_forecast.api_cache import (
    APICache,
    CacheManager,
    get_alerts_cache,
    get_cache_manager,
    get_forecast_cache,
    get_gridpoint_cache,
)


@pytest.fixture
def cache():
    """Create an APICache instance."""
    return APICache(max_size=5, default_ttl=1)


async def test_cache_set_get(cache):
    """Test setting and getting cache entries."""
    await cache.set("test_endpoint", "test_data")

    data = await cache.get("test_endpoint")
    assert data == "test_data"

    # Test with params
    params = {"key": "value"}
    await cache.set("test_endpoint", "test_data_params", params=params)

    data = await cache.get("test_endpoint", params=params)
    assert data == "test_data_params"

    # Ensure params matter
    data = await cache.get("test_endpoint", params={"key": "other"})
    assert data is None


async def test_cache_expiration(cache):
    """Test cache expiration."""
    await cache.set("test_endpoint", "test_data", ttl=0.1)

    data = await cache.get("test_endpoint")
    assert data == "test_data"

    await asyncio.sleep(0.15)

    data = await cache.get("test_endpoint")
    assert data is None


async def test_cache_eviction(cache):
    """Test cache eviction (LRU)."""
    # Fill cache
    for i in range(5):
        await cache.set(f"endpoint_{i}", f"data_{i}")

    assert len(cache._cache) == 5

    # Access endpoint_0 to make it recently used
    await cache.get("endpoint_0")

    # Add one more
    await cache.set("endpoint_5", "data_5")

    # Should evict oldest (endpoint_1, since endpoint_0 was accessed)
    # Wait, implementation evicts oldest 10%. 5 // 10 = 0. max(1, 0) = 1.
    # So 1 entry evicted.

    assert len(cache._cache) == 5

    # endpoint_1 should be gone (it was inserted second, but endpoint_0 was accessed recently)
    # Insertion order: 0, 1, 2, 3, 4.
    # Access: 0.
    # LRU order: 1, 2, 3, 4, 0.
    # Evict 1.

    data = await cache.get("endpoint_1")
    assert data is None

    data = await cache.get("endpoint_0")
    assert data == "data_0"


async def test_cache_delete(cache):
    """Test deleting cache entries."""
    await cache.set("test_endpoint", "test_data")

    deleted = await cache.delete("test_endpoint")
    assert deleted is True

    data = await cache.get("test_endpoint")
    assert data is None

    deleted = await cache.delete("non_existent")
    assert deleted is False


async def test_cache_clear(cache):
    """Test clearing cache."""
    await cache.set("test_endpoint", "test_data")
    await cache.clear()

    assert len(cache._cache) == 0


async def test_cache_cleanup_expired(cache):
    """Test cleanup of expired entries."""
    await cache.set("expired", "data", ttl=0.1)
    await cache.set("valid", "data", ttl=10)

    await asyncio.sleep(0.15)

    removed = await cache.cleanup_expired()
    assert removed == 1

    assert await cache.get("expired") is None
    assert await cache.get("valid") == "data"


async def test_cache_manager():
    """Test CacheManager."""
    manager = CacheManager()

    cache1 = manager.get_cache("test1")
    cache2 = manager.get_cache("test2")
    cache1_again = manager.get_cache("test1")

    assert cache1 is not cache2
    assert cache1 is cache1_again

    # Test cleanup task
    await manager.start_cleanup_task(interval=0.1)
    assert manager._cleanup_task is not None

    await asyncio.sleep(0.2)

    await manager.stop_cleanup_task()
    assert manager._cleanup_task.cancelled() or manager._cleanup_task.done()


def test_helper_functions():
    """Test helper functions."""
    assert isinstance(get_cache_manager(), CacheManager)
    assert isinstance(get_gridpoint_cache(), APICache)
    assert isinstance(get_forecast_cache(), APICache)
    assert isinstance(get_alerts_cache(), APICache)
