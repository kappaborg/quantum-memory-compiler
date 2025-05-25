"""
Qubit Tahsis Algoritmaları modülü
==============================

Kuantum devreleri için farklı qubit tahsis stratejilerini içerir.
"""

import networkx as nx
from abc import ABC, abstractmethod
from collections import defaultdict

from ..core.qubit import QubitType, MemoryLevel


class QubitAllocator(ABC):
    """
    Qubit tahsis algoritmaları için soyut temel sınıf.
    
    Farklı tahsis stratejileri bu sınıftan türetilir.
    """
    
    @abstractmethod
    def allocate(self, circuit, memory_hierarchy):
        """
        Verilen devre için qubit tahsisi yapar
        
        Args:
            circuit: Tahsis yapılacak devre
            memory_hierarchy: Kuantum bellek hiyerarşisi
            
        Returns:
            dict: Tahsis planı (mantıksal qubit -> (fiziksel qubit, bellek seviyesi))
        """
        pass
    
    @abstractmethod
    def get_name(self):
        """Tahsis stratejisinin adını döndürür"""
        pass
    
    @staticmethod
    def create(strategy_name):
        """
        Belirtilen tahsis stratejisini oluşturur
        
        Args:
            strategy_name: Strateji adı ("static", "lifetime", "dynamic")
            
        Returns:
            QubitAllocator: Tahsis stratejisi nesnesi
        """
        if strategy_name == "static":
            return StaticAllocator()
        elif strategy_name == "lifetime":
            return LifetimeAllocator()
        elif strategy_name == "dynamic":
            return DynamicAllocator()
        else:
            raise ValueError(f"Bilinmeyen tahsis stratejisi: {strategy_name}")


class StaticAllocator(QubitAllocator):
    """
    Statik qubit tahsis stratejisi
    
    Tüm qubit'leri statik olarak tahsis eder, her mantıksal qubit için bir fiziksel qubit kullanır.
    """
    
    def allocate(self, circuit, memory_hierarchy):
        """
        Statik qubit tahsisi yapar
        
        Args:
            circuit: Tahsis yapılacak devre
            memory_hierarchy: Kuantum bellek hiyerarşisi
            
        Returns:
            dict: Tahsis planı (mantıksal qubit -> (fiziksel qubit, bellek seviyesi))
        """
        allocation_plan = {}
        
        # Her mantıksal qubit için bir fiziksel qubit tahsis et
        for logical_qubit in circuit.qubits:
            # Tüm qubit'ler L1'de başlasın
            allocation_plan[logical_qubit] = (logical_qubit.id, "L1")
        
        return allocation_plan
    
    def get_name(self):
        return "Static Allocator"


class LifetimeAllocator(QubitAllocator):
    """
    Yaşam süresi tabanlı qubit tahsis stratejisi
    
    Qubit yaşam sürelerine göre analiz yapar ve qubit'leri ilk-uygun stratejisiyle paketler.
    """
    
    def allocate(self, circuit, memory_hierarchy):
        """
        Yaşam süresi tabanlı qubit tahsisi yapar
        
        Args:
            circuit: Tahsis yapılacak devre
            memory_hierarchy: Kuantum bellek hiyerarşisi
            
        Returns:
            dict: Tahsis planı (mantıksal qubit -> (fiziksel qubit, bellek seviyesi))
        """
        allocation_plan = {}
        
        # 1. Her qubit için yaşam süresi aralığını hesapla
        qubit_lifetimes = {}
        for qubit in circuit.qubits:
            first_time, last_time = circuit.get_qubit_lifetime(qubit)
            lifetime = last_time - first_time
            qubit_lifetimes[qubit] = (first_time, last_time, lifetime)
        
        # 2. Qubit'leri başlangıç zamanlarına göre sırala
        sorted_qubits = sorted(circuit.qubits, key=lambda q: qubit_lifetimes[q][0])
        
        # 3. Fiziksel qubit havuzu
        physical_qubits = []
        physical_usage = {}  # Fiziksel qubit -> son kullanım zamanı
        
        # 4. First-Fit paketleme uygula
        for logical_qubit in sorted_qubits:
            start_time, end_time, _ = qubit_lifetimes[logical_qubit]
            
            # Yaşam süresine göre uygun bellek seviyesini belirle
            lifetime = end_time - start_time
            memory_level = memory_hierarchy.get_best_level_for_qubit(logical_qubit, lifetime)
            
            # Uygun fiziksel qubit bul
            assigned = False
            for physical_id in physical_qubits:
                last_usage = physical_usage.get(physical_id, 0)
                
                if last_usage <= start_time:  # Çakışma yok
                    # Bu fiziksel qubit'i kullan
                    allocation_plan[logical_qubit] = (physical_id, memory_level)
                    physical_usage[physical_id] = end_time
                    assigned = True
                    break
            
            if not assigned:
                # Yeni fiziksel qubit gerekli
                new_physical_id = len(physical_qubits)
                physical_qubits.append(new_physical_id)
                allocation_plan[logical_qubit] = (new_physical_id, memory_level)
                physical_usage[new_physical_id] = end_time
        
        return allocation_plan
    
    def get_name(self):
        return "Lifetime-based Allocator"


