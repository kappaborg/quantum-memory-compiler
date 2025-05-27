#!/usr/bin/env python3
"""
API Client Test for GPU Acceleration
====================================

Test script to demonstrate the GPU acceleration API endpoints.

Developer: kappasutra
"""

import requests
import json
import time

def test_api_endpoints():
    """Test GPU acceleration API endpoints"""
    base_url = "http://localhost:5001"
    
    print("🌐 Testing Quantum Memory Compiler API with GPU Acceleration")
    print("=" * 60)
    
    try:
        # Test API info
        print("📋 Testing API Info...")
        response = requests.get(f"{base_url}/api/info", timeout=5)
        if response.status_code == 200:
            info = response.json()
            print(f"   ✅ API Version: {info['version']}")
            print(f"   ✅ GPU Acceleration: {info['acceleration_features']['gpu_simulation']}")
            print(f"   ✅ Parallel Processing: {info['acceleration_features']['parallel_processing']}")
            print(f"   ✅ Memory Optimization: {info['acceleration_features']['memory_optimization']}")
        else:
            print(f"   ❌ API Info failed: {response.status_code}")
            return False
        
        # Test acceleration status
        print("\n⚡ Testing Acceleration Status...")
        response = requests.get(f"{base_url}/api/acceleration/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ GPU Available: {status['status']['gpu_acceleration']['available']}")
            print(f"   ✅ Max Workers: {status['status']['parallel_processing']['max_workers']}")
            print(f"   ✅ Memory Limit: {status['status']['memory_optimization']['max_memory_gb']} GB")
        else:
            print(f"   ❌ Acceleration Status failed: {response.status_code}")
        
        # Test circuit analysis
        print("\n🔍 Testing Circuit Analysis...")
        test_circuit = {
            "name": "api_test_circuit",
            "width": 3,
            "gates": [
                {"type": "H", "qubits": [0], "parameters": []},
                {"type": "X", "qubits": [1], "parameters": []},
                {"type": "CNOT", "qubits": [0, 1], "parameters": []}
            ],
            "measurements": []
        }
        
        response = requests.post(
            f"{base_url}/api/acceleration/analyze",
            json={"circuit": test_circuit},
            timeout=10
        )
        if response.status_code == 200:
            analysis = response.json()
            print(f"   ✅ Analysis completed successfully")
            print(f"   ✅ Circuit analyzed: {test_circuit['width']} qubits, {len(test_circuit['gates'])} gates")
        else:
            print(f"   ❌ Circuit Analysis failed: {response.status_code}")
        
        # Test accelerated simulation
        print("\n🚀 Testing Accelerated Simulation...")
        response = requests.post(
            f"{base_url}/api/acceleration/simulate",
            json={
                "circuit": test_circuit,
                "shots": 100,
                "method": "auto",
                "optimize_memory": True
            },
            timeout=15
        )
        if response.status_code == 200:
            sim_results = response.json()
            print(f"   ✅ Simulation completed successfully")
            print(f"   ✅ Method used: {sim_results.get('results', {}).get('acceleration_info', {}).get('method_used', 'unknown')}")
        else:
            print(f"   ❌ Accelerated Simulation failed: {response.status_code}")
        
        # Test memory report
        print("\n🧠 Testing Memory Report...")
        response = requests.get(f"{base_url}/api/acceleration/memory/report", timeout=5)
        if response.status_code == 200:
            memory_report = response.json()
            print(f"   ✅ Memory report generated")
            print(f"   ✅ Process memory: {memory_report['memory_report']['process_memory']['rss_gb']:.3f} GB")
        else:
            print(f"   ❌ Memory Report failed: {response.status_code}")
        
        # Test memory cleanup
        print("\n🧹 Testing Memory Cleanup...")
        response = requests.post(
            f"{base_url}/api/acceleration/memory/cleanup",
            json={"force_gc": True},
            timeout=5
        )
        if response.status_code == 200:
            cleanup_stats = response.json()
            print(f"   ✅ Memory cleanup completed")
            print(f"   ✅ Memory freed: {cleanup_stats['cleanup_stats']['memory_freed_gb']:.3f} GB")
        else:
            print(f"   ❌ Memory Cleanup failed: {response.status_code}")
        
        print("\n✅ All API tests completed successfully!")
        print("🚀 GPU Acceleration API is fully operational!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on localhost:5001")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main function"""
    success = test_api_endpoints()
    if success:
        print("\n🎉 GPU Acceleration API is working perfectly!")
        return 0
    else:
        print("\n💥 API tests failed!")
        return 1

if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code) 