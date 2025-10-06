"""Caching utilities for URL configuration."""
import json
import time
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class InMemoryCache:
    """Simple in-memory cache implementation as fallback."""
    
    def __init__(self, default_ttl: int = 3600):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if key in self._cache:
            entry = self._cache[key]
            if time.time() < entry["expires_at"]:
                return entry["value"]
            else:
                # Expired, remove from cache
                del self._cache[key]
        return None
    
    async def setex(self, key: str, ttl: int, value: str):
        """Set value in cache with TTL."""
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl
        }
    
    async def delete(self, *keys: str):
        """Delete keys from cache."""
        for key in keys:
            self._cache.pop(key, None)
    
    async def keys(self, pattern: str) -> list:
        """Get keys matching pattern (simple implementation)."""
        # Convert glob pattern to simple matching
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return [key for key in self._cache.keys() if key.startswith(prefix)]
        return [key for key in self._cache.keys() if key == pattern]
    
    def clear_expired(self):
        """Clear expired entries."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time >= entry["expires_at"]
        ]
        for key in expired_keys:
            del self._cache[key]


class CacheManager:
    """Cache manager that handles both Redis and in-memory caching."""
    
    def __init__(self, redis_client=None, default_ttl: int = 3600):
        self.redis_client = redis_client
        self.fallback_cache = InMemoryCache(default_ttl)
        self.default_ttl = default_ttl
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if self.redis_client:
            try:
                return await self.redis_client.get(key)
            except Exception as e:
                logger.warning(f"Redis get failed, using fallback: {e}")
        
        return await self.fallback_cache.get(key)
    
    async def setex(self, key: str, ttl: int, value: str):
        """Set value in cache with TTL."""
        if self.redis_client:
            try:
                await self.redis_client.setex(key, ttl, value)
                return
            except Exception as e:
                logger.warning(f"Redis setex failed, using fallback: {e}")
        
        await self.fallback_cache.setex(key, ttl, value)
    
    async def delete(self, *keys: str):
        """Delete keys from cache."""
        if self.redis_client:
            try:
                if keys:
                    await self.redis_client.delete(*keys)
                return
            except Exception as e:
                logger.warning(f"Redis delete failed, using fallback: {e}")
        
        await self.fallback_cache.delete(*keys)
    
    async def keys(self, pattern: str) -> list:
        """Get keys matching pattern."""
        if self.redis_client:
            try:
                return await self.redis_client.keys(pattern)
            except Exception as e:
                logger.warning(f"Redis keys failed, using fallback: {e}")
        
        return await self.fallback_cache.keys(pattern)
    
    def cleanup(self):
        """Cleanup expired entries (for in-memory cache)."""
        if not self.redis_client:
            self.fallback_cache.clear_expired()


# Global cache instance
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    
    if _cache_manager is None:
        # Try to initialize Redis client
        redis_client = None
        try:
            import redis.asyncio as redis
            from ..config import settings
            
            if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
                redis_client = redis.from_url(settings.REDIS_URL)
                logger.info("Redis cache initialized")
            else:
                logger.info("No Redis URL configured, using in-memory cache")
        except ImportError:
            logger.info("Redis not available, using in-memory cache")
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}, using in-memory cache")
        
        _cache_manager = CacheManager(redis_client)
    
    return _cache_manager


def clear_cache_manager():
    """Clear the global cache manager (for testing)."""
    global _cache_manager
    _cache_manager = None