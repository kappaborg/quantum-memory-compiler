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
Acceleration Manager
===================

Central manager for GPU acceleration features in Quantum Memory Compiler.

Developer: kappasutra
"""

import numpy as np
from typing import Dict, List, Any, Optional, Union
import time
import json

from .gpu_simulator import GPUSimulator
from .parallel_gates import ParallelGateProcessor
from .memory_optimizer import GPUMemoryOptimizer
from ..core.circuit import Circuit


class AccelerationManager:
    """
    Central manager for all GPU acceleration features
    """
    
    def __init__(self, 
                 enable_gpu: bool = True,
                 max_memory_gb: float = 4.0,
                 max_workers: Optional[int] = None,
                 precision: str = 'float32'):
        """
        Initialize acceleration manager
        
        Args:
            enable_gpu: Whether to enable GPU acceleration
            max_memory_gb: Maximum GPU memory to use
            max_workers: Maximum parallel workers
            precision: Numerical precision
        """
        self.enable_gpu = enable_gpu
        self.max_memory_gb = max_memory_gb
        self.max_workers = max_workers
        self.precision = precision
        
        print("🚀 Quantum Memory Compiler - GPU Acceleration Manager")
        print("=" * 60)
        
        # Initialize components
        self.gpu_simulator = GPUSimulator(
            use_gpu=enable_gpu,
            precision=precision
        )
        
        self.parallel_processor = ParallelGateProcessor(
            max_workers=max_workers,
            use_jit=True
        )
        
        self.memory_optimizer = GPUMemoryOptimizer(
            max_memory_gb=max_memory_gb,
            enable_memory_mapping=True
        )
        
        # Performance tracking
        self.performance_history = []
        self.benchmark_results = {}
        
        print("=" * 60)
        print("✅ GPU Acceleration Manager initialized successfully!")
        
        # Run initial system check
        self._system_check()
    
    def _system_check(self):
        """Perform initial system capability check"""
        print("\n🔍 System Capability Check:")
        print("-" * 30)
        
        # Check GPU availability
        gpu_available = hasattr(self.gpu_simulator, 'use_gpu') and self.gpu_simulator.use_gpu
        print(f"   GPU Acceleration: {'✅ Available' if gpu_available else '❌ Not Available'}")
        
        # Check parallel processing
        parallel_available = self.parallel_processor.max_workers > 1
        print(f"   Parallel Processing: {'✅ Available' if parallel_available else '❌ Limited'}")
        print(f"   Worker Threads: {self.parallel_processor.max_workers}")
        
        # Check memory optimization
        memory_available = self.memory_optimizer.max_memory_gb > 0
        print(f"   Memory Optimization: {'✅ Available' if memory_available else '❌ Limited'}")
        print(f"   Memory Limit: {self.memory_optimizer.max_memory_gb:.1f} GB")
        
        # Overall acceleration status
        acceleration_level = sum([gpu_available, parallel_available, memory_available])
        if acceleration_level == 3:
            status = "🚀 Full Acceleration"
        elif acceleration_level == 2:
            status = "⚡ Partial Acceleration"
        elif acceleration_level == 1:
            status = "🔄 Basic Acceleration"
        else:
            status = "❌ No Acceleration"
        
        print(f"   Overall Status: {status}")
        print("-" * 30)
    
    def analyze_circuit(self, circuit: Circuit) -> Dict[str, Any]:
        """
        Comprehensive circuit analysis for acceleration optimization
        
        Args:
            circuit: Quantum circuit to analyze
            
        Returns:
            Analysis results with optimization recommendations
        """
        print(f"\n🔍 Analyzing Circuit: {circuit.name}")
        print("=" * 50)
        
        analysis_start = time.time()
        
        # Basic circuit info
        circuit_info = {
            'name': circuit.name,
            'qubits': circuit.width,
            'gates': len(circuit.gates),
            'depth': circuit.depth
        }
        
        # Memory analysis
        memory_requirements = self.memory_optimizer.estimate_memory_requirements(circuit, self.precision)
        memory_suggestions = self.memory_optimizer.suggest_optimizations(circuit)
        
        # Parallelization analysis
        parallelism_analysis = self.parallel_processor.analyze_circuit_parallelism(circuit)
        
        # GPU compatibility check
        gpu_compatible = memory_requirements['total_memory_gb'] <= self.max_memory_gb
        
        # Performance predictions
        estimated_speedup = self._estimate_speedup(circuit, parallelism_analysis, gpu_compatible)
        
        analysis_time = time.time() - analysis_start
        
        analysis_results = {
            'circuit_info': circuit_info,
            'memory_analysis': {
                'requirements': memory_requirements,
                'suggestions': memory_suggestions,
                'gpu_compatible': gpu_compatible
            },
            'parallelism_analysis': parallelism_analysis,
            'performance_predictions': {
                'estimated_speedup': estimated_speedup,
                'recommended_method': self._recommend_simulation_method(circuit, parallelism_analysis, gpu_compatible)
            },
            'analysis_time': analysis_time
        }
        
        print(f"\n📊 Analysis Summary:")
        print(f"   Circuit: {circuit_info['qubits']} qubits, {circuit_info['gates']} gates")
        print(f"   Memory: {memory_requirements['total_memory_gb']:.3f} GB required")
        print(f"   Parallelization: {parallelism_analysis['parallelization_ratio']:.2%}")
        print(f"   Estimated speedup: {estimated_speedup:.2f}x")
        print(f"   Analysis time: {analysis_time:.3f}s")
        
        return analysis_results
    
    def _estimate_speedup(self, circuit: Circuit, parallelism_analysis: Dict, gpu_compatible: bool) -> float:
        """Estimate potential speedup from acceleration"""
        base_speedup = 1.0
        
        # GPU speedup
        if gpu_compatible and self.enable_gpu:
            base_speedup *= 2.0  # Conservative GPU speedup estimate
        
        # Parallel processing speedup
        if parallelism_analysis['parallelization_ratio'] > 0.1:
            parallel_speedup = min(self.parallel_processor.max_workers, 
                                 parallelism_analysis['max_parallel_gates'])
            base_speedup *= (1 + parallelism_analysis['parallelization_ratio'] * (parallel_speedup - 1))
        
        # Memory optimization speedup
        if len(circuit.gates) > 100:
            base_speedup *= 1.2  # Memory optimization benefits
        
        return base_speedup
    
    def _recommend_simulation_method(self, circuit: Circuit, parallelism_analysis: Dict, gpu_compatible: bool) -> str:
        """Recommend optimal simulation method"""
        if gpu_compatible and self.enable_gpu and parallelism_analysis['parallelization_ratio'] > 0.2:
            return "hybrid_gpu_parallel"
        elif gpu_compatible and self.enable_gpu:
            return "gpu_accelerated"
        elif parallelism_analysis['parallelization_ratio'] > 0.3:
            return "parallel_cpu"
        else:
            return "standard_cpu"
    
    def simulate_circuit(self, circuit: Circuit, 
                        shots: int = 1024,
                        method: str = 'auto',
                        optimize_memory: bool = True) -> Dict[str, Any]:
        """
        Simulate quantum circuit with optimal acceleration
        
        Args:
            circuit: Quantum circuit to simulate
            shots: Number of measurement shots
            method: Simulation method ('auto', 'gpu', 'parallel', 'standard')
            optimize_memory: Whether to optimize memory usage
            
        Returns:
            Simulation results with performance metrics
        """
        print(f"\n🚀 Starting Accelerated Simulation")
        print("=" * 50)
        
        simulation_start = time.time()
        
        # Analyze circuit if method is auto
        if method == 'auto':
            analysis = self.analyze_circuit(circuit)
            method = analysis['performance_predictions']['recommended_method']
            print(f"   Auto-selected method: {method}")
        
        # Memory optimization
        if optimize_memory:
            print("\n🧠 Memory Optimization Phase:")
            memory_start = time.time()
            
            # Get memory suggestions
            suggestions = self.memory_optimizer.suggest_optimizations(circuit)
            
            # Monitor memory usage
            initial_memory = self.memory_optimizer.monitor_memory_usage("simulation_start")
            
            memory_time = time.time() - memory_start
            print(f"   Memory optimization completed in {memory_time:.3f}s")
        
        # Execute simulation based on method
        print(f"\n⚡ Executing Simulation: {method}")
        execution_start = time.time()
        
        if method == 'hybrid_gpu_parallel':
            results = self._hybrid_simulation(circuit, shots)
        elif method == 'gpu_accelerated':
            results = self.gpu_simulator.simulate(circuit, shots)
        elif method == 'parallel_cpu':
            results = self.parallel_processor.parallel_circuit_simulation(circuit, shots)
        else:  # standard_cpu
            results = self._standard_simulation(circuit, shots)
        
        execution_time = time.time() - execution_start
        total_time = time.time() - simulation_start
        
        # Post-simulation memory cleanup
        if optimize_memory:
            cleanup_stats = self.memory_optimizer.cleanup_memory()
            final_memory = self.memory_optimizer.monitor_memory_usage("simulation_end")
        
        # Enhanced results with acceleration metrics
        enhanced_results = {
            **results,
            'acceleration_info': {
                'method_used': method,
                'total_simulation_time': total_time,
                'execution_time': execution_time,
                'memory_optimized': optimize_memory,
                'gpu_used': 'gpu' in method,
                'parallel_used': 'parallel' in method
            }
        }
        
        # Update performance history
        self.performance_history.append({
            'timestamp': time.time(),
            'circuit_name': circuit.name,
            'method': method,
            'qubits': circuit.width,
            'gates': len(circuit.gates),
            'shots': shots,
            'total_time': total_time,
            'execution_time': execution_time
        })
        
        print(f"\n✅ Simulation Completed!")
        print(f"   Method: {method}")
        print(f"   Total time: {total_time:.3f}s")
        print(f"   Execution time: {execution_time:.3f}s")
        
        return enhanced_results
    
    def _hybrid_simulation(self, circuit: Circuit, shots: int) -> Dict[str, Any]:
        """Hybrid GPU + parallel simulation"""
        print("   Using hybrid GPU + parallel processing...")
        
        # Use GPU simulator with parallel gate processing
        # This is a simplified implementation - in practice would coordinate both
        return self.gpu_simulator.simulate(circuit, shots)
    
    def _standard_simulation(self, circuit: Circuit, shots: int) -> Dict[str, Any]:
        """Standard CPU simulation"""
        print("   Using standard CPU simulation...")
        
        # Simplified standard simulation
        start_time = time.time()
        
        # Basic simulation (placeholder)
        results = {'00': shots // 2, '11': shots // 2}  # Simplified results
        
        simulation_time = time.time() - start_time
        
        return {
            'results': results,
            'shots': shots,
            'circuit_info': {
                'qubits': circuit.width,
                'gates': len(circuit.gates),
                'depth': circuit.depth
            },
            'performance': {
                'total_time': simulation_time,
                'device_type': 'CPU',
                'method': 'standard'
            },
            'acceleration_info': {
                'method_used': 'standard_cpu',
                'total_simulation_time': simulation_time,
                'execution_time': simulation_time,
                'memory_optimized': False,
                'gpu_used': False,
                'parallel_used': False
            }
        }
    
    def benchmark_acceleration(self, 
                             qubit_range: List[int] = [4, 6, 8, 10],
                             gate_counts: List[int] = [50, 100, 200],
                             shots: int = 100) -> Dict[str, Any]:
        """
        Comprehensive acceleration benchmarking
        
        Args:
            qubit_range: Range of qubit counts to test
            gate_counts: Range of gate counts to test
            shots: Number of shots per benchmark
            
        Returns:
            Comprehensive benchmark results
        """
        print("\n🏁 Starting Comprehensive Acceleration Benchmark")
        print("=" * 60)
        
        benchmark_start = time.time()
        benchmark_results = {
            'timestamp': time.time(),
            'system_info': self._get_system_info(),
            'test_configurations': [],
            'performance_comparison': {},
            'recommendations': []
        }
        
        # Test different configurations
        for qubits in qubit_range:
            for gates in gate_counts:
                print(f"\n📊 Testing: {qubits} qubits, {gates} gates")
                
                # Create test circuit
                test_circuit = self._create_test_circuit(qubits, gates)
                
                # Test different methods
                methods = ['standard_cpu', 'parallel_cpu']
                if self.enable_gpu:
                    methods.extend(['gpu_accelerated', 'hybrid_gpu_parallel'])
                
                config_results = {
                    'qubits': qubits,
                    'gates': gates,
                    'methods': {}
                }
                
                for method in methods:
                    try:
                        print(f"   Testing {method}...")
                        result = self.simulate_circuit(test_circuit, shots, method, optimize_memory=True)
                        
                        config_results['methods'][method] = {
                            'total_time': result['acceleration_info']['total_time'],
                            'execution_time': result['acceleration_info']['execution_time'],
                            'success': True
                        }
                        
                    except Exception as e:
                        print(f"   {method} failed: {e}")
                        config_results['methods'][method] = {
                            'error': str(e),
                            'success': False
                        }
                
                benchmark_results['test_configurations'].append(config_results)
        
        # Analyze results
        benchmark_results['performance_comparison'] = self._analyze_benchmark_results(
            benchmark_results['test_configurations']
        )
        
        # Generate recommendations
        benchmark_results['recommendations'] = self._generate_recommendations(
            benchmark_results['performance_comparison']
        )
        
        benchmark_time = time.time() - benchmark_start
        benchmark_results['benchmark_time'] = benchmark_time
        
        # Store results
        self.benchmark_results = benchmark_results
        
        print(f"\n✅ Benchmark completed in {benchmark_time:.1f}s")
        self._print_benchmark_summary(benchmark_results)
        
        return benchmark_results
    
    def _create_test_circuit(self, qubits: int, gates: int) -> Circuit:
        """Create test circuit for benchmarking"""
        from ..core.circuit import Circuit
        from ..core.gates import HGate, XGate, CNOTGate
        
        circuit = Circuit(qubits)
        circuit.name = f"benchmark_{qubits}q_{gates}g"
        
        import random
        for _ in range(gates):
            gate_type = random.choice(['H', 'X', 'CNOT'])
            if gate_type == 'CNOT' and qubits > 1:
                control = random.randint(0, qubits - 1)
                target = random.randint(0, qubits - 1)
                while target == control:
                    target = random.randint(0, qubits - 1)
                circuit.add_gate(CNOTGate(), control, target)
            else:
                qubit = random.randint(0, qubits - 1)
                if gate_type == 'H':
                    circuit.add_gate(HGate(), qubit)
                else:
                    circuit.add_gate(XGate(), qubit)
        
        return circuit
    
    def _analyze_benchmark_results(self, configurations: List[Dict]) -> Dict[str, Any]:
        """Analyze benchmark results for performance comparison"""
        analysis = {
            'method_performance': {},
            'speedup_analysis': {},
            'scalability_analysis': {}
        }
        
        # Aggregate performance by method
        for config in configurations:
            for method, result in config['methods'].items():
                if result['success']:
                    if method not in analysis['method_performance']:
                        analysis['method_performance'][method] = []
                    
                    analysis['method_performance'][method].append({
                        'qubits': config['qubits'],
                        'gates': config['gates'],
                        'time': result['total_time']
                    })
        
        # Calculate speedups relative to standard_cpu
        if 'standard_cpu' in analysis['method_performance']:
            baseline_times = {
                (r['qubits'], r['gates']): r['time'] 
                for r in analysis['method_performance']['standard_cpu']
            }
            
            for method, results in analysis['method_performance'].items():
                if method != 'standard_cpu':
                    speedups = []
                    for result in results:
                        key = (result['qubits'], result['gates'])
                        if key in baseline_times:
                            speedup = baseline_times[key] / result['time']
                            speedups.append(speedup)
                    
                    if speedups:
                        analysis['speedup_analysis'][method] = {
                            'average_speedup': np.mean(speedups),
                            'max_speedup': np.max(speedups),
                            'min_speedup': np.min(speedups)
                        }
        
        return analysis
    
    def _generate_recommendations(self, performance_analysis: Dict) -> List[str]:
        """Generate optimization recommendations based on benchmark results"""
        recommendations = []
        
        if 'speedup_analysis' in performance_analysis:
            speedups = performance_analysis['speedup_analysis']
            
            if speedups:  # Check if speedups dictionary is not empty
                # Find best performing method
                best_method = max(speedups.keys(), 
                                key=lambda m: speedups[m]['average_speedup'])
                best_speedup = speedups[best_method]['average_speedup']
                
                recommendations.append(f"Best performing method: {best_method} ({best_speedup:.2f}x speedup)")
                
                # GPU recommendations
                if any('gpu' in method for method in speedups.keys()):
                    gpu_methods = {k: v for k, v in speedups.items() if 'gpu' in k}
                    if gpu_methods:
                        best_gpu = max(gpu_methods.keys(), 
                                     key=lambda m: gpu_methods[m]['average_speedup'])
                        recommendations.append(f"Best GPU method: {best_gpu}")
                
                # Parallel processing recommendations
                if any('parallel' in method for method in speedups.keys()):
                    recommendations.append("Parallel processing shows benefits for this system")
        
        if not recommendations:
            recommendations.append("Standard CPU simulation is optimal for current configuration")
        
        return recommendations
    
    def _print_benchmark_summary(self, results: Dict):
        """Print benchmark summary"""
        print("\n📊 Benchmark Summary:")
        print("-" * 40)
        
        if 'performance_comparison' in results:
            speedups = results['performance_comparison'].get('speedup_analysis', {})
            
            for method, analysis in speedups.items():
                print(f"   {method}: {analysis['average_speedup']:.2f}x average speedup")
        
        print("\n💡 Recommendations:")
        for i, rec in enumerate(results.get('recommendations', []), 1):
            print(f"   {i}. {rec}")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for benchmarking"""
        import platform
        import psutil
        
        return {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(),
            'memory_gb': psutil.virtual_memory().total / (1024**3),
            'gpu_available': self.enable_gpu,
            'max_workers': self.parallel_processor.max_workers
        }
    
    def get_acceleration_status(self) -> Dict[str, Any]:
        """Get current acceleration status and capabilities"""
        return {
            'gpu_acceleration': {
                'enabled': self.enable_gpu,
                'available': hasattr(self.gpu_simulator, 'use_gpu') and self.gpu_simulator.use_gpu,
                'device_count': getattr(self.gpu_simulator, 'device_count', 0)
            },
            'parallel_processing': {
                'enabled': True,
                'max_workers': self.parallel_processor.max_workers,
                'jit_enabled': self.parallel_processor.use_jit
            },
            'memory_optimization': {
                'enabled': True,
                'max_memory_gb': self.memory_optimizer.max_memory_gb,
                'memory_mapping': self.memory_optimizer.enable_memory_mapping
            },
            'performance_history': len(self.performance_history),
            'last_benchmark': self.benchmark_results.get('timestamp', None)
        }
    
    def save_benchmark_results(self, filename: str):
        """Save benchmark results to file"""
        if self.benchmark_results:
            with open(filename, 'w') as f:
                json.dump(self.benchmark_results, f, indent=2, default=str)
            print(f"📁 Benchmark results saved to {filename}")
        else:
            print("⚠️  No benchmark results to save")
    
    def load_benchmark_results(self, filename: str):
        """Load benchmark results from file"""
        try:
            with open(filename, 'r') as f:
                self.benchmark_results = json.load(f)
            print(f"📁 Benchmark results loaded from {filename}")
        except Exception as e:
            print(f"❌ Failed to load benchmark results: {e}") 