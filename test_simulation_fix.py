#!/usr/bin/env python3
"""
Test Circuit Simulation Fix
============================

Test script to verify the circuit simulation API fix.
"""

import requests
import json

def test_circuit_simulation():
    """Test the circuit simulation API endpoint"""
    
    print("🧪 Testing Circuit Simulation API Fix")
    print("=" * 50)
    
    # Test data - simple circuit with H gate and CNOT
    test_circuit = {
        "name": "Test Circuit",
        "width": 2,
        "gates": [
            {"type": "H", "qubits": [0], "parameters": []},
            {"type": "CNOT", "qubits": [0, 1], "parameters": []}
        ]
    }
    
    # API endpoint
    url = "http://localhost:5001/api/circuit/simulate"
    
    # Request data
    data = {
        "circuit": test_circuit,
        "shots": 100,
        "noise": False,
        "mitigation": False
    }
    
    try:
        print("📤 Sending circuit simulation request...")
        print(f"   Circuit: {test_circuit['name']}")
        print(f"   Qubits: {test_circuit['width']}")
        print(f"   Gates: {len(test_circuit['gates'])}")
        print(f"   Shots: {data['shots']}")
        
        response = requests.post(url, json=data, timeout=15)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Circuit simulation successful!")
                print(f"   🎯 Shots: {result.get('shots', 'unknown')}")
                print(f"   ⏱️  Execution time: {result.get('execution_time', 'unknown')}s")
                print(f"   🖥️  Backend: {result.get('backend', 'unknown')}")
                if 'results' in result:
                    print(f"   📊 Results type: {type(result['results'])}")
            else:
                print("❌ Simulation failed")
                print(f"   Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text[:500]}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        print("   Make sure API server is running on port 5001")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_circuit_simulation() 