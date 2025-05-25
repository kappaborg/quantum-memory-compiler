#!/usr/bin/env python
"""
Bell State Example
================

This example demonstrates the use of the Memory-Aware Quantum Compiler for a circuit that creates a Bell state.
"""

import os
import matplotlib.pyplot as plt
from quantum_memory_compiler.compiler.compiler import QuantumCompiler
from quantum_memory_compiler.memory.hierarchy import MemoryHierarchy
from quantum_memory_compiler.core import Circuit, Qubit, Gate
from quantum_memory_compiler.core.gate import GateType
from quantum_memory_compiler.core.visualization import CircuitVisualizer, MemoryVisualizer
from quantum_memory_compiler.simulation.hardware import HardwareModel
from quantum_memory_compiler.simulation.simulator import Simulator
from quantum_memory_compiler.simulation.noise_model import NoiseModel

def main():
    # Create output directory for visualizations if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "visualizations")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create memory hierarchy
    memory = MemoryHierarchy(l1_capacity=10, l2_capacity=20, l3_capacity=30)
    
    # Create a simple hardware model
    hardware = HardwareModel(topology="line", num_qubits=4, coherence_time=100)
    
    # Initialize the compiler
    compiler = QuantumCompiler(memory, allocator_strategy="lifetime")
    
    # Create Bell state circuit with measurements
    circuit = create_bell_state_with_measurements()
    
    print(f"Original circuit: {circuit}")
    print(f"Number of gates: {len(circuit.gates)}")
    print(f"Number of qubits: {circuit.width}")
    print("---")
    
    # Visualize original circuit
    visualizer = CircuitVisualizer()
    fig = visualizer.visualize_circuit(circuit)
    fig.savefig(os.path.join(output_dir, "bell_state_original.png"), dpi=300)
    print("Original circuit visualization saved to 'visualizations/bell_state_original.png'")
    plt.close(fig)
    
    # Compile the circuit
    compiled_circuit = compiler.compile(circuit, hardware)
    
    print(f"Compiled circuit: {compiled_circuit}")
    print(f"Number of gates: {len(compiled_circuit.gates)}")
    print(f"Number of qubits: {compiled_circuit.width}")
    print("---")
    
    # Visualize compiled circuit
    fig = visualizer.visualize_circuit(compiled_circuit)
    fig.savefig(os.path.join(output_dir, "bell_state_compiled.png"), dpi=300)
    print("Compiled circuit visualization saved to 'visualizations/bell_state_compiled.png'")
    plt.close(fig)
    
    # Visualize memory usage
    memory_viz = MemoryVisualizer()
    fig = memory_viz.visualize_memory_usage(memory)
    fig.savefig(os.path.join(output_dir, "bell_state_memory.png"), dpi=300)
    print("Memory usage visualization saved to 'visualizations/bell_state_memory.png'")
    plt.close(fig)
    
    # Show compilation statistics
    stats = compiler.get_last_compilation_stats()
    print("Compilation statistics:")
    print(f"  Number of qubits in input circuit: {stats['input_circuit']['width']}")
    print(f"  Number of qubits in output circuit: {stats['output_circuit']['width']}")
    print(f"  Qubit savings: {stats['qubit_reduction']}")
    print(f"  Circuit depth change: {stats['depth_change']}")
    print(f"  Gate count change: {stats['gate_count_change']}")
    
    # Run with simulator - increase the number of shots
    print("\nRunning simulation...")
    simulator = Simulator()
    results = simulator.run(compiled_circuit, shots=1000)
    
    print("\nSimulation results:")
    print(f"  Measurement outcomes: {results}")
    
    # State vector analysis (before measurement)
    print("\nState vector analysis (before measurement):")
    # Create a circuit without measurement gates
    bell_circuit_no_measure = Circuit.create_bell_state()
    state_vectors = simulator.get_statevector(bell_circuit_no_measure)
    for qubit_id, state_vector in state_vectors.items():
        print(f"  Qubit {qubit_id}: {state_vector}")

def create_bell_state_with_measurements():
    """
    Creates a Bell state circuit with measurement gates
    
    Returns:
        Circuit: Bell state circuit
    """
    # Create a new circuit
    circuit = Circuit(name="bell_state_with_measurements")
    
    # Add two qubits
    q0 = circuit.add_qubit()
    q1 = circuit.add_qubit()
    
    # Add gates for Bell state
    circuit.add_gate(GateType.H, q0, time=0)
    circuit.add_gate(GateType.CNOT, [q0, q1], time=1)
    
    # Add measurement gates
    circuit.add_gate(GateType.MEASURE, q0, [0], time=2)
    circuit.add_gate(GateType.MEASURE, q1, [1], time=2)
    
    return circuit

if __name__ == "__main__":
    main() 