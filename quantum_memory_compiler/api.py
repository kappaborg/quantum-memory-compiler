#!/usr/bin/env python3
"""
Quantum Memory Compiler - Advanced Memory-Aware Quantum Circuit Compilation
Copyright (c) 2025 Quantum Memory Compiler Project

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This file contains proprietary algorithms for quantum memory optimization.
Commercial use requires explicit permission.
"""

"""
Quantum Memory Compiler API
==========================

Flask Restful API entegrations with WebSocket support

Developer: kappasutra
"""

import os
import sys
import json
import base64
import tempfile
import time as time_module
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from io import BytesIO

HAS_FLASK = False
HAS_SOCKETIO = False
try:
    from flask import Flask, request, jsonify, send_file, make_response
    from flask_cors import CORS
    from flask_socketio import SocketIO, emit, join_room, leave_room
    HAS_FLASK = True
    HAS_SOCKETIO = True
    print("✅ Flask and SocketIO libraries loaded successfully.")
except ImportError as e:
    print(f"❌ Flask/SocketIO error: {e}")
    print("   Install with: pip install flask flask-cors flask-socketio eventlet")
    HAS_FLASK = False
    HAS_SOCKETIO = False

# Quantum Memory Compiler modules
from quantum_memory_compiler.core.circuit import Circuit
from quantum_memory_compiler.core.visualization import CircuitVisualizer
from quantum_memory_compiler.simulation.simulator import Simulator
from quantum_memory_compiler.compiler.compiler import QuantumCompiler as Compiler
from quantum_memory_compiler.memory.profiler import MemoryProfiler
from quantum_memory_compiler.simulation.noise_model import NoiseModel
from .acceleration import AccelerationManager

try:
    from quantum_memory_compiler.compiler.metacompiler import MetaCompiler
    HAS_META_COMPILER = True
    print("✅ MetaCompiler successfully loaded.")
except ImportError:
    HAS_META_COMPILER = False
    print("⚠️  MetaCompiler not available.")

# Initialize Flask app and SocketIO
app = None
socketio = None
temp_dir = None
active_sessions = {}  # Track active user sessions

# Initialize acceleration manager
acceleration_manager = AccelerationManager(
    enable_gpu=True,
    max_memory_gb=4.0,
    max_workers=None,
    precision='float32'
)

