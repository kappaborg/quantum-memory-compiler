#!/usr/bin/env python3
"""
Simple API Test Server
======================

API simulation endpoint'ini test etmek için basit bir server.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'quantum_memory_compiler'))

from flask import Flask, request, jsonify
from quantum_memory_compiler.core.circuit import Circuit
from quantum_memory_compiler.core.qubit import Qubit
from quantum_memory_compiler.core.gate import GateType
from quantum_memory_compiler.simulation.simulator import Simulator

app = Flask(__name__)

@app.route('/api/circuit/simulate', methods=['POST'])
def simulate_circuit():
    """Simple simulation endpoint for testing"""
    try:
        print("🧪 simulate_circuit API endpoint called")
        data = request.json
        print(f"📊 Received data: {data}")
        
        if not data or 'circuit' not in data:
            return jsonify({"error": "Valid circuit JSON must be provided"}), 400
            
        # Convert web dashboard format to backend format
        circuit_data = data['circuit']
        print(f"📊 Circuit data received: {circuit_data}")
        
        # Create circuit directly instead of using from_dict
        qubits_count = circuit_data.get('qubits', circuit_data.get('width', 2))
        circuit_name = circuit_data.get('name', 'Unnamed Circuit')
        
        # Create circuit with qubits
        circuit = Circuit()
        circuit.name = circuit_name  # Set name after creation
        qubits = [Qubit(i) for i in range(qubits_count)]  # Use integer IDs
        for qubit in qubits:
            circuit.add_qubit(qubit)
        
        print(f"📊 Created circuit with {len(qubits)} qubits")
        
        # Add gates
        for gate_data in circuit_data.get('gates', []):
            gate_type_str = gate_data.get('type')
            gate_qubits = gate_data.get('qubits', [])
            gate_params = gate_data.get('parameters', gate_data.get('params', []))
            
            if gate_type_str and gate_qubits:
                # Convert string gate type to GateType enum
                try:
                    gate_type = getattr(GateType, gate_type_str.upper())
                    print(f"🔧 Converting gate type: {gate_type_str} -> {gate_type}")
                except AttributeError:
                    print(f"⚠️  Unknown gate type: {gate_type_str}, skipping...")
                    continue
                
                # Map qubit indices to actual qubit objects
                target_qubits = [qubits[i] for i in gate_qubits if i < len(qubits)]
                
                if target_qubits:
                    # Use the correct add_gate method signature
                    circuit.add_gate(gate_type, *target_qubits, parameters=gate_params)
                    print(f"🔧 Added gate: type={gate_type} to qubits {[q.id for q in target_qubits]}")
        
        print(f"✅ Circuit created successfully, width: {circuit.width}, gates: {len(circuit.gates)}")
        
        # Add measurement gates automatically if not present
        has_measurements = any(gate.type == GateType.MEASURE for gate in circuit.gates)
        if not has_measurements:
            print("🔧 Adding automatic measurements to all qubits")
            for i, qubit in enumerate(qubits):
                circuit.add_gate(GateType.MEASURE, qubit, parameters=[i])
            print(f"🔧 Added {len(qubits)} measurement gates")
        
        # Simulation parameters
        shots = data.get('shots', 1024)
        use_noise = data.get('noise', False)
        use_mitigation = data.get('mitigation', False)
        
        print(f"🎯 Simulation parameters: shots={shots}, noise={use_noise}, mitigation={use_mitigation}")
        
        # Noise model
        noise_model = None
        
        # Simulator
        simulator = Simulator(noise_model=noise_model, enable_error_mitigation=use_mitigation)
        
        # Run simulation
        print(f"🔬 About to run simulation with {shots} shots")
        results = simulator.run(circuit, shots=shots)
        print(f"🔬 Simulation returned: {results}")
        print(f"🔬 Type of results: {type(results)}")
        
        print("✅ Simulation completed successfully")
        print(f"🔬 Raw simulation results: {results}")
        
        # Convert numpy types to Python types for JSON serialization
        def convert_numpy_to_python(obj):
            """Convert numpy types to Python types for JSON serialization"""
            if hasattr(obj, 'item'):
                return obj.item()
            elif isinstance(obj, dict):
                return {k: convert_numpy_to_python(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_to_python(item) for item in obj]
            else:
                return obj
        
        # Convert results to JSON-serializable format
        json_results = convert_numpy_to_python(results)
        print(f"🔬 JSON-serializable results: {json_results}")
        
        # Return results
        return jsonify({
            "success": True,
            "results": json_results,
            "execution_time": 0.1,  # Placeholder
            "shots": shots,
            "backend": "qasm_simulator",
            "parameters": {
                "shots": shots,
                "noise": use_noise,
                "mitigation": use_mitigation
            }
        })
            
    except Exception as e:
        print(f"❌ Simulation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🚀 Starting simple API test server on port 5002")
    app.run(host="0.0.0.0", port=5002, debug=True) 