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
Enhanced Cache Manager
=====================

Central cache management system for Quantum Memory Compiler.

Developer: kappasutra
"""

import os
import time
import json
import hashlib
import pickle
import threading
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

import psutil


class CacheType(Enum):
    """Types of cache"""
    CIRCUIT = "circuit"
    SIMULATION = "simulation"
    MEMORY_STATE = "memory_state"
    COMPILATION = "compilation"


@dataclass
class CacheStats:
    """Cache statistics"""
    cache_type: str
    total_entries: int
    total_size_mb: float
    hit_rate: float
    miss_rate: float
    avg_access_time_ms: float
    last_cleanup: float
    memory_usage_mb: float


@dataclass
class CacheEntry:
    """Generic cache entry"""
    key: str
    data: Any
    timestamp: float
    access_count: int
    last_access: float
    size_bytes: int
    ttl: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class CacheManager:
    """Central cache management system"""
    
    def __init__(self, cache_dir: str = "cache", max_memory_mb: float = 1024.0,
                 cleanup_interval: int = 300, enable_persistence: bool = True):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory for persistent cache storage
            max_memory_mb: Maximum memory usage in MB
            cleanup_interval: Cleanup interval in seconds
            enable_persistence: Enable persistent storage
        """
        self.cache_dir = Path(cache_dir)
        self.max_memory_mb = max_memory_mb
        self.cleanup_interval = cleanup_interval
        self.enable_persistence = enable_persistence
        
        # Create cache directory
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache storage
        self.caches: Dict[CacheType, Dict[str, CacheEntry]] = {
            CacheType.CIRCUIT: {},
            CacheType.SIMULATION: {},
            CacheType.MEMORY_STATE: {},
            CacheType.COMPILATION: {}
        }
        
        # Cache statistics
        self.stats: Dict[CacheType, Dict[str, Any]] = {
            cache_type: {
                'hits': 0,
                'misses': 0,
                'total_access_time': 0.0,
                'access_count': 0,
                'last_cleanup': time.time()
            } for cache_type in CacheType
        }
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Background cleanup
        self.cleanup_thread = None
        self.running = True
        
        print("💾 Enhanced Cache Manager initialized")
        print(f"   Cache directory: {self.cache_dir}")
        print(f"   Max memory: {max_memory_mb} MB")
        print(f"   Persistence: {'enabled' if enable_persistence else 'disabled'}")
        
        # Load persistent cache
        if self.enable_persistence:
            self._load_persistent_cache()
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_worker():
            while self.running:
                try:
                    time.sleep(self.cleanup_interval)
                    if self.running:
                        self.cleanup_expired()
                        self._check_memory_usage()
                except Exception as e:
                    print(f"❌ Cache cleanup error: {e}")
        
        self.cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self.cleanup_thread.start()
    
    def put(self, cache_type: CacheType, key: str, data: Any, 
            ttl: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store data in cache
        
        Args:
            cache_type: Type of cache
            key: Cache key
            data: Data to cache
            ttl: Time to live in seconds
            metadata: Additional metadata
            
        Returns:
            True if stored successfully
        """
        start_time = time.time()
        
        try:
            with self.lock:
                # Calculate data size
                try:
                    size_bytes = len(pickle.dumps(data))
                except:
                    size_bytes = 1024  # Fallback estimate
                
                # Create cache entry
                entry = CacheEntry(
                    key=key,
                    data=data,
                    timestamp=time.time(),
                    access_count=0,
                    last_access=time.time(),
                    size_bytes=size_bytes,
                    ttl=ttl,
                    metadata=metadata or {}
                )
                
                # Store in memory cache
                self.caches[cache_type][key] = entry
                
                # Store persistently if enabled
                if self.enable_persistence:
                    self._save_to_disk(cache_type, key, entry)
                
                # Update stats
                access_time = (time.time() - start_time) * 1000
                self.stats[cache_type]['total_access_time'] += access_time
                self.stats[cache_type]['access_count'] += 1
                
                return True
                
        except Exception as e:
            print(f"❌ Cache put error: {e}")
            return False
    
    def get(self, cache_type: CacheType, key: str) -> Optional[Any]:
        """
        Retrieve data from cache
        
        Args:
            cache_type: Type of cache
            key: Cache key
            
        Returns:
            Cached data or None if not found
        """
        start_time = time.time()
        
        try:
            with self.lock:
                # Check memory cache first
                if key in self.caches[cache_type]:
                    entry = self.caches[cache_type][key]
                    
                    # Check if expired
                    if self._is_expired(entry):
                        del self.caches[cache_type][key]
                        self._record_miss(cache_type, start_time)
                        return None
                    
                    # Update access info
                    entry.access_count += 1
                    entry.last_access = time.time()
                    
                    self._record_hit(cache_type, start_time)
                    return entry.data
                
                # Try to load from disk
                if self.enable_persistence:
                    entry = self._load_from_disk(cache_type, key)
                    if entry and not self._is_expired(entry):
                        # Restore to memory cache
                        self.caches[cache_type][key] = entry
                        entry.access_count += 1
                        entry.last_access = time.time()
                        
                        self._record_hit(cache_type, start_time)
                        return entry.data
                
                # Cache miss
                self._record_miss(cache_type, start_time)
                return None
                
        except Exception as e:
            print(f"❌ Cache get error: {e}")
            self._record_miss(cache_type, start_time)
            return None
    
    def invalidate(self, cache_type: CacheType, key: str) -> bool:
        """
        Invalidate cache entry
        
        Args:
            cache_type: Type of cache
            key: Cache key
            
        Returns:
            True if invalidated successfully
        """
        try:
            with self.lock:
                # Remove from memory
                if key in self.caches[cache_type]:
                    del self.caches[cache_type][key]
                
                # Remove from disk
                if self.enable_persistence:
                    self._remove_from_disk(cache_type, key)
                
                return True
                
        except Exception as e:
            print(f"❌ Cache invalidate error: {e}")
            return False
    
    def clear(self, cache_type: Optional[CacheType] = None) -> bool:
        """
        Clear cache
        
        Args:
            cache_type: Type of cache to clear (None for all)
            
        Returns:
            True if cleared successfully
        """
        try:
            with self.lock:
                if cache_type:
                    # Clear specific cache type
                    self.caches[cache_type].clear()
                    if self.enable_persistence:
                        cache_dir = self.cache_dir / cache_type.value
                        if cache_dir.exists():
                            for file in cache_dir.glob("*.cache"):
                                file.unlink()
                else:
                    # Clear all caches
                    for ct in CacheType:
                        self.caches[ct].clear()
                    
                    if self.enable_persistence and self.cache_dir.exists():
                        for file in self.cache_dir.rglob("*.cache"):
                            file.unlink()
                
                return True
                
        except Exception as e:
            print(f"❌ Cache clear error: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired cache entries
        
        Returns:
            Number of entries removed
        """
        removed_count = 0
        
        try:
            with self.lock:
                current_time = time.time()
                
                for cache_type in CacheType:
                    expired_keys = []
                    
                    for key, entry in self.caches[cache_type].items():
                        if self._is_expired(entry):
                            expired_keys.append(key)
                    
                    # Remove expired entries
                    for key in expired_keys:
                        del self.caches[cache_type][key]
                        if self.enable_persistence:
                            self._remove_from_disk(cache_type, key)
                        removed_count += 1
                    
                    # Update cleanup time
                    self.stats[cache_type]['last_cleanup'] = current_time
                
                if removed_count > 0:
                    print(f"🧹 Cache cleanup: removed {removed_count} expired entries")
                
        except Exception as e:
            print(f"❌ Cache cleanup error: {e}")
        
        return removed_count
    
    def get_stats(self) -> Dict[str, CacheStats]:
        """Get cache statistics"""
        stats = {}
        
        try:
            with self.lock:
                for cache_type in CacheType:
                    cache_data = self.caches[cache_type]
                    stat_data = self.stats[cache_type]
                    
                    total_entries = len(cache_data)
                    total_size_bytes = sum(entry.size_bytes for entry in cache_data.values())
                    total_size_mb = total_size_bytes / (1024 * 1024)
                    
                    hits = stat_data['hits']
                    misses = stat_data['misses']
                    total_accesses = hits + misses
                    
                    hit_rate = (hits / total_accesses * 100) if total_accesses > 0 else 0
                    miss_rate = (misses / total_accesses * 100) if total_accesses > 0 else 0
                    
                    avg_access_time = (stat_data['total_access_time'] / stat_data['access_count']) if stat_data['access_count'] > 0 else 0
                    
                    # Memory usage
                    process = psutil.Process()
                    memory_usage_mb = process.memory_info().rss / (1024 * 1024)
                    
                    stats[cache_type.value] = CacheStats(
                        cache_type=cache_type.value,
                        total_entries=total_entries,
                        total_size_mb=total_size_mb,
                        hit_rate=hit_rate,
                        miss_rate=miss_rate,
                        avg_access_time_ms=avg_access_time,
                        last_cleanup=stat_data['last_cleanup'],
                        memory_usage_mb=memory_usage_mb
                    )
        
        except Exception as e:
            print(f"❌ Error getting cache stats: {e}")
        
        return stats
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired"""
        if entry.ttl is None:
            return False
        
        return (time.time() - entry.timestamp) > entry.ttl
    
    def _record_hit(self, cache_type: CacheType, start_time: float):
        """Record cache hit"""
        access_time = (time.time() - start_time) * 1000
        self.stats[cache_type]['hits'] += 1
        self.stats[cache_type]['total_access_time'] += access_time
        self.stats[cache_type]['access_count'] += 1
    
    def _record_miss(self, cache_type: CacheType, start_time: float):
        """Record cache miss"""
        access_time = (time.time() - start_time) * 1000
        self.stats[cache_type]['misses'] += 1
        self.stats[cache_type]['total_access_time'] += access_time
        self.stats[cache_type]['access_count'] += 1
    
    def _check_memory_usage(self):
        """Check and manage memory usage"""
        try:
            # Calculate current cache memory usage
            total_size_mb = 0
            for cache_type in CacheType:
                for entry in self.caches[cache_type].values():
                    total_size_mb += entry.size_bytes / (1024 * 1024)
            
            if total_size_mb > self.max_memory_mb:
                print(f"⚠️  Cache memory usage ({total_size_mb:.1f} MB) exceeds limit ({self.max_memory_mb} MB)")
                self._evict_lru_entries(total_size_mb - self.max_memory_mb)
        
        except Exception as e:
            print(f"❌ Memory check error: {e}")
    
    def _evict_lru_entries(self, target_mb: float):
        """Evict least recently used entries"""
        try:
            # Collect all entries with access info
            all_entries = []
            for cache_type in CacheType:
                for key, entry in self.caches[cache_type].items():
                    all_entries.append((cache_type, key, entry))
            
            # Sort by last access time (oldest first)
            all_entries.sort(key=lambda x: x[2].last_access)
            
            # Evict entries until target is reached
            freed_mb = 0
            evicted_count = 0
            
            for cache_type, key, entry in all_entries:
                if freed_mb >= target_mb:
                    break
                
                # Remove entry
                del self.caches[cache_type][key]
                if self.enable_persistence:
                    self._remove_from_disk(cache_type, key)
                
                freed_mb += entry.size_bytes / (1024 * 1024)
                evicted_count += 1
            
            print(f"🗑️  Evicted {evicted_count} LRU entries, freed {freed_mb:.1f} MB")
        
        except Exception as e:
            print(f"❌ LRU eviction error: {e}")
    
    def _save_to_disk(self, cache_type: CacheType, key: str, entry: CacheEntry):
        """Save cache entry to disk"""
        try:
            cache_dir = self.cache_dir / cache_type.value
            cache_dir.mkdir(exist_ok=True)
            
            # Create safe filename
            safe_key = hashlib.md5(key.encode()).hexdigest()
            cache_file = cache_dir / f"{safe_key}.cache"
            
            # Save entry
            with open(cache_file, 'wb') as f:
                pickle.dump(entry, f)
        
        except Exception as e:
            print(f"❌ Error saving to disk: {e}")
    
    def _load_from_disk(self, cache_type: CacheType, key: str) -> Optional[CacheEntry]:
        """Load cache entry from disk"""
        try:
            cache_dir = self.cache_dir / cache_type.value
            safe_key = hashlib.md5(key.encode()).hexdigest()
            cache_file = cache_dir / f"{safe_key}.cache"
            
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
        
        except Exception as e:
            print(f"❌ Error loading from disk: {e}")
        
        return None
    
    def _remove_from_disk(self, cache_type: CacheType, key: str):
        """Remove cache entry from disk"""
        try:
            cache_dir = self.cache_dir / cache_type.value
            safe_key = hashlib.md5(key.encode()).hexdigest()
            cache_file = cache_dir / f"{safe_key}.cache"
            
            if cache_file.exists():
                cache_file.unlink()
        
        except Exception as e:
            print(f"❌ Error removing from disk: {e}")
    
    def _load_persistent_cache(self):
        """Load persistent cache from disk"""
        try:
            if not self.cache_dir.exists():
                return
            
            loaded_count = 0
            
            for cache_type in CacheType:
                cache_dir = self.cache_dir / cache_type.value
                if not cache_dir.exists():
                    continue
                
                for cache_file in cache_dir.glob("*.cache"):
                    try:
                        with open(cache_file, 'rb') as f:
                            entry = pickle.load(f)
                        
                        # Check if not expired
                        if not self._is_expired(entry):
                            self.caches[cache_type][entry.key] = entry
                            loaded_count += 1
                        else:
                            # Remove expired file
                            cache_file.unlink()
                    
                    except Exception as e:
                        print(f"⚠️  Could not load cache file {cache_file}: {e}")
                        # Remove corrupted file
                        try:
                            cache_file.unlink()
                        except:
                            pass
            
            if loaded_count > 0:
                print(f"📂 Loaded {loaded_count} cache entries from disk")
        
        except Exception as e:
            print(f"❌ Error loading persistent cache: {e}")
    
    def shutdown(self):
        """Shutdown cache manager"""
        print("🔄 Shutting down cache manager...")
        
        self.running = False
        
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)
        
        # Save current state if persistence enabled
        if self.enable_persistence:
            try:
                with self.lock:
                    for cache_type in CacheType:
                        for key, entry in self.caches[cache_type].items():
                            self._save_to_disk(cache_type, key, entry)
            except Exception as e:
                print(f"❌ Error saving cache on shutdown: {e}")
        
        print("✅ Cache manager shutdown complete")
    
    def __del__(self):
        """Destructor"""
        try:
            self.shutdown()
        except:
            pass 