class DynamicAllocator(QubitAllocator):
    """
    Dinamik qubit tahsis stratejisi
    
    Devre aşamalara bölünür ve her aşama için ayrı tahsis yapılır, aşamalar arası durumlar taşınır.
    """
    
    def allocate(self, circuit, memory_hierarchy):
        """
        Dinamik qubit tahsisi yapar
        
        Args:
            circuit: Tahsis yapılacak devre
            memory_hierarchy: Kuantum bellek hiyerarşisi
            
        Returns:
            dict: Tahsis planı (mantıksal qubit -> (fiziksel qubit, bellek seviyesi, zaman aralığı listesi))
        """
        # Sonuç formatı: {logical_qubit: [(physical_id, memory_level, (start_time, end_time)), ...]}
        allocation_plan = defaultdict(list)
        
        # 1. Devreyi zaman dilimlerine böl
        phases = self._divide_into_phases(circuit)
        
        # 2. Her aşama için ayrı tahsis yap
        for phase_start, phase_end, active_qubits in phases:
            # Bu aşamada aktif olan qubit'ler
            phase_qubits = active_qubits
            
            # Bu aşama için yeniden tahsis yap
            sub_allocation = self._allocate_phase(circuit, memory_hierarchy, phase_qubits, phase_start, phase_end)
            
            # Sonuçları ana plana ekle
            for logical_qubit, (physical_id, memory_level) in sub_allocation.items():
                allocation_plan[logical_qubit].append((physical_id, memory_level, (phase_start, phase_end)))
        
        return dict(allocation_plan)
    
    def _divide_into_phases(self, circuit, max_phases=10):
        """
        Devreyi mantıklı aşamalara böler
        
        Args:
            circuit: Bölünecek devre
            max_phases: Maksimum aşama sayısı
            
        Returns:
            list: Aşamalar listesi [(başlangıç, bitiş, aktif_qubit'ler), ...]
        """
        # Basit bir bölme stratejisi: Devre süresini max_phases'e böl
        total_depth = circuit.calculate_depth()
        if total_depth == 0:
            # Boş devre
            return []
        
        # Aşama uzunluğunu belirle
        phase_length = total_depth / min(max_phases, total_depth)
        phases = []
        
        for i in range(min(max_phases, total_depth)):
            phase_start = i * phase_length
            phase_end = (i + 1) * phase_length
            
            # Bu aşamada aktif olan qubit'leri bul
            active_qubits = []
            for qubit in circuit.qubits:
                first_time, last_time = circuit.get_qubit_lifetime(qubit)
                if last_time >= phase_start and first_time <= phase_end:
                    active_qubits.append(qubit)
            
            phases.append((phase_start, phase_end, active_qubits))
        
        return phases
    
    def _allocate_phase(self, circuit, memory_hierarchy, phase_qubits, phase_start, phase_end):
        """
        Belirli bir aşama için qubit tahsisi yapar
        
        Args:
            circuit: Devre
            memory_hierarchy: Bellek hiyerarşisi
            phase_qubits: Bu aşamada aktif olan qubit'ler
            phase_start: Aşama başlangıç zamanı
            phase_end: Aşama bitiş zamanı
            
        Returns:
            dict: Bu aşama için tahsis planı
        """
        phase_allocation = {}
        
        # Bu aşamadaki qubit'ler arası etkileşim grafiği oluştur
        interaction_graph = self._build_interaction_graph(circuit, phase_qubits, phase_start, phase_end)
        
        # Graf renklendirme algoritması kullan (minimum sayıda renk)
        coloring = nx.coloring.greedy_color(interaction_graph, strategy="largest_first")
        
        # Her renk bir fiziksel qubit'e karşılık gelir
        for logical_qubit, color in coloring.items():
            # Yaşam süresine göre bellek seviyesini seç
            first_time, last_time = circuit.get_qubit_lifetime(logical_qubit)
            lifetime = min(last_time, phase_end) - max(first_time, phase_start)
            memory_level = memory_hierarchy.get_best_level_for_qubit(logical_qubit, lifetime)
            
            phase_allocation[logical_qubit] = (color, memory_level)
        
        return phase_allocation
    
    def _build_interaction_graph(self, circuit, qubits, start_time, end_time):
        """
        Qubit'ler arası etkileşim grafiğini oluşturur
        
        Args:
            circuit: Devre
            qubits: Grafiğe dahil edilecek qubit'ler
            start_time: Başlangıç zamanı
            end_time: Bitiş zamanı
            
        Returns:
            nx.Graph: Etkileşim grafiği
        """
        graph = nx.Graph()
        
        # Qubit'leri düğüm olarak ekle
        for qubit in qubits:
            graph.add_node(qubit)
        
        # Belirli zaman aralığındaki çok-qubit kapılarını bul
        gates = circuit.get_gates_in_time_range(start_time, end_time)
        
        # Kapıları kenar olarak ekle
        for gate in gates:
            if len(gate.qubits) >= 2:
                # Bu bir çok-qubit kapısı
                for i in range(len(gate.qubits) - 1):
                    for j in range(i + 1, len(gate.qubits)):
                        q1, q2 = gate.qubits[i], gate.qubits[j]
                        if q1 in qubits and q2 in qubits:
                            graph.add_edge(q1, q2)
        
        return graph
    
    def get_name(self):
        return "Dynamic Phase-based Allocator"


