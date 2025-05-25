#!/usr/bin/env python3
"""
Test Circuit Visualization Fix
==============================

Test script to verify the circuit visualization API fix.
"""

import requests
import json

def test_circuit_visualization():
    """Test the circuit visualization API endpoint"""
    
    print("🧪 Testing Circuit Visualization API Fix")
    print("=" * 50)
    
    # Test data - simple circuit with H gate
    test_circuit = {
        "name": "Test Circuit",
        "width": 2,
        "gates": [
            {"type": "H", "qubits": [0], "parameters": []},
            {"type": "X", "qubits": [1], "parameters": []}
        ]
    }
    
    # API endpoint
    url = "http://localhost:5001/api/circuit/visualize"
    
    # Request data
    data = {
        "circuit": test_circuit,
        "format": "base64"
    }
    
    try:
        print("📤 Sending circuit visualization request...")
        response = requests.post(url, json=data, timeout=10)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "image" in result:
                print("✅ Circuit visualization successful!")
                print(f"   📊 Image data length: {len(result['image'])} characters")
                print(f"   🎨 Format: {result.get('format', 'unknown')}")
            else:
                print("❌ No image data in response")
                print(f"   Response: {result}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text[:200]}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_circuit_visualization() 