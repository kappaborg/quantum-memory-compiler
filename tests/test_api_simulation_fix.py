#!/usr/bin/env python3
"""
API Simulation Endpoint Test
============================

Bu script API simulation endpoint'indeki hataları test eder ve düzeltir.
"""

import requests
import json
import time

def test_simulation_endpoint():
    """Test the simulation endpoint with a simple Bell state circuit"""
    
    # API endpoint
    url = "http://localhost:5001/api/circuit/simulate"
    
    # Bell state circuit data
    circuit_data = {
        "name": "Bell State Test",
        "qubits": 2,
        "width": 2,
        "gates": [
            {
                "type": "H",
                "qubits": [0],
                "parameters": []
            },
            {
                "type": "CNOT", 
                "qubits": [0, 1],
                "parameters": []
            }
        ],
        "measurements": [
            {"qubit": 0, "classical_bit": 0},
            {"qubit": 1, "classical_bit": 1}
        ]
    }
    
    # Request payload
    payload = {
        "circuit": circuit_data,
        "shots": 1024,
        "noise": False,
        "mitigation": False
    }
    
    print("🧪 Testing API simulation endpoint...")
    print(f"📡 URL: {url}")
    print(f"📊 Circuit: {circuit_data['name']}")
    print(f"🎯 Shots: {payload['shots']}")
    
    try:
        # Send request
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"📈 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Simulation successful!")
            print(f"📊 Results: {result.get('results', {})}")
            print(f"⏱️  Execution time: {result.get('execution_time', 'N/A')}")
            print(f"🎯 Shots: {result.get('shots', 'N/A')}")
            print(f"🖥️  Backend: {result.get('backend', 'N/A')}")
            return True
        else:
            print("❌ Simulation failed!")
            try:
                error_data = response.json()
                print(f"🚨 Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"🚨 Raw response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure the API server is running on port 5001")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timeout!")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_compilation_endpoint():
    """Test the compilation endpoint"""
    
    # API endpoint
    url = "http://localhost:5001/api/circuit/compile"
    
    # Simple circuit data
    circuit_data = {
        "name": "Test Compilation",
        "qubits": 3,
        "width": 3,
        "gates": [
            {"type": "H", "qubits": [0], "parameters": []},
            {"type": "CNOT", "qubits": [0, 1], "parameters": []},
            {"type": "CNOT", "qubits": [1, 2], "parameters": []},
            {"type": "X", "qubits": [2], "parameters": []}
        ]
    }
    
    payload = {
        "circuit": circuit_data,
        "strategy": "balanced",
        "use_meta_compiler": False
    }
    
    print("\n🔧 Testing API compilation endpoint...")
    print(f"📡 URL: {url}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"📈 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Compilation successful!")
            print(f"📊 Original qubits: {result.get('metrics', {}).get('original_qubits', 'N/A')}")
            print(f"📊 Compiled qubits: {result.get('metrics', {}).get('compiled_qubits', 'N/A')}")
            return True
        else:
            print("❌ Compilation failed!")
            try:
                error_data = response.json()
                print(f"🚨 Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"🚨 Raw response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure the API server is running on port 5001")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_api_info():
    """Test the API info endpoint"""
    
    url = "http://localhost:5001/api/info"
    
    print("\n📋 Testing API info endpoint...")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            info = response.json()
            print("✅ API info retrieved successfully!")
            print(f"📦 Version: {info.get('version', 'N/A')}")
            print(f"🖥️  System: {info.get('system_info', {}).get('platform', 'N/A')}")
            print(f"🐍 Python: {info.get('system_info', {}).get('python_version', 'N/A')}")
            print(f"🚀 GPU Support: {info.get('gpu_support', 'N/A')}")
            return True
        else:
            print("❌ API info failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error getting API info: {e}")
        return False

def main():
    """Main test function"""
    
    print("🧪 API Endpoint Testing Suite")
    print("=" * 50)
    
    # Test API info first
    info_success = test_api_info()
    
    # Test simulation endpoint
    sim_success = test_simulation_endpoint()
    
    # Test compilation endpoint
    comp_success = test_compilation_endpoint()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"📋 API Info: {'✅ PASS' if info_success else '❌ FAIL'}")
    print(f"🧪 Simulation: {'✅ PASS' if sim_success else '❌ FAIL'}")
    print(f"🔧 Compilation: {'✅ PASS' if comp_success else '❌ FAIL'}")
    
    if all([info_success, sim_success, comp_success]):
        print("\n🎉 All tests passed!")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the API server logs for details.")
        return False

if __name__ == "__main__":
    main() 