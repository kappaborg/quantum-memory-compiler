import pytest
from quantum_memory_compiler.core import Qubit, Gate, Circuit
from quantum_memory_compiler.core.qubit import QubitType, MemoryLevel

def test_qubit_creation():
    """Test qubit creation and basic properties"""
    qubit = Qubit(0, QubitType.LOGICAL, MemoryLevel.L1)
    assert qubit.id == 0
    assert qubit.type == QubitType.LOGICAL
    assert qubit.memory_level == MemoryLevel.L1
    assert not qubit.is_allocated
    assert not qubit.is_active

def test_circuit_creation():
    """Test circuit creation and basic functionality"""
    circuit = Circuit("test_circuit")
    assert circuit.name == "test_circuit"
    assert circuit.width == 0
    assert circuit.depth == 0
    
    # Add qubits
    q0 = circuit.add_qubit()
    q1 = circuit.add_qubit()
    assert circuit.width == 2
    
    # Add gates
    circuit.h(q0)
    circuit.cnot(q0, q1)
    assert len(circuit.gates) == 2

def test_bell_state():
    """Test the bell state creation"""
    circuit = Circuit.create_bell_state()
    assert circuit.width == 2
    assert len(circuit.gates) == 2
    
    # First gate should be H on q0
    assert circuit.gates[0].type.name == "H"
    
    # Second gate should be CNOT from q0 to q1
    assert circuit.gates[1].type.name == "CNOT"
    assert circuit.gates[1].qubits[0].id == 0  # control qubit
    assert circuit.gates[1].qubits[1].id == 1  # target qubit 