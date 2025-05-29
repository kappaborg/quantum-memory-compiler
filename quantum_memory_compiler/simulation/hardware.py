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
HardwareModel modülü
=================

Kuantum donanımının fiziksel özelliklerini ve topolojisini modelleyen sınıf.
"""

import networkx as nx
from ..core.qubit import Qubit, QubitType


class HardwareModel:
    """
    Kuantum donanımının fiziksel özelliklerini ve topolojisini modelleyen sınıf
    
    Farklı topolojileri (çizgisel, çember, kafes, vs.) ve donanım özelliklerini destekler.
    """
    
    def __init__(self, topology="line", num_qubits=5, coherence_time=100, gate_error_rate=0.001):
        """
        HardwareModel nesnesini başlatır
        
        Args:
            topology: Donanım topolojisi ("line", "ring", "grid", "ibm_eagle", vs.)
            num_qubits: Qubit sayısı
            coherence_time: Koherans süresi (simülasyon zaman birimi)
            gate_error_rate: Kapı hata oranı
        """
        self.topology = topology
        self.num_qubits = num_qubits
        self.coherence_time = coherence_time
        self.gate_error_rate = gate_error_rate
        
        # Fiziksel qubit'leri oluştur
        self.qubits = [Qubit(i, QubitType.PHYSICAL) for i in range(num_qubits)]
        
        # Her qubit için uygun koherans süresi ve hata oranını ayarla
        for qubit in self.qubits:
            qubit.coherence_time = coherence_time
            qubit.error_rate = gate_error_rate
        
        # Topoloji grafiğini oluştur
        self.connectivity_graph = self._build_connectivity_graph()
        
        # Desteklenen kapılar
        from ..core.gate import GateType
        self.supported_gates = [
            GateType.I, GateType.X, GateType.Y, GateType.Z, GateType.H,
            GateType.S, GateType.SDG, GateType.T, GateType.TDG,
            GateType.RX, GateType.RY, GateType.RZ, GateType.P,
            GateType.CNOT, GateType.CZ, GateType.SWAP,
            GateType.MEASURE, GateType.RESET, GateType.BARRIER
        ]
    
    def _build_connectivity_graph(self):
        """
        Topoloji grafiğini oluşturur
        
        Returns:
            nx.Graph: Bağlantı grafiği
        """
        graph = nx.Graph()
        
        # Tüm qubit'leri düğüm olarak ekle
        for qubit in self.qubits:
            graph.add_node(qubit.id, qubit=qubit)
        
        # Topolojiye göre kenarları oluştur
        if self.topology == "line":
            # Çizgisel topoloji (1D dizisi)
            for i in range(self.num_qubits - 1):
                graph.add_edge(i, i + 1)
                
        elif self.topology == "ring":
            # Çember topoloji (kapalı çizgi)
            for i in range(self.num_qubits):
                graph.add_edge(i, (i + 1) % self.num_qubits)
                
        elif self.topology == "grid":
            # 2D kafes topolojisi
            size = int(self.num_qubits**0.5)  # Kare kafes yaklaşımı
            for i in range(size):
                for j in range(size):
                    node_id = i * size + j
                    if node_id >= self.num_qubits:
                        continue
                        
                    # Sağ bağlantı
                    if j < size - 1 and node_id + 1 < self.num_qubits:
                        graph.add_edge(node_id, node_id + 1)
                        
                    # Alt bağlantı
                    if i < size - 1 and node_id + size < self.num_qubits:
                        graph.add_edge(node_id, node_id + size)
        
        elif self.topology == "ibm_eagle":
            # IBM Eagle benzeri topoloji (basitleştirilmiş)
            # Gerçek Eagle topolojisi daha karmaşıktır
            for i in range(self.num_qubits - 1):
                graph.add_edge(i, i + 1)
                
            # Bazı çapraz bağlantılar ekle
            for i in range(0, self.num_qubits - 2, 2):
                graph.add_edge(i, i + 2)
                
        else:
            # Varsayılan: tam bağlantılı (her qubit diğer tüm qubit'lere bağlı)
            for i in range(self.num_qubits):
                for j in range(i + 1, self.num_qubits):
                    graph.add_edge(i, j)
        
        return graph
    
    def get_connections(self):
        """
        Qubit'ler arası bağlantıları döndürür
        
        Returns:
            list: (qubit1_id, qubit2_id) bağlantı çiftleri
        """
        return list(self.connectivity_graph.edges())
    
    def are_connected(self, qubit1, qubit2):
        """
        İki qubit'in doğrudan bağlantılı olup olmadığını kontrol eder
        
        Args:
            qubit1: Birinci qubit
            qubit2: İkinci qubit
            
        Returns:
            bool: Qubit'ler bağlantılıysa True
        """
        qubit1_id = qubit1.id if hasattr(qubit1, 'id') else qubit1
        qubit2_id = qubit2.id if hasattr(qubit2, 'id') else qubit2
        
        return self.connectivity_graph.has_edge(qubit1_id, qubit2_id)
    
    def shortest_path(self, qubit1, qubit2):
        """
        İki qubit arasındaki en kısa yolu döndürür
        
        Args:
            qubit1: Başlangıç qubit'i
            qubit2: Hedef qubit
            
        Returns:
            list: Qubit ID'lerinin en kısa yolu
        """
        qubit1_id = qubit1.id if hasattr(qubit1, 'id') else qubit1
        qubit2_id = qubit2.id if hasattr(qubit2, 'id') else qubit2
        
        if not (qubit1_id in self.connectivity_graph.nodes() and 
                qubit2_id in self.connectivity_graph.nodes()):
            return []
        
        try:
            return nx.shortest_path(self.connectivity_graph, qubit1_id, qubit2_id)
        except nx.NetworkXNoPath:
            return []
    
    def __str__(self):
        return f"HardwareModel(topology={self.topology}, qubits={self.num_qubits}, coherence_time={self.coherence_time})" 