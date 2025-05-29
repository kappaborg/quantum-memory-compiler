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
Circuit sınıfı
============

Kuantum devrelerini temsil eden sınıf.
"""

import uuid
import numpy as np
from collections import defaultdict

from .qubit import Qubit, QubitType, MemoryLevel
from .gate import Gate, GateType


class Circuit:
    """Kuantum devresini temsil eden sınıf"""
    
    def __init__(self, name_or_qubits=None):
        """
        Circuit nesnesini başlatır
        
        Args:
            name_or_qubits: Devrenin adı (str) veya qubit sayısı (int) 
                          (varsayılan: None, otomatik oluşturulur)
        """
        # Determine if input is name or number of qubits
        if isinstance(name_or_qubits, int):
            # If integer, treat as number of qubits
            num_qubits = name_or_qubits
            self.name = f"circuit_{uuid.uuid4().hex[:8]}"
        elif isinstance(name_or_qubits, str):
            # If string, treat as name
            num_qubits = 0
            self.name = name_or_qubits
        else:
            # If None or other, use defaults
            num_qubits = 0
            self.name = f"circuit_{uuid.uuid4().hex[:8]}"
        
        # Devre bileşenleri
        self.qubits = []  # Devre içinde kullanılan qubit'ler
        self.gates = []   # Devrenin kapıları
        self.measurements = {}  # Ölçüm sonuçları: {qubit_id: ölçüm sonucu}
        
        # Devre metadata
        self.depth = 0  # Devre derinliği
        self.width = 0  # Toplam qubit sayısı
        
        # Derleyici bilgileri
        self.is_transpiled = False
        self.original_circuit = None  # Transpile öncesi orijinal devre
        
        # Zaman bilgisi
        self.current_time = 0  # Devrenin şu anki zamanı
        
        # Optimizasyon bilgileri
        self.gate_counts = defaultdict(int)  # Her bir kapı tipinden kaç tane var
        self.swap_count = 0  # Eklenen SWAP kapısı sayısı
        
        # Add qubits if specified
        if num_qubits > 0:
            self.add_qubits(num_qubits)
    
    def add_qubit(self, qubit=None, qubit_type=QubitType.LOGICAL, memory_level=MemoryLevel.L1):
       
        if qubit is None:
            qubit_id = len(self.qubits)
            qubit = Qubit(qubit_id, qubit_type, memory_level)
        
        self.qubits.append(qubit)
        self.width = len(self.qubits)
        return qubit
    
    def add_qubits(self, n, qubit_type=QubitType.LOGICAL, memory_level=MemoryLevel.L1):
        
        return [self.add_qubit(None, qubit_type, memory_level) for _ in range(n)]
    
    def add_gate(self, gate_or_type, *qubits, parameters=None, time=None):
        """
        Add a gate to the circuit
        
        Args:
            gate_or_type: Either a Gate object or GateType enum
            *qubits: Qubit indices or objects (variable arguments)
            parameters: Gate parameters (for parametric gates)
            time: Gate execution time
        """
        # Zaman belirlenmemişse şu anki devredeki zamanı kullan
        if time is None:
            time = self.current_time
        
        # Handle different input types
        if hasattr(gate_or_type, 'type'):
            # It's a Gate object from gates.py (HGate, XGate, etc.)
            gate_type = getattr(gate_or_type, 'type', None)
            if gate_type is None:
                # Try to infer from class name
                class_name = gate_or_type.__class__.__name__
                if class_name.endswith('Gate'):
                    gate_name = class_name[:-4].upper()  # Remove 'Gate' suffix
                    try:
                        gate_type = GateType[gate_name]
                    except KeyError:
                        raise ValueError(f"Unknown gate type: {class_name}")
                else:
                    raise ValueError(f"Cannot determine gate type from {class_name}")
            
            # Get parameters from gate object if available
            if hasattr(gate_or_type, 'params'):
                parameters = gate_or_type.params
            elif hasattr(gate_or_type, 'parameters'):
                parameters = gate_or_type.parameters
            elif hasattr(gate_or_type, 'theta'):
                parameters = [gate_or_type.theta]
            
        elif isinstance(gate_or_type, GateType):
            # It's a GateType enum (old usage)
            gate_type = gate_or_type
        else:
            raise ValueError(f"Expected Gate object or GateType, got {type(gate_or_type)}")
        
        # Convert qubits to list
        qubit_list = list(qubits)
        
        # Qubit'leri ID ile geçirilmişse, onları Qubit nesnelerine dönüştür
        processed_qubits = []
        for q in qubit_list:
            if isinstance(q, int):
                if q >= len(self.qubits):
                    raise ValueError(f"Qubit ID {q} aralık dışında, mevcut qubit sayısı: {len(self.qubits)}")
                processed_qubits.append(self.qubits[q])
            else:
                processed_qubits.append(q)
        
        # Kapıyı oluştur ve ekle
        gate = Gate(gate_type, processed_qubits, parameters, time)
        self.gates.append(gate)
        
        # Devre istatistiklerini güncelle
        self.gate_counts[gate_type] += 1
        if gate_type == GateType.SWAP and gate.is_inserted_swap:
            self.swap_count += 1
        
        # Devre derinliğini güncelle
        self.depth = max(self.depth, gate.end_time)
        
        # Devrenin geçerli zamanını güncelle
        self.current_time = max(self.current_time, gate.end_time)
        
        # Qubit'lerin son kullanım zamanını güncelle
        for qubit in processed_qubits:
            qubit.update_usage_time(gate.end_time)
        
        return gate
    
    def add_measurement(self, qubit, classical_bit=None):
        
        classical_target = classical_bit if classical_bit is not None else qubit.id
        return self.add_gate(GateType.MEASURE, qubit, [classical_target])
    
    def add_reset(self, qubit):
        
        return self.add_gate(GateType.RESET, qubit)
    
    def get_qubit_by_id(self, qubit_id):
        
        #Return by qubit id
        for qubit in self.qubits:
            if qubit.id == qubit_id:
                return qubit
        return None
    
    def get_gates_by_type(self, gate_type):
        
        #Filter gates by type
        return [gate for gate in self.gates if gate.type == gate_type]
    
    def get_gates_by_qubit(self, qubit):
        
        qubit_id = qubit.id if isinstance(qubit, Qubit) else qubit
        
        if isinstance(qubit, int):
            qubit = self.get_qubit_by_id(qubit)
            if not qubit:
                return []
        
        return [gate for gate in self.gates if qubit in gate.qubits]
    
    def get_gates_in_time_range(self, start_time, end_time):
        
        #Filter gates by time range
        return [gate for gate in self.gates if gate.time >= start_time and gate.end_time <= end_time]
    
    def get_qubit_lifetime(self, qubit):
        
        gates = self.get_gates_by_qubit(qubit)
        if not gates:
            return (0, 0)
        
        first_gate_time = min(gate.time for gate in gates)
        last_gate_time = max(gate.end_time for gate in gates)
        
        return (first_gate_time, last_gate_time)
    
    def calculate_depth(self):
        
        if not self.gates:
            return 0
        
        return max(gate.end_time for gate in self.gates)
    
    def calculate_qubit_usage(self):
        
        #Calculate qubit usage
        usage = {}
        total_depth = self.calculate_depth()
        
        if total_depth == 0:
            return {qubit.id: (0, 0, 0.0) for qubit in self.qubits}
        
        for qubit in self.qubits:
            first_time, last_time = self.get_qubit_lifetime(qubit)
            lifetime = last_time - first_time
            usage_ratio = lifetime / total_depth if total_depth > 0 else 0.0
            usage[qubit.id] = (first_time, last_time, usage_ratio)
        
        return usage
    
    def validate_circuit(self):
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check for gate parameter validity
        self._validate_gate_parameters(validation_results)
        
        # Check for proper qubit usage
        self._validate_qubit_usage(validation_results)
        
        # Check for gate sequence issues
        self._validate_gate_sequences(validation_results)
        
        # Check for gate overlap issues
        self._validate_gate_timing(validation_results)
        
        # Circuit is invalid if it has errors
        if validation_results["errors"]:
            validation_results["valid"] = False
            
        return validation_results
    
    def _validate_gate_parameters(self, results):
        
        for i, gate in enumerate(self.gates):
            # Check for missing required parameters
            if gate.type in [GateType.RX, GateType.RY, GateType.RZ, GateType.P, GateType.U1, 
                            GateType.CP, GateType.CRX, GateType.CRY, GateType.CRZ, GateType.CU1,
                            GateType.RXX, GateType.RYY, GateType.RZZ]:
                if not gate.parameters or len(gate.parameters) < 1:
                    results["errors"].append(f"Gate {i} ({gate.type.name}) is missing required parameter(s)")
            
            elif gate.type == GateType.U2:
                if not gate.parameters or len(gate.parameters) < 2:
                    results["errors"].append(f"Gate {i} ({gate.type.name}) requires 2 parameters")
            
            elif gate.type in [GateType.U3, GateType.CU3]:
                if not gate.parameters or len(gate.parameters) < 3:
                    results["errors"].append(f"Gate {i} ({gate.type.name}) requires 3 parameters")
            
            # Check parameter types
            if gate.parameters:
                for j, param in enumerate(gate.parameters):
                    if not isinstance(param, (int, float, complex)):
                        results["errors"].append(f"Gate {i} ({gate.type.name}) parameter {j} has invalid type: {type(param)}")
    
    def _validate_qubit_usage(self, results):
        
        # Check that all qubits used in gates are in the circuit's qubit list
        all_circuit_qubits = set(self.qubits)
        for i, gate in enumerate(self.gates):
            for qubit in gate.qubits:
                if qubit not in all_circuit_qubits:
                    results["errors"].append(f"Gate {i} ({gate.type.name}) uses qubit {qubit.id} which is not in the circuit")
        
        # Check for qubits that are used after measurement
        measured_qubits = {}  # Maps qubit to the gate index where it was measured
        for i, gate in enumerate(self.gates):
            # Track measurements
            if gate.type == GateType.MEASURE:
                measured_qubit = gate.qubits[0]
                measured_qubits[measured_qubit] = i
            
            # Check if any qubit was used after measurement
            for qubit in gate.qubits:
                if qubit in measured_qubits and i > measured_qubits[qubit] and gate.type != GateType.BARRIER:
                    results["errors"].append(f"Qubit {qubit.id} is used in gate {i} ({gate.type.name}) after being measured in gate {measured_qubits[qubit]}")
        
        # Check if there are any unitialized qubits
        for qubit in self.qubits:
            if qubit.is_active and not qubit.is_allocated:
                results["warnings"].append(f"Qubit {qubit.id} is active but not explicitly allocated")
        
        # Check for computational qubits without measurements
        computational_qubits = set()
        measured_qubit_set = set(measured_qubits.keys())
        
        for gate in self.gates:
            # Skip measurement, reset, and barrier gates for counting computational qubits
            if gate.type in [GateType.MEASURE, GateType.RESET, GateType.BARRIER]:
                continue
            
            # Add qubits used in computational gates
            for qubit in gate.qubits:
                computational_qubits.add(qubit)
        
        unmeasured = computational_qubits - measured_qubit_set
        if unmeasured:
            unmeasured_ids = [q.id for q in unmeasured]
            results["warnings"].append(f"Qubits {unmeasured_ids} are used in computation but never measured")
    
    def _validate_gate_sequences(self, results):
        
        # Check for gates that should be followed by others (e.g., Hadamard before measurement)
        for qubit in self.qubits:
            qubit_gates = self.get_gates_by_qubit(qubit)
            qubit_gates.sort(key=lambda g: g.time)  # Sort by time
            
            # Check for direct measurement of qubits in |0⟩ or |1⟩ basis without Hadamard
            found_superposition = False
            last_superposition_gate_idx = -1
            
            for i, gate in enumerate(qubit_gates):
                # These gates can create superposition
                if gate.type in [GateType.H, GateType.RX, GateType.RY, GateType.SX, GateType.U2, GateType.U3]:
                    found_superposition = True
                    last_superposition_gate_idx = i
                
                # These gates destroy superposition
                elif gate.type in [GateType.MEASURE, GateType.RESET]:
                    found_superposition = False
                
                # Check if measuring directly in computational basis without Hadamard
                if gate.type == GateType.MEASURE and not found_superposition:
                    if i > 0 and qubit_gates[i-1].type not in [GateType.H, GateType.RESET, GateType.MEASURE]:
                        # Only warn if there were non-trivial gates before measurement
                        if i > 0 and qubit_gates[i-1].type not in [GateType.I, GateType.BARRIER]:
                            results["warnings"].append(f"Qubit {qubit.id} is measured directly in computational basis. Consider adding H before measurement if measuring in X basis.")
        
        # Check for Reset followed immediately by gates (probable error)
        for i, gate in enumerate(self.gates[:-1]):
            if gate.type == GateType.RESET:
                reset_qubit = gate.qubits[0]
                next_gate = self.gates[i+1]
                if reset_qubit in next_gate.qubits and next_gate.type == GateType.RESET:
                    results["errors"].append(f"Qubit {reset_qubit.id} is reset twice in a row (gates {i} and {i+1})")
        
        # Check for barrier at end of circuit (useless)
        if self.gates and self.gates[-1].type == GateType.BARRIER:
            results["warnings"].append("Circuit ends with a barrier gate, which has no effect")
    
    def _validate_gate_timing(self, results):
        
        # Check for overlapping gates on the same qubits
        for qubit in self.qubits:
            # Get all gates using this qubit
            qubit_gates = [(i, gate) for i, gate in enumerate(self.gates) if qubit in gate.qubits]
            
            # Sort by start time
            qubit_gates.sort(key=lambda g: g[1].time)
            
            # Check for overlapping gates
            for j in range(len(qubit_gates) - 1):
                curr_idx, curr_gate = qubit_gates[j]
                next_idx, next_gate = qubit_gates[j + 1]
                
                if curr_gate.end_time > next_gate.time:
                    results["errors"].append(
                        f"Gates {curr_idx} ({curr_gate.type.name}) and {next_idx} ({next_gate.type.name}) "
                        f"overlap in time on qubit {qubit.id}"
                    )
        
        # Check for negative timing
        for i, gate in enumerate(self.gates):
            if gate.time < 0:
                results["errors"].append(f"Gate {i} ({gate.type.name}) has negative start time: {gate.time}")
            if gate.duration <= 0:
                results["warnings"].append(f"Gate {i} ({gate.type.name}) has non-positive duration: {gate.duration}")
    
    def is_valid(self):
        
        validation_results = self.validate_circuit()
        return validation_results["valid"]
    
    def is_memory_efficient(self, threshold=0.7):
        
        usage_stats = self.calculate_qubit_usage()
        avg_usage = sum(ratio for _, _, ratio in usage_stats.values()) / len(usage_stats)
        return avg_usage >= threshold
    
    def to_qasm(self):
        
        #Convert to QASM
        qasm_lines = [
            "OPENQASM 2.0;",
            'include "qelib1.inc";',
            "",
            f"// Circuit: {self.name}",
            f"// Qubits: {self.width}",
            f"// Depth: {self.depth}",
            "",
            f"qreg q[{self.width}];",
            f"creg c[{self.width}];"
        ]
        
        # Kapıları zaman sırasına göre sırala
        sorted_gates = sorted(self.gates, key=lambda g: g.time)
        
        # Her kapıyı QASM'e çevir
        for gate in sorted_gates:
            qasm_lines.append(gate.to_qasm())
        
        return "\n".join(qasm_lines)
    
    def copy(self):
        
        import copy
        
        new_circuit = Circuit(self.name + "_copy")
        
        # Qubit'leri kopyala
        qubit_map = {}  # Eski qubit -> yeni qubit eşlemesi
        for qubit in self.qubits:
            new_qubit = copy.deepcopy(qubit)
            qubit_map[qubit] = new_qubit
            new_circuit.qubits.append(new_qubit)
        
        # Kapıları kopyala
        for gate in self.gates:
            new_qubits = [qubit_map[q] for q in gate.qubits]
            new_gate = copy.deepcopy(gate)
            new_gate.qubits = new_qubits
            new_circuit.gates.append(new_gate)
        
        # Meta verileri kopyala
        new_circuit.depth = self.depth
        new_circuit.width = self.width
        new_circuit.current_time = self.current_time
        new_circuit.gate_counts = self.gate_counts.copy()
        new_circuit.swap_count = self.swap_count
        
        return new_circuit
    
    def __str__(self):
        
        gate_count_str = ", ".join(f"{gate_type.name}: {count}" for gate_type, count in self.gate_counts.items())
        return (f"Circuit(name={self.name}, qubits={self.width}, depth={self.depth}, "
                f"gate_count={{{gate_count_str}}})")
    
    # Convenience methods for adding specific gates
    def h(self, qubit):
        """Adds a Hadamard gate to the circuit"""
        return self.add_gate(GateType.H, qubit)
    
    def x(self, qubit):
        """Adds a Pauli-X gate to the circuit"""
        return self.add_gate(GateType.X, qubit)
    
    def y(self, qubit):
        """Adds a Pauli-Y gate to the circuit"""
        return self.add_gate(GateType.Y, qubit)
    
    def z(self, qubit):
        """Adds a Pauli-Z gate to the circuit"""
        return self.add_gate(GateType.Z, qubit)
    
    def rx(self, qubit, theta):
        """Adds an RX (rotation around X-axis) gate to the circuit"""
        return self.add_gate(GateType.RX, qubit, parameters=[theta])
    
    def ry(self, qubit, theta):
        """Adds an RY (rotation around Y-axis) gate to the circuit"""
        return self.add_gate(GateType.RY, qubit, parameters=[theta])
    
    def rz(self, qubit, theta):
        """Adds an RZ (rotation around Z-axis) gate to the circuit"""
        return self.add_gate(GateType.RZ, qubit, parameters=[theta])
    
    def p(self, qubit, phi):
        """Adds a phase gate to the circuit"""
        return self.add_gate(GateType.P, qubit, parameters=[phi])
    
    def cnot(self, control, target):
        """Adds a CNOT gate to the circuit"""
        return self.add_gate(GateType.CNOT, control, target)
    
    def cz(self, control, target):
        """Adds a CZ gate to the circuit"""
        return self.add_gate(GateType.CZ, control, target)
    
    def swap(self, qubit1, qubit2):
        """Adds a SWAP gate to the circuit"""
        return self.add_gate(GateType.SWAP, qubit1, qubit2)
    
    def toffoli(self, control1, control2, target):
        """Adds a Toffoli (CCNOT) gate to the circuit"""
        return self.add_gate(GateType.TOFFOLI, control1, control2, target)
    
    # New gate methods
    def s(self, qubit):
        """Adds an S (phase) gate to the circuit"""
        return self.add_gate(GateType.S, qubit)
    
    def sdg(self, qubit):
        """Adds an S-dagger gate to the circuit"""
        return self.add_gate(GateType.SDG, qubit)
    
    def t(self, qubit):
        """Adds a T gate to the circuit"""
        return self.add_gate(GateType.T, qubit)
    
    def tdg(self, qubit):
        """Adds a T-dagger gate to the circuit"""
        return self.add_gate(GateType.TDG, qubit)
    
    def sx(self, qubit):
        """Adds a square root of X gate to the circuit"""
        return self.add_gate(GateType.SX, qubit)
    
    def sy(self, qubit):
        """Adds a square root of Y gate to the circuit"""
        return self.add_gate(GateType.SY, qubit)
    
    def u1(self, qubit, lambda_param):
        """Adds a U1 gate to the circuit"""
        return self.add_gate(GateType.U1, qubit, [lambda_param])
    
    def u2(self, qubit, phi, lambda_param):
        """Adds a U2 gate to the circuit"""
        return self.add_gate(GateType.U2, qubit, [phi, lambda_param])
    
    def u3(self, qubit, theta, phi, lambda_param):
        """Adds a U3 gate to the circuit"""
        return self.add_gate(GateType.U3, qubit, [theta, phi, lambda_param])
    
    def iswap(self, qubit1, qubit2):
        """Adds an iSWAP gate to the circuit"""
        return self.add_gate(GateType.ISWAP, qubit1, qubit2)
    
    def cp(self, control, target, phi):
        """Adds a controlled-phase gate to the circuit"""
        return self.add_gate(GateType.CP, control, target, parameters=[phi])
    
    def crx(self, control, target, theta):
        """Adds a controlled-RX gate to the circuit"""
        return self.add_gate(GateType.CRX, control, target, parameters=[theta])
    
    def cry(self, control, target, theta):
        """Adds a controlled-RY gate to the circuit"""
        return self.add_gate(GateType.CRY, control, target, parameters=[theta])
    
    def crz(self, control, target, theta):
        """Adds a controlled-RZ gate to the circuit"""
        return self.add_gate(GateType.CRZ, control, target, parameters=[theta])
    
    def cu1(self, control, target, lambda_param):
        """Adds a controlled-U1 gate to the circuit"""
        return self.add_gate(GateType.CU1, control, target, parameters=[lambda_param])
    
    def cu3(self, control, target, theta, phi, lambda_param):
        """Adds a controlled-U3 gate to the circuit"""
        return self.add_gate(GateType.CU3, control, target, parameters=[theta, phi, lambda_param])
    
    def rxx(self, qubit1, qubit2, theta):
        """Adds an RXX (Ising coupling) gate to the circuit"""
        return self.add_gate(GateType.RXX, qubit1, qubit2, parameters=[theta])
    
    def ryy(self, qubit1, qubit2, theta):
        """Adds an RYY (Ising coupling) gate to the circuit"""
        return self.add_gate(GateType.RYY, qubit1, qubit2, parameters=[theta])
    
    def rzz(self, qubit1, qubit2, theta):
        """Adds an RZZ (Ising coupling) gate to the circuit"""
        return self.add_gate(GateType.RZZ, qubit1, qubit2, parameters=[theta])
    
    def ccz(self, control1, control2, target):
        """Adds a controlled-controlled-Z gate to the circuit"""
        return self.add_gate(GateType.CCZ, control1, control2, target)
    
    def cswap(self, control, target1, target2):
        """Adds a controlled-SWAP (Fredkin) gate to the circuit"""
        return self.add_gate(GateType.CSWAP, control, target1, target2)
    
    def barrier(self, qubits=None):
        #Add barrier
        if qubits is None:
            qubits = self.qubits
        return self.add_gate(GateType.BARRIER, qubits)
        
    @classmethod
    def create_bell_state(cls):
        
        circuit = cls("bell_state")
        q0, q1 = circuit.add_qubits(2)
        circuit.h(q0)
        circuit.cnot(q0, q1)
        return circuit
    
    @classmethod
    def create_ghz_state(cls, n=3):
        
        circuit = cls(f"ghz_state_{n}")
        qubits = circuit.add_qubits(n)
        
        circuit.h(qubits[0])
        for i in range(n-1):
            circuit.cnot(qubits[i], qubits[i+1])
        
        return circuit
    
    @classmethod
    def create_qft(cls, n=4):
       
        circuit = cls(f"QFT_{n}")
        qubits = circuit.add_qubits(n)
        
        for i in range(n):
            circuit.h(qubits[i])
            for j in range(i+1, n):
                # Kontrollü faz dönüşümü
                phase = 2 * np.pi / (2 ** (j - i + 1))
                circuit.cp(qubits[j], qubits[i], phase)
        
        # Qubit'leri tersine çevir (n/2 swap işlemi)
        for i in range(n // 2):
            circuit.swap(qubits[i], qubits[n - i - 1])
            
        return circuit
        
    @classmethod
    def from_dict(cls, data):
        
        if not isinstance(data, dict):
            raise ValueError("Giriş verisi bir sözlük (dict) olmalıdır")
            
        # Yeni devre oluştur
        circuit = cls(data.get('name', None))
        
        # Qubit'leri ekle
        num_qubits = data.get('qubits', 0)
        if num_qubits > 0:
            circuit.add_qubits(num_qubits)
        
        # Kapıları ekle
        for gate_data in data.get('gates', []):
            gate_type_str = gate_data.get('type')
            try:
                gate_type = GateType[gate_type_str]
            except (KeyError, TypeError):
                raise ValueError(f"Geçersiz kapı tipi: {gate_type_str}")
                
            qubit_indices = gate_data.get('qubits', [])
            # İndisleri qubit nesnelerine dönüştür - circuit.qubits listesini kullan
            qubit_objects = []
            for idx in qubit_indices:
                if idx < len(circuit.qubits):
                    qubit_objects.append(circuit.qubits[idx])
                else:
                    raise ValueError(f"Qubit index {idx} out of range, circuit has {len(circuit.qubits)} qubits")
            
            params = gate_data.get('params', [])
            
            circuit.add_gate(gate_type, *qubit_objects, parameters=params)
        
        # Ölçümleri ekle
        for measurement in data.get('measurements', []):
            qubit_index = measurement.get('qubit')
            bit_index = measurement.get('bit', qubit_index)
            register = measurement.get('register', 'c')
            
            if qubit_index is not None and qubit_index < len(circuit.qubits):
                circuit.add_measurement(circuit.qubits[qubit_index], bit_index)
        
        return circuit
        
    def to_dict(self):
        
        gates_data = []
        for gate in self.gates:
            gate_data = {
                'type': gate.type.name,
                'qubits': [q.id for q in gate.qubits],
                'params': gate.parameters
            }
            gates_data.append(gate_data)
            
        measurements = []
        for gate in self.get_gates_by_type(GateType.MEASURE):
            measurement = {
                'qubit': gate.qubits[0].id,
                'bit': gate.parameters[0] if gate.parameters else gate.qubits[0].id,
                'register': 'c'
            }
            measurements.append(measurement)
            
        return {
            'name': self.name,
            'qubits': len(self.qubits),
            'gates': gates_data,
            'measurements': measurements
        } 
    
    def combine(self, other_circuit):
        """
        Combine this circuit with another circuit sequentially.
        The qubits of the other circuit are appended after this circuit's qubits.
        The gates of the other circuit are appended with time shifted appropriately.
        """
        import copy
        combined = copy.deepcopy(self)
        qubit_id_offset = len(combined.qubits)
        time_offset = combined.current_time

        # Map other_circuit's qubits to new qubits in combined
        qubit_map = {}
        for q in other_circuit.qubits:
            new_q = combined.add_qubit(qubit_type=q.type, memory_level=q.memory_level)
            qubit_map[q.id] = new_q

        # Add gates from other_circuit, shifting time and remapping qubits
        for gate in other_circuit.gates:
            mapped_qubits = [qubit_map[q.id] for q in gate.qubits]
            new_time = gate.time + time_offset
            combined.add_gate(gate.type, mapped_qubits, parameters=gate.parameters, time=new_time)

        return combined 