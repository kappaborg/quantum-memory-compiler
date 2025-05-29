#!/usr/bin/env python3
"""
Quantum Memory Compiler - Advanced Memory-Aware Quantum Circuit Compilation
Copyright (c) 2025 Quantum Memory Compiler Project

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This file contains proprietary algorithms for quantum memory optimization.
Commercial use requires explicit permission.
"""

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