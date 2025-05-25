#!/usr/bin/env python
"""
Quantum Memory Compiler - Presentation Demo
==========================================

This script contains a comprehensive demo showcasing all features of the Quantum Memory Compiler.
Prepared for presentation purposes.
"""

import os
import time
import matplotlib.pyplot as plt
from quantum_memory_compiler.core import Circuit
from quantum_memory_compiler.core.gate import GateType
from quantum_memory_compiler.compiler.compiler import QuantumCompiler
from quantum_memory_compiler.memory.hierarchy import MemoryHierarchy
from quantum_memory_compiler.simulation.simulator import Simulator
from quantum_memory_compiler.simulation.noise_model import NoiseModel
from quantum_memory_compiler.core.visualization import CircuitVisualizer, MemoryVisualizer

def print_header(title):
    """Prints header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(step_num, description):
    """Prints step"""
    print(f"\n[Step {step_num}] {description}")
    print("-" * 40)

def create_bell_state_circuit():
    """Creates Bell state circuit"""
    circuit = Circuit(name="bell_state_demo")
    
    # Add qubits
    q0 = circuit.add_qubit()
    q1 = circuit.add_qubit()
    
    # Bell state gates
    circuit.add_gate(GateType.H, q0, time=0)
    circuit.add_gate(GateType.CNOT, [q0, q1], time=1)
    
    # Measurements
    circuit.add_gate(GateType.MEASURE, q0, [0], time=2)
    circuit.add_gate(GateType.MEASURE, q1, [1], time=2)
    
    return circuit

def create_grover_circuit():
    """Creates 3-qubit Grover algorithm circuit"""
    circuit = Circuit(name="grover_3qubit_demo")
    
    # Add qubits
    qubits = [circuit.add_qubit() for _ in range(3)]
    
    # Create superposition
    for i, qubit in enumerate(qubits):
        circuit.add_gate(GateType.H, qubit, time=0)
    
    # Oracle (mark |101⟩ state)
    circuit.add_gate(GateType.X, qubits[0], time=1)
    circuit.add_gate(GateType.X, qubits[2], time=1)
    circuit.add_gate(GateType.CCZ, qubits, time=2)  # Controlled-controlled-Z
    circuit.add_gate(GateType.X, qubits[0], time=3)
    circuit.add_gate(GateType.X, qubits[2], time=3)
    
    # Diffusion operator
    for i, qubit in enumerate(qubits):
        circuit.add_gate(GateType.H, qubit, time=4)
        circuit.add_gate(GateType.X, qubit, time=5)
    
    circuit.add_gate(GateType.CCZ, qubits, time=6)
    
    for i, qubit in enumerate(qubits):
        circuit.add_gate(GateType.X, qubit, time=7)
        circuit.add_gate(GateType.H, qubit, time=8)
    
    # Measurements
    for i, qubit in enumerate(qubits):
        circuit.add_gate(GateType.MEASURE, qubit, [i], time=9)
    
    return circuit

def demo_basic_functionality():
    """Basic functionality demo"""
    print_header("QUANTUM MEMORY COMPILER - BASIC FUNCTIONALITY")
    
    print_step(1, "Creating Bell State Circuit")
    circuit = create_bell_state_circuit()
    print(f"✓ Circuit created: {circuit}")
    print(f"  - Number of qubits: {circuit.width}")
    print(f"  - Number of gates: {len(circuit.gates)}")
    print(f"  - Circuit depth: {circuit.depth}")
    
    print_step(2, "Circuit Visualization")
    visualizer = CircuitVisualizer()
    fig = visualizer.visualize_circuit(circuit, filename="demo_bell_original.png")
    plt.close(fig)
    print("✓ Circuit visualized: demo_bell_original.png")
    
    print_step(3, "Creating Memory Hierarchy")
    memory = MemoryHierarchy(l1_capacity=10, l2_capacity=20, l3_capacity=50)
    print("✓ Memory hierarchy created:")
    for name, level in memory.levels.items():
        print(f"  - {name}: {level.capacity} qubits, {level.coherence_time}μs coherence")
    
    print_step(4, "Compilation Process")
    compiler = QuantumCompiler(memory)
    compiled_circuit = compiler.compile(circuit)
    print(f"✓ Circuit compiled: {compiled_circuit}")
    print(f"  - Original: {circuit.width} qubits, {len(circuit.gates)} gates")
    print(f"  - Compiled: {compiled_circuit.width} qubits, {len(compiled_circuit.gates)} gates")
    
    # Visualize compiled circuit
    fig = visualizer.visualize_circuit(compiled_circuit, filename="demo_bell_compiled.png")
    plt.close(fig)
    print("✓ Compiled circuit visualized: demo_bell_compiled.png")
    
    return circuit, compiled_circuit, memory

def demo_simulation():
    """Simulation demo"""
    print_header("SIMULATION FEATURES")
    
    circuit = create_bell_state_circuit()
    
    print_step(1, "Ideal Simulation")
    simulator = Simulator()
    ideal_results = simulator.run(circuit, shots=1000)
    print("✓ Ideal simulation completed:")
    for state, prob in sorted(ideal_results.items(), key=lambda x: -x[1]):
        print(f"  - |{state}⟩: {prob:.3f}")
    
    print_step(2, "Noisy Simulation")
    noise_model = NoiseModel(
        depolarizing_prob=0.01,
        bit_flip_prob=0.005,
        phase_flip_prob=0.005
    )
    noisy_simulator = Simulator(noise_model=noise_model)
    noisy_results = noisy_simulator.run(circuit, shots=1000)
    print("✓ Noisy simulation completed:")
    for state, prob in sorted(noisy_results.items(), key=lambda x: -x[1]):
        print(f"  - |{state}⟩: {prob:.3f}")
    
    print_step(3, "Results Comparison")
    print("Fidelity analysis:")
    for state in ideal_results:
        ideal_prob = ideal_results.get(state, 0)
        noisy_prob = noisy_results.get(state, 0)
        diff = abs(ideal_prob - noisy_prob)
        print(f"  - |{state}⟩: Ideal={ideal_prob:.3f}, Noisy={noisy_prob:.3f}, Diff={diff:.3f}")

def demo_advanced_features():
    """Advanced features demo"""
    print_header("ADVANCED FEATURES")
    
    print_step(1, "Grover Algorithm Circuit")
    grover_circuit = create_grover_circuit()
    print(f"✓ Grover circuit created: {grover_circuit}")
    print(f"  - Number of qubits: {grover_circuit.width}")
    print(f"  - Number of gates: {len(grover_circuit.gates)}")
    
    print_step(2, "Different Compilation Strategies")
    memory = MemoryHierarchy(l1_capacity=5, l2_capacity=10, l3_capacity=20)
    
    # Memory-optimized strategy
    compiler_memory = QuantumCompiler(memory)
    compiled_memory = compiler_memory.compile(grover_circuit)
    print(f"✓ Memory-optimized: {compiled_memory.width} qubits, {len(compiled_memory.gates)} gates")
    
    # Balanced strategy
    compiler_balanced = QuantumCompiler(memory)
    compiled_balanced = compiler_balanced.compile(grover_circuit)
    print(f"✓ Balanced: {compiled_balanced.width} qubits, {len(compiled_balanced.gates)} gates")
    
    print_step(3, "Memory Usage Analysis")
    memory_viz = MemoryVisualizer()
    fig = memory_viz.visualize_memory_usage(memory, filename="demo_memory_usage.png")
    plt.close(fig)
    print("✓ Memory usage analyzed: demo_memory_usage.png")
    
    print_step(4, "Performance Metrics")
    stats = compiler_memory.get_last_compilation_stats()
    print("✓ Compilation statistics:")
    print(f"  - Qubit savings: {stats['qubit_reduction']}")
    print(f"  - Depth change: {stats['depth_change']}")
    print(f"  - Gate count change: {stats['gate_count_change']}")

def demo_cli_features():
    """CLI features demo"""
    print_header("COMMAND LINE INTERFACE (CLI)")
    
    print("Quantum Memory Compiler CLI commands:")
    print()
    print("📊 Visualization:")
    print("   qmc visualize circuit.qmc --output circuit.png")
    print()
    print("⚙️  Compilation:")
    print("   qmc compile circuit.qmc --output compiled.qmc --strategy memory")
    print()
    print("🔬 Simulation:")
    print("   qmc simulate circuit.qmc --shots 1024 --noise --mitigation")
    print()
    print("📈 Profiling:")
    print("   qmc profile circuit.qmc --output profile.png")
    print()
    print("💾 Memory Management:")
    print("   qmc memory --config memory.json --visualize")
    print()
    print("📚 Examples:")
    print("   qmc examples --list")
    print("   qmc examples --run bell_state")
    print()
    print("🔌 API Server:")
    print("   qmc api --port 5000 --debug")

def demo_jupyter_integration():
    """Jupyter integration demo"""
    print_header("JUPYTER LAB INTEGRATION")
    
    print("Using Quantum Memory Compiler in Jupyter Lab:")
    print()
    print("1️⃣ Load extension:")
    print("   %load_ext quantum_memory_compiler_magic")
    print()
    print("2️⃣ Create circuit:")
    print("   %%qmc_circuit bell_state")
    print("   from quantum_memory_compiler.core import Circuit, GateType")
    print("   circuit = Circuit(2)")
    print("   circuit.add_gate(GateType.H, 0)")
    print("   circuit.add_gate(GateType.CNOT, [0, 1])")
    print()
    print("3️⃣ Simulate:")
    print("   %qmc_simulate bell_state shots=2048 noise=True")
    print()
    print("4️⃣ Compile:")
    print("   %qmc_compile bell_state strategy=meta")
    print()
    print("5️⃣ Profile:")
    print("   %qmc_profile bell_state")

def demo_architecture():
    """Architecture explanation"""
    print_header("ARCHITECTURE AND COMPONENTS")
    
    print("🏗️ Quantum Memory Compiler Architecture:")
    print()
    print("📦 Core (Base Components):")
    print("   ├── Circuit: Quantum circuit structure")
    print("   ├── Gate: Quantum gates")
    print("   ├── Qubit: Quantum bits")
    print("   └── Visualization: Visualization tools")
    print()
    print("⚙️ Compiler:")
    print("   ├── QuantumCompiler: Main compiler")
    print("   ├── Optimizer: Gate optimization")
    print("   ├── Mapper: Physical qubit mapping")
    print("   └── MetaCompiler: Strategy evaluation")
    print()
    print("💾 Memory (Memory Management):")
    print("   ├── Hierarchy: Memory level definitions")
    print("   ├── Manager: Qubit allocation and recycling")
    print("   └── Profiler: Memory usage analysis")
    print()
    print("🔬 Simulation:")
    print("   ├── Simulator: Quantum circuit simulator")
    print("   ├── NoiseModel: Noise modeling")
    print("   └── ErrorMitigation: Error mitigation")
    print()
    print("🖥️ Interface:")
    print("   ├── CLI: Command line interface")
    print("   ├── API: REST API server")
    print("   ├── Jupyter: Notebook integration")
    print("   └── Cursor: IDE extension")

def main():
    """Main demo function"""
    print("🚀 QUANTUM MEMORY COMPILER PRESENTATION DEMO STARTING...")
    time.sleep(1)
    
    # Create output directory
    os.makedirs("demo_outputs", exist_ok=True)
    os.chdir("demo_outputs")
    
    try:
        # 1. Basic functionality
        circuit, compiled_circuit, memory = demo_basic_functionality()
        time.sleep(2)
        
        # 2. Simulation features
        demo_simulation()
        time.sleep(2)
        
        # 3. Advanced features
        demo_advanced_features()
        time.sleep(2)
        
        # 4. CLI features
        demo_cli_features()
        time.sleep(2)
        
        # 5. Jupyter integration
        demo_jupyter_integration()
        time.sleep(2)
        
        # 6. Architecture explanation
        demo_architecture()
        
        print_header("DEMO COMPLETED!")
        print("✅ All features successfully demonstrated.")
        print("📁 Output files can be found in 'demo_outputs/' directory.")
        print("🎯 Ready for presentation!")
        
    except Exception as e:
        print(f"❌ Error occurred during demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Return to main directory
        os.chdir("..")

if __name__ == "__main__":
    main() 