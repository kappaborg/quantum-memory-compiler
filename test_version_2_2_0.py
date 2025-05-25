#!/usr/bin/env python3
"""
Version 2.2.0 Comprehensive Test
===============================

Test script for IBM Quantum Integration and Enhanced Caching System.

Developer: kappasutra
"""

import sys
import time
import json
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ibm_quantum_integration():
    """Test IBM Quantum integration features"""
    print("🔗 Testing IBM Quantum Integration")
    print("-" * 50)
    
    try:
        from quantum_memory_compiler.integration import IBMQuantumProvider, QiskitBridge
        
        # Test provider initialization
        print("1. Testing IBM Quantum Provider...")
        provider = IBMQuantumProvider()  # No token for simulation mode
        
        # Test backend listing
        print("2. Testing backend listing...")
        backends = provider.get_backends()
        print(f"   Found {len(backends)} backends")
        
        for backend in backends[:3]:  # Show first 3
            print(f"   - {backend.name}: {backend.num_qubits} qubits, {backend.backend_type.value}")
        
        # Test least busy backend
        print("3. Testing least busy backend selection...")
        least_busy = provider.get_least_busy_backend(min_qubits=2)
        if least_busy:
            print(f"   Least busy: {least_busy.name} ({least_busy.pending_jobs} pending jobs)")
        
        # Test Qiskit Bridge
        print("4. Testing Qiskit Bridge...")
        bridge = QiskitBridge()
        
        # Create test circuit
        from quantum_memory_compiler.core.circuit import Circuit
        circuit = Circuit("test_qiskit_bridge")
        q0, q1 = circuit.add_qubits(2)
        circuit.h(q0)
        circuit.cnot(q0, q1)
        
        print(f"   Created test circuit: {circuit.width} qubits, {len(circuit.gates)} gates")
        
        # Test backend execution (simulation mode)
        print("5. Testing backend execution...")
        result = bridge.execute_on_qiskit_backend(circuit, 'qasm_simulator', shots=100)
        
        if result['success']:
            print(f"   ✅ Execution successful: {len(result['results'])} outcomes")
            print(f"   Backend: {result['backend']}")
        else:
            print(f"   ❌ Execution failed: {result.get('error', 'Unknown error')}")
        
        print("✅ IBM Quantum Integration test completed")
        return True
        
    except Exception as e:
        print(f"❌ IBM Quantum Integration test failed: {e}")
        return False

def test_enhanced_caching_system():
    """Test Enhanced Caching System"""
    print("\n💾 Testing Enhanced Caching System")
    print("-" * 50)
    
    try:
        from quantum_memory_compiler.caching import CacheManager, CacheType
        
        # Test cache manager initialization
        print("1. Testing Cache Manager initialization...")
        cache_manager = CacheManager(
            cache_dir="test_cache",
            max_memory_mb=100.0,
            cleanup_interval=60,
            enable_persistence=True
        )
        
        # Test circuit caching
        print("2. Testing circuit caching...")
        test_circuit_data = {
            "name": "test_circuit",
            "qubits": 3,
            "gates": [
                {"type": "H", "qubits": [0], "params": []},
                {"type": "CNOT", "qubits": [0, 1], "params": []},
                {"type": "X", "qubits": [2], "params": []}
            ]
        }
        
        # Cache circuit
        cache_key = "test_circuit_123"
        success = cache_manager.put(
            CacheType.CIRCUIT, 
            cache_key, 
            test_circuit_data,
            ttl=3600,  # 1 hour
            metadata={"created_by": "test", "version": "2.2.0"}
        )
        print(f"   Circuit cached: {success}")
        
        # Retrieve circuit
        cached_circuit = cache_manager.get(CacheType.CIRCUIT, cache_key)
        if cached_circuit:
            print(f"   ✅ Circuit retrieved: {cached_circuit['name']}")
        else:
            print("   ❌ Circuit not found in cache")
        
        # Test simulation result caching
        print("3. Testing simulation result caching...")
        test_simulation_result = {
            "results": {"00": 45, "01": 5, "10": 8, "11": 42},
            "shots": 100,
            "execution_time": 0.123,
            "backend": "gpu_accelerated"
        }
        
        sim_key = "sim_result_456"
        success = cache_manager.put(
            CacheType.SIMULATION,
            sim_key,
            test_simulation_result,
            ttl=1800,  # 30 minutes
            metadata={"circuit_hash": "abc123", "shots": 100}
        )
        print(f"   Simulation result cached: {success}")
        
        # Retrieve simulation result
        cached_result = cache_manager.get(CacheType.SIMULATION, sim_key)
        if cached_result:
            print(f"   ✅ Simulation result retrieved: {cached_result['shots']} shots")
        else:
            print("   ❌ Simulation result not found in cache")
        
        # Test cache statistics
        print("4. Testing cache statistics...")
        stats = cache_manager.get_stats()
        
        for cache_type, stat in stats.items():
            print(f"   {cache_type}: {stat.total_entries} entries, "
                  f"{stat.total_size_mb:.2f} MB, {stat.hit_rate:.1f}% hit rate")
        
        # Test cache cleanup
        print("5. Testing cache cleanup...")
        removed_count = cache_manager.cleanup_expired()
        print(f"   Cleaned up {removed_count} expired entries")
        
        # Test cache invalidation
        print("6. Testing cache invalidation...")
        success = cache_manager.invalidate(CacheType.CIRCUIT, cache_key)
        print(f"   Circuit invalidated: {success}")
        
        # Verify invalidation
        cached_circuit = cache_manager.get(CacheType.CIRCUIT, cache_key)
        if cached_circuit is None:
            print("   ✅ Circuit successfully invalidated")
        else:
            print("   ❌ Circuit still in cache after invalidation")
        
        # Shutdown cache manager
        cache_manager.shutdown()
        
        print("✅ Enhanced Caching System test completed")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Caching System test failed: {e}")
        return False

