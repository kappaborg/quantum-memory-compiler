#!/usr/bin/env python3
"""
Circuit Cache
=============

Circuit-specific caching functionality.

Developer: kappasutra
"""

from .cache_manager import CacheManager, CacheType


class CircuitCache:
    """Circuit-specific cache wrapper"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
    
    def get(self, key: str):
        """Get cached circuit"""
        return self.cache_manager.get(CacheType.CIRCUIT, key)
    
    def put(self, key: str, circuit_data, ttl=None, metadata=None):
        """Cache circuit"""
        return self.cache_manager.put(CacheType.CIRCUIT, key, circuit_data, ttl, metadata)


class CircuitCacheManager:
    """Circuit cache manager"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.circuit_cache = CircuitCache(self.cache_manager) 