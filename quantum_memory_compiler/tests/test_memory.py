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

import pytest
from quantum_memory_compiler.memory import MemoryHierarchy, MemoryManager
from quantum_memory_compiler.memory.allocation import QubitAllocator
from quantum_memory_compiler.memory.recycling import QubitRecycler, RecyclingStrategy
from quantum_memory_compiler.core import Circuit

def test_memory_hierarchy_creation():
    """Test memory hierarchy creation and properties"""
    memory = MemoryHierarchy(l1_capacity=50, l2_capacity=100, l3_capacity=200)
    
    # Check levels
    assert memory.levels["L1"].capacity == 50
    assert memory.levels["L2"].capacity == 100
    assert memory.levels["L3"].capacity == 200
    
    # Check total capacity
    assert memory.get_total_capacity() == 350
    
    # Check utilization stats
    utilization = memory.get_utilization_stats()
    assert all(v == 0 for v in utilization.values())  # All levels should be empty

def test_memory_manager():
    """Test memory manager and qubit allocation"""
    hierarchy = MemoryHierarchy(l1_capacity=10, l2_capacity=20, l3_capacity=30)
    manager = MemoryManager(hierarchy, allocator_strategy="static")
    
    # Allocate qubits
    qubits = manager.allocate_qubits(5, level_name="L1")
    assert len(qubits) == 5
    assert all(q.memory_level.name == "L1" for q in qubits)
    
    # Check memory stats
    stats = manager.get_memory_stats()
    assert stats["active_qubits"] == 5
    assert stats["level_stats"]["L1"] == 0.5  # 5/10 = 0.5 utilization
    
    # Deallocate a qubit
    manager.deallocate_qubit(qubits[0])
    stats = manager.get_memory_stats()
    assert stats["active_qubits"] == 4
    
    # Reset manager
    manager.reset()
    stats = manager.get_memory_stats()
    assert stats["active_qubits"] == 0

def test_qubit_allocator():
    """Test different qubit allocation strategies"""
    circuit = Circuit.create_bell_state()
    hierarchy = MemoryHierarchy()
    
    # Test static allocator
    static_allocator = QubitAllocator.create("static")
    allocation = static_allocator.allocate(circuit, hierarchy)
    assert len(allocation) == 2  # Bell state has 2 qubits
    
    # Test lifetime allocator
    lifetime_allocator = QubitAllocator.create("lifetime")
    allocation = lifetime_allocator.allocate(circuit, hierarchy)
    assert len(allocation) == 2

def test_qubit_recycler():
    """Test qubit recycling strategies"""
    recycler = QubitRecycler(RecyclingStrategy.RESET_BASED)
    circuit = Circuit.create_bell_state()
    
    # Optimize and check results
    optimized, saved = recycler.optimize(circuit)
    
    # Check stats
    stats = recycler.get_stats()
    assert stats["strategy"] == "RESET_BASED"
    
    # Reset stats
    recycler.reset_stats()
    assert recycler.get_stats()["saved_qubits"] == 0 