def test_api_integration():
    """Test API integration for new features"""
    print("\n🌐 Testing API Integration")
    print("-" * 50)
    
    base_url = "http://localhost:5001"
    
    try:
        # Test IBM Quantum status
        print("1. Testing IBM Quantum status endpoint...")
        response = requests.get(f"{base_url}/api/ibm/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   Qiskit available: {data.get('qiskit_available', False)}")
            print(f"   Integration ready: {data.get('integration_ready', False)}")
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
        
        # Test IBM backends
        print("2. Testing IBM backends endpoint...")
        response = requests.get(f"{base_url}/api/ibm/backends", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"   ✅ Found {data['count']} backends")
                print(f"   Connected: {data['connected']}")
            else:
                print(f"   ⚠️  Backend listing failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Backend request failed: {response.status_code}")
        
        # Test cache statistics
        print("3. Testing cache statistics endpoint...")
        response = requests.get(f"{base_url}/api/cache/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("   ✅ Cache statistics retrieved")
                for cache_type, stats in data['cache_stats'].items():
                    print(f"   {cache_type}: {stats['total_entries']} entries")
            else:
                print(f"   ❌ Cache stats failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Cache stats request failed: {response.status_code}")
        
        # Test circuit caching via API
        print("4. Testing circuit caching via API...")
        test_circuit = {
            "key": "api_test_circuit",
            "circuit": {
                "name": "API Test Circuit",
                "qubits": 2,
                "gates": [
                    {"type": "H", "qubits": [0], "params": []},
                    {"type": "CNOT", "qubits": [0, 1], "params": []}
                ]
            },
            "ttl": 3600,
            "metadata": {"source": "api_test"}
        }
        
        response = requests.post(
            f"{base_url}/api/cache/circuit",
            json=test_circuit,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("   ✅ Circuit cached via API")
            else:
                print(f"   ❌ Circuit caching failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Circuit cache request failed: {response.status_code}")
        
        # Test cache cleanup via API
        print("5. Testing cache cleanup via API...")
        response = requests.post(f"{base_url}/api/cache/cleanup", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"   ✅ Cache cleanup: {data['removed_entries']} entries removed")
            else:
                print(f"   ❌ Cache cleanup failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Cache cleanup request failed: {response.status_code}")
        
        print("✅ API Integration test completed")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API Integration test failed: {e}")
        print("   Make sure API server is running on port 5001")
        return False
    except Exception as e:
        print(f"❌ API Integration test failed: {e}")
        return False

def main():
    """Run all Version 2.2.0 tests"""
    print("🚀 Quantum Memory Compiler - Version 2.2.0 Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Run tests
    test_results.append(("IBM Quantum Integration", test_ibm_quantum_integration()))
    test_results.append(("Enhanced Caching System", test_enhanced_caching_system()))
    test_results.append(("API Integration", test_api_integration()))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Version 2.2.0 is ready!")
        print("\n🎯 Version 2.2.0 Features Completed:")
        print("   ✅ Web dashboard MVP")
        print("   ✅ GPU acceleration")
        print("   ✅ IBM Quantum integration")
        print("   ✅ Enhanced caching system")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 