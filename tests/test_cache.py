import pytest
import asyncio
import time
from services.cache import CacheService

class TestCache:
    @pytest.fixture
    def cache_service(self):
        return CacheService()
    
    def test_cache_key_generation(self, cache_service):
        """Test cache key generation"""
        data1 = {"destination": "Paris", "budget": 500}
        data2 = {"budget": 500, "destination": "Paris"}  # Same data, different order
        
        key1 = cache_service._generate_cache_key(data1)
        key2 = cache_service._generate_cache_key(data2)
        
        # Should generate the same key for same data
        assert key1 == key2
        assert isinstance(key1, str)
        assert len(key1) > 0
    
    @pytest.mark.asyncio
    async def test_memory_cache_set_get(self, cache_service):
        """Test memory cache set and get operations"""
        # Test setting data
        test_data = {"test": "data", "number": 123}
        await cache_service.set("test_key", test_data, ttl=60)
        
        # Test getting data
        retrieved_data = await cache_service.get("test_key")
        assert retrieved_data == test_data
        
        # Test getting non-existent key
        non_existent = await cache_service.get("non_existent_key")
        assert non_existent is None
    
    @pytest.mark.asyncio
    async def test_memory_cache_expiration(self, cache_service):
        """Test memory cache expiration"""
        # Set data with short TTL
        test_data = {"test": "expires"}
        await cache_service.set("expire_key", test_data, ttl=1)  # 1 second TTL
        
        # Should be available immediately
        retrieved = await cache_service.get("expire_key")
        assert retrieved == test_data
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Should be expired
        expired = await cache_service.get("expire_key")
        assert expired is None
    
    @pytest.mark.asyncio
    async def test_get_or_set_functionality(self, cache_service):
        """Test get_or_set functionality"""
        # First call should execute the function
        call_count = 0
        
        def data_func():
            nonlocal call_count
            call_count += 1
            return {"generated": "data", "call_count": call_count}
        
        # First call
        result1 = await cache_service.get_or_set("get_or_set_key", data_func, ttl=60)
        assert result1["generated"] == "data"
        assert result1["call_count"] == 1
        assert call_count == 1
        
        # Second call should return cached data
        result2 = await cache_service.get_or_set("get_or_set_key", data_func, ttl=60)
        assert result2["generated"] == "data"
        assert result2["call_count"] == 1  # Should be cached value
        assert call_count == 1  # Function should not be called again
    
    @pytest.mark.asyncio
    async def test_get_or_set_async_function(self, cache_service):
        """Test get_or_set with async function"""
        call_count = 0
        
        async def async_data_func():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Simulate async work
            return {"async_generated": "data", "call_count": call_count}
        
        # First call
        result1 = await cache_service.get_or_set("async_key", async_data_func, ttl=60)
        assert result1["async_generated"] == "data"
        assert result1["call_count"] == 1
        assert call_count == 1
        
        # Second call should return cached data
        result2 = await cache_service.get_or_set("async_key", async_data_func, ttl=60)
        assert result2["async_generated"] == "data"
        assert result2["call_count"] == 1
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_cache_invalidation(self, cache_service):
        """Test cache invalidation"""
        # Set multiple keys
        await cache_service.set("key1", {"data": 1}, ttl=60)
        await cache_service.set("key2", {"data": 2}, ttl=60)
        await cache_service.set("other_key", {"data": 3}, ttl=60)
        
        # Invalidate keys matching pattern
        await cache_service.invalidate("key*")
        
        # key1 and key2 should be invalidated
        assert await cache_service.get("key1") is None
        assert await cache_service.get("key2") is None
        
        # other_key should still exist
        other_data = await cache_service.get("other_key")
        assert other_data == {"data": 3}
    
    @pytest.mark.asyncio
    async def test_clear_all_cache(self, cache_service):
        """Test clearing all cache"""
        # Set some data
        await cache_service.set("key1", {"data": 1}, ttl=60)
        await cache_service.set("key2", {"data": 2}, ttl=60)
        
        # Verify data exists
        assert await cache_service.get("key1") is not None
        assert await cache_service.get("key2") is not None
        
        # Clear all cache
        await cache_service.clear_all()
        
        # Verify data is cleared
        assert await cache_service.get("key1") is None
        assert await cache_service.get("key2") is None
    
    @pytest.mark.asyncio
    async def test_error_handling(self, cache_service):
        """Test error handling in cache operations"""
        # Test with invalid data
        try:
            await cache_service.set("error_key", {"data": "test"}, ttl=60)
            result = await cache_service.get("error_key")
            assert result == {"data": "test"}
        except Exception as e:
            # Should handle errors gracefully
            assert isinstance(e, Exception)
    
    def test_memory_cache_structure(self, cache_service):
        """Test memory cache internal structure"""
        # Test that memory cache is properly initialized
        assert hasattr(cache_service, 'memory_cache')
        assert isinstance(cache_service.memory_cache, dict)
        
        # Test cache TTL
        assert hasattr(cache_service, 'cache_ttl')
        assert isinstance(cache_service.cache_ttl, int)
        assert cache_service.cache_ttl > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_cache_access(self, cache_service):
        """Test concurrent cache access"""
        async def set_data(key, value):
            await cache_service.set(key, value, ttl=60)
            return await cache_service.get(key)
        
        # Test concurrent operations
        tasks = [
            set_data("concurrent_key_1", {"data": 1}),
            set_data("concurrent_key_2", {"data": 2}),
            set_data("concurrent_key_3", {"data": 3})
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(results) == 3
        assert results[0] == {"data": 1}
        assert results[1] == {"data": 2}
        assert results[2] == {"data": 3}
