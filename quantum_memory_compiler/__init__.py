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

__version__ = '0.1.0'

# Core modülünden sınıfları içe aktar
from .core.circuit import Circuit
from .core.gate import Gate, GateType
from .core.qubit import Qubit, QubitType, MemoryLevel
from .core.visualization import CircuitVisualizer

# Compiler modülünden sınıfları içe aktar
from .compiler import QuantumCompiler
from .compiler.optimizer import Optimizer
from .compiler.mapper import QubitMapper
from .compiler.scheduler import GateScheduler

# Simulation modülünden sınıfları içe aktar
from .simulation.simulator import Simulator
from .simulation.noise_model import NoiseModel

# Memory modülünden sınıfları içe aktar
from .memory.manager import MemoryManager
from .memory.hierarchy import MemoryHierarchy
from .memory.allocation import QubitAllocator
from .memory.recycling import QubitRecycler, RecyclingStrategy
from .memory.profiler import MemoryProfiler

# CLI modülünü içe aktar
from . import cli

# Public API'yi tanımla
__all__ = [
    # Core modülü
    'Circuit', 'Gate', 'GateType', 'Qubit', 'QubitType', 'MemoryLevel', 'CircuitVisualizer',
    
    # Compiler modülü
    'QuantumCompiler', 'Optimizer', 'QubitMapper', 'GateScheduler',
    
    # Simulation modülü
    'Simulator', 'NoiseModel',
    
    # Memory modülü
    'MemoryManager', 'MemoryHierarchy', 'QubitAllocator', 'QubitRecycler', 
    'RecyclingStrategy', 'MemoryProfiler',
    
    # CLI modülü
    'cli',
    "MemoryHierarchy",
] 