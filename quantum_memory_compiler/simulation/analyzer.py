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
PerformanceAnalyzer modülü
======================

Kuantum devrelerinin performansını analiz eden sınıf.
"""

import numpy as np
from collections import defaultdict


class PerformanceAnalyzer:
    """
    Kuantum devrelerinin performansını analiz eden sınıf
    
    Farklı performans metrikleri hesaplar.
    """
    
    def __init__(self):
        """PerformanceAnalyzer nesnesini başlatır"""
        self.metrics = {}
    
    def analyze_circuit(self, circuit, hardware_model=None):
        """
        Devrenin performansını analiz eder
        
        Args:
            circuit: Analiz edilecek devre
            hardware_model: Donanım modeli (opsiyonel)
            
        Returns:
            dict: Performans metrikleri
        """
        metrics = {}
        
        # Temel metrikler
        metrics["qubit_count"] = circuit.width
        metrics["gate_count"] = len(circuit.gates)
        metrics["circuit_depth"] = circuit.depth
        
        # Kapı istatistikleri
        gate_counts = {}
        for gate_type, count in circuit.gate_counts.items():
            gate_counts[gate_type.name] = count
        metrics["gate_counts"] = gate_counts
        
        # Bellek kullanım metrikleri
        metrics["memory_efficiency"] = self._calculate_memory_efficiency(circuit)
        metrics["qubit_usage"] = self._calculate_qubit_usage(circuit)
        
        # Eğer donanım modeli verildiyse donanım uyumluluk metriklerini hesapla
        if hardware_model:
            metrics["hardware_compatibility"] = self._calculate_hardware_compatibility(circuit, hardware_model)
        
        self.metrics = metrics
        return metrics
    
    def _calculate_memory_efficiency(self, circuit):
        """
        Devrenin bellek verimliliğini hesaplar
        
        Args:
            circuit: Analiz edilecek devre
            
        Returns:
            dict: Bellek verimliliği metrikleri
        """
        # Qubit kullanım oranları
        usage_stats = circuit.calculate_qubit_usage()
        
        # Ortalama qubit kullanım oranı
        avg_usage = sum(ratio for _, _, ratio in usage_stats.values()) / len(usage_stats) if usage_stats else 0
        
        # Maksimum ve minimum kullanım oranları
        max_usage = max(ratio for _, _, ratio in usage_stats.values()) if usage_stats else 0
        min_usage = min(ratio for _, _, ratio in usage_stats.values()) if usage_stats else 0
        
        # Sonuç
        return {
            "average_usage_ratio": avg_usage,
            "max_usage_ratio": max_usage,
            "min_usage_ratio": min_usage,
            "is_memory_efficient": circuit.is_memory_efficient()
        }
    
    def _calculate_qubit_usage(self, circuit):
        """
        Qubit kullanım metriklerini hesaplar
        
        Args:
            circuit: Analiz edilecek devre
            
        Returns:
            dict: Qubit kullanım metrikleri
        """
        # Her qubit'in ne kadar süre kullanıldığını hesapla
        qubit_lifetimes = {}
        for qubit in circuit.qubits:
            first_time, last_time = circuit.get_qubit_lifetime(qubit)
            lifetime = last_time - first_time
            qubit_lifetimes[qubit.id] = lifetime
        
        # Kullanım süreleri istatistikleri
        avg_lifetime = sum(qubit_lifetimes.values()) / len(qubit_lifetimes) if qubit_lifetimes else 0
        max_lifetime = max(qubit_lifetimes.values()) if qubit_lifetimes else 0
        min_lifetime = min(qubit_lifetimes.values()) if qubit_lifetimes else 0
        
        # Kapı sayısı dağılımı
        gate_distribution = defaultdict(int)
        for qubit in circuit.qubits:
            gate_count = len(circuit.get_gates_by_qubit(qubit))
            gate_distribution[qubit.id] = gate_count
        
        # Ortalama, maksimum ve minimum kapı sayısı
        avg_gates = sum(gate_distribution.values()) / len(gate_distribution) if gate_distribution else 0
        max_gates = max(gate_distribution.values()) if gate_distribution else 0
        min_gates = min(gate_distribution.values()) if gate_distribution else 0
        
        return {
            "average_lifetime": avg_lifetime,
            "max_lifetime": max_lifetime,
            "min_lifetime": min_lifetime,
            "average_gates_per_qubit": avg_gates,
            "max_gates_per_qubit": max_gates,
            "min_gates_per_qubit": min_gates,
            "qubit_lifetimes": qubit_lifetimes,
            "gate_distribution": dict(gate_distribution)
        }
    
    def _calculate_hardware_compatibility(self, circuit, hardware_model):
        """
        Devrenin donanımla uyumluluğunu hesaplar
        
        Args:
            circuit: Analiz edilecek devre
            hardware_model: Donanım modeli
            
        Returns:
            dict: Donanım uyumluluğu metrikleri
        """
        # Desteklenmeyen kapıları say
        unsupported_gates = []
        for gate in circuit.gates:
            if gate.type not in hardware_model.supported_gates:
                unsupported_gates.append(gate)
        
        # Qubit sayısı uyumluluğu
        qubit_count_compatible = circuit.width <= hardware_model.num_qubits
        
        # Çok qubitli kapılar için bağlantı uyumluluğu
        connectivity_violations = []
        for gate in circuit.gates:
            if len(gate.qubits) <= 1:
                continue
                
            for i in range(len(gate.qubits) - 1):
                for j in range(i + 1, len(gate.qubits)):
                    q1, q2 = gate.qubits[i], gate.qubits[j]
                    if not hardware_model.are_connected(q1, q2):
                        connectivity_violations.append((gate, q1, q2))
        
        return {
            "qubit_count_compatible": qubit_count_compatible,
            "unsupported_gate_count": len(unsupported_gates),
            "connectivity_violations": len(connectivity_violations),
            "overall_compatibility": (qubit_count_compatible and 
                                     len(unsupported_gates) == 0 and 
                                     len(connectivity_violations) == 0)
        }
    
    def compare_circuits(self, original_circuit, compiled_circuit):
        """
        İki devreyi karşılaştırır
        
        Args:
            original_circuit: Orijinal devre
            compiled_circuit: Derlenmiş devre
            
        Returns:
            dict: Karşılaştırma metrikleri
        """
        # Her iki devreyi de analiz et
        original_metrics = self.analyze_circuit(original_circuit)
        compiled_metrics = self.analyze_circuit(compiled_circuit)
        
        # Değişim metrikleri
        comparison = {
            "qubit_count_change": compiled_metrics["qubit_count"] - original_metrics["qubit_count"],
            "gate_count_change": compiled_metrics["gate_count"] - original_metrics["gate_count"],
            "depth_change": compiled_metrics["circuit_depth"] - original_metrics["circuit_depth"],
            "memory_efficiency_change": (compiled_metrics["memory_efficiency"]["average_usage_ratio"] - 
                                        original_metrics["memory_efficiency"]["average_usage_ratio"])
        }
        
        # Yüzdelik değişimler
        if original_metrics["qubit_count"] > 0:
            comparison["qubit_reduction_percent"] = ((original_metrics["qubit_count"] - compiled_metrics["qubit_count"]) / 
                                                   original_metrics["qubit_count"] * 100)
        else:
            comparison["qubit_reduction_percent"] = 0
            
        if original_metrics["gate_count"] > 0:
            comparison["gate_count_change_percent"] = ((compiled_metrics["gate_count"] - original_metrics["gate_count"]) / 
                                                     original_metrics["gate_count"] * 100)
        else:
            comparison["gate_count_change_percent"] = 0
            
        if original_metrics["circuit_depth"] > 0:
            comparison["depth_change_percent"] = ((compiled_metrics["circuit_depth"] - original_metrics["circuit_depth"]) / 
                                               original_metrics["circuit_depth"] * 100)
        else:
            comparison["depth_change_percent"] = 0
        
        return comparison
    
    def get_last_metrics(self):
        """
        Son hesaplanan metrikleri döndürür
        
        Returns:
            dict: Performans metrikleri
        """
        return self.metrics 