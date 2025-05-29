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
MetaCompiler Module
==================

Module providing AI and machine learning based quantum circuit optimization.
"""

import numpy as np
import time
import logging
from typing import Dict, List, Callable, Any, Optional, Tuple
from collections import defaultdict

# Use proper imports to avoid circular import
from quantum_memory_compiler.compiler.compiler import QuantumCompiler as Compiler
from quantum_memory_compiler.core.circuit import Circuit
from quantum_memory_compiler.core.gate import Gate, GateType
from quantum_memory_compiler.memory.profiler import MemoryProfiler
from quantum_memory_compiler.simulation.simulator import Simulator

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MetaCompiler:
    """
    AI and machine learning based compiler optimization
    
    Tries to find the best result by testing different compiler strategies,
    applies learning-based optimizations and creates customized compiler
    configurations.
    """
    
    def __init__(self):
        """Initialize MetaCompiler object"""
        self.compilers = []
        self.strategies = []
        self.performance_history = defaultdict(list)
        self.best_strategy = None
        self.profiler = MemoryProfiler()
        
        # Start with a standard compiler
        self.compilers.append(Compiler())
        
        # Load default strategies
        self._load_default_strategies()
    
    def _load_default_strategies(self):
        """Load default optimization strategies"""
        # Different strategy combinations
        self.strategies = [
            {
                "name": "memory_aware_basic",
                "description": "Basic optimization with memory awareness",
                "params": {
                    "enable_recycling": True,
                    "recycling_threshold": 0.5,
                    "enable_teleportation": False,
                    "memory_hierarchy_aware": True,
                    "optimize_2q_gates": True
                }
            },
            {
                "name": "gate_count_reduction",
                "description": "Optimization focused on reducing gate count",
                "params": {
                    "enable_recycling": True,
                    "recycling_threshold": 0.3,
                    "enable_teleportation": True,
                    "optimize_2q_gates": True,
                    "combine_single_qubit_gates": True,
                    "memory_hierarchy_aware": False
                }
            },
            {
                "name": "balanced",
                "description": "Balance between memory usage and gate count",
                "params": {
                    "enable_recycling": True,
                    "recycling_threshold": 0.4,
                    "enable_teleportation": True, 
                    "optimize_2q_gates": True,
                    "combine_single_qubit_gates": True,
                    "memory_hierarchy_aware": True
                }
            },
            {
                "name": "depth_reduction",
                "description": "Focused on reducing circuit depth",
                "params": {
                    "enable_recycling": False,
                    "enable_teleportation": True,
                    "parallelize_gates": True,
                    "memory_hierarchy_aware": False,
                    "optimize_2q_gates": True
                }
            },
            {
                "name": "low_error",
                "description": "Strategy that minimizes error rate",
                "params": {
                    "enable_recycling": True,
                    "recycling_threshold": 0.6,
                    "enable_teleportation": False,
                    "optimize_2q_gates": True,
                    "error_aware_mapping": True,
                    "memory_hierarchy_aware": True
                }
            }
        ]
    
    def add_strategy(self, name: str, description: str, params: Dict):
        """
        Add a new optimization strategy
        
        Args:
            name: Strategy name
            description: Strategy description
            params: Strategy parameters
        """
        # Update if strategy with same name exists
        for i, strategy in enumerate(self.strategies):
            if strategy["name"] == name:
                self.strategies[i] = {
                    "name": name,
                    "description": description,
                    "params": params
                }
                logger.info(f"Strategy updated: {name}")
                return
        
        # Add new strategy
        self.strategies.append({
            "name": name,
            "description": description,
            "params": params
        })
        logger.info(f"New strategy added: {name}")
    
    def compile(self, circuit: Circuit, evaluate: bool = True, 
               custom_strategy: Optional[Dict] = None) -> Circuit:
        """
        Find and apply the best compiler strategy for the circuit
        
        Args:
            circuit: Circuit to compile
            evaluate: Evaluate results and select best strategy
            custom_strategy: Custom strategy (optional)
            
        Returns:
            Circuit: Compiled circuit
        """
        if custom_strategy:
            # Use custom strategy directly
            logger.info(f"Using custom strategy: {custom_strategy.get('name', 'unnamed')}")
            result = self._compile_with_strategy(circuit, custom_strategy)
            return result["circuit"]
        
        if not evaluate or len(self.strategies) <= 1:
            # Use first strategy if not evaluating
            strategy = self.strategies[0]
            logger.info(f"Using single strategy: {strategy['name']}")
            result = self._compile_with_strategy(circuit, strategy)
            return result["circuit"]
        
        # Try all strategies and select the best
        logger.info(f"Evaluating {len(self.strategies)} strategies for optimization...")
        
        results = []
        for strategy in self.strategies:
            logger.info(f"Trying strategy: {strategy['name']}")
            result = self._compile_with_strategy(circuit, strategy)
            results.append(result)
            
            # Save results
            self.performance_history[strategy["name"]].append({
                "circuit_width": circuit.width,
                "circuit_depth": len(circuit.gates),
                "result": result
            })
        
        # Find best result
        best_result = self._select_best_result(results)
        self.best_strategy = best_result["strategy"]
        
        logger.info(f"Best strategy: {self.best_strategy['name']}")
        logger.info(f"Maximum resource usage: {best_result['max_resource_usage']}")
        logger.info(f"Total cost: {best_result['total_cost']}")
        
        return best_result["circuit"]
    
    def _compile_with_strategy(self, circuit: Circuit, strategy: Dict) -> Dict:
        """
        Run compiler with a specific strategy
        
        Args:
            circuit: Circuit to compile
            strategy: Strategy to use
            
        Returns:
            Dict: Result information (circuit, metrics)
        """
        # Profile before compilation
        before_profile = self.profiler.profile_circuit(circuit)
        
        # Create compiler and set parameters
        compiler = Compiler()
        
        # Set strategy parameters
        for param, value in strategy["params"].items():
            if hasattr(compiler, param):
                setattr(compiler, param, value)
        
        # Time and compile
        start_time = time.time()
        compiled_circuit = compiler.compile(circuit)
        compilation_time = time.time() - start_time
        
        # Profile after compilation
        after_profile = self.profiler.profile_circuit(compiled_circuit)
        
        # Calculate metrics
        metrics = {
            "compilation_time": compilation_time,
            "original_width": circuit.width,
            "compiled_width": compiled_circuit.width,
            "original_depth": len(circuit.gates),
            "compiled_depth": len(compiled_circuit.gates),
            "max_resource_usage": after_profile["max_qubits"],
            "avg_qubit_lifetime": after_profile["avg_lifetime"],
            "bottlenecks": after_profile["bottlenecks"],
            "improvement_ratio": circuit.width / compiled_circuit.width if compiled_circuit.width > 0 else 0
        }
        
        # Calculate total cost (with balanced weights for different factors)
        total_cost = (
            0.3 * metrics["compiled_width"] / circuit.width + 
            0.3 * metrics["compiled_depth"] / len(circuit.gates) +
            0.2 * metrics["max_resource_usage"] / circuit.width +
            0.1 * metrics["compilation_time"] +
            0.1 * (1.0 - metrics["improvement_ratio"])
        )
        
        return {
            "circuit": compiled_circuit,
            "metrics": metrics,
            "strategy": strategy,
            "total_cost": total_cost,
            "max_resource_usage": metrics["max_resource_usage"]
        }
    
    def _select_best_result(self, results: List[Dict]) -> Dict:
        """
        Select the best result from results
        
        Args:
            results: List of compilation results
            
        Returns:
            Dict: Best result
        """
        # Select result with lowest cost
        return min(results, key=lambda x: x["total_cost"])
    
    def get_strategy_recommendations(self, circuit: Circuit) -> List[Dict]:
        """
        Return recommended strategies for the circuit
        
        Args:
            circuit: Circuit to evaluate
            
        Returns:
            List[Dict]: Recommended strategies, sorted
        """
        # Score strategies based on circuit properties
        scored_strategies = []
        
        # Circuit profile
        profile = self.profiler.profile_circuit(circuit)
        
        # Circuit properties
        circuit_properties = {
            "width": circuit.width,
            "depth": len(circuit.gates),
            "avg_lifetime": profile["avg_lifetime"],
            "has_measurement": any(gate.type == GateType.MEASURE for gate in circuit.gates),
            "multi_qubit_ratio": sum(1 for gate in circuit.gates if len(gate.qubits) > 1) / max(len(circuit.gates), 1),
        }
        
        for strategy in self.strategies:
            score = self._score_strategy_for_circuit(strategy, circuit_properties)
            scored_strategies.append({
                "strategy": strategy,
                "score": score
            })
        
        # Sort by score (highest first)
        scored_strategies.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top 3 strategies
        top_strategies = [item["strategy"] for item in scored_strategies[:3]]
        return top_strategies
    
    def _score_strategy_for_circuit(self, strategy: Dict, properties: Dict) -> float:
        """
        Score a strategy for circuit properties
        
        Args:
            strategy: Strategy to score
            properties: Circuit properties
            
        Returns:
            float: Score (between 0-1)
        """
        score = 0.0
        
        # Based on circuit width
        if properties["width"] > 20:
            # Memory awareness important for large circuits
            if strategy["params"].get("enable_recycling", False):
                score += 0.3
            if strategy["params"].get("memory_hierarchy_aware", False):
                score += 0.2
        else:
            # Gate optimization important for small circuits
            if strategy["params"].get("optimize_2q_gates", False):
                score += 0.3
            if strategy["params"].get("combine_single_qubit_gates", False):
                score += 0.2
        
        # Based on multi-qubit gate ratio
        if properties["multi_qubit_ratio"] > 0.3:
            # Important to optimize multi-qubit gates if many
            if strategy["params"].get("optimize_2q_gates", False):
                score += 0.2
        
        # Based on presence of measurements
        if properties["has_measurement"]:
            # Error reduction important with measurements
            if strategy["params"].get("error_aware_mapping", False):
                score += 0.1
        
        # Based on average qubit lifetime
        if properties["avg_lifetime"] > 5:
            # Recycling important with long qubit lifetimes
            recycling_threshold = strategy["params"].get("recycling_threshold", 0)
            if recycling_threshold > 0.4:
                score += 0.2
        
        # Past performance (has this been compiled?)
        for history in self.performance_history.get(strategy["name"], []):
            if history["circuit_width"] == properties["width"] and \
               history["circuit_depth"] == properties["depth"]:
                # Success in similar past circuits
                improvement = history["result"]["metrics"]["improvement_ratio"]
                if improvement > 1.2:
                    score += 0.2
        
        return min(1.0, score)  # Ensure not greater than 1.0
    
    def get_strategies(self) -> List[Dict]:
        """Return all available strategies"""
        return self.strategies
    
    def get_performance_history(self) -> Dict:
        """Return performance history"""
        return dict(self.performance_history) 