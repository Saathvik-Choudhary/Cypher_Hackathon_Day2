import json
import hashlib
import time
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import redis
from config import Config

class CacheService:
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Try to connect to Redis if available
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            self.redis_client.ping()
            print("✅ Connected to Redis cache")
        except Exception as e:
            print(f"⚠️ Redis not available, using memory cache: {e}")
            self.redis_client = None
    
    def _generate_cache_key(self, data: Dict[str, Any]) -> str:
        """Generate a cache key from the data"""
        # Create a deterministic key from the data
        key_data = json.dumps(data, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get data from cache"""
        try:
            if self.redis_client:
                # Try Redis first
                cached_data = self.redis_client.get(key)
                if cached_data:
                    return json.loads(cached_data)
            else:
                # Fall back to memory cache
                if key in self.memory_cache:
                    cached_item = self.memory_cache[key]
                    if time.time() < cached_item['expires_at']:
                        return cached_item['data']
                    else:
                        # Expired, remove from cache
                        del self.memory_cache[key]
            
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """Set data in cache"""
        try:
            ttl = ttl or self.cache_ttl
            
            if self.redis_client:
                # Use Redis
                self.redis_client.setex(key, ttl, json.dumps(data))
            else:
                # Use memory cache
                self.memory_cache[key] = {
                    'data': data,
                    'expires_at': time.time() + ttl
                }
            
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def get_or_set(self, key: str, data_func, ttl: Optional[int] = None) -> Any:
        """Get data from cache or set it using the provided function"""
        # Try to get from cache first
        cached_data = await self.get(key)
        if cached_data is not None:
            return cached_data
        
        # If not in cache, generate the data
        if callable(data_func):
            data = await data_func() if asyncio.iscoroutinefunction(data_func) else data_func()
        else:
            data = data_func
        
        # Store in cache
        await self.set(key, data, ttl)
        return data
    
    async def invalidate(self, pattern: str) -> bool:
        """Invalidate cache entries matching a pattern"""
        try:
            if self.redis_client:
                # Use Redis pattern matching
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            else:
                # Use memory cache pattern matching
                keys_to_delete = [key for key in self.memory_cache.keys() if pattern in key]
                for key in keys_to_delete:
                    del self.memory_cache[key]
            
            return True
        except Exception as e:
            print(f"Cache invalidation error: {e}")
            return False
    
    async def clear_all(self) -> bool:
        """Clear all cache entries"""
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            else:
                self.memory_cache.clear()
            
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False

# Global cache instance
cache_service = CacheService()
