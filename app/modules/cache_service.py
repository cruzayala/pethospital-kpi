# coding: utf-8
"""
Cache Service Module

Provides caching functionality using Redis:
- Cache frequently accessed analytics
- TTL-based invalidation
- Graceful fallback when Redis unavailable
"""
from typing import Optional, Any, Callable
from functools import wraps
import json
import hashlib
from datetime import timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from loguru import logger


class CacheService:
    """Service for caching analytics data with Redis"""

    def __init__(self, redis_url: str = "redis://localhost:6379/0", enabled: bool = True):
        """
        Initialize cache service

        Args:
            redis_url: Redis connection URL
            enabled: Whether caching is enabled
        """
        self.enabled = enabled and REDIS_AVAILABLE
        self.client = None

        if self.enabled:
            try:
                self.client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                # Test connection
                self.client.ping()
                logger.info(f"Redis cache initialized: {redis_url}")
            except Exception as e:
                logger.warning(f"Redis not available, caching disabled: {e}")
                self.enabled = False
                self.client = None
        else:
            if not REDIS_AVAILABLE:
                logger.warning("Redis library not installed, caching disabled")
            else:
                logger.info("Caching disabled by configuration")

    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate cache key from prefix and parameters

        Args:
            prefix: Key prefix (e.g., 'analytics:centers')
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Cache key string
        """
        # Create a string representation of all parameters
        params_str = json.dumps({
            "args": args,
            "kwargs": sorted(kwargs.items())
        }, sort_keys=True)

        # Create hash of parameters to keep key size manageable
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:12]

        return f"{prefix}:{params_hash}"

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.enabled or not self.client:
            return None

        try:
            value = self.client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            logger.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.warning(f"Cache get error for {key}: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: int = 300
    ) -> bool:
        """
        Set value in cache with TTL

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (default: 5 minutes)

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            serialized = json.dumps(value, default=str)  # default=str for dates
            self.client.setex(key, ttl, serialized)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.warning(f"Cache set error for {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete key from cache

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            self.client.delete(key)
            logger.debug(f"Cache deleted: {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern

        Args:
            pattern: Key pattern (e.g., 'analytics:*')

        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self.client:
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                count = self.client.delete(*keys)
                logger.info(f"Cleared {count} cache keys matching: {pattern}")
                return count
            return 0
        except Exception as e:
            logger.warning(f"Cache clear pattern error for {pattern}: {e}")
            return 0

    def cached(
        self,
        prefix: str,
        ttl: int = 300
    ):
        """
        Decorator to cache function results

        Args:
            prefix: Cache key prefix
            ttl: Time to live in seconds

        Usage:
            @cache_service.cached('analytics:centers', ttl=600)
            def get_centers_data(days: int):
                # expensive computation
                return data
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._make_key(prefix, *args, **kwargs)

                # Try to get from cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # Call function
                result = func(*args, **kwargs)

                # Store in cache
                self.set(cache_key, result, ttl)

                return result

            # Add method to clear this function's cache
            def clear_cache(*args, **kwargs):
                cache_key = self._make_key(prefix, *args, **kwargs)
                return self.delete(cache_key)

            wrapper.clear_cache = clear_cache
            return wrapper

        return decorator

    def get_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        if not self.enabled or not self.client:
            return {
                "enabled": False,
                "reason": "Redis not available or disabled"
            }

        try:
            info = self.client.info('stats')
            return {
                "enabled": True,
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get('keyspace_hits', 0),
                    info.get('keyspace_misses', 0)
                ),
                "total_keys": self.client.dbsize()
            }
        except Exception as e:
            logger.warning(f"Cache stats error: {e}")
            return {
                "enabled": True,
                "error": str(e)
            }

    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)


# Global cache instance (will be initialized in main.py)
cache_service: Optional[CacheService] = None


def get_cache_service() -> Optional[CacheService]:
    """Get global cache service instance"""
    return cache_service


def init_cache_service(redis_url: str = "redis://localhost:6379/0", enabled: bool = True) -> CacheService:
    """
    Initialize global cache service

    Args:
        redis_url: Redis connection URL
        enabled: Whether caching is enabled

    Returns:
        CacheService instance
    """
    global cache_service
    cache_service = CacheService(redis_url, enabled)
    return cache_service
