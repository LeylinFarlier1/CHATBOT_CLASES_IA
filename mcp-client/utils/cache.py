"""
Resource Cache System
Provides TTL-based caching for MCP resources and tools.
"""

import time
from typing import Any, Optional, Dict, Tuple


class ResourceCache:
    """Simple TTL-based cache for MCP resources and tools."""

    def __init__(self, ttl: int = 300):
        """
        Initialize resource cache.

        Args:
            ttl: Time to live in seconds (default: 300 = 5 minutes)
        """
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                # Remove expired entry
                del self.cache[key]

        return None

    def set(self, key: str, value: Any):
        """
        Set value in cache with current timestamp.

        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = (value, time.time())

    def invalidate(self, key: str) -> bool:
        """
        Invalidate (delete) a cache entry.

        Args:
            key: Cache key

        Returns:
            True if entry was deleted, False if not found
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from cache.

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.ttl
        ]

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        current_time = time.time()
        valid_entries = 0
        expired_entries = 0

        for _, (_, timestamp) in self.cache.items():
            if current_time - timestamp < self.ttl:
                valid_entries += 1
            else:
                expired_entries += 1

        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'ttl_seconds': self.ttl
        }

    def has(self, key: str) -> bool:
        """
        Check if key exists and is not expired.

        Args:
            key: Cache key

        Returns:
            True if key exists and is valid, False otherwise
        """
        return self.get(key) is not None

    def set_ttl(self, ttl: int):
        """
        Update TTL for cache.

        Args:
            ttl: New time to live in seconds
        """
        self.ttl = ttl

    def __len__(self) -> int:
        """Return number of entries in cache (including expired)."""
        return len(self.cache)

    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache (regardless of expiration)."""
        return key in self.cache
