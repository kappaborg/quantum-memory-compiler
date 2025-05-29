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
Mapper modülü
===========

Mantıksal qubit'leri fiziksel qubit'lere eşleyen sınıf.
"""

import logging
import networkx as nx
import numpy as np
from collections import defaultdict

from ..core.gate import GateType
from ..core.qubit import QubitType


class QubitMapper:
    """
    Mantıksal qubit'leri fiziksel qubit'lere eşleyen sınıf
    
    Farklı yerleşim stratejileri ve yönlendirme algoritmaları uygular.
    """
    
    def __init__(self):
        """QubitMapper nesnesini başlatır"""
        self.logger = logging.getLogger("QubitMapper")
        self.logger.setLevel(logging.INFO)
        
        # İstatistikler
        self.stats = {
            "mapped_circuits": 0,
            "total_swaps": 0,
            "total_mapped_qubits": 0
        }
    
    def map_qubits(self, circuit, hardware_model):
        """
        Devredeki mantıksal qubit'leri fiziksel qubit'lere eşler
        
        Args:
            circuit: Eşlenecek devre
            hardware_model: Hedef donanım modeli
            
        Returns:
            Circuit: Fiziksel yerleşimi yapılmış devre
        """
        self.logger.info(f"Mapping qubits for circuit '{circuit.name}' to hardware model")
        
        # Devrenin kopyasını oluştur
        mapped_circuit = circuit.copy()
        
        # Etkileşim grafiği oluştur
        interaction_graph = self._build_interaction_graph(mapped_circuit)
        
        # Donanım grafiği oluştur
        hardware_graph = self._build_hardware_graph(hardware_model)
        
        # Yerleşim algoritması uygula
        qubit_mapping = self._initial_placement(interaction_graph, hardware_graph, mapped_circuit)
        
        # Eşlemeyi uygula
        mapped_circuit = self._apply_mapping(mapped_circuit, qubit_mapping)
        
        # İstatistikleri güncelle
        self.stats["mapped_circuits"] += 1
        self.stats["total_mapped_qubits"] += len(qubit_mapping)
        
        self.logger.info(f"Mapped {len(qubit_mapping)} logical qubits to physical qubits")
        
        return mapped_circuit
    
    def route_gates(self, circuit, hardware_model):
        """
        Çok-qubitli kapılar için gerekli SWAP operasyonlarını ekler
        
        Args:
            circuit: İşlenecek devre
            hardware_model: Hedef donanım modeli
            
        Returns:
            Circuit: SWAP'lar eklenmiş devre
        """
        self.logger.info(f"Routing gates for circuit '{circuit.name}' on hardware model")
        
        # Devrenin kopyasını oluştur
        routed_circuit = circuit.copy()
        
        # Donanım grafiği oluştur
        hardware_graph = self._build_hardware_graph(hardware_model)
        
        # Kapıları zamanlarına göre sırala
        gates = sorted(routed_circuit.gates, key=lambda g: g.time)
        
        # Her kapı için gerekli SWAP'ları ekle
        added_swaps = 0
        current_mapping = {q.id: q.id for q in routed_circuit.qubits}  # Başlangıçta 1-1 eşleme
        
        for gate in gates:
            # Sadece çok-qubitli kapılar için yönlendirme gerekir
            if len(gate.qubits) <= 1 or gate.type == GateType.BARRIER:
                continue
                
            # Bu kapı donanımda doğrudan uygulanabilir mi?
            if self._is_executable(gate, current_mapping, hardware_graph):
                continue
                
            # SWAP'lar ekleyerek kapıyı uygulama yapılabilir hale getir
            swaps = self._find_swaps(gate, current_mapping, hardware_graph)
            
            # SWAP'ları devreye ekle
            for q1, q2 in swaps:
                swap_time = gate.time - 1  # Kapıdan önce SWAP uygula
                qubit1 = routed_circuit.get_qubit_by_id(q1)
                qubit2 = routed_circuit.get_qubit_by_id(q2)
                
                # SWAP ekle
                swap_gate = routed_circuit.add_gate(GateType.SWAP, [qubit1, qubit2], time=swap_time)
                swap_gate.is_inserted_swap = True
                
                # Eşlemeyi güncelle
                current_mapping[q1], current_mapping[q2] = current_mapping[q2], current_mapping[q1]
                
                added_swaps += 1
        
        # İstatistikleri güncelle
        self.stats["total_swaps"] += added_swaps
        routed_circuit.swap_count = added_swaps
        
        self.logger.info(f"Added {added_swaps} SWAP gates for routing")
        
        return routed_circuit
    
    def _build_interaction_graph(self, circuit):
        """
        Devredeki qubit'ler arası etkileşim grafiğini oluşturur
        
        Args:
            circuit: İncelenecek devre
            
        Returns:
            nx.Graph: Etkileşim grafiği
        """
        graph = nx.Graph()
        
        # Tüm qubit'leri düğüm olarak ekle
        for qubit in circuit.qubits:
            graph.add_node(qubit.id, qubit=qubit)
        
        # Çok-qubitli kapıları kenar olarak ekle
        edge_weights = defaultdict(int)
        
        for gate in circuit.gates:
            if len(gate.qubits) >= 2:
                for i in range(len(gate.qubits) - 1):
                    for j in range(i + 1, len(gate.qubits)):
                        q1, q2 = gate.qubits[i], gate.qubits[j]
                        edge_weights[(q1.id, q2.id)] += 1
        
        # Kenarları ağırlıklarıyla ekle
        for (q1_id, q2_id), weight in edge_weights.items():
            graph.add_edge(q1_id, q2_id, weight=weight)
        
        return graph
    
    def _build_hardware_graph(self, hardware_model):
        """
        Donanım modelinin bağlantı grafiğini oluşturur
        
        Args:
            hardware_model: Hedef donanım modeli
            
        Returns:
            nx.Graph: Donanım grafiği
        """
        graph = nx.Graph()
        
        # Fiziksel qubit'leri düğüm olarak ekle
        for qubit in hardware_model.qubits:
            graph.add_node(qubit.id, qubit=qubit)
        
        # Qubit'ler arası bağlantıları kenar olarak ekle
        for q1_id, q2_id in hardware_model.get_connections():
            graph.add_edge(q1_id, q2_id)
        
        return graph
    
    def _initial_placement(self, interaction_graph, hardware_graph, circuit):
        """
        İlk yerleşim stratejisini uygular
        
        Args:
            interaction_graph: Devre etkileşim grafiği
            hardware_graph: Donanım grafiği
            circuit: Devreyi
            
        Returns:
            dict: {mantıksal_qubit_id: fiziksel_qubit_id} eşlemesi
        """
        # Stratejiler:
        # 1. İlk sıra (trivial): Sırayla eşle
        # 2. Rastgele: Rastgele eşle
        # 3. Alt-graf isomorfizmi: En iyi eşleşmeyi bul
        
        # Bu örnekte alt-graf isomorfizmi tabanlı yerleşim kullanılıyor
        # (Basitleştirilmiş bir versiyon)
        
        logical_qubits = list(interaction_graph.nodes())
        physical_qubits = list(hardware_graph.nodes())
        
        # Mantıksal qubit'ler, fiziksel qubit'lerden fazlaysa, hata ver
        if len(logical_qubits) > len(physical_qubits):
            raise ValueError(f"Hardware model has {len(physical_qubits)} qubits, but circuit needs {len(logical_qubits)}")
        
        # Basit bir açgözlü algoritma:
        # En yüksek ağırlıklı kenarlardan başlayarak eşle
        
        # Kenarları ağırlıklarına göre azalan sırada sırala
        edges = list(interaction_graph.edges(data=True))
        edges.sort(key=lambda e: e[2].get('weight', 0), reverse=True)
        
        # Yerleşimi oluştur
        placement = {}
        available_physical = set(physical_qubits)
        
        # Önce yüksek etkileşimli qubit'leri yerleştir
        for q1, q2, _ in edges:
            if q1 not in placement and q2 not in placement:
                # Bu iki mantıksal qubit'i donanımda bağlantılı iki fiziksel qubit'e yerleştir
                for p1 in available_physical:
                    for p2 in hardware_graph.neighbors(p1):
                        if p2 in available_physical:
                            # Bu iki fiziksel qubit uygun
                            placement[q1] = p1
                            placement[q2] = p2
                            available_physical.remove(p1)
                            available_physical.remove(p2)
                            break
                    if q1 in placement:
                        break
            elif q1 not in placement:
                # q2 zaten yerleştirilmiş, q1'i q2'ye komşu bir fiziksel qubit'e yerleştir
                p2 = placement[q2]
                for p1 in hardware_graph.neighbors(p2):
                    if p1 in available_physical:
                        placement[q1] = p1
                        available_physical.remove(p1)
                        break
            elif q2 not in placement:
                # q1 zaten yerleştirilmiş, q2'yi q1'e komşu bir fiziksel qubit'e yerleştir
                p1 = placement[q1]
                for p2 in hardware_graph.neighbors(p1):
                    if p2 in available_physical:
                        placement[q2] = p2
                        available_physical.remove(p2)
                        break
        
        # Kalan qubit'leri herhangi bir boş fiziksel qubit'e yerleştir
        for q in logical_qubits:
            if q not in placement:
                if not available_physical:
                    raise ValueError("Not enough physical qubits available for mapping")
                p = available_physical.pop()
                placement[q] = p
        
        return placement
    
    def _apply_mapping(self, circuit, qubit_mapping):
        """
        Eşlemeyi devreye uygular
        
        Args:
            circuit: Uygulanacak devre
            qubit_mapping: {mantıksal_qubit_id: fiziksel_qubit_id} eşlemesi
            
        Returns:
            Circuit: Eşlemesi uygulanmış devre
        """
        # Qubit'leri eşleme bilgisiyle güncelle
        for qubit in circuit.qubits:
            if qubit.id in qubit_mapping:
                qubit.mapped_to = qubit_mapping[qubit.id]
        
        return circuit
    
    def _is_executable(self, gate, current_mapping, hardware_graph):
        """
        Kapının mevcut eşleme ile doğrudan yürütülebilir olup olmadığını kontrol eder
        
        Args:
            gate: Kontrol edilecek kapı
            current_mapping: Mevcut {mantıksal_qubit_id: fiziksel_qubit_id} eşlemesi
            hardware_graph: Donanım grafiği
            
        Returns:
            bool: Kapı doğrudan yürütülebilir mi?
        """
        # Tek qubit kapıları her zaman yürütülebilir
        if len(gate.qubits) <= 1:
            return True
            
        # Çok qubitli kapılar için, tüm qubit çiftlerinin donanımda bağlantılı olması gerekir
        for i in range(len(gate.qubits) - 1):
            for j in range(i + 1, len(gate.qubits)):
                q1_id = gate.qubits[i].id
                q2_id = gate.qubits[j].id
                
                # Eşlenmiş fiziksel qubit'leri al
                p1_id = current_mapping[q1_id]
                p2_id = current_mapping[q2_id]
                
                # Fiziksel qubit'ler donanımda bağlantılı mı?
                if not hardware_graph.has_edge(p1_id, p2_id):
                    return False
                    
        return True
    
    def _find_swaps(self, gate, current_mapping, hardware_graph):
        """
        Kapıyı yürütülebilir hale getirmek için gerekli SWAP'ları bulur
        
        Args:
            gate: Yönlendirilecek kapı
            current_mapping: Mevcut {mantıksal_qubit_id: fiziksel_qubit_id} eşlemesi
            hardware_graph: Donanım grafiği
            
        Returns:
            list: Gerekli SWAP'lar listesi [(q1_id, q2_id), ...]
        """
        # Basit bir yönlendirme algoritması:
        # 1. Her qubit çifti için, aralarındaki en kısa yolu bul
        # 2. En az toplam SWAP gerektiren çözümü seç
        
        # Bu örnekte, CNOT kapısı gibi iki qubitli kapılara odaklanıyoruz
        if len(gate.qubits) != 2:
            self.logger.warning(f"Complex routing for gates with {len(gate.qubits)} qubits is not fully implemented")
            return []
            
        q1_id = gate.qubits[0].id
        q2_id = gate.qubits[1].id
        
        # Eşlenmiş fiziksel qubit'leri al
        p1_id = current_mapping[q1_id]
        p2_id = current_mapping[q2_id]
        
        # Fiziksel qubit'ler zaten bağlantılıysa, SWAP gerekmez
        if hardware_graph.has_edge(p1_id, p2_id):
            return []
            
        # İki fiziksel qubit arasındaki en kısa yolu bul
        try:
            path = nx.shortest_path(hardware_graph, p1_id, p2_id)
        except nx.NetworkXNoPath:
            raise ValueError(f"No path between physical qubits {p1_id} and {p2_id}")
            
        # Yol üzerindeki SWAP'ları oluştur
        # En basit strateji: Yol üzerindeki her adımda SWAP uygula
        swaps = []
        
        # SWAP sayısını azaltmak için, yolun ortasına doğru hareket et
        if len(path) <= 2:
            # Doğrudan bağlantılı
            return []
            
        # Yolun ortasını hedefle
        mid_point = len(path) // 2
        
        # p1'i orta noktaya taşımak için SWAP'lar
        for i in range(mid_point - 1):
            swaps.append((path[i], path[i+1]))
            
        # p2'yi orta noktaya taşımak için SWAP'lar (ters yönden)
        for i in range(len(path) - 1, mid_point, -1):
            swaps.append((path[i], path[i-1]))
            
        return swaps
    
    def get_stats(self):
        """
        Yerleşim istatistiklerini döndürür
        
        Returns:
            dict: Yerleşim istatistikleri
        """
        return self.stats
    
    def reset_stats(self):
        """Yerleşim istatistiklerini sıfırlar"""
        self.stats = {
            "mapped_circuits": 0,
            "total_swaps": 0,
            "total_mapped_qubits": 0
        } 