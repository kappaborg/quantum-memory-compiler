#!/usr/bin/env python3
"""
Simulation Cache
===============

Simulation result caching functionality.

Developer: kappasutra
"""

from .cache_manager import CacheManager, CacheType


class SimulationCache:
    """Simulation result cache wrapper"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
    
    def get(self, key: str):
        """Get cached simulation result"""
        return self.cache_manager.get(CacheType.SIMULATION, key)
    
    def put(self, key: str, result_data, ttl=3600, metadata=None):
        """Cache simulation result"""
        return self.cache_manager.put(CacheType.SIMULATION, key, result_data, ttl, metadata)


class SimulationCacheManager:
    """Simulation cache manager"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.simulation_cache = SimulationCache(self.cache_manager) 