if HAS_FLASK and HAS_SOCKETIO:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'quantum_memory_compiler_secret_key_2025'
    
    # Initialize SocketIO with CORS support
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
    
    CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"], 
                                    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})
    temp_dir = tempfile.mkdtemp(prefix="qmc_api_")
    print("✅ Flask app and SocketIO initialized successfully.")
    
    # WebSocket Event Handlers
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        session_id = request.sid
        active_sessions[session_id] = {
            'connected_at': __import__('datetime').datetime.now(),
            'circuits': [],
            'last_activity': __import__('datetime').datetime.now()
        }
        print(f"🔌 Client connected: {session_id}")
        emit('connection_response', {
            'status': 'connected',
            'session_id': session_id,
            'message': 'Welcome to Quantum Lab API!'
        })
        
        # Send current system status
        emit('system_status', {
            'api_version': '2.2.0',
            'active_sessions': len(active_sessions),
            'endpoints_available': 6,
            'websocket_enabled': True
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        session_id = request.sid
        if session_id in active_sessions:
            del active_sessions[session_id]
        print(f"🔌 Client disconnected: {session_id}")
    
    @socketio.on('join_room')
    def handle_join_room(data):
        """Handle room joining for collaboration"""
        room = data.get('room', 'general')
        join_room(room)
        session_id = request.sid
        print(f"🏠 Client {session_id} joined room: {room}")
        emit('room_joined', {'room': room, 'session_id': session_id})
        
        # Notify others in the room
        emit('user_joined', {
            'session_id': session_id,
            'message': f'User {session_id[:8]} joined the room'
        }, room=room, include_self=False)
    
    @socketio.on('leave_room')
    def handle_leave_room(data):
        """Handle room leaving"""
        room = data.get('room', 'general')
        leave_room(room)
        session_id = request.sid
        print(f"🏠 Client {session_id} left room: {room}")
        emit('room_left', {'room': room, 'session_id': session_id})
        
        # Notify others in the room
        emit('user_left', {
            'session_id': session_id,
            'message': f'User {session_id[:8]} left the room'
        }, room=room, include_self=False)
    
    @socketio.on('circuit_update')
    def handle_circuit_update(data):
        """Handle real-time circuit updates"""
        session_id = request.sid
        room = data.get('room', 'general')
        circuit_data = data.get('circuit')
        
        if session_id in active_sessions:
            active_sessions[session_id]['last_activity'] = __import__('datetime').datetime.now()
            active_sessions[session_id]['circuits'].append(circuit_data)
        
        print(f"🔄 Circuit update from {session_id} in room {room}")
        
        # Broadcast to room members
        emit('circuit_updated', {
            'session_id': session_id,
            'circuit': circuit_data,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }, room=room, include_self=False)
    
    @socketio.on('request_system_stats')
    def handle_system_stats():
        """Handle system statistics request"""
        stats = {
            'active_sessions': len(active_sessions),
            'total_circuits': sum(len(session['circuits']) for session in active_sessions.values()),
            'api_version': '2.2.0',
            'websocket_enabled': True,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        emit('system_stats', stats)

    @app.after_request
    def add_cors_headers(response):
        """Adding CORS headers"""
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response

    @app.route('/api/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        """OPTIONS request"""
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response

    @app.route('/api/info', methods=['GET'])
    def get_info():
        """API info"""
        return jsonify({
            "name": "Quantum Memory Compiler API",
            "version": "2.2.0",
            "developer": "kappasutra",
            "features": {
                "websocket_support": True,
                "file_upload_download": True,
                "real_time_collaboration": True,
                "session_management": True,
                "gpu_acceleration": True,
                "parallel_processing": True,
                "memory_optimization": True,
                "acceleration_benchmarking": True
            },
            "endpoints": [
                {"path": "/api/info", "method": "GET", "description": "Returns API information"},
                {"path": "/api/circuit/visualize", "method": "POST", "description": "Visualizes quantum circuits"},
                {"path": "/api/circuit/simulate", "method": "POST", "description": "Simulates quantum circuits"},
                {"path": "/api/circuit/compile", "method": "POST", "description": "Compiles quantum circuits"},
                {"path": "/api/circuit/upload", "method": "POST", "description": "Upload circuit files (JSON, QASM)"},
                {"path": "/api/circuit/download", "method": "POST", "description": "Download circuits (JSON, QASM, Python)"},
                {"path": "/api/memory/profile", "method": "POST", "description": "Creates memory profiles"},
                {"path": "/api/examples", "method": "GET", "description": "Lists available examples"},
                {"path": "/api/acceleration/status", "method": "GET", "description": "Get GPU acceleration status"},
                {"path": "/api/acceleration/analyze", "method": "POST", "description": "Analyze circuit for acceleration"},
                {"path": "/api/acceleration/simulate", "method": "POST", "description": "Run accelerated simulation"},
                {"path": "/api/acceleration/benchmark", "method": "POST", "description": "Run acceleration benchmark"},
                {"path": "/api/acceleration/memory/report", "method": "GET", "description": "Get memory usage report"},
                {"path": "/api/acceleration/memory/cleanup", "method": "POST", "description": "Clean up GPU memory"},
                {"path": "/api/ibm/backends", "method": "GET", "description": "Get available IBM Quantum backends"},
                {"path": "/api/ibm/execute", "method": "POST", "description": "Execute circuit on IBM Quantum backend"},
                {"path": "/api/ibm/transpile", "method": "POST", "description": "Transpile circuit for IBM Quantum backend"},
                {"path": "/api/ibm/status", "method": "GET", "description": "Get IBM Quantum integration status"},
                {"path": "/api/cache/stats", "method": "GET", "description": "Get cache statistics"},
                {"path": "/api/cache/clear", "method": "POST", "description": "Clear cache"},
                {"path": "/api/cache/cleanup", "method": "POST", "description": "Clean up expired cache entries"},
                {"path": "/api/cache/circuit", "method": "GET", "description": "Get cached circuit"},
                {"path": "/api/cache/circuit", "method": "POST", "description": "Cache circuit"},
                {"path": "/api/cache/circuit", "method": "DELETE", "description": "Remove circuit from cache"},
                {"path": "/api/cache/simulation", "method": "GET", "description": "Get cached simulation result"},
                {"path": "/api/cache/simulation", "method": "POST", "description": "Cache simulation result"},
                {"path": "/api/cache/simulation", "method": "DELETE", "description": "Remove simulation result from cache"}
            ],
            "websocket_events": [
                {"event": "connect", "description": "Client connection with session management"},
                {"event": "disconnect", "description": "Client disconnection"},
                {"event": "join_room", "description": "Join collaboration room"},
                {"event": "leave_room", "description": "Leave collaboration room"},
                {"event": "circuit_update", "description": "Real-time circuit sharing"},
                {"event": "request_system_stats", "description": "Get live system statistics"},
                {"event": "acceleration_status_request", "description": "Request acceleration status"},
                {"event": "start_benchmark", "description": "Start acceleration benchmark"}
            ],
            "acceleration_features": {
                "gpu_simulation": acceleration_manager.gpu_simulator.use_gpu,
                "parallel_processing": acceleration_manager.parallel_processor.max_workers > 1,
                "memory_optimization": acceleration_manager.memory_optimizer.max_memory_gb > 0,
                "jit_compilation": acceleration_manager.parallel_processor.use_jit,
                "device_count": acceleration_manager.gpu_simulator.device_count,
                "max_memory_gb": acceleration_manager.memory_optimizer.max_memory_gb
            },
            "statistics": {
                "active_sessions": len(active_sessions),
                "total_circuits": sum(len(session.get('circuits', [])) for session in active_sessions.values()),
                "websocket_enabled": True,
                "acceleration_enabled": True
            }
        })

    @app.route('/api/circuit/visualize', methods=['POST'])
    def visualize_circuit():
        """
        Circuit visualization API endpoint
        
        Request JSON:
        {
            "circuit": {...}  // Circuit JSON object
        }
        
        Returns:
            JSON or image: Visualization or error message
        """
        try:
            print("🎨 visualize_circuit API endpoint called")
            data = request.json
            if not data or 'circuit' not in data:
                print("❌ Error: No valid circuit JSON provided")
                return jsonify({"error": "Valid circuit JSON must be provided"}), 400
                
            circuit_data = data['circuit']
            print(f"📊 Circuit data received: {circuit_data}")
            
            # Convert web dashboard format to backend format
            converted_data = {
                'name': circuit_data.get('name', 'Unnamed Circuit'),
                'qubits': circuit_data.get('width', circuit_data.get('qubits', 0)),  # Handle both 'width' and 'qubits'
                'gates': [],
                'measurements': circuit_data.get('measurements', [])
            }
            
            # Convert gates format
            for gate in circuit_data.get('gates', []):
                converted_gate = {
                    'type': gate.get('type'),
                    'qubits': gate.get('qubits', []),
                    'params': gate.get('parameters', gate.get('params', []))  # Handle both 'parameters' and 'params'
                }
                converted_data['gates'].append(converted_gate)
            
            print(f"🔄 Converted circuit data: {converted_data}")
            
            try:
                circuit = Circuit.from_dict(converted_data)
                print(f"✅ Circuit created successfully, width: {circuit.width}, gates: {len(circuit.gates)}")
            except Exception as ce:
                print(f"❌ Error creating circuit: {ce}")
                return jsonify({"error": f"Error creating circuit: {ce}"}), 400
            
            # Visualize
            visualizer = CircuitVisualizer()
            print("🎨 CircuitVisualizer created")
            
            # Determine format
            format_type = data.get('format', 'png')
            print(f"📸 Visualization format: {format_type}")
            
            if format_type == 'base64':
                try:
                    # Visualize to memory
                    print("🔄 Creating base64 visualization...")
                    img_buf = BytesIO()
                    visualizer.visualize_circuit(circuit, img_buf)
                    img_buf.seek(0)
                    
                    # Encode to base64
                    encoded = base64.b64encode(img_buf.read()).decode('utf-8')
                    print("✅ Visualization successful, base64 encoded")
                    return jsonify({"image": encoded, "format": "base64"})
                except Exception as ve:
                    print(f"❌ Visualization error (base64): {ve}")
                    return jsonify({"error": f"Visualization error: {ve}"}), 500
            else:
                try:
                    # Visualize to file
                    print(f"💾 Creating file visualization (format: {format_type})...")
                    output_file = os.path.join(temp_dir, f"circuit_{id(circuit)}.{format_type}")
                    visualizer.visualize_circuit(circuit, output_file)
                    print(f"✅ Visualization successful, file: {output_file}")
                    
                    return send_file(output_file, mimetype=f'image/{format_type}')
                except Exception as ve:
                    print(f"❌ Visualization error (file): {ve}")
                    return jsonify({"error": f"Visualization error: {ve}"}), 500
                
        except Exception as e:
            print(f"❌ General error: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/circuit/simulate', methods=['POST'])
    def simulate_circuit():
        """
        Circuit simulation API endpoint
        
        Request JSON:
        {
            "circuit": {...},  // Circuit JSON object
            "shots": 1024,     // Number of simulation shots
            "noise": true,     // Use noise model
            "mitigation": false  // Use error mitigation
        }
        
        Returns:
            JSON: Simulation results or error message
        """
        try:
            print("🔬 simulate_circuit API endpoint called")
            data = request.json
            if not data or 'circuit' not in data:
                return jsonify({"error": "Valid circuit JSON must be provided"}), 400
                
            # Convert web dashboard format to backend format
            circuit_data = data['circuit']
            print(f"📊 Circuit data received: {circuit_data}")
            
            # Create circuit directly instead of using from_dict
            from quantum_memory_compiler.core.qubit import Qubit
            from quantum_memory_compiler.core.gate import Gate, GateType
            
            print("🔧 Imported Gate and GateType successfully")
            
            qubits_count = circuit_data.get('qubits', circuit_data.get('width', 2))
            circuit_name = circuit_data.get('name', 'Unnamed Circuit')
            
            print(f"🔧 Creating circuit: name={circuit_name}, qubits={qubits_count}")
            
            # Create circuit with qubits
            circuit = Circuit()
            circuit.name = circuit_name  # Set name after creation
            qubits = [Qubit(i) for i in range(qubits_count)]  # Use integer IDs
            for qubit in qubits:
                circuit.add_qubit(qubit)
            
            print(f"🔧 Circuit created with {len(circuit.qubits)} qubits")
            
            # Add gates
            for gate_data in circuit_data.get('gates', []):
                gate_type_str = gate_data.get('type')
                gate_qubits = gate_data.get('qubits', [])
                gate_params = gate_data.get('parameters', gate_data.get('params', []))
                
                print(f"🔧 Processing gate: {gate_type_str} on qubits {gate_qubits}")
                
                if gate_type_str and gate_qubits:
                    # Convert string gate type to GateType enum
                    try:
                        gate_type = getattr(GateType, gate_type_str.upper())
                        print(f"🔧 Converted gate type: {gate_type_str} -> {gate_type}")
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
                print("🔧 Adding automatic measurements to all qubits for compilation")
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
            if use_noise:
                noise_model = NoiseModel()
            
            # Simulator
            simulator = Simulator(noise_model=noise_model, enable_error_mitigation=use_mitigation)
            
            # Run simulation
            print(f"🔬 About to run simulation with {shots} shots")
            sys.stdout.flush()
            
            # Check simulator before running
            print(f"🔬 Simulator object: {simulator}")
            print(f"🔬 Simulator type: {type(simulator)}")
            sys.stdout.flush()
            
            results = simulator.run(circuit, shots=shots)
            
            print(f"🔬 Simulation returned: {results}")
            print(f"🔬 Type of results: {type(results)}")
            print(f"🔬 Results is None: {results is None}")
            print(f"🔬 Results length: {len(results) if results else 'N/A'}")
            sys.stdout.flush()
            
            # Also check simulator.results attribute
            print(f"🔬 Simulator.results: {simulator.results}")
            print(f"🔬 Simulator.results type: {type(simulator.results)}")
            sys.stdout.flush()
            
            print("✅ Simulation completed successfully")
            print(f"🔬 Raw simulation results: {results}")
            sys.stdout.flush()
            
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

    @app.route('/api/circuit/compile', methods=['POST'])
    def compile_circuit():
        """
        Circuit compilation API endpoint
        
        Request JSON:
        {
            "circuit": {...},   // Circuit JSON object
            "strategy": "balanced",  // Compilation strategy
            "use_meta_compiler": false  // Use meta-compiler
        }
        
        Returns:
            JSON: Compiled circuit and metrics
        """
        try:
            print("⚙️ compile_circuit API endpoint called")
            data = request.json
            if not data or 'circuit' not in data:
                return jsonify({"error": "Valid circuit JSON must be provided"}), 400
                
            # Convert web dashboard format to backend format
            circuit_data = data['circuit']
            print(f"📊 Circuit data received: {circuit_data}")
            
            # Create circuit directly instead of using from_dict
            from quantum_memory_compiler.core.qubit import Qubit
            from quantum_memory_compiler.core.gate import Gate, GateType
            
            qubits_count = circuit_data.get('qubits', circuit_data.get('width', 2))
            circuit_name = circuit_data.get('name', 'Unnamed Circuit')
            
            # Create circuit with qubits
            circuit = Circuit()
            circuit.name = circuit_name  # Set name after creation
            qubits = [Qubit(i) for i in range(qubits_count)]  # Use integer IDs
            for qubit in qubits:
                circuit.add_qubit(qubit)
            
            # Add gates
            for gate_data in circuit_data.get('gates', []):
                gate_type_str = gate_data.get('type')
                gate_qubits = gate_data.get('qubits', [])
                gate_params = gate_data.get('parameters', gate_data.get('params', []))
                
                if gate_type_str and gate_qubits:
                    # Convert string gate type to GateType enum
                    try:
                        gate_type = getattr(GateType, gate_type_str.upper())
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
                print("🔧 Adding automatic measurements to all qubits for compilation")
                for i, qubit in enumerate(qubits):
                    circuit.add_gate(GateType.MEASURE, qubit, parameters=[i])
                print(f"🔧 Added {len(qubits)} measurement gates")
            
            # Compilation parameters
            strategy = data.get('strategy', 'balanced')
            use_meta = data.get('use_meta_compiler', False)
            
            print(f"🔧 Compilation parameters: strategy={strategy}, meta={use_meta}")
            
            # Create memory hierarchy (default)
            from quantum_memory_compiler.memory.hierarchy import MemoryHierarchy
            memory = MemoryHierarchy(l1_capacity=10, l2_capacity=20, l3_capacity=50)
            
            # Compiler
            if use_meta and HAS_META_COMPILER:
                compiler = MetaCompiler(memory)
            else:
                compiler = Compiler(memory)
            
            # Compile
            compiled_circuit = compiler.compile(circuit)
            
            print("✅ Compilation completed successfully")
            
            # Metrics
            metrics = {
                "original_qubits": circuit.width,
                "compiled_qubits": compiled_circuit.width,
                "original_gates": len(circuit.gates),
                "compiled_gates": len(compiled_circuit.gates),
                "original_depth": circuit.depth,
                "compiled_depth": compiled_circuit.depth,
                "strategy": strategy,
                "meta_compiler_used": use_meta and HAS_META_COMPILER
            }
            
            return jsonify({
                "success": True,
                "compiled_circuit": compiled_circuit.to_dict(),
                "metrics": metrics
            })
                
        except Exception as e:
            print(f"❌ Compilation error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route('/api/memory/profile', methods=['POST'])
    def profile_memory():
        """
        Memory profiling API endpoint
        
        Request JSON:
        {
            "circuit": {...}  // Circuit JSON object
        }
        
        Returns:
            JSON: Profiling results and graph (base64)
        """
        try:
            print("💾 Memory profiling API endpoint called")
            data = request.json
            if not data or 'circuit' not in data:
                return jsonify({"error": "Valid circuit JSON must be provided"}), 400
                
            # Create circuit from JSON
            circuit_data = data['circuit']
            
            # Create circuit directly instead of using from_dict
            from quantum_memory_compiler.core.qubit import Qubit
            from quantum_memory_compiler.core.gate import Gate, GateType
            
            qubits_count = circuit_data.get('qubits', circuit_data.get('width', 2))
            circuit_name = circuit_data.get('name', 'Unnamed Circuit')
            
            # Create circuit with qubits
            circuit = Circuit()
            circuit.name = circuit_name  # Set name after creation
            qubits = [Qubit(i) for i in range(qubits_count)]  # Use integer IDs
            for qubit in qubits:
                circuit.add_qubit(qubit)
            
            # Add gates
            for gate_data in circuit_data.get('gates', []):
                gate_type_str = gate_data.get('type')
                gate_qubits = gate_data.get('qubits', [])
                gate_params = gate_data.get('parameters', gate_data.get('params', []))
                
                if gate_type_str and gate_qubits:
                    # Convert string gate type to GateType enum
                    try:
                        gate_type = getattr(GateType, gate_type_str.upper())
                    except AttributeError:
                        print(f"⚠️  Unknown gate type: {gate_type_str}, skipping...")
                        continue
                    
                    # Map qubit indices to actual qubit objects
                    target_qubits = [qubits[i] for i in gate_qubits if i < len(qubits)]
                    
                    if target_qubits:
                        gate = Gate(gate_type, target_qubits, parameters=gate_params)
                        circuit.add_gate(gate)
            
            print(f"✅ Circuit created successfully, width: {circuit.width}, gates: {len(circuit.gates)}")
            
            # Create profiler
            profiler = MemoryProfiler()
            
            # Create profile
            profile = profiler.profile_circuit_execution(circuit)
            
            # Analyze results
            bottlenecks = profiler.analyze_bottlenecks(profile)
            recommendations = profiler.recommend_optimizations(profile)
            
            # Helper function to convert numpy values to Python native values
            def convert_numpy_to_python(obj):
                import numpy as np
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {k: convert_numpy_to_python(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy_to_python(i) for i in obj]
                else:
                    return obj
            
            # Summary results
            profile_results = {
                "circuit_name": profile.circuit_name,
                "qubit_count": sum(profile.qubit_counts.values()),
                "operation_counts": {k.name: v for k, v in profile.operation_counts.items()},
                "avg_qubit_lifetime": profile.get_average_qubit_lifetime(),
                "usage_stats": profile.get_memory_usage_stats(),
                "bottlenecks": bottlenecks,
                "hotspots": profile.hotspots,
                "recommendations": recommendations
            }
            
            # Convert numpy values
            profile_results = convert_numpy_to_python(profile_results)
            
            # Create profile visualization
            img_buf = BytesIO()
            profile.plot_memory_profile(img_buf)
            img_buf.seek(0)
            
            # Encode to base64
            encoded = base64.b64encode(img_buf.read()).decode('utf-8')
            
            print("✅ Profiling successful, returning results")
            return jsonify({
                "profile_results": profile_results,
                "image": encoded,
                "format": "base64"
            })
                
        except Exception as e:
            print(f"❌ Profiling error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route('/api/examples', methods=['GET'])
    def list_examples():
        """
        Lists available examples
        
        Returns:
            JSON: List of available examples
        """
        try:
            print("📚 list_examples API endpoint called")
            # Examples directory
            examples_dir = Path(__file__).parent / "examples"
            
            # Find example files
            examples = []
            for example_file in examples_dir.glob("*.py"):
                if example_file.name != "__init__.py":
                    examples.append({
                        "name": example_file.stem,
                        "path": str(example_file.relative_to(Path(__file__).parent.parent)),
                        "description": get_example_description(example_file)
                    })
            
            print(f"✅ Found {len(examples)} examples")
            return jsonify({"examples": examples})
                
        except Exception as e:
            print(f"❌ Examples listing error: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/circuit/upload', methods=['POST'])
    def upload_circuit():
        """
        Upload circuit file (JSON, QASM, etc.)
        
        Request: Multipart form data with file
        
        Returns:
            JSON: Uploaded circuit data or error message
        """
        try:
            print("📤 upload_circuit API endpoint called")
            
            if 'file' not in request.files:
                return jsonify({"error": "No file provided"}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            # Read file content
            file_content = file.read().decode('utf-8')
            filename = file.filename
            file_ext = Path(filename).suffix.lower()
            
            print(f"📁 Processing file: {filename} ({file_ext})")
            
            circuit_data = None
            
            if file_ext == '.json':
                # JSON circuit file
                try:
                    circuit_data = json.loads(file_content)
                    print("✅ JSON circuit loaded successfully")
                except json.JSONDecodeError as e:
                    return jsonify({"error": f"Invalid JSON format: {e}"}), 400
                    
            elif file_ext == '.qasm':
                # QASM file - basic parsing
                try:
                    # Simple QASM parser (basic implementation)
                    lines = file_content.strip().split('\n')
                    qubits = 0
                    gates = []
                    
                    for line in lines:
                        line = line.strip()
                        if line.startswith('qreg'):
                            # Extract qubit count
                            qubits = int(line.split('[')[1].split(']')[0])
                        elif line and not line.startswith('//') and not line.startswith('OPENQASM'):
                            # Basic gate parsing
                            if 'h ' in line:
                                qubit = int(line.split('[')[1].split(']')[0])
                                gates.append({"type": "H", "qubits": [qubit], "parameters": []})
                            elif 'x ' in line:
                                qubit = int(line.split('[')[1].split(']')[0])
                                gates.append({"type": "X", "qubits": [qubit], "parameters": []})
                            elif 'cx ' in line:
                                parts = line.split('[')
                                control = int(parts[1].split(']')[0])
                                target = int(parts[2].split(']')[0])
                                gates.append({"type": "CNOT", "qubits": [control, target], "parameters": []})
                    
                    circuit_data = {
                        "name": Path(filename).stem,
                        "width": qubits,
                        "gates": gates,
                        "measurements": []
                    }
                    print("✅ QASM circuit parsed successfully")
                    
                except Exception as e:
                    return jsonify({"error": f"QASM parsing error: {e}"}), 400
                    
            else:
                return jsonify({"error": f"Unsupported file format: {file_ext}"}), 400
            
            # Store in session if available
            session_id = request.headers.get('X-Session-ID')
            if session_id and session_id in active_sessions:
                active_sessions[session_id]['circuits'].append(circuit_data)
                active_sessions[session_id]['last_activity'] = __import__('datetime').datetime.now()
            
            return jsonify({
                "circuit": circuit_data,
                "filename": filename,
                "format": file_ext,
                "message": "Circuit uploaded successfully"
            })
                
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/circuit/download', methods=['POST'])
    def download_circuit():
        """
        Download circuit as file (JSON, QASM, Python)
        
        Request JSON:
        {
            "circuit": {...},  // Circuit JSON object
            "format": "json",  // Output format: json, qasm, python
            "filename": "my_circuit"  // Optional filename
        }
        
        Returns:
            File download or error message
        """
        try:
            print("📥 download_circuit API endpoint called")
            data = request.json
            
            if not data or 'circuit' not in data:
                return jsonify({"error": "Valid circuit JSON must be provided"}), 400
            
            circuit_data = data['circuit']
            format_type = data.get('format', 'json').lower()
            filename = data.get('filename', 'quantum_circuit')
            
            print(f"📁 Generating {format_type} file for download")
            
            if format_type == 'json':
                # JSON format
                content = json.dumps(circuit_data, indent=2)
                mimetype = 'application/json'
                extension = '.json'
                
            elif format_type == 'qasm':
                # QASM format
                lines = ['OPENQASM 2.0;', 'include "qelib1.inc";', '']
                lines.append(f'qreg q[{circuit_data.get("width", 2)}];')
                lines.append('creg c[{}];'.format(circuit_data.get("width", 2)))
                lines.append('')
                
                for gate in circuit_data.get('gates', []):
                    gate_type = gate.get('type', '').upper()
                    qubits = gate.get('qubits', [])
                    params = gate.get('parameters', [])
                    
                    if gate_type == 'H':
                        lines.append(f'h q[{qubits[0]}];')
                    elif gate_type == 'X':
                        lines.append(f'x q[{qubits[0]}];')
                    elif gate_type == 'Y':
                        lines.append(f'y q[{qubits[0]}];')
                    elif gate_type == 'Z':
                        lines.append(f'z q[{qubits[0]}];')
                    elif gate_type == 'CNOT':
                        lines.append(f'cx q[{qubits[0]}],q[{qubits[1]}];')
                    elif gate_type == 'RX' and params:
                        lines.append(f'rx({params[0]}) q[{qubits[0]}];')
                    elif gate_type == 'RY' and params:
                        lines.append(f'ry({params[0]}) q[{qubits[0]}];')
                    elif gate_type == 'RZ' and params:
                        lines.append(f'rz({params[0]}) q[{qubits[0]}];')
                
                # Add measurements
                for i in range(circuit_data.get("width", 2)):
                    lines.append(f'measure q[{i}] -> c[{i}];')
                
                content = '\n'.join(lines)
                mimetype = 'text/plain'
                extension = '.qasm'
                
            elif format_type == 'python':
                # Python code format
                lines = ['# Quantum Circuit - Generated by Quantum Memory Compiler', 
                        '# Developer: kappasutra', '', 
                        'from quantum_memory_compiler.core.circuit import Circuit',
                        'from quantum_memory_compiler.core.gates import *', '', 
                        '# Create circuit']
                
                circuit_name = circuit_data.get('name', 'quantum_circuit').replace(' ', '_')
                lines.append(f'{circuit_name} = Circuit({circuit_data.get("width", 2)})')
                lines.append('')
                
                for gate in circuit_data.get('gates', []):
                    gate_type = gate.get('type', '')
                    qubits = gate.get('qubits', [])
                    params = gate.get('parameters', [])
                    
                    if gate_type == 'H':
                        lines.append(f'{circuit_name}.add_gate(HGate(), {qubits[0]})')
                    elif gate_type == 'X':
                        lines.append(f'{circuit_name}.add_gate(XGate(), {qubits[0]})')
                    elif gate_type == 'Y':
                        lines.append(f'{circuit_name}.add_gate(YGate(), {qubits[0]})')
                    elif gate_type == 'Z':
                        lines.append(f'{circuit_name}.add_gate(ZGate(), {qubits[0]})')
                    elif gate_type == 'CNOT':
                        lines.append(f'{circuit_name}.add_gate(CNOTGate(), {qubits[0]}, {qubits[1]})')
                    elif gate_type == 'RX' and params:
                        lines.append(f'{circuit_name}.add_gate(RXGate({params[0]}), {qubits[0]})')
                    elif gate_type == 'RY' and params:
                        lines.append(f'{circuit_name}.add_gate(RYGate({params[0]}), {qubits[0]})')
                    elif gate_type == 'RZ' and params:
                        lines.append(f'{circuit_name}.add_gate(RZGate({params[0]}), {qubits[0]})')
                
                lines.extend(['', '# Visualize circuit', f'{circuit_name}.visualize()', 
                             '', '# Simulate circuit', 
                             'from quantum_memory_compiler.simulation.simulator import Simulator',
                             'simulator = Simulator()', f'results = simulator.run({circuit_name})',
                             'print("Simulation results:", results)'])
                
                content = '\n'.join(lines)
                mimetype = 'text/x-python'
                extension = '.py'
                
            else:
                return jsonify({"error": f"Unsupported format: {format_type}"}), 400
            
            # Create temporary file
            temp_file = os.path.join(temp_dir, f"{filename}{extension}")
            with open(temp_file, 'w') as f:
                f.write(content)
            
            print(f"✅ File generated successfully: {filename}{extension}")
            return send_file(temp_file, as_attachment=True, 
                           download_name=f"{filename}{extension}", 
                           mimetype=mimetype)
                
        except Exception as e:
            print(f"❌ Download error: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/acceleration/status', methods=['GET'])
    def get_acceleration_status():
        """Get GPU acceleration status and capabilities"""
        try:
            status = acceleration_manager.get_acceleration_status()
            return jsonify({
                'success': True,
                'status': status,
                'timestamp': time_module.time()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/acceleration/analyze', methods=['POST'])
    def analyze_circuit_acceleration():
        """Analyze circuit for acceleration optimization"""
        try:
            data = request.get_json()
            
            if 'circuit' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Circuit data required'
                }), 400
            
            # Create circuit from data
            circuit_data = data['circuit']
            circuit = Circuit(circuit_data.get('width', 2))
            circuit.name = circuit_data.get('name', 'api_circuit')
            
            # Add gates (simplified)
            for gate_data in circuit_data.get('gates', []):
                # This would need proper gate reconstruction
                pass
            
            # Analyze circuit
            analysis = acceleration_manager.analyze_circuit(circuit)
            
            return jsonify({
                'success': True,
                'analysis': analysis,
                'timestamp': time_module.time()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/acceleration/simulate', methods=['POST'])
    def accelerated_simulation():
        """Run accelerated quantum circuit simulation"""
        try:
            data = request.get_json()
            
            if 'circuit' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Circuit data required'
                }), 400
            
            # Extract parameters
            circuit_data = data['circuit']
            shots = data.get('shots', 1024)
            method = data.get('method', 'auto')
            optimize_memory = data.get('optimize_memory', True)
            
            # Create circuit
            circuit = Circuit(circuit_data.get('width', 2))
            circuit.name = circuit_data.get('name', 'api_circuit')
            
            # Add gates (simplified)
            for gate_data in circuit_data.get('gates', []):
                # This would need proper gate reconstruction
                pass
            
            # Run accelerated simulation
            results = acceleration_manager.simulate_circuit(
                circuit=circuit,
                shots=shots,
                method=method,
                optimize_memory=optimize_memory
            )
            
            return jsonify({
                'success': True,
                'results': results,
                'timestamp': time_module.time()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/acceleration/benchmark', methods=['POST'])
    def run_acceleration_benchmark():
        """Run comprehensive acceleration benchmark"""
        try:
            data = request.get_json() or {}
            
            # Extract benchmark parameters
            qubit_range = data.get('qubit_range', [4, 6])
            gate_counts = data.get('gate_counts', [50, 100])
            shots = data.get('shots', 100)
            
            # Run benchmark
            benchmark_results = acceleration_manager.benchmark_acceleration(
                qubit_range=qubit_range,
                gate_counts=gate_counts,
                shots=shots
            )
            
            return jsonify({
                'success': True,
                'benchmark_results': benchmark_results,
                'timestamp': time_module.time()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/acceleration/memory/report', methods=['GET'])
    def get_memory_report():
        """Get comprehensive memory usage report"""
        try:
            report = acceleration_manager.memory_optimizer.get_memory_report()
            
            return jsonify({
                'success': True,
                'memory_report': report,
                'timestamp': time_module.time()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/acceleration/memory/cleanup', methods=['POST'])
    def cleanup_memory():
        """Clean up GPU memory"""
        try:
            data = request.get_json() or {}
            force_gc = data.get('force_gc', True)
            
            cleanup_stats = acceleration_manager.memory_optimizer.cleanup_memory(force_gc)
            
            return jsonify({
                'success': True,
                'cleanup_stats': cleanup_stats,
                'timestamp': time_module.time()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # WebSocket events for acceleration
    @socketio.on('acceleration_status_request')
    def handle_acceleration_status_request():
        """Handle real-time acceleration status requests"""
        try:
            status = acceleration_manager.get_acceleration_status()
            emit('acceleration_status_update', {
                'status': status,
                'timestamp': time_module.time()
            })
        except Exception as e:
            emit('acceleration_error', {'error': str(e)})

    @socketio.on('start_benchmark')
    def handle_start_benchmark(data):
        """Handle real-time benchmark execution"""
        try:
            # Extract parameters
            qubit_range = data.get('qubit_range', [4, 6])
            gate_counts = data.get('gate_counts', [50])
            shots = data.get('shots', 100)
            
            # Emit benchmark start
            emit('benchmark_started', {
                'message': 'Benchmark started',
                'parameters': {
                    'qubit_range': qubit_range,
                    'gate_counts': gate_counts,
                    'shots': shots
                }
            })
            
            # Run benchmark (this would ideally be in a separate thread)
            benchmark_results = acceleration_manager.benchmark_acceleration(
                qubit_range=qubit_range,
                gate_counts=gate_counts,
                shots=shots
            )
            
            # Emit results
            emit('benchmark_completed', {
                'results': benchmark_results,
                'timestamp': time_module.time()
            })
            
        except Exception as e:
            emit('benchmark_error', {'error': str(e)})

    # IBM Quantum Integration endpoints
    @app.route('/api/ibm/backends', methods=['GET'])
    def get_ibm_backends():
        """Get available IBM Quantum backends"""
        try:
            from quantum_memory_compiler.integration import IBMQuantumProvider
            
            # Get token from request or environment
            token = request.args.get('token') or os.environ.get('IBM_QUANTUM_TOKEN')
            
            provider = IBMQuantumProvider(token=token)
            backends = provider.get_backends()
            
            # Convert to JSON-serializable format
            backend_list = []
            for backend in backends:
                backend_list.append({
                    'name': backend.name,
                    'type': backend.backend_type.value,
                    'num_qubits': backend.num_qubits,
                    'coupling_map': backend.coupling_map,
                    'basis_gates': backend.basis_gates,
                    'max_shots': backend.max_shots,
                    'simulator': backend.simulator,
                    'operational': backend.operational,
                    'pending_jobs': backend.pending_jobs,
                    'least_busy': backend.least_busy
                })
            
            return jsonify({
                'success': True,
                'backends': backend_list,
                'connected': provider.connected,
                'count': len(backend_list)
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'backends': []
            }), 500

    @app.route('/api/ibm/execute', methods=['POST'])
    def execute_on_ibm():
        """Execute circuit on IBM Quantum backend"""
        try:
            data = request.json
            if not data or 'circuit' not in data:
                return jsonify({"error": "Valid circuit JSON must be provided"}), 400
            
            # Get parameters
            backend_name = data.get('backend', 'qasm_simulator')
            shots = data.get('shots', 1024)
            optimization_level = data.get('optimization_level', 1)
            monitor = data.get('monitor', False)
            token = data.get('token') or request.headers.get('X-IBM-Token') or os.environ.get('IBM_QUANTUM_TOKEN')
            
            print(f"🔗 IBM Quantum execution request:")
            print(f"   Backend: {backend_name}")
            print(f"   Shots: {shots}")
            print(f"   Optimization: {optimization_level}")
            print(f"   Token provided: {'Yes' if token else 'No'}")
            
            # Convert circuit data to proper format
            circuit_data = data['circuit']
            
            # Create a simple circuit for IBM Quantum execution
            try:
                import qiskit
                from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
                
                # Create Qiskit circuit directly
                num_qubits = circuit_data.get('qubits', circuit_data.get('width', 2))
                qc = QuantumCircuit(num_qubits, num_qubits)
                
                # Add gates from circuit data
                for gate in circuit_data.get('gates', []):
                    gate_type = gate.get('type', '').upper()
                    qubits = gate.get('qubits', [])
                    params = gate.get('parameters', gate.get('params', []))
                    
                    try:
                        if gate_type == 'H' and len(qubits) >= 1:
                            qc.h(qubits[0])
                        elif gate_type == 'X' and len(qubits) >= 1:
                            qc.x(qubits[0])
                        elif gate_type == 'Y' and len(qubits) >= 1:
                            qc.y(qubits[0])
                        elif gate_type == 'Z' and len(qubits) >= 1:
                            qc.z(qubits[0])
                        elif gate_type in ['CNOT', 'CX'] and len(qubits) >= 2:
                            qc.cx(qubits[0], qubits[1])
                        elif gate_type == 'CZ' and len(qubits) >= 2:
                            qc.cz(qubits[0], qubits[1])
                        elif gate_type == 'SWAP' and len(qubits) >= 2:
                            qc.swap(qubits[0], qubits[1])
                        elif gate_type == 'RX' and len(qubits) >= 1 and len(params) >= 1:
                            qc.rx(params[0], qubits[0])
                        elif gate_type == 'RY' and len(qubits) >= 1 and len(params) >= 1:
                            qc.ry(params[0], qubits[0])
                        elif gate_type == 'RZ' and len(qubits) >= 1 and len(params) >= 1:
                            qc.rz(params[0], qubits[0])
                        elif gate_type == 'S' and len(qubits) >= 1:
                            qc.s(qubits[0])
                        elif gate_type == 'T' and len(qubits) >= 1:
                            qc.t(qubits[0])
                    except Exception as gate_error:
                        print(f"⚠️  Error adding gate {gate_type}: {gate_error}")
                        continue
                
                # Add measurements
                measurements = circuit_data.get('measurements', [])
                if measurements:
                    for measurement in measurements:
                        qubit_idx = measurement.get('qubit', 0)
                        bit_idx = measurement.get('classical_bit', qubit_idx)
                        if qubit_idx < num_qubits and bit_idx < num_qubits:
                            qc.measure(qubit_idx, bit_idx)
                else:
                    # Add measurements for all qubits if none specified
                    qc.measure_all()
                
                print(f"✅ Qiskit circuit created with {num_qubits} qubits and {len(qc.data)} operations")
                
                # Try to use IBM Quantum if token is provided
                if token:
                    try:
                        from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
                        from qiskit import transpile
                        
                        # Initialize IBM Quantum service
                        service = QiskitRuntimeService(token=token)
                        
                        # Get backend
                        if backend_name in ['qasm_simulator', 'statevector_simulator']:
                            # Use local simulator for simulator backends
                            from qiskit_aer import AerSimulator
                            if backend_name == 'statevector_simulator':
                                backend = AerSimulator(method='statevector')
                            else:
                                backend = AerSimulator()
                            
                            # Execute locally using new API
                            job = backend.run(qc, shots=shots)
                            result = job.result()
                            counts = result.get_counts()
                            
                            return jsonify({
                                'success': True,
                                'job_id': f'local_{int(time_module.time())}',
                                'status': 'COMPLETED',
                                'backend': backend_name,
                                'shots': shots,
                                'results': counts,
                                'execution_time': 0.1,
                                'queue_time': 0.0,
                                'error_message': None,
                                'execution_type': 'local_simulator'
                            })
                        else:
                            # Try to get real IBM backend
                            try:
                                backend = service.backend(backend_name)
                                
                                # Transpile for the backend
                                transpiled = transpile(qc, backend=backend, optimization_level=optimization_level)
                                
                                # Use Sampler primitive for execution
                                sampler = Sampler(backend=backend)
                                job = sampler.run([transpiled], shots=shots)
                                
                                if monitor:
                                    print(f"🔄 Job submitted to {backend_name}, monitoring...")
                                
                                result = job.result()
                                counts = result[0].data.meas.get_counts()
                                
                                return jsonify({
                                    'success': True,
                                    'job_id': job.job_id,
                                    'status': 'COMPLETED',
                                    'backend': backend_name,
                                    'shots': shots,
                                    'results': counts,
                                    'execution_time': 1.0,
                                    'queue_time': 0.0,
                                    'error_message': None,
                                    'execution_type': 'ibm_quantum'
                                })
                                
                            except Exception as ibm_error:
                                print(f"⚠️  IBM Quantum backend error: {ibm_error}")
                                # Fallback to local simulation
                                from qiskit_aer import AerSimulator
                                backend = AerSimulator()
                                
                                job = backend.run(qc, shots=shots)
                                result = job.result()
                                counts = result.get_counts()
                                
                                return jsonify({
                                    'success': True,
                                    'job_id': f'fallback_{int(time_module.time())}',
                                    'status': 'COMPLETED',
                                    'backend': f'{backend_name}_fallback',
                                    'shots': shots,
                                    'results': counts,
                                    'execution_time': 0.1,
                                    'queue_time': 0.0,
                                    'error_message': f'IBM backend unavailable: {str(ibm_error)}',
                                    'execution_type': 'fallback_simulator'
                                })
                                
                    except ImportError as import_error:
                        print(f"⚠️  IBM Quantum Runtime not available: {import_error}")
                        # Fallback to Aer simulator
                        from qiskit_aer import AerSimulator
                        backend = AerSimulator()
                        job = backend.run(qc, shots=shots)
                        result = job.result()
                        counts = result.get_counts()
                        
                        return jsonify({
                            'success': True,
                            'job_id': f'aer_{int(time_module.time())}',
                            'status': 'COMPLETED',
                            'backend': backend_name,
                            'shots': shots,
                            'results': counts,
                            'execution_time': 0.1,
                            'queue_time': 0.0,
                            'error_message': 'IBM Quantum Runtime not available, using local simulator',
                            'execution_type': 'aer_simulator'
                        })
                        
                else:
                    # No token provided, use local simulation
                    print("⚠️  No IBM token provided, using local simulation")
                    from qiskit_aer import AerSimulator
                    backend = AerSimulator()
                    job = backend.run(qc, shots=shots)
                    result = job.result()
                    counts = result.get_counts()
                    
                    return jsonify({
                        'success': True,
                        'job_id': f'local_{int(time_module.time())}',
                        'status': 'COMPLETED',
                        'backend': backend_name,
                        'shots': shots,
                        'results': counts,
                        'execution_time': 0.1,
                        'queue_time': 0.0,
                        'error_message': 'No IBM token provided',
                        'execution_type': 'local_simulator'
                    })
                
            except ImportError:
                # Qiskit not available, use simple simulation
                print("⚠️  Qiskit not available, using simple simulation")
                import random
                
                num_qubits = circuit_data.get('qubits', circuit_data.get('width', 2))
                results = {}
                
                # Generate random results based on circuit
                for _ in range(shots):
                    bitstring = ''.join(random.choice(['0', '1']) for _ in range(num_qubits))
                    results[bitstring] = results.get(bitstring, 0) + 1
                
                return jsonify({
                    'success': True,
                    'job_id': f'sim_{int(time_module.time())}',
                    'status': 'COMPLETED',
                    'backend': backend_name,
                    'shots': shots,
                    'results': results,
                    'execution_time': 0.1,
                    'queue_time': 0.0,
                    'error_message': 'Qiskit not available',
                    'execution_type': 'simple_simulator'
                })
            
        except Exception as e:
            print(f"❌ IBM Quantum execution error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e),
                'execution_type': 'error'
            }), 500

    @app.route('/api/ibm/transpile', methods=['POST'])
    def transpile_for_ibm():
        """Transpile circuit for IBM Quantum backend"""
        try:
            data = request.json
            if not data or 'circuit' not in data:
                return jsonify({"error": "Valid circuit JSON must be provided"}), 400
            
            backend_name = data.get('backend', 'qasm_simulator')
            optimization_level = data.get('optimization_level', 1)
            
            print(f"🔄 Transpiling circuit for IBM backend: {backend_name}")
            
            # Convert circuit
            circuit_data = data['circuit']
            converted_data = {
                'name': circuit_data.get('name', 'transpile_circuit'),
                'qubits': circuit_data.get('width', circuit_data.get('qubits', 0)),
                'gates': [],
                'measurements': circuit_data.get('measurements', [])
            }
            
            for gate in circuit_data.get('gates', []):
                converted_gate = {
                    'type': gate.get('type'),
                    'qubits': gate.get('qubits', []),
                    'params': gate.get('parameters', gate.get('params', []))
                }
                converted_data['gates'].append(converted_gate)
            
            circuit = Circuit.from_dict(converted_data)
            
            # Transpile using Qiskit bridge
            from quantum_memory_compiler.integration import QiskitBridge
            
            bridge = QiskitBridge()
            transpiled_circuit = bridge.transpile_for_backend(
                circuit, 
                backend_name, 
                optimization_level
            )
            
            # Convert back to JSON
            result_data = transpiled_circuit.to_dict()
            
            return jsonify({
                'success': True,
                'original_circuit': {
                    'qubits': circuit.width,
                    'gates': len(circuit.gates),
                    'depth': circuit.depth
                },
                'transpiled_circuit': result_data,
                'optimization_level': optimization_level,
                'backend': backend_name
            })
            
        except Exception as e:
            print(f"❌ Transpilation error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/ibm/status', methods=['GET'])
    def get_ibm_status():
        """Get IBM Quantum integration status"""
        try:
            # Check if Qiskit is available
            try:
                import qiskit
                qiskit_version = qiskit.__version__
                qiskit_available = True
            except ImportError:
                qiskit_version = None
                qiskit_available = False
            
            # Check token
            token = request.args.get('token') or os.environ.get('IBM_QUANTUM_TOKEN')
            token_provided = token is not None
            
            # Try to connect if token provided
            connected = False
            if token_provided and qiskit_available:
                try:
                    from quantum_memory_compiler.integration import IBMQuantumProvider
                    provider = IBMQuantumProvider(token=token)
                    connected = provider.connected
                except:
                    connected = False
            
            return jsonify({
                'qiskit_available': qiskit_available,
                'qiskit_version': qiskit_version,
                'token_provided': token_provided,
                'connected': connected,
                'integration_ready': qiskit_available and token_provided
            })
            
        except Exception as e:
            return jsonify({
                'error': str(e),
                'qiskit_available': False,
                'connected': False,
                'integration_ready': False
            }), 500

    # Enhanced Caching System endpoints
    @app.route('/api/cache/stats', methods=['GET'])
    def get_cache_stats():
        """Get cache statistics"""
        try:
            from .caching import CacheManager
            
            # Initialize cache manager if not exists
            if not hasattr(app, 'cache_manager'):
                app.cache_manager = CacheManager()
            
            stats = app.cache_manager.get_stats()
            
            # Convert dataclass to dict for JSON serialization
            stats_dict = {}
            for cache_type, stat in stats.items():
                stats_dict[cache_type] = {
                    'cache_type': stat.cache_type,
                    'total_entries': stat.total_entries,
                    'total_size_mb': stat.total_size_mb,
                    'hit_rate': stat.hit_rate,
                    'miss_rate': stat.miss_rate,
                    'avg_access_time_ms': stat.avg_access_time_ms,
                    'last_cleanup': stat.last_cleanup,
                    'memory_usage_mb': stat.memory_usage_mb
                }
            
            return jsonify({
                'success': True,
                'cache_stats': stats_dict,
                'timestamp': time_module.time()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/cache/clear', methods=['POST'])
    def clear_cache():
        """Clear cache"""
        try:
            data = request.get_json() or {}
            cache_type = data.get('cache_type')  # None for all caches
            
            from .caching import CacheManager, CacheType
            
            # Initialize cache manager if not exists
            if not hasattr(app, 'cache_manager'):
                app.cache_manager = CacheManager()
            
            # Convert string to enum if provided
            cache_type_enum = None
            if cache_type:
                try:
                    cache_type_enum = CacheType(cache_type)
                except ValueError:
                    return jsonify({
                        'success': False,
                        'error': f"Invalid cache type: {cache_type}"
                    }), 400
            
            success = app.cache_manager.clear(cache_type_enum)
            
            return jsonify({
                'success': success,
                'message': f"Cache {'cleared' if success else 'clear failed'}",
                'cache_type': cache_type or 'all'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/cache/cleanup', methods=['POST'])
    def cleanup_cache():
        """Clean up expired cache entries"""
        try:
            from .caching import CacheManager
            
            # Initialize cache manager if not exists
            if not hasattr(app, 'cache_manager'):
                app.cache_manager = CacheManager()
            
            removed_count = app.cache_manager.cleanup_expired()
            
            return jsonify({
                'success': True,
                'removed_entries': removed_count,
                'message': f"Cleaned up {removed_count} expired entries"
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/cache/circuit', methods=['GET', 'POST', 'DELETE'])
    def handle_circuit_cache():
        """Handle circuit cache operations"""
        try:
            from .caching import CacheManager, CacheType
            
            # Initialize cache manager if not exists
            if not hasattr(app, 'cache_manager'):
                app.cache_manager = CacheManager()
            
            if request.method == 'GET':
                # Get cached circuit
                circuit_key = request.args.get('key')
                if not circuit_key:
                    return jsonify({'error': 'Circuit key required'}), 400
                
                cached_data = app.cache_manager.get(CacheType.CIRCUIT, circuit_key)
                
                if cached_data:
                    return jsonify({
                        'success': True,
                        'found': True,
                        'circuit': cached_data
                    })
                else:
                    return jsonify({
                        'success': True,
                        'found': False,
                        'message': 'Circuit not found in cache'
                    })
            
            elif request.method == 'POST':
                # Cache circuit
                data = request.get_json()
                if not data or 'key' not in data or 'circuit' not in data:
                    return jsonify({'error': 'Key and circuit data required'}), 400
                
                circuit_key = data['key']
                circuit_data = data['circuit']
                ttl = data.get('ttl')  # Time to live in seconds
                metadata = data.get('metadata', {})
                
                success = app.cache_manager.put(
                    CacheType.CIRCUIT, 
                    circuit_key, 
                    circuit_data,
                    ttl=ttl,
                    metadata=metadata
                )
                
                return jsonify({
                    'success': success,
                    'message': 'Circuit cached successfully' if success else 'Failed to cache circuit'
                })
            
            elif request.method == 'DELETE':
                # Remove circuit from cache
                circuit_key = request.args.get('key')
                if not circuit_key:
                    return jsonify({'error': 'Circuit key required'}), 400
                
                success = app.cache_manager.invalidate(CacheType.CIRCUIT, circuit_key)
                
                return jsonify({
                    'success': success,
                    'message': 'Circuit removed from cache' if success else 'Failed to remove circuit'
                })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/cache/simulation', methods=['GET', 'POST', 'DELETE'])
    def handle_simulation_cache():
        """Handle simulation cache operations"""
        try:
            from .caching import CacheManager, CacheType
            
            # Initialize cache manager if not exists
            if not hasattr(app, 'cache_manager'):
                app.cache_manager = CacheManager()
            
            if request.method == 'GET':
                # Get cached simulation result
                sim_key = request.args.get('key')
                if not sim_key:
                    return jsonify({'error': 'Simulation key required'}), 400
                
                cached_data = app.cache_manager.get(CacheType.SIMULATION, sim_key)
                
                if cached_data:
                    return jsonify({
                        'success': True,
                        'found': True,
                        'simulation_result': cached_data
                    })
                else:
                    return jsonify({
                        'success': True,
                        'found': False,
                        'message': 'Simulation result not found in cache'
                    })
            
            elif request.method == 'POST':
                # Cache simulation result
                data = request.get_json()
                if not data or 'key' not in data or 'result' not in data:
                    return jsonify({'error': 'Key and result data required'}), 400
                
                sim_key = data['key']
                result_data = data['result']
                ttl = data.get('ttl', 3600)  # Default 1 hour TTL for simulation results
                metadata = data.get('metadata', {})
                
                success = app.cache_manager.put(
                    CacheType.SIMULATION, 
                    sim_key, 
                    result_data,
                    ttl=ttl,
                    metadata=metadata
                )
                
                return jsonify({
                    'success': success,
                    'message': 'Simulation result cached successfully' if success else 'Failed to cache result'
                })
            
            elif request.method == 'DELETE':
                # Remove simulation result from cache
                sim_key = request.args.get('key')
                if not sim_key:
                    return jsonify({'error': 'Simulation key required'}), 400
                
                success = app.cache_manager.invalidate(CacheType.SIMULATION, sim_key)
                
                return jsonify({
                    'success': success,
                    'message': 'Simulation result removed from cache' if success else 'Failed to remove result'
                })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

else:
    print("❌ Flask not available. API server cannot be started.")

def get_example_description(example_file: Path) -> str:
    """
    Returns the description of an example file
    
    Args:
        example_file: Example file path
        
    Returns:
        str: File description or empty string
    """
    try:
        with open(example_file, 'r') as f:
            content = f.read(1000)  # Read first 1000 characters
            
        # Look for docstring or comment lines
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                # Multi-line description
                start = i
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().endswith('"""') or lines[j].strip().endswith("'''"):
                        end = j
                        return "\n".join(lines[start:end+1]).strip('"\' \n\t')
            elif line.strip().startswith("#"):
                # Single-line description
                return line.strip("# \t")
                
        return "No description available"
    except:
        return "Description could not be read"

def run_api_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
    """
    Runs the Flask API server with WebSocket support
    
    Args:
        host: Host to bind to (default: "0.0.0.0")
        port: Port to bind to (default: 5000)
        debug: Debug mode (default: False)
    """
    if not HAS_FLASK or not HAS_SOCKETIO:
        print("❌ Flask or SocketIO library not installed. API server cannot be started.")
        print("   Install with: pip install flask flask-cors flask-socketio eventlet")
        return
    
    if app is None:
        print("❌ Flask app could not be created.")
        return
    
    print(f"🚀 Starting API server: http://{host}:{port}")
    print(f"📋 Available API endpoints:")
    print(f"   - GET  /api/info              : Get API information")
    print(f"   - POST /api/circuit/visualize : Visualize circuits")
    print(f"   - POST /api/circuit/simulate  : Simulate circuits")
    print(f"   - POST /api/circuit/compile   : Compile circuits")
    print(f"   - POST /api/memory/profile    : Create memory profiles")
    print(f"   - GET  /api/examples          : List available examples")
    print(f"🔧 Developer: kappasutra")
    
    try:
        # Use Flask run instead of SocketIO run for debugging
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        print(f"   Host: {host}, Port: {port}, Debug: {debug}")
        # Try alternative port
        alt_port = port + 1
        print(f"🔄 Trying alternative port: {alt_port}")
        try:
            app.run(host=host, port=alt_port, debug=debug)
        except Exception as e2:
            print(f"❌ Could not start with alternative port either: {e2}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Quantum Memory Compiler API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host address to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    run_api_server(host=args.host, port=args.port, debug=args.debug) 