class RecyclingAllocator(QubitAllocator):
    """
    Qubit yeniden kullanım stratejisi
    
    Qubit'lerin sıfırlanmasını (reset) ve yeniden kullanımını optimize eder.
    """
    
    def __init__(self, base_allocator="lifetime"):
        """
        RecyclingAllocator nesnesini başlatır
        
        Args:
            base_allocator: Temel tahsis stratejisi
        """
        self.base_allocator = QubitAllocator.create(base_allocator)
    
    def allocate(self, circuit, memory_hierarchy):
        """
        Qubit tahsisi yapar ve sıfırlama operasyonları ekler
        
        Args:
            circuit: Tahsis yapılacak devre
            memory_hierarchy: Kuantum bellek hiyerarşisi
            
        Returns:
            tuple: (tahsis planı, reset operasyonları listesi)
        """
        # Önce temel tahsis stratejisini kullan
        base_allocation = self.base_allocator.allocate(circuit, memory_hierarchy)
        
        # Reset eklenecek noktaları belirle
        reset_operations = self._identify_reset_points(circuit, base_allocation)
        
        return (base_allocation, reset_operations)
    
    def _identify_reset_points(self, circuit, allocation):
        """
        Qubit'lerin sıfırlanabileceği noktaları belirler
        
        Args:
            circuit: Devre
            allocation: Tahsis planı
            
        Returns:
            list: Reset operasyonları listesi [(qubit, zaman), ...]
        """
        reset_points = []
        
        # Her qubit için son kullanım zamanını belirle
        for qubit in circuit.qubits:
            first_time, last_time = circuit.get_qubit_lifetime(qubit)
            
            if last_time < circuit.calculate_depth():
                # Bu qubit'in son kullanımından sonra hala devre devam ediyor
                # Bu noktada reset eklenebilir
                reset_points.append((qubit, last_time))
        
        return reset_points
    
    def get_name(self):
        return f"Recycling Allocator (base: {self.base_allocator.get_name()})"


