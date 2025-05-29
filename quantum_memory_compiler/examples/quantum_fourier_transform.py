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
Quantum Fourier Transform Example
================================

This script demonstrates the implementation of a Quantum Fourier Transform circuit.
"""

import os
import json
from datetime import datetime
from quantum_memory_compiler.core import Circuit
from quantum_memory_compiler.core.gate import GateType
from quantum_memory_compiler.compiler.compiler import QuantumCompiler

# Directory structure
CIRCUITS_DIR = "quantum_memory_compiler/circuits"
OUTPUTS_DIR = "quantum_memory_compiler/outputs"
LOGS_DIR = "quantum_memory_compiler/logs"

def ensure_directories():
    """Create necessary directories if they don't exist."""
    for directory in [CIRCUITS_DIR, OUTPUTS_DIR, LOGS_DIR]:
        os.makedirs(directory, exist_ok=True)

def create_qft_circuit(num_qubits=3):
    """Create a Quantum Fourier Transform circuit."""
    circuit = Circuit(name="qft_example")
    
    # Add qubits
    qubits = [circuit.add_qubit() for _ in range(num_qubits)]
    
    # Implement QFT
    current_time = 0
    for i in range(num_qubits):
        # Apply Hadamard to current qubit
        circuit.add_gate(GateType.H, qubits[i], time=current_time)
        current_time += 1
        
        # Apply controlled phase rotations
        for j in range(i + 1, num_qubits):
            circuit.add_gate(GateType.CNOT, [qubits[i], qubits[j]], time=current_time)
            current_time += 1
    
    # Swap qubits to get the correct output order
    for i in range(num_qubits // 2):
        # Implement SWAP using 3 CNOT gates
        circuit.add_gate(GateType.CNOT, [qubits[i], qubits[num_qubits - i - 1]], time=current_time)
        current_time += 1
        circuit.add_gate(GateType.CNOT, [qubits[num_qubits - i - 1], qubits[i]], time=current_time)
        current_time += 1
        circuit.add_gate(GateType.CNOT, [qubits[i], qubits[num_qubits - i - 1]], time=current_time)
        current_time += 1
    
    # Add measurements to all qubits
    for i, qubit in enumerate(qubits):
        circuit.add_gate(GateType.MEASURE, qubit, [i], time=current_time)
    
    return circuit

def main():
    # Create necessary directories
    ensure_directories()
    
    # Create timestamp for logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"qft_execution_{timestamp}.log")
    
    # Create and save the original circuit
    circuit = create_qft_circuit()
    circuit_file = os.path.join(CIRCUITS_DIR, "qft_example.qmc")
    with open(circuit_file, "w") as f:
        json.dump(circuit.to_dict(), f, indent=2)
    
    # Initialize compiler
    compiler = QuantumCompiler()
    
    # Compile the circuit
    compiled_circuit = compiler.compile(circuit)
    
    # Save the compiled circuit
    compiled_file = os.path.join(OUTPUTS_DIR, f"qft_compiled_{timestamp}.qmc")
    with open(compiled_file, "w") as f:
        json.dump(compiled_circuit.to_dict(), f, indent=2)
    
    # Log execution information
    with open(log_file, "w") as log:
        log.write(f"QFT Execution Log - {timestamp}\n")
        log.write("=" * 50 + "\n\n")
        log.write(f"Original Circuit:\n")
        log.write(f"  File: {circuit_file}\n")
        log.write(f"  Gates: {len(circuit.gates)}\n")
        log.write(f"  Qubits: {circuit.width}\n")
        log.write(f"\nCompiled Circuit:\n")
        log.write(f"  File: {compiled_file}\n")
        log.write(f"  Gates: {len(compiled_circuit.gates)}\n")
        log.write(f"  Qubits: {compiled_circuit.width}\n")
    
    # Print summary to console
    print(f"QFT Circuit Generation Complete:")
    print(f"  Original circuit saved to: {circuit_file}")
    print(f"  Compiled circuit saved to: {compiled_file}")
    print(f"  Log file: {log_file}")

if __name__ == "__main__":
    main() 