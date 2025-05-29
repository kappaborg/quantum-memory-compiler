#!/usr/bin/env python

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
Grover's Search Algorithm Example
===============================

This example demonstrates the use of the Memory-Aware Quantum Compiler for Grover's search algorithm.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from quantum_memory_compiler.compiler.compiler import QuantumCompiler
from quantum_memory_compiler.memory.hierarchy import MemoryHierarchy
from quantum_memory_compiler.core import Circuit, Qubit, Gate
from quantum_memory_compiler.core.gate import GateType
from quantum_memory_compiler.simulation.hardware import HardwareModel
from quantum_memory_compiler.simulation.simulator import Simulator
from quantum_memory_compiler.simulation.noise_model import NoiseModel

def main():
    # Create memory hierarchy
    memory = MemoryHierarchy(l1_capacity=15, l2_capacity=25, l3_capacity=40)
    
    # Create a hardware model
    hardware = HardwareModel(topology="grid", num_qubits=16, coherence_time=500)
    
    # Initialize the compiler
    compiler = QuantumCompiler(memory, allocator_strategy="lifetime")
    
    # Search space size (2^n)
    n_bits = 3  # 3 qubits means searching through 8 items
    
    # Target item to search for (as a bit string)
    target = "101"  # We're looking for item 5 (in binary: 101)
    
    # Create Grover's algorithm circuit
    grover_circuit = create_grover_circuit(n_bits, target)
    
    print(f"Original circuit: {grover_circuit}")
    print(f"Number of gates: {len(grover_circuit.gates)}")
    print(f"Number of qubits: {grover_circuit.width}")
    print(f"Circuit depth: {grover_circuit.depth}")
    print(f"Searching for target: |{target}⟩")
    print("---")
    
    # Compile the circuit
    compiled_circuit = compiler.compile(grover_circuit, hardware)
    
    print(f"Compiled circuit: {compiled_circuit}")
    print(f"Number of gates: {len(compiled_circuit.gates)}")
    print(f"Number of qubits: {compiled_circuit.width}")
    print(f"Circuit depth: {compiled_circuit.depth}")
    print("---")
    
    # Show compilation statistics
    stats = compiler.get_last_compilation_stats()
    print("Compilation statistics:")
    print(f"  Number of qubits in input circuit: {stats['input_circuit']['width']}")
    print(f"  Number of qubits in output circuit: {stats['output_circuit']['width']}")
    print(f"  Qubit savings: {stats['qubit_reduction']}")
    print(f"  Circuit depth change: {stats['depth_change']}")
    print(f"  Gate count change: {stats['gate_count_change']}")
    
    # Run with simulator
    print("\nRunning simulation...")
    simulator = Simulator()
    
    # Run multiple times to see the probabilistic nature
    total_shots = 1000
    results = simulator.run(compiled_circuit, shots=total_shots)
    
    print("\nSimulation results:")
    print(f"  Target item: |{target}⟩")
    
    # Sort results by count and analyze
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    print(f"  Measurement outcomes (from {total_shots} shots):")
    
    for outcome, count in sorted_results[:5]:
        probability = count / total_shots
        print(f"    |{outcome}⟩: {count} shots ({probability:.4f} probability)")
    
    # Check if target was found most frequently
    most_frequent = sorted_results[0][0]
    if most_frequent.endswith(target):
        print(f"\n✓ Success! Target |{target}⟩ was the most frequently measured outcome.")
    else:
        print(f"\n✗ Target |{target}⟩ was not the most frequently measured outcome.")
        # Find target in results
        for outcome, count in sorted_results:
            if outcome.endswith(target):
                probability = count / total_shots
                print(f"  Target |{target}⟩ appeared {count} times ({probability:.4f} probability)")
                break
    
    # Calculate theoretical success probability
    num_iterations = int(math.pi/4 * math.sqrt(2**n_bits))
    theoretical_prob = math.sin((2*num_iterations + 1) * math.asin(1/math.sqrt(2**n_bits)))**2
    
    print(f"\nTheoretical success probability: {theoretical_prob:.4f}")
    print(f"Number of Grover iterations used: {num_iterations}")
    print(f"Classical search would require {2**n_bits / 2} comparisons on average.")
    print(f"Quantum search requires only {num_iterations} iterations.")