class HierarchicalAllocator(QubitAllocator):
    """
    Hiyerarşik bellek yönetimini kullanan tahsis stratejisi
    
    Qubit'leri bellek hiyerarşisinde optimize eder ve katmanlar arası transferleri planlar.
    """
    
    def __init__(self, base_allocator="lifetime"):
        """
        HierarchicalAllocator nesnesini başlatır
        
        Args:
            base_allocator: Temel tahsis stratejisi
        """
        self.base_allocator = QubitAllocator.create(base_allocator)
    
    def allocate(self, circuit, memory_hierarchy):
        """
        Qubit tahsisi yapar ve bellek hiyerarşisi transferlerini planlar
        
        Args:
            circuit: Tahsis yapılacak devre
            memory_hierarchy: Kuantum bellek hiyerarşisi
            
        Returns:
            tuple: (tahsis planı, transfer operasyonları listesi)
        """
        # Önce temel tahsis stratejisini kullan
        base_allocation = self.base_allocator.allocate(circuit, memory_hierarchy)
        
        # Bellek hiyerarşisi transferlerini planla
        transfers = self._plan_memory_transfers(circuit, base_allocation, memory_hierarchy)
        
        return (base_allocation, transfers)
    
    def _plan_memory_transfers(self, circuit, allocation, memory_hierarchy):
        """
        Bellek hiyerarşisi transferlerini planlar
        
        Args:
            circuit: Devre
            allocation: Tahsis planı
            memory_hierarchy: Bellek hiyerarşisi
            
        Returns:
            list: Transfer operasyonları listesi [(qubit, kaynak_seviye, hedef_seviye, zaman), ...]
        """
        transfers = []
        total_depth = circuit.calculate_depth()
        
        # Dinamik tahsis stratejisinde, her qubit için zaman dilimlerine göre bellek seviyelerini planla
        if isinstance(self.base_allocator, DynamicAllocator):
            for qubit, assignments in allocation.items():
                current_level = None
                
                # Her zaman dilimi için
                for physical_id, memory_level, (start_time, end_time) in sorted(assignments, key=lambda x: x[2][0]):
                    if current_level is not None and current_level != memory_level:
                        # Seviye değişimi gerekiyor
                        transfers.append((qubit, current_level, memory_level, start_time))
                    
                    current_level = memory_level
        else:
            # Diğer tahsis stratejileri için, qubit'in yaşam süresine göre bellek seviyesini belirle
            for qubit, (physical_id, memory_level) in allocation.items():
                first_time, last_time = circuit.get_qubit_lifetime(qubit)
                lifetime = last_time - first_time
                remaining_lifetime = total_depth - first_time
                
                # Başlangıçta L1'de
                initial_level = "L1"
                
                # Uzun süreli kullanım için bellek seviyesini değiştir
                if remaining_lifetime > memory_hierarchy.levels["L1"].coherence_time:
                    target_level = memory_hierarchy.get_best_level_for_qubit(qubit, remaining_lifetime)
                    
                    if target_level != initial_level:
                        # Başlangıçta L1'den hedef seviyeye transfer
                        transfers.append((qubit, initial_level, target_level, first_time))
                        
                        # İşlem bitince geri L1'e transfer
                        transfers.append((qubit, target_level, "L1", last_time))
        
        return transfers
    
    def get_name(self):
        return f"Hierarchical Memory Allocator (base: {self.base_allocator.get_name()})" 