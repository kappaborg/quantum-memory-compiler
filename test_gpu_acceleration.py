#!/usr/bin/env python3
"""
GPU Acceleration Test Script
===========================

Test script for Quantum Memory Compiler GPU acceleration features.

Developer: kappasutra
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_gpu_acceleration():
    """Test GPU acceleration features"""
    print("🚀 Testing GPU Acceleration Features")
    print("=" * 50)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from quantum_memory_compiler.acceleration import AccelerationManager
        from quantum_memory_compiler.core.circuit import Circuit
        from quantum_memory_compiler.core.gates import HGate, XGate
        print("   ✅ All imports successful")
        
        # Initialize acceleration manager
        print("\n🔧 Initializing Acceleration Manager...")
        manager = AccelerationManager(
            enable_gpu=True,
            max_memory_gb=2.0,
            max_workers=4,
            precision='float32'
        )
        print("   ✅ Acceleration Manager initialized")
        
        # Get status
        print("\n📊 Getting acceleration status...")
        status = manager.get_acceleration_status()
        print(f"   GPU enabled: {status['gpu_acceleration']['enabled']}")
        print(f"   Parallel workers: {status['parallel_processing']['max_workers']}")
        print(f"   Memory limit: {status['memory_optimization']['max_memory_gb']} GB")
        
        # Create simple test circuit
        print("\n🔬 Creating test circuit...")
        circuit = Circuit(3)
        circuit.name = "test_circuit"
        circuit.add_gate(HGate(), 0)
        circuit.add_gate(XGate(), 1)
        circuit.add_gate(HGate(), 2)
        print(f"   ✅ Circuit created: {circuit.width} qubits, {len(circuit.gates)} gates")
        
        # Analyze circuit
        print("\n🔍 Analyzing circuit...")
        analysis = manager.analyze_circuit(circuit)
        print(f"   Memory required: {analysis['memory_analysis']['requirements']['total_memory_gb']:.6f} GB")
        print(f"   Recommended method: {analysis['performance_predictions']['recommended_method']}")
        
        # Test simulation
        print("\n⚡ Testing simulation...")
        results = manager.simulate_circuit(
            circuit=circuit,
            shots=100,
            method='auto',
            optimize_memory=True
        )
        print(f"   ✅ Simulation completed in {results['acceleration_info']['total_simulation_time']:.3f}s")
        print(f"   Method used: {results['acceleration_info']['method_used']}")
        
        print("\n✅ All GPU acceleration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🧪 Quantum Memory Compiler - GPU Acceleration Test")
    print("=" * 60)
    
    success = test_gpu_acceleration()
    
    if success:
        print("\n🎉 GPU Acceleration is working correctly!")
        return 0
    else:
        print("\n💥 GPU Acceleration test failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 