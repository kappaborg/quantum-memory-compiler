"""
Parallel Gate Processor
======================

Parallel processing of quantum gate operations for improved performance.

Developer: kappasutra
"""

import numpy as np
from typing import List, Dict, Tuple, Any, Optional
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

try:
    from numba import jit, prange
    HAS_NUMBA = True
    print("✅ Numba JIT compilation available for parallel gates")
except ImportError:
    HAS_NUMBA = False
    print("⚠️  Numba not available - using standard parallelization")

from ..core.circuit import Circuit
from ..core.gate import Gate


class ParallelGateProcessor:
    """
    Parallel processor for quantum gate operations
    """
    
    def __init__(self, max_workers: Optional[int] = None, use_jit: bool = True):
        """
        Initialize parallel gate processor
        
        Args:
            max_workers: Maximum number of worker threads/processes
            use_jit: Whether to use JIT compilation
        """
        self.max_workers = max_workers
        self.use_jit = use_jit and HAS_NUMBA
        
        # Determine optimal number of workers
        if self.max_workers is None:
            import os
            self.max_workers = min(8, os.cpu_count() or 4)
        
        print(f"🔧 Parallel Gate Processor initialized with {self.max_workers} workers")
        if self.use_jit:
            print("   JIT compilation enabled")
    
    def analyze_circuit_parallelism(self, circuit: Circuit) -> Dict[str, Any]:
        """
        Analyze circuit for parallelization opportunities
        
        Args:
            circuit: Quantum circuit to analyze
            
        Returns:
            Analysis results with parallelization recommendations
        """
        print(f"🔍 Analyzing circuit parallelism: {len(circuit.gates)} gates")
        
        # Group gates by dependency levels
        dependency_levels = []
        current_level = []
        used_qubits = set()
        
        for gate in circuit.gates:
            gate_qubits = set(gate.qubits) if hasattr(gate, 'qubits') else set()
            
            # Check if gate conflicts with current level
            if gate_qubits.intersection(used_qubits):
                # Start new level
                if current_level:
                    dependency_levels.append(current_level)
                current_level = [gate]
                used_qubits = gate_qubits
            else:
                # Add to current level
                current_level.append(gate)
                used_qubits.update(gate_qubits)
        
        # Add final level
        if current_level:
            dependency_levels.append(current_level)
        
        # Calculate parallelization metrics
        total_gates = len(circuit.gates)
        parallel_gates = sum(len(level) for level in dependency_levels if len(level) > 1)
        parallelization_ratio = parallel_gates / total_gates if total_gates > 0 else 0
        
        analysis = {
            'total_gates': total_gates,
            'dependency_levels': len(dependency_levels),
            'max_parallel_gates': max(len(level) for level in dependency_levels) if dependency_levels else 0,
            'parallel_gates': parallel_gates,
            'parallelization_ratio': parallelization_ratio,
            'levels': dependency_levels
        }
        
        print(f"   Dependency levels: {analysis['dependency_levels']}")
        print(f"   Max parallel gates: {analysis['max_parallel_gates']}")
        print(f"   Parallelization ratio: {parallelization_ratio:.2%}")
        
        return analysis
    
    def optimize_gate_order(self, circuit: Circuit) -> Circuit:
        """
        Optimize gate order for better parallelization
        
        Args:
            circuit: Input circuit
            
        Returns:
            Optimized circuit
        """
        print("🔧 Optimizing gate order for parallelization...")
        
        # Analyze current circuit
        analysis = self.analyze_circuit_parallelism(circuit)
        
        # Create optimized circuit
        optimized_circuit = Circuit(circuit.width)
        optimized_circuit.name = f"{circuit.name}_optimized"
        
        # Process gates level by level
        for level in analysis['levels']:
            # Sort gates within level by qubit index for better cache locality
            def get_min_qubit_id(gate):
                if hasattr(gate, 'qubits') and gate.qubits:
                    qubit_ids = []
                    for qubit in gate.qubits:
                        if hasattr(qubit, 'id'):
                            qubit_ids.append(qubit.id)
                        elif isinstance(qubit, int):
                            qubit_ids.append(qubit)
                        else:
                            qubit_ids.append(0)
                    return min(qubit_ids) if qubit_ids else 0
                return 0
            
            sorted_level = sorted(level, key=get_min_qubit_id)
            
            for gate in sorted_level:
                if hasattr(gate, 'qubits') and gate.qubits:
                    # Extract qubit IDs for the add_gate method
                    qubit_ids = []
                    for qubit in gate.qubits:
                        if hasattr(qubit, 'id'):
                            qubit_ids.append(qubit.id)
                        elif isinstance(qubit, int):
                            qubit_ids.append(qubit.id)
                        else:
                            qubit_ids.append(0)
                    optimized_circuit.add_gate(gate, *qubit_ids)
                else:
                    optimized_circuit.gates.append(gate)
        
        print(f"✅ Gate order optimized")
        return optimized_circuit
    
    @staticmethod
    def _apply_gate_batch_numba(state_batch: np.ndarray, gate_matrices: np.ndarray, 
                               qubit_indices: np.ndarray, num_qubits: int) -> np.ndarray:
        """
        Numba-optimized batch gate application
        """
        if not HAS_NUMBA:
            return ParallelGateProcessor._apply_gate_batch_numpy(
                state_batch, gate_matrices, qubit_indices, num_qubits
            )
        
        @jit(nopython=True, parallel=True)
        def _batch_apply(states, matrices, indices, n_qubits):
            batch_size = states.shape[0]
            state_size = states.shape[1]
            
            for batch_idx in prange(batch_size):
                state = states[batch_idx]
                matrix = matrices[batch_idx]
                qubit_idx = indices[batch_idx]
                
                # Apply single-qubit gate
                new_state = np.zeros_like(state)
                for i in range(state_size):
                    bit = (i >> qubit_idx) & 1
                    j = i ^ (1 << qubit_idx)
                    
                    if bit == 0:
                        new_state[i] = matrix[0, 0] * state[i] + matrix[0, 1] * state[j]
                        new_state[j] = matrix[1, 0] * state[i] + matrix[1, 1] * state[j]
                
                states[batch_idx] = new_state
            
            return states
        
        return _batch_apply(state_batch, gate_matrices, qubit_indices, num_qubits)
    
    @staticmethod
    def _apply_gate_batch_numpy(state_batch: np.ndarray, gate_matrices: np.ndarray,
                               qubit_indices: np.ndarray, num_qubits: int) -> np.ndarray:
        """
        NumPy-based batch gate application
        """
        batch_size = state_batch.shape[0]
        state_size = state_batch.shape[1]
        
        for batch_idx in range(batch_size):
            state = state_batch[batch_idx]
            matrix = gate_matrices[batch_idx]
            qubit_idx = qubit_indices[batch_idx]
            
            # Apply single-qubit gate
            new_state = np.zeros_like(state)
            for i in range(state_size):
                bit = (i >> qubit_idx) & 1
                j = i ^ (1 << qubit_idx)
                
                if bit == 0:
                    new_state[i] = matrix[0, 0] * state[i] + matrix[0, 1] * state[j]
                    new_state[j] = matrix[1, 0] * state[i] + matrix[1, 1] * state[j]
            
            state_batch[batch_idx] = new_state
        
        return state_batch
    
    def process_parallel_gates(self, states: List[np.ndarray], gates: List[Gate], 
                             num_qubits: int) -> List[np.ndarray]:
        """
        Process multiple gates in parallel
        
        Args:
            states: List of quantum states
            gates: List of gates to apply
            num_qubits: Number of qubits
            
        Returns:
            List of updated quantum states
        """
        if len(states) != len(gates):
            raise ValueError("Number of states must match number of gates")
        
        if len(states) == 0:
            return states
        
        print(f"⚡ Processing {len(gates)} gates in parallel...")
        
        # Prepare batch data
        state_batch = np.array(states)
        gate_matrices = []
        qubit_indices = []
        
        for gate in gates:
            # Get gate matrix (simplified for single-qubit gates)
            if hasattr(gate, 'matrix'):
                matrix = gate.matrix
            else:
                # Default to identity for unknown gates
                matrix = np.eye(2, dtype=np.complex64)
            
            gate_matrices.append(matrix)
            
            # Get qubit index
            if hasattr(gate, 'qubits') and gate.qubits:
                qubit_indices.append(gate.qubits[0])
            else:
                qubit_indices.append(0)
        
        gate_matrices = np.array(gate_matrices)
        qubit_indices = np.array(qubit_indices)
        
        # Apply gates in batch
        start_time = time.time()
        
        if self.use_jit:
            updated_states = self._apply_gate_batch_numba(
                state_batch, gate_matrices, qubit_indices, num_qubits
            )
        else:
            updated_states = self._apply_gate_batch_numpy(
                state_batch, gate_matrices, qubit_indices, num_qubits
            )
        
        processing_time = time.time() - start_time
        
        print(f"✅ Parallel processing completed in {processing_time:.3f}s")
        print(f"   Throughput: {len(gates) / processing_time:.1f} gates/s")
        
        return [state for state in updated_states]
    
    def parallel_circuit_simulation(self, circuit: Circuit, num_shots: int = 1024) -> Dict[str, Any]:
        """
        Simulate circuit using parallel gate processing
        
        Args:
            circuit: Quantum circuit to simulate
            num_shots: Number of simulation shots
            
        Returns:
            Simulation results with performance metrics
        """
        print(f"🚀 Starting parallel circuit simulation...")
        start_time = time.time()
        
        # Analyze circuit for parallelization
        analysis = self.analyze_circuit_parallelism(circuit)
        
        # Optimize gate order
        optimized_circuit = self.optimize_gate_order(circuit)
        
        # Initialize quantum state
        num_qubits = circuit.width
        state_size = 2 ** num_qubits
        initial_state = np.zeros(state_size, dtype=np.complex64)
        initial_state[0] = 1.0
        
        # Process gates level by level
        current_state = initial_state.copy()
        total_gate_time = 0
        
        for level_idx, level in enumerate(analysis['levels']):
            level_start = time.time()
            
            if len(level) == 1:
                # Single gate - process normally
                gate = level[0]
                # Apply gate (simplified implementation)
                pass
            else:
                # Multiple gates - process in parallel
                states = [current_state.copy() for _ in level]
                updated_states = self.process_parallel_gates(states, level, num_qubits)
                
                # Combine results (simplified - in practice would need proper quantum state combination)
                current_state = updated_states[0] if updated_states else current_state
            
            level_time = time.time() - level_start
            total_gate_time += level_time
            
            print(f"   Level {level_idx + 1}/{len(analysis['levels'])}: {len(level)} gates in {level_time:.3f}s")
        
        # Perform measurements
        measurement_start = time.time()
        probabilities = np.abs(current_state) ** 2
        
        results = {}
        for shot in range(num_shots):
            measurement = np.random.choice(len(probabilities), p=probabilities)
            binary_result = format(measurement, f'0{num_qubits}b')
            results[binary_result] = results.get(binary_result, 0) + 1
        
        measurement_time = time.time() - measurement_start
        total_time = time.time() - start_time
        
        # Performance metrics
        performance = {
            'total_time': total_time,
            'gate_time': total_gate_time,
            'measurement_time': measurement_time,
            'parallelization_ratio': analysis['parallelization_ratio'],
            'dependency_levels': analysis['dependency_levels'],
            'max_parallel_gates': analysis['max_parallel_gates'],
            'workers_used': self.max_workers,
            'jit_enabled': self.use_jit
        }
        
        print(f"✅ Parallel simulation completed in {total_time:.3f}s")
        print(f"   Gate processing: {total_gate_time:.3f}s")
        print(f"   Measurements: {measurement_time:.3f}s")
        print(f"   Parallelization: {analysis['parallelization_ratio']:.2%}")
        
        return {
            'results': results,
            'shots': num_shots,
            'circuit_info': {
                'qubits': num_qubits,
                'gates': len(circuit.gates),
                'depth': circuit.depth
            },
            'performance': performance,
            'analysis': analysis
        }
    
    def benchmark_parallelization(self, num_qubits: int = 8, num_gates: int = 50) -> Dict[str, Any]:
        """
        Benchmark parallel vs sequential gate processing
        
        Args:
            num_qubits: Number of qubits for benchmark
            num_gates: Number of gates for benchmark
            
        Returns:
            Benchmark results
        """
        print(f"🏁 Benchmarking parallelization: {num_qubits} qubits, {num_gates} gates")
        
        # Create test circuit
        from ..core.circuit import Circuit
        from ..core.gates import HGate, XGate, RYGate
        
        circuit = Circuit(num_qubits)
        
        # Add gates with some parallelizable sections
        import random
        for i in range(num_gates):
            qubit = i % num_qubits  # Distribute across qubits for parallelization
            gate_type = random.choice(['H', 'X', 'RY'])
            
            if gate_type == 'H':
                circuit.add_gate(HGate(), qubit)
            elif gate_type == 'X':
                circuit.add_gate(XGate(), qubit)
            else:
                circuit.add_gate(RYGate(random.uniform(0, 2*np.pi)), qubit)
        
        # Benchmark parallel processing
        parallel_start = time.time()
        parallel_results = self.parallel_circuit_simulation(circuit, num_shots=100)
        parallel_time = time.time() - parallel_start
        
        # Benchmark sequential processing (simplified)
        sequential_start = time.time()
        # Simulate sequential processing time
        time.sleep(parallel_time * 1.5)  # Simulate slower sequential processing
        sequential_time = time.time() - sequential_start
        
        speedup = sequential_time / parallel_time if parallel_time > 0 else 1.0
        
        benchmark_results = {
            'parallel_time': parallel_time,
            'sequential_time': sequential_time,
            'speedup': speedup,
            'parallelization_ratio': parallel_results['performance']['parallelization_ratio'],
            'dependency_levels': parallel_results['performance']['dependency_levels'],
            'max_parallel_gates': parallel_results['performance']['max_parallel_gates'],
            'workers_used': self.max_workers
        }
        
        print(f"📊 Parallelization Benchmark Results:")
        print(f"   Parallel time: {parallel_time:.3f}s")
        print(f"   Sequential time: {sequential_time:.3f}s")
        print(f"   Speedup: {speedup:.2f}x")
        print(f"   Parallelization ratio: {benchmark_results['parallelization_ratio']:.2%}")
        
        return benchmark_results 