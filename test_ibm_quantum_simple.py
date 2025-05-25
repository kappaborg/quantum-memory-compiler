#!/usr/bin/env python3
"""
IBM Quantum Simple Test
======================

Simple test for IBM Quantum integration without token.

Developer: kappasutra
"""

import requests
import json
import time

API_BASE = "http://localhost:5001"

def test_ibm_status():
    """Test IBM Quantum status"""
    print("🔍 Testing IBM Quantum Status...")
    
    try:
        response = requests.get(f"{API_BASE}/api/ibm/status")
        data = response.json()
        
        print(f"✅ Status Response:")
        print(f"   Qiskit Available: {data.get('qiskit_available')}")
        print(f"   Qiskit Version: {data.get('qiskit_version')}")
        print(f"   Token Provided: {data.get('token_provided')}")
        print(f"   Connected: {data.get('connected')}")
        print(f"   Integration Ready: {data.get('integration_ready')}")
        
        return data
    except Exception as e:
        print(f"❌ Status test failed: {e}")
        return None

def test_ibm_backends():
    """Test IBM Quantum backends"""
    print("\n🔍 Testing IBM Quantum Backends...")
    
    try:
        response = requests.get(f"{API_BASE}/api/ibm/backends")
        data = response.json()
        
        print(f"✅ Backends Response:")
        print(f"   Success: {data.get('success')}")
        print(f"   Connected: {data.get('connected')}")
        print(f"   Backend Count: {data.get('count')}")
        
        backends = data.get('backends', [])
        for backend in backends:
            print(f"   - {backend['name']}: {backend['num_qubits']} qubits, {backend['type']}")
        
        return data
    except Exception as e:
        print(f"❌ Backends test failed: {e}")
        return None

def test_circuit_execution():
    """Test circuit execution without token"""
    print("\n🔍 Testing Circuit Execution (Local Simulation)...")
    
    circuit_data = {
        "circuit": {
            "name": "test_bell_state",
            "qubits": 2,
            "gates": [
                {"type": "H", "qubits": [0]},
                {"type": "CNOT", "qubits": [0, 1]}
            ]
        },
        "backend": "qasm_simulator",
        "shots": 100
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/ibm/execute",
            json=circuit_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Execution Response:")
            print(f"   Success: {data.get('success')}")
            print(f"   Job ID: {data.get('job_id')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Backend: {data.get('backend')}")
            print(f"   Shots: {data.get('shots')}")
            print(f"   Execution Type: {data.get('execution_type')}")
            
            results = data.get('results', {})
            print(f"   Results:")
            for state, count in results.items():
                probability = count / data.get('shots', 1)
                print(f"     |{state}⟩: {count} ({probability:.2%})")
            
            return data
        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Execution test failed: {e}")
        return None

def test_with_token(token):
    """Test with actual IBM Quantum token"""
    print(f"\n🔍 Testing with IBM Quantum Token...")
    
    # Test status with token
    try:
        response = requests.get(f"{API_BASE}/api/ibm/status", params={"token": token})
        data = response.json()
        
        print(f"✅ Status with Token:")
        print(f"   Token Provided: {data.get('token_provided')}")
        print(f"   Connected: {data.get('connected')}")
        print(f"   Integration Ready: {data.get('integration_ready')}")
        
        if data.get('connected'):
            print("🎉 Successfully connected to IBM Quantum!")
            
            # Test backends with token
            response = requests.get(f"{API_BASE}/api/ibm/backends", params={"token": token})
            backends_data = response.json()
            
            backends = backends_data.get('backends', [])
            real_backends = [b for b in backends if not b.get('simulator')]
            
            print(f"   Real Hardware Backends: {len(real_backends)}")
            for backend in real_backends[:3]:  # Show first 3
                print(f"     - {backend['name']}: {backend['num_qubits']} qubits")
        
        return data
        
    except Exception as e:
        print(f"❌ Token test failed: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 IBM Quantum Integration Test")
    print("=" * 50)
    
    # Test basic functionality
    status = test_ibm_status()
    backends = test_ibm_backends()
    execution = test_circuit_execution()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   Status Test: {'✅ PASS' if status else '❌ FAIL'}")
    print(f"   Backends Test: {'✅ PASS' if backends else '❌ FAIL'}")
    print(f"   Execution Test: {'✅ PASS' if execution else '❌ FAIL'}")
    
    if status and backends and execution:
        print("\n🎉 All basic tests passed!")
        print("\n📝 Next Steps:")
        print("   1. Get your IBM Quantum token from: https://quantum.ibm.com/")
        print("   2. Open web dashboard: http://localhost:3000")
        print("   3. Go to IBM Quantum page")
        print("   4. Click 'Token Ayarla' and paste your token")
        print("   5. Test real IBM Quantum backends!")
    else:
        print("\n❌ Some tests failed. Check the API server and try again.")
    
    # Test with token if provided
    token = input("\n🔑 Enter your IBM Quantum token (or press Enter to skip): ").strip()
    if token:
        test_with_token(token)

if __name__ == "__main__":
    main() 