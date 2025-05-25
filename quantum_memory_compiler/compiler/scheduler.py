"""
GateScheduler modülü
=================

Kuantum kapılarının zamanlamasını optimize eden sınıf.
"""

import networkx as nx
from collections import defaultdict


class GateScheduler:
    """
    Kuantum kapılarının zamanlamasını optimize eden sınıf
    
    Kapı paralelliğini maksimize ederek devreyi sığıştırır.
    """
    
    def __init__(self):
        """GateScheduler nesnesini başlatır"""
        self.stats = {
            "scheduled_circuits": 0,
            "total_depth_reduction": 0,
            "avg_depth_reduction": 0.0
        }
    
    def schedule(self, circuit):
        """
        Devre kapılarını optimize eder
        
        Args:
            circuit: Zamanlanacak devre
            
        Returns:
            Circuit: Zamanlanmış devre
        """
        # Devrenin kopyasını oluştur
        scheduled_circuit = circuit.copy()
        
        # Bağımlılık grafiğini oluştur
        dependency_graph = self._build_dependency_graph(scheduled_circuit)
        
        # ASAP (olabildiğince erken) zamanlama algoritması uygula
        self._schedule_asap(scheduled_circuit, dependency_graph)
        
        # İstatistikleri güncelle
        initial_depth = circuit.depth
        final_depth = scheduled_circuit.depth
        depth_reduction = max(0, initial_depth - final_depth)
        
        self.stats["scheduled_circuits"] += 1
        self.stats["total_depth_reduction"] += depth_reduction
        self.stats["avg_depth_reduction"] = (self.stats["total_depth_reduction"] / 
                                          self.stats["scheduled_circuits"])
        
        return scheduled_circuit
    
    def _build_dependency_graph(self, circuit):
        """
        Kapılar arası bağımlılık grafiğini oluşturur
        
        Args:
            circuit: Devre
            
        Returns:
            nx.DiGraph: Yönlü bağımlılık grafiği
        """
        graph = nx.DiGraph()
        
        # Tüm kapıları düğüm olarak ekle
        for i, gate in enumerate(circuit.gates):
            graph.add_node(i, gate=gate)
        
        # Her qubit için kapı sırasını takip et
        qubit_last_gate = {}
        
        # Sort gates by time
        sorted_gates = sorted(enumerate(circuit.gates), key=lambda x: x[1].time)
        
        # Kapılar arası bağımlılıkları ekle
        for gate_idx, gate in sorted_gates:
            # Bu kapının qubit'leri
            for qubit in gate.qubits:
                # Bu qubit'in son kapısı varsa, kenar ekle
                if qubit in qubit_last_gate:
                    last_gate_idx = qubit_last_gate[qubit]
                    graph.add_edge(last_gate_idx, gate_idx)
                
                # Bu qubit için son kapıyı güncelle
                qubit_last_gate[qubit] = gate_idx
        
        return graph
    
    def _schedule_asap(self, circuit, dependency_graph):
        """
        ASAP (As Soon As Possible) zamanlama algoritmasını uygular
        
        Args:
            circuit: Zamanlanacak devre
            dependency_graph: Bağımlılık grafiği
        """
        # Topolojik sıralama yap
        try:
            topological_order = list(nx.topological_sort(dependency_graph))
        except nx.NetworkXUnfeasible:
            # Döngü varsa, normal sırayı kullan
            topological_order = list(range(len(circuit.gates)))
        
        # Her düğümün en erken zamanını hesapla
        earliest_time = {}
        
        for node in topological_order:
            # Düğümün en erken zamanı: tüm öncüllerinin bitiş zamanının maksimumu
            predecessors = list(dependency_graph.predecessors(node))
            
            if not predecessors:
                # Öncüsü yoksa, zaman 0'da başlayabilir
                earliest_time[node] = 0
            else:
                # Öncülerin bitiş zamanlarının maksimumunu al
                max_pred_end_time = max(earliest_time[pred] + circuit.gates[pred].duration 
                                      for pred in predecessors)
                earliest_time[node] = max_pred_end_time
        
        # Kapıları yeni zamanlarıyla güncelle
        for node, time in earliest_time.items():
            circuit.gates[node].time = time
        
        # Devre derinliğini güncelle
        circuit.depth = circuit.calculate_depth()
    
    def _schedule_alap(self, circuit, dependency_graph):
        """
        ALAP (As Late As Possible) zamanlama algoritmasını uygular
        
        Args:
            circuit: Zamanlanacak devre
            dependency_graph: Bağımlılık grafiği
        """
        # Ters topolojik sıralama yap
        try:
            reverse_topological_order = list(reversed(list(nx.topological_sort(dependency_graph))))
        except nx.NetworkXUnfeasible:
            # Döngü varsa, ters normal sırayı kullan
            reverse_topological_order = list(reversed(range(len(circuit.gates))))
        
        # Devre derinliğini hesapla
        circuit_depth = circuit.calculate_depth()
        
        # Her düğümün en geç zamanını hesapla
        latest_time = {}
        
        for node in reverse_topological_order:
            # Düğümün en geç zamanı: tüm ardıllarının başlangıç zamanının minimumu
            successors = list(dependency_graph.successors(node))
            
            if not successors:
                # Ardılı yoksa, devrenin sonunda olabilir
                latest_time[node] = circuit_depth - circuit.gates[node].duration
            else:
                # Ardılların başlangıç zamanlarının minimumunu al
                min_succ_start_time = min(latest_time[succ] for succ in successors)
                latest_time[node] = min_succ_start_time - circuit.gates[node].duration
        
        # Kapıları yeni zamanlarıyla güncelle
        for node, time in latest_time.items():
            circuit.gates[node].time = max(0, time)  # Negatif olmadığından emin ol
        
        # Devre derinliğini güncelle
        circuit.depth = circuit.calculate_depth()
    
    def get_stats(self):
        """
        Zamanlama istatistiklerini döndürür
        
        Returns:
            dict: Zamanlama istatistikleri
        """
        return self.stats
    
    def reset_stats(self):
        """Zamanlama istatistiklerini sıfırlar"""
        self.stats = {
            "scheduled_circuits": 0,
            "total_depth_reduction": 0,
            "avg_depth_reduction": 0.0
        } 