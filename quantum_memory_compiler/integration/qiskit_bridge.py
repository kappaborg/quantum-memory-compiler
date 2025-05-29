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
Qiskit Bridge
=============

Bridge for converting between Quantum Memory Compiler circuits and Qiskit circuits.

Developer: kappasutra
"""

import numpy as np
from typing import Dict, List, Optional, Any, Union

try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit.circuit import Parameter
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    print("⚠️  Qiskit not available. Bridge will use fallback mode.")

from ..core.circuit import Circuit
from ..core.gate import GateType


class QiskitConverter:
    """Converter between Quantum Memory Compiler and Qiskit formats"""
    
    # Gate mapping from our format to Qiskit
    GATE_MAPPING = {
        GateType.I: 'id',
        GateType.X: 'x',
        GateType.Y: 'y', 
        GateType.Z: 'z',
        GateType.H: 'h',
        GateType.S: 's',
        GateType.SDG: 'sdg',
        GateType.T: 't',
        GateType.TDG: 'tdg',
        GateType.SX: 'sx',
        GateType.RX: 'rx',
        GateType.RY: 'ry',
        GateType.RZ: 'rz',
        GateType.P: 'p',
        GateType.U1: 'u1',
        GateType.U2: 'u2',
        GateType.U3: 'u3',
        GateType.CNOT: 'cx',
        GateType.CZ: 'cz',
        GateType.SWAP: 'swap',
        GateType.TOFFOLI: 'ccx',
        GateType.CP: 'cp',
        GateType.CRX: 'crx',
        GateType.CRY: 'cry',
        GateType.CRZ: 'crz',
        GateType.ISWAP: 'iswap',
        GateType.MEASURE: 'measure',
        GateType.RESET: 'reset',
        GateType.BARRIER: 'barrier'
    }
    
    @staticmethod
    def to_qiskit(circuit: Circuit) -> 'QuantumCircuit':
        """
        Convert Quantum Memory Compiler circuit to Qiskit circuit
        
        Args:
            circuit: Quantum Memory Compiler circuit
            
        Returns:
            Qiskit QuantumCircuit
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for circuit conversion")
        
        print(f"🔄 Converting circuit '{circuit.name}' to Qiskit format...")
        
        # Create quantum and classical registers
        qreg = QuantumRegister(circuit.width, 'q')
        creg = ClassicalRegister(circuit.width, 'c')
        qiskit_circuit = QuantumCircuit(qreg, creg, name=circuit.name)
        
        # Sort gates by time
        sorted_gates = sorted(circuit.gates, key=lambda g: g.time)
        
        # Convert each gate
        for gate in sorted_gates:
            QiskitConverter._add_gate_to_qiskit(qiskit_circuit, gate, qreg, creg)
        
        print(f"✅ Converted to Qiskit: {qiskit_circuit.num_qubits} qubits, {len(qiskit_circuit.data)} gates")
        return qiskit_circuit
    
    @staticmethod
    def _add_gate_to_qiskit(qiskit_circuit: 'QuantumCircuit', gate, qreg, creg):
        """Add a single gate to Qiskit circuit"""
        gate_type = gate.type
        qubits = [qreg[q.id] for q in gate.qubits]
        params = gate.parameters or []
        
        # Get Qiskit gate name
        qiskit_gate = QiskitConverter.GATE_MAPPING.get(gate_type)
        
        if not qiskit_gate:
            print(f"⚠️  Unsupported gate type: {gate_type}")
            return
        
        try:
            if gate_type == GateType.I:
                qiskit_circuit.id(qubits[0])
            elif gate_type == GateType.X:
                qiskit_circuit.x(qubits[0])
            elif gate_type == GateType.Y:
                qiskit_circuit.y(qubits[0])
            elif gate_type == GateType.Z:
                qiskit_circuit.z(qubits[0])
            elif gate_type == GateType.H:
                qiskit_circuit.h(qubits[0])
            elif gate_type == GateType.S:
                qiskit_circuit.s(qubits[0])
            elif gate_type == GateType.SDG:
                qiskit_circuit.sdg(qubits[0])
            elif gate_type == GateType.T:
                qiskit_circuit.t(qubits[0])
            elif gate_type == GateType.TDG:
                qiskit_circuit.tdg(qubits[0])
            elif gate_type == GateType.SX:
                qiskit_circuit.sx(qubits[0])
            elif gate_type == GateType.RX:
                qiskit_circuit.rx(params[0], qubits[0])
            elif gate_type == GateType.RY:
                qiskit_circuit.ry(params[0], qubits[0])
            elif gate_type == GateType.RZ:
                qiskit_circuit.rz(params[0], qubits[0])
            elif gate_type == GateType.P:
                qiskit_circuit.p(params[0], qubits[0])
            elif gate_type == GateType.U1:
                qiskit_circuit.u1(params[0], qubits[0])
            elif gate_type == GateType.U2:
                qiskit_circuit.u2(params[0], params[1], qubits[0])
            elif gate_type == GateType.U3:
                qiskit_circuit.u3(params[0], params[1], params[2], qubits[0])
            elif gate_type == GateType.CNOT:
                qiskit_circuit.cx(qubits[0], qubits[1])
            elif gate_type == GateType.CZ:
                qiskit_circuit.cz(qubits[0], qubits[1])
            elif gate_type == GateType.SWAP:
                qiskit_circuit.swap(qubits[0], qubits[1])
            elif gate_type == GateType.TOFFOLI:
                qiskit_circuit.ccx(qubits[0], qubits[1], qubits[2])
            elif gate_type == GateType.CP:
                qiskit_circuit.cp(params[0], qubits[0], qubits[1])
            elif gate_type == GateType.CRX:
                qiskit_circuit.crx(params[0], qubits[0], qubits[1])
            elif gate_type == GateType.CRY:
                qiskit_circuit.cry(params[0], qubits[0], qubits[1])
            elif gate_type == GateType.CRZ:
                qiskit_circuit.crz(params[0], qubits[0], qubits[1])
            elif gate_type == GateType.MEASURE:
                # Measurement to classical bit
                classical_bit = params[0] if params else qubits[0].index
                qiskit_circuit.measure(qubits[0], creg[classical_bit])
            elif gate_type == GateType.RESET:
                qiskit_circuit.reset(qubits[0])
            elif gate_type == GateType.BARRIER:
                qiskit_circuit.barrier(qubits)
            else:
                print(f"⚠️  Gate {gate_type} not implemented in converter")
                
        except Exception as e:
            print(f"❌ Error adding gate {gate_type}: {e}")
    
    @staticmethod
    def from_qiskit(qiskit_circuit: 'QuantumCircuit') -> Circuit:
        """
        Convert Qiskit circuit to Quantum Memory Compiler circuit
        
        Args:
            qiskit_circuit: Qiskit QuantumCircuit
            
        Returns:
            Quantum Memory Compiler Circuit
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for circuit conversion")
        
        print(f"🔄 Converting Qiskit circuit to Quantum Memory Compiler format...")
        
        # Create our circuit
        circuit = Circuit(qiskit_circuit.name or "qiskit_circuit")
        
        # Add qubits
        circuit.add_qubits(qiskit_circuit.num_qubits)
        
        # Convert gates
        for instruction, qargs, cargs in qiskit_circuit.data:
            QiskitConverter._add_gate_from_qiskit(circuit, instruction, qargs, cargs)
        
        print(f"✅ Converted from Qiskit: {circuit.width} qubits, {len(circuit.gates)} gates")
        return circuit
    
    @staticmethod
    def _add_gate_from_qiskit(circuit: Circuit, instruction, qargs, cargs):
        """Add a gate from Qiskit instruction to our circuit"""
        gate_name = instruction.name.upper()
        qubit_indices = [q.index for q in qargs]
        params = [float(p) for p in instruction.params] if instruction.params else []
        
        # Map Qiskit gate names to our GateType
        gate_mapping_reverse = {
            'ID': GateType.I,
            'X': GateType.X,
            'Y': GateType.Y,
            'Z': GateType.Z,
            'H': GateType.H,
            'S': GateType.S,
            'SDG': GateType.SDG,
            'T': GateType.T,
            'TDG': GateType.TDG,
            'SX': GateType.SX,
            'RX': GateType.RX,
            'RY': GateType.RY,
            'RZ': GateType.RZ,
            'P': GateType.P,
            'U1': GateType.U1,
            'U2': GateType.U2,
            'U3': GateType.U3,
            'CX': GateType.CNOT,
            'CZ': GateType.CZ,
            'SWAP': GateType.SWAP,
            'CCX': GateType.TOFFOLI,
            'CP': GateType.CP,
            'CRX': GateType.CRX,
            'CRY': GateType.CRY,
            'CRZ': GateType.CRZ,
            'MEASURE': GateType.MEASURE,
            'RESET': GateType.RESET,
            'BARRIER': GateType.BARRIER
        }
        
        gate_type = gate_mapping_reverse.get(gate_name)
        
        if gate_type:
            try:
                # Get qubit objects
                qubits = [circuit.qubits[i] for i in qubit_indices]
                
                # Add measurement classical bit info if needed
                if gate_type == GateType.MEASURE and cargs:
                    params = [cargs[0].index]
                
                circuit.add_gate(gate_type, *qubits, parameters=params)
                
            except Exception as e:
                print(f"❌ Error converting gate {gate_name}: {e}")
        else:
            print(f"⚠️  Unsupported Qiskit gate: {gate_name}")


class QiskitBridge:
    """High-level bridge for Qiskit integration"""
    
    def __init__(self):
        """Initialize Qiskit bridge"""
        self.converter = QiskitConverter()
        print("🌉 Qiskit Bridge initialized")
    
    def execute_on_qiskit_backend(self, circuit: Circuit, backend_name: str, 
                                 shots: int = 1024, **kwargs) -> Dict[str, Any]:
        """
        Execute a circuit on a Qiskit backend
        
        Args:
            circuit: Quantum Memory Compiler circuit
            backend_name: Name of Qiskit backend
            shots: Number of shots
            **kwargs: Additional execution parameters
            
        Returns:
            Execution results
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for backend execution")
        
        print(f"🚀 Executing circuit on Qiskit backend: {backend_name}")
        
        try:
            # Convert to Qiskit
            qiskit_circuit = self.converter.to_qiskit(circuit)
            
            # Add measurements if not present
            if not any(instr.name == 'measure' for instr, _, _ in qiskit_circuit.data):
                qiskit_circuit.measure_all()
            
            # Get backend
            from qiskit import Aer, execute
            
            if backend_name in ['qasm_simulator', 'statevector_simulator']:
                backend = Aer.get_backend(backend_name)
            else:
                # Try to get IBM backend
                try:
                    from qiskit.providers.ibmq import IBMQ
                    IBMQ.load_account()
                    provider = IBMQ.get_provider()
                    backend = provider.get_backend(backend_name)
                except:
                    print(f"⚠️  Could not get backend {backend_name}, using qasm_simulator")
                    backend = Aer.get_backend('qasm_simulator')
            
            # Execute
            job = execute(qiskit_circuit, backend, shots=shots, **kwargs)
            result = job.result()
            
            # Get counts
            counts = result.get_counts()
            
            print(f"✅ Execution completed: {len(counts)} unique outcomes")
            
            return {
                'success': True,
                'results': counts,
                'shots': shots,
                'backend': backend_name,
                'job_id': job.job_id() if hasattr(job, 'job_id') else 'local'
            }
            
        except Exception as e:
            print(f"❌ Execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'backend': backend_name
            }
    
    def get_qiskit_backends(self) -> List[Dict[str, Any]]:
        """Get available Qiskit backends"""
        backends = []
        
        if not QISKIT_AVAILABLE:
            return backends
        
        try:
            # Local Aer backends
            from qiskit import Aer
            aer_backends = Aer.backends()
            
            for backend in aer_backends:
                backends.append({
                    'name': backend.name(),
                    'type': 'simulator',
                    'provider': 'Aer',
                    'num_qubits': getattr(backend.configuration(), 'n_qubits', 32),
                    'operational': True
                })
            
            # IBM Quantum backends
            try:
                from qiskit.providers.ibmq import IBMQ
                IBMQ.load_account()
                provider = IBMQ.get_provider()
                
                for backend in provider.backends():
                    config = backend.configuration()
                    status = backend.status()
                    
                    backends.append({
                        'name': config.backend_name,
                        'type': 'hardware' if not config.simulator else 'simulator',
                        'provider': 'IBM Quantum',
                        'num_qubits': config.n_qubits,
                        'operational': status.operational,
                        'pending_jobs': status.pending_jobs
                    })
                    
            except Exception as e:
                print(f"⚠️  Could not load IBM Quantum backends: {e}")
        
        except Exception as e:
            print(f"❌ Error getting backends: {e}")
        
        return backends
    
    def transpile_for_backend(self, circuit: Circuit, backend_name: str, 
                             optimization_level: int = 1) -> Circuit:
        """
        Transpile circuit for specific backend
        
        Args:
            circuit: Input circuit
            backend_name: Target backend name
            optimization_level: Optimization level (0-3)
            
        Returns:
            Transpiled circuit
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for transpilation")
        
        print(f"🔄 Transpiling circuit for backend: {backend_name}")
        
        try:
            # Convert to Qiskit
            qiskit_circuit = self.converter.to_qiskit(circuit)
            
            # Get backend
            from qiskit import Aer, transpile
            
            if backend_name in ['qasm_simulator', 'statevector_simulator']:
                backend = Aer.get_backend(backend_name)
            else:
                try:
                    from qiskit.providers.ibmq import IBMQ
                    IBMQ.load_account()
                    provider = IBMQ.get_provider()
                    backend = provider.get_backend(backend_name)
                except:
                    print(f"⚠️  Could not get backend {backend_name}")
                    return circuit
            
            # Transpile
            transpiled = transpile(
                qiskit_circuit, 
                backend=backend,
                optimization_level=optimization_level
            )
            
            # Convert back
            result_circuit = self.converter.from_qiskit(transpiled)
            result_circuit.name = f"{circuit.name}_transpiled"
            
            print(f"✅ Transpilation completed")
            print(f"   Original: {circuit.width} qubits, {len(circuit.gates)} gates")
            print(f"   Transpiled: {result_circuit.width} qubits, {len(result_circuit.gates)} gates")
            
            return result_circuit
            
        except Exception as e:
            print(f"❌ Transpilation failed: {e}")
            return circuit 