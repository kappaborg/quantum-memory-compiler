#!/usr/bin/env python3
"""
Direct Simulator Test
====================

Simulator'ı doğrudan test eder.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'quantum_memory_compiler'))

from quantum_memory_compiler.core.circuit import Circuit
from quantum_memory_compiler.core.qubit import Qubit
from quantum_memory_compiler.core.gate import GateType
from quantum_memory_compiler.simulation.simulator import Simulator

def test_simulator_direct():
    """Test simulator directly"""
    
    print("🧪 Direct Simulator Test")
    print("=" * 50)
    
    # Create Bell state circuit
    circuit = Circuit()
    circuit.name = "Bell State Test"
    
    # Add qubits
    qubit0 = Qubit(0)
    qubit1 = Qubit(1)
    circuit.add_qubit(qubit0)
    circuit.add_qubit(qubit1)
    
    print(f"📊 Circuit created with {len(circuit.qubits)} qubits")
    
    # Add gates
    circuit.add_gate(GateType.H, qubit0)
    circuit.add_gate(GateType.CNOT, qubit0, qubit1)
    
    print(f"📊 Added {len(circuit.gates)} gates")
    for i, gate in enumerate(circuit.gates):
        print(f"   Gate {i}: {gate.type.name} on qubits {[q.id for q in gate.qubits]}")
    
    # Add measurements
    circuit.add_gate(GateType.MEASURE, qubit0, parameters=[0])
    circuit.add_gate(GateType.MEASURE, qubit1, parameters=[1])
    
    print(f"📊 Total gates after measurements: {len(circuit.gates)}")
    
    # Create simulator
    simulator = Simulator()
    
    # Run simulation
    print("\n🔬 Running simulation...")
    results = simulator.run(circuit, shots=100)
    
    print(f"\n✅ Simulation completed!")
    print(f"📊 Results: {results}")
    
    return results

if __name__ == "__main__":
    test_simulator_direct() 