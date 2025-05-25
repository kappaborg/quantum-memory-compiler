"""
Quantum Memory Compiler
===========================

Kuantum devreleri için bellek-bilinçli derleme ve simülasyon aracı.
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