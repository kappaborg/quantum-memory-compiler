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
Error Mitigation Demo
==================

This script demonstrates the various error mitigation techniques implemented in the
quantum memory compiler, including:

1. Measurement error mitigation
2. Zero-noise extrapolation
3. Richardson extrapolation
4. Probabilistic error cancellation
"""

import numpy as np
import matplotlib.pyplot as plt
import os

from quantum_memory_compiler.core import Circuit, GateType
from quantum_memory_compiler.simulation import (
    NoiseModel, Simulator, ErrorMitigation, ErrorVisualization
)


def create_test_circuit():
    """
    Creates a simple test circuit for error mitigation demonstrations.
    
    Returns:
        Circuit: A simple quantum circuit
    """
    circuit = Circuit("error_mitigation_test")
    
    # Add 3 qubits
    q0, q1, q2 = circuit.add_qubits(3)
    
    # Create a simple circuit with all main gate types
    circuit.h(q0)
    circuit.x(q1)
    circuit.rx(q2, np.pi/4)
    
    circuit.cnot(q0, q1)
    circuit.cz(q1, q2)
    
    circuit.rz(q0, np.pi/2)
    circuit.ry(q1, np.pi/3)
    
    circuit.barrier([q0, q1, q2])
    
    # Adding measurements
    circuit.add_measurement(q0)
    circuit.add_measurement(q1)
    circuit.add_measurement(q2)
    
    return circuit


def create_ghz_circuit(n_qubits=3):
    """
    Creates a GHZ state preparation circuit.
    
    Args:
        n_qubits: Number of qubits in the GHZ state
        
    Returns:
        Circuit: A GHZ state preparation circuit
    """
    circuit = Circuit(f"ghz_{n_qubits}")
    
    # Add qubits
    qubits = circuit.add_qubits(n_qubits)
    
    # Create GHZ state
    circuit.h(qubits[0])
    for i in range(n_qubits - 1):
        circuit.cnot(qubits[i], qubits[i + 1])
    
    # Add measurements
    for q in qubits:
        circuit.add_measurement(q)
    
    return circuit


def demonstrate_noise_effects():
    """
    Demonstrates the effects of different noise types on quantum circuits.
    """
    print("\n=== Demonstrating Noise Effects ===")
    
    # Create a test circuit
    circuit = create_test_circuit()
    
    # Create noise models with different dominant error types
    noise_models = {
        "No Noise": None,
        "Bit Flip": NoiseModel(bit_flip_prob=0.05, phase_flip_prob=0.001),
        "Phase Flip": NoiseModel(bit_flip_prob=0.001, phase_flip_prob=0.05),
        "Depolarizing": NoiseModel(depolarizing_prob=0.05),
        "Amplitude Damping": NoiseModel(amplitude_damping_prob=0.05),
        "Measurement Error": NoiseModel(measurement_error_prob=0.1),
        "Realistic": NoiseModel(
            bit_flip_prob=0.01,
            phase_flip_prob=0.01,
            depolarizing_prob=0.005,
            amplitude_damping_prob=0.01,
            thermal_relaxation_prob=0.005,
            measurement_error_prob=0.03,
            crosstalk_prob=0.002
        )
    }
    
    # Run simulations and collect results
    results = {}
    for name, noise_model in noise_models.items():
        simulator = Simulator(noise_model=noise_model)
        results[name] = simulator.run(circuit, shots=1024)
        
        # Print summary
        print(f"\n{name} Results:")
        for bitstring, count in sorted(results[name].items(), key=lambda x: -x[1]):
            probability = count / 1024
            if probability > 0.05:  # Only show results with >5% probability
                print(f"  |{bitstring}⟩: {probability:.2%}")
    
    # Visualize the results
    plt.figure(figsize=(12, 6))
    bar_width = 0.15
    index = np.arange(8)  # 8 possible bitstrings for 3 qubits
    
    bitstrings = [f"{i:03b}" for i in range(8)]
    
    for i, (name, noise_dict) in enumerate(results.items()):
        counts = [noise_dict.get(bitstring, 0) / 1024 for bitstring in bitstrings]
        plt.bar(index + i*bar_width, counts, bar_width, label=name)
    
    plt.xlabel('Bitstring')
    plt.ylabel('Probability')
    plt.title('Effects of Different Noise Types')
    plt.xticks(index + bar_width * (len(noise_models) - 1) / 2, bitstrings)
    plt.legend()
    plt.tight_layout()
    plt.savefig('noise_effects.png')
    print("\nSaved noise effects visualization to 'noise_effects.png'")


def demonstrate_error_mitigation():
    """
    Demonstrates measurement error mitigation technique.
    """
    print("\n=== Demonstrating Measurement Error Mitigation ===")
    
    # Create a GHZ circuit
    circuit = create_ghz_circuit(3)
    
    # Create a noise model with significant measurement error
    noise_model = NoiseModel(
        bit_flip_prob=0.01,
        phase_flip_prob=0.01,
        measurement_error_prob=0.1  # Significant measurement error
    )
    
    # Create simulator and error mitigation
    simulator = Simulator(noise_model=noise_model)
    error_mitigation = ErrorMitigation(simulator)
    
    # Run ideal simulation (no noise)
    simulator.noise_model = None  # Gürültüyü devre dışı bırak
    ideal_results = simulator.run(circuit, shots=1024)
    
    # Run noisy simulation without mitigation
    noisy_results = simulator.run(circuit, shots=1024)
    
    # Calibrate measurement errors
    print("Calibrating measurement errors...")
    error_mitigation.calibrate_measurement_errors(circuit, shots=1024)
    
    # Run with measurement error mitigation
    mitigated_results = simulator.run_with_error_mitigation(
        circuit, shots=1024, technique="measurement_error_mitigation"
    )
    
    # Print results
    print("\nResults comparison:")
    print(f"  Ideal simulation (expected GHZ state):")
    for bitstring, count in sorted(ideal_results.items(), key=lambda x: -x[1]):
        if count > 20:  # Only show significant results
            print(f"    |{bitstring}⟩: {count/1024:.2%}")
    
    print(f"\n  Noisy simulation (with measurement errors):")
    for bitstring, count in sorted(noisy_results.items(), key=lambda x: -x[1]):
        if count > 20:
            print(f"    |{bitstring}⟩: {count/1024:.2%}")
    
    print(f"\n  Mitigated results:")
    for bitstring, count in sorted(mitigated_results.items(), key=lambda x: -x[1]):
        if count > 20:
            print(f"    |{bitstring}⟩: {count/1024:.2%}")
    
    # Visualize results
    viz = ErrorVisualization(simulator)
    viz.plot_results_comparison(
        ideal_results, noisy_results, mitigated_results,
        title="Measurement Error Mitigation",
        save_path="measurement_mitigation.png"
    )
    print("\nSaved measurement error mitigation visualization to 'measurement_mitigation.png'")


def demonstrate_zero_noise_extrapolation():
    """
    Demonstrates Zero-Noise Extrapolation (ZNE) technique.
    """
    print("\n=== Demonstrating Zero-Noise Extrapolation ===")
    
    # Create a circuit
    circuit = create_test_circuit()
    
    # Create a noise model
    noise_model = NoiseModel(
        depolarizing_prob=0.02,
        bit_flip_prob=0.01,
        phase_flip_prob=0.01
    )
    
    # Create simulator and error mitigation
    simulator = Simulator(noise_model=noise_model)
    error_mitigation = ErrorMitigation(simulator)
    
    # Define observable function (expectation value of first qubit)
    def observable_fn(results):
        """Calculate expectation value of Z on first qubit"""
        expectation = 0
        total_shots = sum(results.values())
        
        for bitstring, count in results.items():
            # Get the first qubit's value (0 or 1)
            first_qubit = int(bitstring[0])
            # +1 for |0⟩, -1 for |1⟩
            expectation += (-1)**first_qubit * count
            
        return expectation / total_shots
    
    # Run ZNE
    print("Running zero-noise extrapolation...")
    zne_result = error_mitigation.zero_noise_extrapolation(
        circuit, observable_fn, shots=1024, scale_noise=True
    )
    
    # Run ideal and noisy simulations for comparison
    simulator.noise_model = None  # Gürültüsüz simülasyon
    ideal_result = observable_fn(simulator.run(circuit, shots=1024))
    simulator.noise_model = noise_model  # Gürültülü simülasyon
    noisy_result = observable_fn(simulator.run(circuit, shots=1024))
    
    print(f"\nObservable expectation values:")
    print(f"  Ideal result: {ideal_result:.4f}")
    print(f"  Noisy result: {noisy_result:.4f}")
    print(f"  ZNE result:   {zne_result:.4f}")
    
    # Visualize ZNE extrapolation
    viz = ErrorVisualization(simulator)
    viz.plot_zne_extrapolation(
        error_mitigation, circuit_name=circuit.name,
        title="Zero-Noise Extrapolation",
        save_path="zne_extrapolation.png"
    )
    print("\nSaved ZNE visualization to 'zne_extrapolation.png'")


def demonstrate_richardson_extrapolation():
    """
    Demonstrates Richardson extrapolation with gate folding.
    """
    print("\n=== Demonstrating Richardson Extrapolation ===")
    
    # Create a circuit with GHZ state
    circuit = create_ghz_circuit(3)
    
    # Create a noise model
    noise_model = NoiseModel(
        depolarizing_prob=0.01,
        bit_flip_prob=0.01,
        phase_flip_prob=0.01
    )
    
    # Create simulator and error mitigation
    simulator = Simulator(noise_model=noise_model)
    error_mitigation = ErrorMitigation(simulator)
    
    # Define observable function (parity of all qubits)
    def observable_fn(results):
        """Calculate expectation value of Z⊗Z⊗Z (parity)"""
        expectation = 0
        total_shots = sum(results.values())
        
        for bitstring, count in results.items():
            # Count the number of 1s in the bitstring
            num_ones = bitstring.count('1')
            # Parity is +1 if even number of 1s, -1 if odd
            parity = (-1)**num_ones
            expectation += parity * count
            
        return expectation / total_shots
    
    # Run Richardson extrapolation
    print("Running Richardson extrapolation...")
    richardson_result = error_mitigation.richardson_extrapolation(
        circuit, observable_fn, shots=1024
    )
    
    # Run ideal and noisy simulations for comparison
    simulator.noise_model = None  # Gürültüsüz simülasyon
    ideal_result = observable_fn(simulator.run(circuit, shots=1024))
    simulator.noise_model = noise_model  # Gürültülü simülasyon
    noisy_result = observable_fn(simulator.run(circuit, shots=1024))
    
    print(f"\nObservable expectation values:")
    print(f"  Ideal result:        {ideal_result:.4f}")
    print(f"  Noisy result:        {noisy_result:.4f}")
    print(f"  Richardson result:   {richardson_result:.4f}")
    
    # Compare to ZNE for the same circuit
    zne_result = error_mitigation.zero_noise_extrapolation(
        circuit, observable_fn, shots=1024
    )
    print(f"  ZNE result (compare): {zne_result:.4f}")
    
    # Visualize extrapolation data
    viz = ErrorVisualization(simulator)
    viz.plot_error_scaling_comparison(
        circuit, shots=1024, 
        observable_fn=observable_fn,
        title="Richardson Extrapolation vs. ZNE",
        save_path="richardson_extrapolation.png"
    )
    print("\nSaved Richardson extrapolation visualization to 'richardson_extrapolation.png'")


def demonstrate_all_error_statistics():
    """
    Demonstrates all error statistics and visualization capabilities.
    """
    print("\n=== Demonstrating Error Statistics and Visualization ===")
    
    # Create a test circuit
    circuit = create_ghz_circuit(3)
    
    # Create a realistic noise model
    noise_model = NoiseModel(
        bit_flip_prob=0.01,
        phase_flip_prob=0.01,
        depolarizing_prob=0.005,
        amplitude_damping_prob=0.01,
        thermal_relaxation_prob=0.005,
        measurement_error_prob=0.03,
        crosstalk_prob=0.002
    )
    
    # Create simulator
    simulator = Simulator(noise_model=noise_model)
    
    # Run circuit multiple times to gather statistics
    print("Running multiple circuit executions to gather error statistics...")
    for _ in range(10):
        simulator.run(circuit, shots=100)
    
    # Get error statistics
    stats = noise_model.get_error_statistics()
    
    print("\nError statistics summary:")
    print(f"  Total gate operations: {stats['total_gates']}")
    print(f"  Total errors: {stats['total_errors']}")
    print(f"  Error rate: {stats['error_rate']:.2%}")
    print("\nError types:")
    for error_type, count in stats['error_types'].items():
        print(f"  {error_type}: {count} ({count/stats['total_errors']:.2%})")
    
    # Create error visualization
    viz = ErrorVisualization(simulator)
    
    # Plot error distribution
    viz.plot_error_distribution(
        noise_model, gate_runs=500,
        title="Quantum Error Distribution",
        save_path="error_distribution.png"
    )
    
    # Create error mitigation for readout calibration matrix
    error_mitigation = ErrorMitigation(simulator)
    error_mitigation.calibrate_measurement_errors(circuit, shots=1024)
    
    # Plot readout calibration matrix
    viz.plot_readout_calibration_matrix(
        error_mitigation, num_qubits=3,
        title="Readout Error Calibration Matrix",
        save_path="calibration_matrix.png"
    )
    
    print("\nSaved error visualization files:")
    print("  - 'error_distribution.png'")
    print("  - 'calibration_matrix.png'")
    
    # Run comprehensive analysis
    viz.plot_all_error_statistics(
        noise_model, circuit, shots=1024,
        title_prefix="Comprehensive Error Analysis",
        save_dir="."
    )
    print("  - 'comprehensive_error_analysis.png'")


def main():
    """
    Main function that demonstrates all error mitigation techniques.
    """
    print("=== Quantum Memory Compiler: Error Mitigation Demo ===")
    print("This demo showcases the error mitigation capabilities implemented in the quantum memory compiler")
    print("Each section demonstrates a different technique for mitigating quantum hardware errors\n")
    
    # Demonstrate noise effects
    demonstrate_noise_effects()
    
    # Demonstrate measurement error mitigation
    demonstrate_error_mitigation()
    
    # Demonstrate zero-noise extrapolation
    demonstrate_zero_noise_extrapolation()
    
    # Demonstrate Richardson extrapolation
    demonstrate_richardson_extrapolation()
    
    # Demonstrate comprehensive error statistics and visualization
    demonstrate_all_error_statistics()
    
    print("\nDemo completed! All error mitigation techniques have been demonstrated.")
    print("Visualization files have been saved to the current directory.")
    print("\nTo use these techniques in your own code, import the following components:")
    print("  from quantum_memory_compiler.simulation import NoiseModel, Simulator, ErrorMitigation, ErrorVisualization")
    print("  from quantum_memory_compiler.core import Circuit")


if __name__ == "__main__":
    main() 