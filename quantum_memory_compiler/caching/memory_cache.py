#!/usr/bin/env python3
"""
Memory State Cache
=================

Memory state caching functionality.

Developer: kappasutra
"""

from .cache_manager import CacheManager, CacheType


class MemoryStateCache:
    """Memory state cache wrapper"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
    
    def get(self, key: str):
        """Get cached memory state"""
        return self.cache_manager.get(CacheType.MEMORY_STATE, key)
    
    def put(self, key: str, state_data, ttl=1800, metadata=None):
        """Cache memory state"""
        return self.cache_manager.put(CacheType.MEMORY_STATE, key, state_data, ttl, metadata)


class MemoryStateCacheManager:
    """Memory state cache manager"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.memory_cache = MemoryStateCache(self.cache_manager) 