def create_grover_circuit(n_bits, target):
    """
    Creates a Grover's search algorithm circuit
    
    Args:
        n_bits: Number of bits (qubits) to search through
        target: Target bit string to search for
        
    Returns:
        Circuit: Grover's algorithm circuit
    """
    # Create a new circuit
    circuit = Circuit(name=f"grover_{n_bits}bits_target{target}")
    
    # Add qubits: n for the register + 1 for the oracle's workspace
    register_qubits = [circuit.add_qubit() for _ in range(n_bits)]
    oracle_qubit = circuit.add_qubit()
    
    # Current time tracker
    current_time = 0
    
    # Initialize all qubits in superposition
    # Initialize register qubits with Hadamard
    for q in register_qubits:
        circuit.add_gate(GateType.H, q, time=current_time)
    
    # Initialize oracle qubit in |-⟩ state (apply X then H)
    circuit.add_gate(GateType.X, oracle_qubit, time=current_time)
    circuit.add_gate(GateType.H, oracle_qubit, time=current_time+1)
    current_time += 2
    
    # Calculate optimal number of iterations
    num_iterations = int(math.pi/4 * math.sqrt(2**n_bits))
    
    # Perform Grover iterations
    for iteration in range(num_iterations):
        # Oracle - marks the target state
        oracle_circuit(circuit, register_qubits, oracle_qubit, target, current_time)
        current_time += n_bits + 1
        
        # Diffusion operator - amplifies the marked state
        diffusion_circuit(circuit, register_qubits, current_time)
        current_time += n_bits + 2
    
    # Measure register qubits
    for i, q in enumerate(register_qubits):
        circuit.add_gate(GateType.MEASURE, q, [i], time=current_time)
    
    return circuit

def oracle_circuit(circuit, register_qubits, oracle_qubit, target, start_time):
    """
    Adds the oracle circuit that marks the target state
    
    Args:
        circuit: The quantum circuit
        register_qubits: List of register qubits
        oracle_qubit: Oracle workspace qubit
        target: Target bit string
        start_time: Starting time step
    """
    # The oracle flips the sign of the target state
    # For each 0 in the target string, apply X gate before and after multi-controlled-Z
    current_time = start_time
    
    # Apply X gates to qubits where target bit is 0
    for i, bit in enumerate(target):
        if bit == '0':
            circuit.add_gate(GateType.X, register_qubits[i], time=current_time)
    
    current_time += 1
    
    # Apply multi-controlled Z gate (simplified as CNOT gates for this example)
    for q in register_qubits:
        circuit.add_gate(GateType.CNOT, [q, oracle_qubit], time=current_time)
    
    current_time += 1
    
    # Apply X gates again to qubits where target bit is 0
    for i, bit in enumerate(target):
        if bit == '0':
            circuit.add_gate(GateType.X, register_qubits[i], time=current_time)

def diffusion_circuit(circuit, register_qubits, start_time):
    """
    Adds the diffusion operator circuit that amplifies the amplitude of the marked state
    
    Args:
        circuit: The quantum circuit
        register_qubits: List of register qubits
        start_time: Starting time step
    """
    current_time = start_time
    
    # Apply H to all register qubits
    for q in register_qubits:
        circuit.add_gate(GateType.H, q, time=current_time)
    
    current_time += 1
    
    # Apply X to all register qubits
    for q in register_qubits:
        circuit.add_gate(GateType.X, q, time=current_time)
    
    current_time += 1
    
    # Apply multi-controlled Z (simplified for this example)
    # In reality, this would be a multi-controlled Z gate
    # We're using a simplified approach with multiple CNOTs
    for i in range(len(register_qubits)-1):
        circuit.add_gate(GateType.CNOT, [register_qubits[i], register_qubits[i+1]], time=current_time)
    
    current_time += 1
    
    # Apply X to all register qubits
    for q in register_qubits:
        circuit.add_gate(GateType.X, q, time=current_time)
    
    current_time += 1
    
    # Apply H to all register qubits
    for q in register_qubits:
        circuit.add_gate(GateType.H, q, time=current_time)

if __name__ == "__main__":
    main() 