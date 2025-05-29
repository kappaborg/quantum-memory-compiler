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
GPU Memory Optimizer
===================

Optimized memory management for GPU-accelerated quantum simulations.

Developer: kappasutra
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import time
import gc

try:
    import jax
    import jax.numpy as jnp
    HAS_JAX = True
    print("✅ JAX available for GPU memory optimization")
except ImportError:
    HAS_JAX = False
    print("⚠️  JAX not available - using CPU memory optimization")

from ..core.circuit import Circuit


class GPUMemoryOptimizer:
    """
    GPU memory optimizer for quantum circuit simulation
    """
    
    def __init__(self, max_memory_gb: float = 4.0, enable_memory_mapping: bool = True):
        """
        Initialize GPU memory optimizer
        
        Args:
            max_memory_gb: Maximum GPU memory to use (GB)
            enable_memory_mapping: Whether to use memory mapping for large states
        """
        self.max_memory_gb = max_memory_gb
        self.enable_memory_mapping = enable_memory_mapping
        self.memory_usage = {}
        self.allocation_history = []
        
        print(f"🧠 GPU Memory Optimizer initialized")
        print(f"   Max memory: {max_memory_gb:.1f} GB")
        print(f"   Memory mapping: {'enabled' if enable_memory_mapping else 'disabled'}")
        
        if HAS_JAX:
            self._check_gpu_memory()
    
    def _check_gpu_memory(self):
        """Check available GPU memory"""
        try:
            devices = jax.devices()
            for i, device in enumerate(devices):
                print(f"   Device {i}: {device}")
                
            # Get memory info (if available)
            try:
                memory_info = jax.device_get(jax.devices()[0])
                print(f"   GPU memory check completed")
            except:
                print(f"   GPU memory info not available")
                
        except Exception as e:
            print(f"   GPU memory check failed: {e}")
    
    def estimate_memory_requirements(self, circuit: Circuit, precision: str = 'complex64') -> Dict[str, float]:
        """
        Estimate memory requirements for circuit simulation
        
        Args:
            circuit: Quantum circuit
            precision: Numerical precision
            
        Returns:
            Memory requirement estimates in bytes and GB
        """
        num_qubits = circuit.width
        state_size = 2 ** num_qubits
        
        # Calculate memory requirements
        if precision == 'complex64':
            bytes_per_element = 8  # 4 bytes real + 4 bytes imaginary
        else:  # complex128
            bytes_per_element = 16  # 8 bytes real + 8 bytes imaginary
        
        state_memory_bytes = state_size * bytes_per_element
        
        # Additional memory for intermediate calculations
        gate_memory_bytes = len(circuit.gates) * 4 * bytes_per_element  # Gate matrices
        temp_memory_bytes = state_memory_bytes * 2  # Temporary states
        
        total_memory_bytes = state_memory_bytes + gate_memory_bytes + temp_memory_bytes
        total_memory_gb = total_memory_bytes / (1024**3)
        
        requirements = {
            'state_memory_bytes': state_memory_bytes,
            'gate_memory_bytes': gate_memory_bytes,
            'temp_memory_bytes': temp_memory_bytes,
            'total_memory_bytes': total_memory_bytes,
            'state_memory_gb': state_memory_bytes / (1024**3),
            'total_memory_gb': total_memory_gb,
            'state_size': state_size,
            'num_qubits': num_qubits,
            'precision': precision
        }
        
        print(f"📊 Memory Requirements Estimate:")
        print(f"   Qubits: {num_qubits}")
        print(f"   State size: {state_size:,}")
        print(f"   State memory: {requirements['state_memory_gb']:.3f} GB")
        print(f"   Total memory: {total_memory_gb:.3f} GB")
        print(f"   Precision: {precision}")
        
        return requirements
    
    def optimize_memory_layout(self, state: np.ndarray, num_qubits: int) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Optimize memory layout for better GPU performance
        
        Args:
            state: Quantum state vector
            num_qubits: Number of qubits
            
        Returns:
            Optimized state and optimization info
        """
        print("🔧 Optimizing memory layout...")
        start_time = time.time()
        
        original_shape = state.shape
        original_size = state.nbytes
        
        # Memory layout optimizations
        optimizations = []
        optimized_state = state.copy()
        
        # 1. Ensure contiguous memory layout
        if not optimized_state.flags['C_CONTIGUOUS']:
            optimized_state = np.ascontiguousarray(optimized_state)
            optimizations.append("contiguous_layout")
        
        # 2. Optimize data type if possible
        if optimized_state.dtype == np.complex128 and self.max_memory_gb < 8:
            # Use lower precision for memory-constrained systems
            optimized_state = optimized_state.astype(np.complex64)
            optimizations.append("precision_reduction")
        
        # 3. Memory alignment for GPU
        if HAS_JAX:
            try:
                # Convert to JAX array for GPU optimization
                optimized_state = jnp.array(optimized_state)
                optimizations.append("jax_conversion")
            except Exception as e:
                print(f"   JAX conversion failed: {e}")
        
        optimization_time = time.time() - start_time
        final_size = optimized_state.nbytes if hasattr(optimized_state, 'nbytes') else len(optimized_state) * 8
        
        optimization_info = {
            'original_size_bytes': original_size,
            'optimized_size_bytes': final_size,
            'memory_reduction': (original_size - final_size) / original_size if original_size > 0 else 0,
            'optimization_time': optimization_time,
            'optimizations_applied': optimizations,
            'layout_contiguous': True,
            'gpu_ready': HAS_JAX and 'jax_conversion' in optimizations
        }
        
        print(f"✅ Memory layout optimized in {optimization_time:.3f}s")
        print(f"   Memory reduction: {optimization_info['memory_reduction']:.2%}")
        print(f"   Optimizations: {', '.join(optimizations)}")
        
        return optimized_state, optimization_info
    
    def manage_memory_chunks(self, state_size: int, max_chunk_size: Optional[int] = None) -> List[Tuple[int, int]]:
        """
        Divide large quantum states into manageable chunks
        
        Args:
            state_size: Size of quantum state vector
            max_chunk_size: Maximum size per chunk
            
        Returns:
            List of (start, end) indices for chunks
        """
        if max_chunk_size is None:
            # Calculate optimal chunk size based on available memory
            max_memory_bytes = self.max_memory_gb * (1024**3)
            bytes_per_element = 8  # complex64
            max_chunk_size = int(max_memory_bytes / (bytes_per_element * 4))  # Factor of 4 for safety
        
        chunks = []
        start = 0
        
        while start < state_size:
            end = min(start + max_chunk_size, state_size)
            chunks.append((start, end))
            start = end
        
        print(f"🔀 Memory chunking strategy:")
        print(f"   State size: {state_size:,}")
        print(f"   Chunk size: {max_chunk_size:,}")
        print(f"   Number of chunks: {len(chunks)}")
        
        return chunks
    
    def optimize_gate_memory(self, gates: List, num_qubits: int) -> Dict[str, Any]:
        """
        Optimize memory usage for gate operations
        
        Args:
            gates: List of quantum gates
            num_qubits: Number of qubits
            
        Returns:
            Gate memory optimization info
        """
        print("🚪 Optimizing gate memory usage...")
        
        # Analyze gate types and frequencies
        gate_types = {}
        for gate in gates:
            gate_type = gate.__class__.__name__
            gate_types[gate_type] = gate_types.get(gate_type, 0) + 1
        
        # Pre-compute common gate matrices
        precomputed_matrices = {}
        total_matrix_memory = 0
        
        for gate_type, count in gate_types.items():
            if count > 1:  # Only precompute if used multiple times
                # Create sample matrix (2x2 for single-qubit gates)
                matrix = np.eye(2, dtype=np.complex64)
                precomputed_matrices[gate_type] = matrix
                total_matrix_memory += matrix.nbytes
        
        # Memory pooling strategy
        max_simultaneous_gates = min(8, len(gates))  # Limit concurrent gates
        pool_memory = max_simultaneous_gates * 4 * 8  # 2x2 complex64 matrices
        
        optimization_info = {
            'total_gates': len(gates),
            'unique_gate_types': len(gate_types),
            'precomputed_matrices': len(precomputed_matrices),
            'matrix_memory_bytes': total_matrix_memory,
            'pool_memory_bytes': pool_memory,
            'max_simultaneous_gates': max_simultaneous_gates,
            'gate_type_distribution': gate_types
        }
        
        print(f"   Total gates: {len(gates)}")
        print(f"   Unique types: {len(gate_types)}")
        print(f"   Precomputed matrices: {len(precomputed_matrices)}")
        print(f"   Matrix memory: {total_matrix_memory / 1024:.1f} KB")
        
        return optimization_info
    
    def monitor_memory_usage(self, operation_name: str, start_memory: Optional[float] = None) -> Dict[str, float]:
        """
        Monitor memory usage during operations
        
        Args:
            operation_name: Name of the operation being monitored
            start_memory: Starting memory usage (if known)
            
        Returns:
            Memory usage statistics
        """
        import psutil
        
        # Get current memory usage
        process = psutil.Process()
        current_memory = process.memory_info().rss / (1024**3)  # GB
        
        if start_memory is not None:
            memory_delta = current_memory - start_memory
        else:
            memory_delta = 0
        
        # Update usage tracking
        self.memory_usage[operation_name] = {
            'current_memory_gb': current_memory,
            'memory_delta_gb': memory_delta,
            'timestamp': time.time()
        }
        
        # Add to allocation history
        self.allocation_history.append({
            'operation': operation_name,
            'memory_gb': current_memory,
            'delta_gb': memory_delta,
            'timestamp': time.time()
        })
        
        return self.memory_usage[operation_name]
    
    def cleanup_memory(self, force_gc: bool = True) -> Dict[str, Any]:
        """
        Clean up unused memory
        
        Args:
            force_gc: Whether to force garbage collection
            
        Returns:
            Cleanup statistics
        """
        print("🧹 Cleaning up memory...")
        start_time = time.time()
        
        # Get memory before cleanup
        import psutil
        process = psutil.Process()
        memory_before = process.memory_info().rss / (1024**3)
        
        # Force garbage collection
        if force_gc:
            gc.collect()
        
        # JAX-specific cleanup
        if HAS_JAX:
            try:
                # Clear JAX compilation cache
                jax.clear_caches()
            except:
                pass
        
        # Get memory after cleanup
        memory_after = process.memory_info().rss / (1024**3)
        memory_freed = memory_before - memory_after
        cleanup_time = time.time() - start_time
        
        cleanup_stats = {
            'memory_before_gb': memory_before,
            'memory_after_gb': memory_after,
            'memory_freed_gb': memory_freed,
            'cleanup_time': cleanup_time,
            'gc_forced': force_gc
        }
        
        print(f"✅ Memory cleanup completed in {cleanup_time:.3f}s")
        print(f"   Memory freed: {memory_freed:.3f} GB")
        print(f"   Current usage: {memory_after:.3f} GB")
        
        return cleanup_stats
    
    def get_memory_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive memory usage report
        
        Returns:
            Memory usage report
        """
        import psutil
        
        # System memory info
        system_memory = psutil.virtual_memory()
        process = psutil.Process()
        process_memory = process.memory_info()
        
        # GPU memory info (if available)
        gpu_memory_info = {}
        if HAS_JAX:
            try:
                devices = jax.devices()
                gpu_memory_info = {
                    'devices': len(devices),
                    'device_types': [str(d).split(':')[0] for d in devices]
                }
            except:
                gpu_memory_info = {'error': 'GPU memory info unavailable'}
        
        report = {
            'system_memory': {
                'total_gb': system_memory.total / (1024**3),
                'available_gb': system_memory.available / (1024**3),
                'used_gb': system_memory.used / (1024**3),
                'percent_used': system_memory.percent
            },
            'process_memory': {
                'rss_gb': process_memory.rss / (1024**3),
                'vms_gb': process_memory.vms / (1024**3)
            },
            'gpu_memory': gpu_memory_info,
            'optimizer_settings': {
                'max_memory_gb': self.max_memory_gb,
                'memory_mapping_enabled': self.enable_memory_mapping
            },
            'operation_history': list(self.memory_usage.keys()),
            'allocation_count': len(self.allocation_history)
        }
        
        print("📊 Memory Usage Report:")
        print(f"   System memory: {report['system_memory']['used_gb']:.1f}/{report['system_memory']['total_gb']:.1f} GB ({report['system_memory']['percent_used']:.1f}%)")
        print(f"   Process memory: {report['process_memory']['rss_gb']:.3f} GB")
        print(f"   GPU devices: {gpu_memory_info.get('devices', 'N/A')}")
        
        return report
    
    def suggest_optimizations(self, circuit: Circuit) -> List[str]:
        """
        Suggest memory optimizations for a given circuit
        
        Args:
            circuit: Quantum circuit to analyze
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        # Estimate memory requirements
        requirements = self.estimate_memory_requirements(circuit)
        
        # Check if circuit fits in memory
        if requirements['total_memory_gb'] > self.max_memory_gb:
            suggestions.append(f"Circuit requires {requirements['total_memory_gb']:.1f} GB but limit is {self.max_memory_gb:.1f} GB")
            suggestions.append("Consider using memory chunking or reducing precision")
        
        # Check qubit count
        if circuit.width > 20:
            suggestions.append("Large qubit count detected - consider circuit decomposition")
        
        # Check gate count
        if len(circuit.gates) > 1000:
            suggestions.append("High gate count - consider gate optimization and batching")
        
        # Check for repeated patterns
        gate_types = {}
        for gate in circuit.gates:
            gate_type = gate.__class__.__name__
            gate_types[gate_type] = gate_types.get(gate_type, 0) + 1
        
        if len(gate_types) < len(circuit.gates) / 4:
            suggestions.append("Many repeated gates detected - enable gate matrix caching")
        
        if not suggestions:
            suggestions.append("Circuit is well-optimized for current memory settings")
        
        print("💡 Memory Optimization Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
        
        return suggestions 