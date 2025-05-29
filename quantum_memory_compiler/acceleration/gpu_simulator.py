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
GPU-Accelerated Quantum Circuit Simulator
=========================================

High-performance quantum circuit simulation using JAX and GPU acceleration.

Developer: kappasutra
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import time

# GPU acceleration imports
HAS_JAX = False
HAS_NUMBA = False

try:
    import jax
    import jax.numpy as jnp
    from jax import jit, vmap, pmap
    HAS_JAX = True
    print("✅ JAX GPU acceleration available")
except ImportError:
    print("⚠️  JAX not available - falling back to CPU")
    HAS_JAX = False

try:
    from numba import jit as numba_jit, cuda
    HAS_NUMBA = True
    print("✅ Numba JIT compilation available")
except ImportError:
    print("⚠️  Numba not available")
    HAS_NUMBA = False

from ..core.circuit import Circuit
from ..core.gate import Gate


class GPUSimulator:
    """
    GPU-accelerated quantum circuit simulator using JAX
    """
    
    def __init__(self, use_gpu: bool = True, precision: str = 'float32'):
        """
        Initialize GPU simulator
        
        Args:
            use_gpu: Whether to use GPU acceleration
            precision: Numerical precision ('float32' or 'float64')
        """
        self.use_gpu = use_gpu and HAS_JAX
        self.precision = precision
        self.device_count = 1
        
        if self.use_gpu:
            try:
                # Check available devices
                devices = jax.devices()
                self.device_count = len(devices)
                print(f"🚀 GPU Simulator initialized with {self.device_count} device(s)")
                print(f"   Devices: {[str(d) for d in devices]}")
                
                # Set precision
                if precision == 'float64':
                    jax.config.update("jax_enable_x64", True)
                    
            except Exception as e:
                print(f"⚠️  GPU initialization failed: {e}")
                self.use_gpu = False
        
        if not self.use_gpu:
            print("🔄 Using CPU-based simulation")
            
        # Initialize gate matrices
        self._init_gate_matrices()
    
    def _init_gate_matrices(self):
        """Initialize common quantum gate matrices"""
        if self.use_gpu:
            # JAX arrays for GPU
            self.I = jnp.array([[1, 0], [0, 1]], dtype=jnp.complex64)
            self.X = jnp.array([[0, 1], [1, 0]], dtype=jnp.complex64)
            self.Y = jnp.array([[0, -1j], [1j, 0]], dtype=jnp.complex64)
            self.Z = jnp.array([[1, 0], [0, -1]], dtype=jnp.complex64)
            self.H = jnp.array([[1, 1], [1, -1]], dtype=jnp.complex64) / jnp.sqrt(2)
            self.S = jnp.array([[1, 0], [0, 1j]], dtype=jnp.complex64)
            self.T = jnp.array([[1, 0], [0, jnp.exp(1j * jnp.pi / 4)]], dtype=jnp.complex64)
        else:
            # NumPy arrays for CPU
            self.I = np.array([[1, 0], [0, 1]], dtype=np.complex64)
            self.X = np.array([[0, 1], [1, 0]], dtype=np.complex64)
            self.Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex64)
            self.Z = np.array([[1, 0], [0, -1]], dtype=np.complex64)
            self.H = np.array([[1, 1], [1, -1]], dtype=np.complex64) / np.sqrt(2)
            self.S = np.array([[1, 0], [0, 1j]], dtype=np.complex64)
            self.T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=np.complex64)
    
    def _get_gate_matrix(self, gate_type: str, params: List[float] = None) -> np.ndarray:
        """Get matrix representation of a quantum gate"""
        if params is None:
            params = []
            
        if gate_type == 'I':
            return self.I
        elif gate_type == 'X':
            return self.X
        elif gate_type == 'Y':
            return self.Y
        elif gate_type == 'Z':
            return self.Z
        elif gate_type == 'H':
            return self.H
        elif gate_type == 'S':
            return self.S
        elif gate_type == 'T':
            return self.T
        elif gate_type == 'RX' and len(params) > 0:
            theta = params[0]
            if self.use_gpu:
                return jnp.array([
                    [jnp.cos(theta/2), -1j*jnp.sin(theta/2)],
                    [-1j*jnp.sin(theta/2), jnp.cos(theta/2)]
                ], dtype=jnp.complex64)
            else:
                return np.array([
                    [np.cos(theta/2), -1j*np.sin(theta/2)],
                    [-1j*np.sin(theta/2), np.cos(theta/2)]
                ], dtype=np.complex64)
        elif gate_type == 'RY' and len(params) > 0:
            theta = params[0]
            if self.use_gpu:
                return jnp.array([
                    [jnp.cos(theta/2), -jnp.sin(theta/2)],
                    [jnp.sin(theta/2), jnp.cos(theta/2)]
                ], dtype=jnp.complex64)
            else:
                return np.array([
                    [np.cos(theta/2), -np.sin(theta/2)],
                    [np.sin(theta/2), np.cos(theta/2)]
                ], dtype=np.complex64)
        elif gate_type == 'RZ' and len(params) > 0:
            theta = params[0]
            if self.use_gpu:
                return jnp.array([
                    [jnp.exp(-1j*theta/2), 0],
                    [0, jnp.exp(1j*theta/2)]
                ], dtype=jnp.complex64)
            else:
                return np.array([
                    [np.exp(-1j*theta/2), 0],
                    [0, np.exp(1j*theta/2)]
                ], dtype=np.complex64)
        else:
            # Default to identity
            return self.I
    
    def _create_initial_state(self, num_qubits: int):
        """Create initial |0...0> state"""
        state_size = 2 ** num_qubits
        if self.use_gpu:
            state = jnp.zeros(state_size, dtype=jnp.complex64)
            state = state.at[0].set(1.0)
            return state
        else:
            state = np.zeros(state_size, dtype=np.complex64)
            state[0] = 1.0
            return state
    
    def _apply_single_qubit_gate(self, state, gate_matrix, qubit_idx: int, num_qubits: int):
        """Apply single-qubit gate to quantum state"""
        if self.use_gpu:
            return self._apply_single_qubit_gate_jax(state, gate_matrix, qubit_idx, num_qubits)
        else:
            return self._apply_single_qubit_gate_numpy(state, gate_matrix, qubit_idx, num_qubits)
    
    def _apply_single_qubit_gate_jax(self, state, gate_matrix, qubit_idx: int, num_qubits: int):
        """JAX implementation of single-qubit gate application"""
        state_size = 2 ** num_qubits
        new_state = jnp.zeros_like(state)
        
        # Vectorized gate application
        for i in range(state_size):
            # Extract bit at qubit_idx position
            bit = (i >> qubit_idx) & 1
            # Flip the bit
            j = i ^ (1 << qubit_idx)
            
            if bit == 0:
                new_state = new_state.at[i].add(gate_matrix[0, 0] * state[i] + gate_matrix[0, 1] * state[j])
                new_state = new_state.at[j].add(gate_matrix[1, 0] * state[i] + gate_matrix[1, 1] * state[j])
        
        return new_state
    
    def _apply_single_qubit_gate_numpy(self, state, gate_matrix, qubit_idx: int, num_qubits: int):
        """NumPy implementation of single-qubit gate application"""
        state_size = 2 ** num_qubits
        new_state = np.zeros_like(state)
        
        for i in range(state_size):
            # Extract bit at qubit_idx position
            bit = (i >> qubit_idx) & 1
            # Flip the bit
            j = i ^ (1 << qubit_idx)
            
            if bit == 0:
                new_state[i] += gate_matrix[0, 0] * state[i] + gate_matrix[0, 1] * state[j]
                new_state[j] += gate_matrix[1, 0] * state[i] + gate_matrix[1, 1] * state[j]
        
        return new_state
    
    def _apply_cnot_gate(self, state, control_qubit: int, target_qubit: int, num_qubits: int):
        """Apply CNOT gate to quantum state"""
        if self.use_gpu:
            return self._apply_cnot_gate_jax(state, control_qubit, target_qubit, num_qubits)
        else:
            return self._apply_cnot_gate_numpy(state, control_qubit, target_qubit, num_qubits)
    
    def _apply_cnot_gate_jax(self, state, control_qubit: int, target_qubit: int, num_qubits: int):
        """JAX implementation of CNOT gate"""
        state_size = 2 ** num_qubits
        new_state = jnp.copy(state)
        
        for i in range(state_size):
            # Check if control qubit is 1
            if (i >> control_qubit) & 1:
                # Flip target qubit
                j = i ^ (1 << target_qubit)
                new_state = new_state.at[i].set(state[j])
                new_state = new_state.at[j].set(state[i])
        
        return new_state
    
    def _apply_cnot_gate_numpy(self, state, control_qubit: int, target_qubit: int, num_qubits: int):
        """NumPy implementation of CNOT gate"""
        state_size = 2 ** num_qubits
        new_state = np.copy(state)
        
        for i in range(state_size):
            # Check if control qubit is 1
            if (i >> control_qubit) & 1:
                # Flip target qubit
                j = i ^ (1 << target_qubit)
                new_state[i] = state[j]
                new_state[j] = state[i]
        
        return new_state
    
    def simulate(self, circuit: Circuit, shots: int = 1024) -> Dict[str, Any]:
        """
        Simulate quantum circuit with GPU acceleration
        
        Args:
            circuit: Quantum circuit to simulate
            shots: Number of measurement shots
            
        Returns:
            Dictionary containing simulation results
        """
        start_time = time.time()
        
        print(f"🚀 Starting GPU simulation: {circuit.width} qubits, {len(circuit.gates)} gates")
        
        # Initialize quantum state
        num_qubits = circuit.width
        state = self._create_initial_state(num_qubits)
        
        # Apply gates
        gate_time = 0
        for i, gate in enumerate(circuit.gates):
            gate_start = time.time()
            
            # Determine gate type
            if hasattr(gate, 'type') and hasattr(gate.type, 'name'):
                gate_type = gate.type.name
            elif hasattr(gate, 'name'):
                gate_type = gate.name
            else:
                gate_type = str(gate.__class__.__name__).replace('Gate', '').upper()
            
            qubits = gate.qubits if hasattr(gate, 'qubits') else []
            
            # Get parameters
            if hasattr(gate, 'parameters'):
                params = gate.parameters
            elif hasattr(gate, 'params'):
                params = gate.params
            else:
                params = []
            
            # Extract qubit IDs from Qubit objects
            qubit_ids = []
            for qubit in qubits:
                if hasattr(qubit, 'id'):
                    qubit_ids.append(qubit.id)
                elif isinstance(qubit, int):
                    qubit_ids.append(qubit)
                else:
                    qubit_ids.append(0)  # Default fallback
            
            if gate_type == 'CNOT' and len(qubit_ids) >= 2:
                state = self._apply_cnot_gate(state, qubit_ids[0], qubit_ids[1], num_qubits)
            elif len(qubit_ids) >= 1:
                gate_matrix = self._get_gate_matrix(gate_type, params)
                state = self._apply_single_qubit_gate(state, gate_matrix, qubit_ids[0], num_qubits)
            
            gate_time += time.time() - gate_start
            
            if (i + 1) % 10 == 0:
                print(f"   Processed {i + 1}/{len(circuit.gates)} gates")
        
        # Perform measurements
        measurement_time = time.time()
        
        if self.use_gpu:
            # Convert to numpy for measurements
            state_np = np.array(state)
        else:
            state_np = state
            
        probabilities = np.abs(state_np) ** 2
        
        # Sample measurements
        results = {}
        for shot in range(shots):
            measurement = np.random.choice(len(probabilities), p=probabilities)
            # Convert to binary string
            binary_result = format(measurement, f'0{num_qubits}b')
            if binary_result in results:
                results[binary_result] += 1
            else:
                results[binary_result] = 1
        
        measurement_time = time.time() - measurement_time
        total_time = time.time() - start_time
        
        # Performance metrics
        performance = {
            'total_time': total_time,
            'gate_time': gate_time,
            'measurement_time': measurement_time,
            'gates_per_second': len(circuit.gates) / gate_time if gate_time > 0 else 0,
            'device_type': 'GPU' if self.use_gpu else 'CPU',
            'device_count': self.device_count,
            'precision': self.precision
        }
        
        print(f"✅ Simulation completed in {total_time:.3f}s")
        print(f"   Gate operations: {gate_time:.3f}s ({performance['gates_per_second']:.1f} gates/s)")
        print(f"   Measurements: {measurement_time:.3f}s")
        print(f"   Device: {performance['device_type']}")
        
        return {
            'results': results,
            'shots': shots,
            'circuit_info': {
                'qubits': num_qubits,
                'gates': len(circuit.gates),
                'depth': circuit.depth
            },
            'performance': performance,
            'final_state': state_np.tolist() if len(state_np) <= 32 else None  # Only return for small states
        }
    
    def benchmark(self, num_qubits: int = 10, num_gates: int = 100) -> Dict[str, float]:
        """
        Benchmark GPU vs CPU performance
        
        Args:
            num_qubits: Number of qubits for benchmark
            num_gates: Number of gates for benchmark
            
        Returns:
            Performance comparison results
        """
        print(f"🏁 Running benchmark: {num_qubits} qubits, {num_gates} gates")
        
        # Create benchmark circuit
        from ..core.circuit import Circuit
        from ..core.gates import HGate, XGate, CNOTGate
        
        circuit = Circuit(num_qubits)
        
        # Add random gates
        import random
        for _ in range(num_gates):
            gate_type = random.choice(['H', 'X', 'CNOT'])
            if gate_type == 'CNOT' and num_qubits > 1:
                control = random.randint(0, num_qubits - 1)
                target = random.randint(0, num_qubits - 1)
                while target == control:
                    target = random.randint(0, num_qubits - 1)
                circuit.add_gate(CNOTGate(), control, target)
            else:
                qubit = random.randint(0, num_qubits - 1)
                if gate_type == 'H':
                    circuit.add_gate(HGate(), qubit)
                else:
                    circuit.add_gate(XGate(), qubit)
        
        # Benchmark GPU
        gpu_start = time.time()
        self.use_gpu = True and HAS_JAX
        gpu_results = self.simulate(circuit, shots=100)
        gpu_time = time.time() - gpu_start
        
        # Benchmark CPU
        cpu_start = time.time()
        self.use_gpu = False
        cpu_results = self.simulate(circuit, shots=100)
        cpu_time = time.time() - cpu_start
        
        # Restore GPU setting
        self.use_gpu = True and HAS_JAX
        
        speedup = cpu_time / gpu_time if gpu_time > 0 else 1.0
        
        benchmark_results = {
            'gpu_time': gpu_time,
            'cpu_time': cpu_time,
            'speedup': speedup,
            'gpu_gates_per_second': gpu_results['performance']['gates_per_second'],
            'cpu_gates_per_second': cpu_results['performance']['gates_per_second']
        }
        
        print(f"📊 Benchmark Results:")
        print(f"   GPU Time: {gpu_time:.3f}s")
        print(f"   CPU Time: {cpu_time:.3f}s")
        print(f"   Speedup: {speedup:.2f}x")
        
        return benchmark_results 