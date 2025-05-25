"""
Kuantum Derleyici modülü
=====================

Kuantum devreleri için hafıza-bilinçli derleyici sınıfı.
"""

import logging
from enum import Enum, auto

from ..core.circuit import Circuit
from ..memory.manager import MemoryManager
from ..memory.hierarchy import MemoryHierarchy
from ..memory.allocation import QubitAllocator, LifetimeAllocator
from ..memory.recycling import QubitRecycler, RecyclingStrategy
from .optimizer import Optimizer
from .mapper import QubitMapper
from .scheduler import GateScheduler


class CompilationStage(Enum):
    """Derleyici aşamaları"""
    PREPROCESSING = auto()    # Ön işleme
    MEMORY_PLANNING = auto()  # Bellek planlama
    GATE_OPTIMIZATION = auto() # Kapı optimizasyonu
    MAPPING = auto()          # Qubit yerleşimi
    SCHEDULING = auto()       # Kapı zamanlaması
    ROUTING = auto()          # Kapı yönlendirme
    POSTPROCESSING = auto()   # Son işleme


class CompilationTarget(Enum):
    """Derleyici hedefleri"""
    MEMORY_EFFICIENCY = auto()  # Bellek verimliliği
    CIRCUIT_DEPTH = auto()      # Devre derinliği minimizasyonu
    GATE_COUNT = auto()         # Kapı sayısı minimizasyonu
    FIDELITY = auto()           # Sadakat maksimizasyonu
    BALANCED = auto()           # Dengeli optimizasyon


class QuantumCompiler:
    """
    Kuantum devreleri için hafıza-bilinçli derleyici
    
    Bu derleyici, bellek yönetimi ve qubit tahsisi konusunda optimize edilmiş kuantum 
    devreleri üretir.
    """
    
    def __init__(self, memory_hierarchy=None, allocator_strategy="lifetime", 
                 recycling_strategy=RecyclingStrategy.RESET_BASED,
                 optimization_level=1, target=CompilationTarget.BALANCED):
        """
        QuantumCompiler nesnesini başlatır
        
        Args:
            memory_hierarchy: Kuantum bellek hiyerarşisi
            allocator_strategy: Qubit tahsis stratejisi
            recycling_strategy: Qubit geri dönüşüm stratejisi
            optimization_level: Optimizasyon seviyesi (0-3)
            target: Derleyici hedefi
        """
        # Bellek yönetimi bileşenleri
        self.memory_hierarchy = memory_hierarchy if memory_hierarchy else MemoryHierarchy()
        self.allocator = QubitAllocator.create(allocator_strategy)
        self.recycler = QubitRecycler(recycling_strategy)
        self.memory_manager = MemoryManager(self.memory_hierarchy, allocator_strategy)
        
        # Optimizasyon bileşenleri
        self.optimizer = Optimizer(optimization_level)
        self.mapper = QubitMapper()
        self.scheduler = GateScheduler()
        
        # Derleyici yapılandırması
        self.optimization_level = optimization_level
        self.target = target
        
        # İzleme ve loglama
        self.compilation_history = []
        self.logger = logging.getLogger("QuantumCompiler")
        self.logger.setLevel(logging.INFO)
    
    def compile(self, circuit, hardware_model=None):
        """
        Kuantum devresini hafıza-bilinçli şekilde derler
        
        Args:
            circuit: Derlenmek üzere giriş devresi
            hardware_model: Hedef donanım modeli
            
        Returns:
            Circuit: Derlenmiş devre
        """
        self.logger.info(f"Compiling circuit '{circuit.name}' (qubits: {circuit.width}, depth: {circuit.depth})")
        
        # İşlem öncesi devreyi kaydet
        original_circuit = circuit.copy()
        
        # 1. Ön işleme aşaması
        self.logger.info("Stage 1: Preprocessing")
        preprocessed_circuit = self._preprocessing(circuit)
        
        # 2. Bellek planlama aşaması
        self.logger.info("Stage 2: Memory planning")
        memory_planned_circuit = self._memory_planning(preprocessed_circuit)
        
        # 3. Kapı optimizasyonu aşaması
        self.logger.info("Stage 3: Gate optimization")
        optimized_circuit = self._gate_optimization(memory_planned_circuit)
        
        # 4. Qubit yerleşimi aşaması
        self.logger.info("Stage 4: Qubit mapping")
        mapped_circuit = self._qubit_mapping(optimized_circuit, hardware_model)
        
        # 5. Kapı zamanlaması aşaması
        self.logger.info("Stage 5: Gate scheduling")
        scheduled_circuit = self._gate_scheduling(mapped_circuit)
        
        # 6. Kapı yönlendirme aşaması
        self.logger.info("Stage 6: Qubit routing")
        routed_circuit = self._qubit_routing(scheduled_circuit, hardware_model)
        
        # 7. Son işleme aşaması
        self.logger.info("Stage 7: Postprocessing")
        final_circuit = self._postprocessing(routed_circuit)
        
        # İşlem sonrası meta verileri ayarla
        final_circuit.is_transpiled = True
        final_circuit.original_circuit = original_circuit
        
        # Derleme istatistiklerini kaydet
        compilation_result = {
            'input_circuit': {
                'width': circuit.width,
                'depth': circuit.depth,
                'gate_count': len(circuit.gates)
            },
            'output_circuit': {
                'width': final_circuit.width,
                'depth': final_circuit.depth,
                'gate_count': len(final_circuit.gates)
            },
            'qubit_reduction': circuit.width - final_circuit.width,
            'depth_change': final_circuit.depth - circuit.depth,
            'gate_count_change': len(final_circuit.gates) - len(circuit.gates)
        }
        
        self.compilation_history.append(compilation_result)
        
        self.logger.info(f"Compilation completed: {circuit.width} -> {final_circuit.width} qubits, "
                        f"depth {circuit.depth} -> {final_circuit.depth}")
        
        return final_circuit
    
    def _preprocessing(self, circuit):
        """
        Ön işleme aşaması
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Ön işleme tamamlanmış devre
        """
        # Devrenin kopyasını oluştur
        preprocessed_circuit = circuit.copy()
        
        # Temel kapı optimizasyonları ve sadeleştirmeler
        # Örneğin, I kapılarını kaldır, ardışık aynı kapıları sadeleştir
        cleaned_circuit = self.optimizer.simplify_gates(preprocessed_circuit)
        
        return cleaned_circuit
    
    def _memory_planning(self, circuit):
        """
        Bellek planlama aşaması
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Bellek planlaması tamamlanmış devre
        """
        # Devrenin kopyasını oluştur
        memory_planned_circuit = circuit.copy()
        
        # 1. Qubit yaşam süreleri analizi
        qubit_lifetimes = memory_planned_circuit.calculate_qubit_usage()
        
        # 2. Bellek hiyerarşisi için qubit tahsisi planla
        allocation_plan = self.allocator.allocate(memory_planned_circuit, self.memory_hierarchy)
        
        # 3. Qubit geri dönüşümünü optimize et
        recycled_circuit, saved_qubits = self.recycler.optimize(memory_planned_circuit)
        
        self.logger.info(f"Memory planning: saved {saved_qubits} qubits through recycling")
        
        return recycled_circuit
    
    def _gate_optimization(self, circuit):
        """
        Kapı optimizasyonu aşaması
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Kapı optimizasyonu tamamlanmış devre
        """
        # Devrenin kopyasını oluştur
        optimized_circuit = circuit.copy()
        
        # Optimizasyon seviyesine göre farklı optimizasyonlar uygula
        if self.optimization_level >= 1:
            # Seviye 1: Temel optimizasyonlar
            optimized_circuit = self.optimizer.commute_gates(optimized_circuit)
            
        if self.optimization_level >= 2:
            # Seviye 2: Orta düzey optimizasyonlar
            optimized_circuit = self.optimizer.merge_rotations(optimized_circuit)
            
        if self.optimization_level >= 3:
            # Seviye 3: İleri düzey optimizasyonlar
            optimized_circuit = self.optimizer.template_matching(optimized_circuit)
        
        # Optimizasyon istatistiklerini raporla
        gate_reduction = len(circuit.gates) - len(optimized_circuit.gates)
        self.logger.info(f"Gate optimization: removed {gate_reduction} gates")
        
        return optimized_circuit
    
    def _qubit_mapping(self, circuit, hardware_model):
        """
        Qubit yerleşimi aşaması
        
        Args:
            circuit: İşlenecek devre
            hardware_model: Hedef donanım modeli
            
        Returns:
            Circuit: Qubit yerleşimi tamamlanmış devre
        """
        # Donanım modeli yoksa, bu aşamayı atla
        if hardware_model is None:
            return circuit.copy()
        
        # Qubit'leri fiziksel qubit'lere yerleştir
        mapped_circuit = self.mapper.map_qubits(circuit, hardware_model)
        
        # Yerleşim istatistiklerini raporla
        self.logger.info(f"Qubit mapping: mapped {mapped_circuit.width} logical qubits to physical qubits")
        
        return mapped_circuit
    
    def _gate_scheduling(self, circuit):
        """
        Kapı zamanlaması aşaması
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Kapı zamanlaması tamamlanmış devre
        """
        # Kapıları paralel yürütülecek şekilde yeniden zamanla
        scheduled_circuit = self.scheduler.schedule(circuit)
        
        # Zamanlama sonuçlarını raporla
        depth_reduction = circuit.depth - scheduled_circuit.depth
        self.logger.info(f"Gate scheduling: reduced depth by {depth_reduction} units")
        
        return scheduled_circuit
    
    def _qubit_routing(self, circuit, hardware_model):
        """
        Kapı yönlendirme aşaması
        
        Args:
            circuit: İşlenecek devre
            hardware_model: Hedef donanım modeli
            
        Returns:
            Circuit: Kapı yönlendirmesi tamamlanmış devre
        """
        # Donanım modeli yoksa, bu aşamayı atla
        if hardware_model is None:
            return circuit.copy()
        
        # Çok-qubitli kapılar için SWAP kapıları ekleyerek uyumlu hale getir
        routed_circuit = self.mapper.route_gates(circuit, hardware_model)
        
        # SWAP sayısını raporla
        swap_count = routed_circuit.swap_count
        self.logger.info(f"Qubit routing: inserted {swap_count} SWAP gates")
        
        return routed_circuit
    
    def _postprocessing(self, circuit):
        """
        Son işleme aşaması
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Son işleme tamamlanmış devre
        """
        # Devrenin kopyasını oluştur
        final_circuit = circuit.copy()
        
        # Gereksiz bariyer ve ID kapılarını kaldır
        final_circuit = self.optimizer.clean_circuit(final_circuit)
        
        # Son optimizasyonları uygula
        if self.optimization_level >= 1:
            final_circuit = self.optimizer.final_optimization(final_circuit)
        
        return final_circuit
    
    def get_compilation_stats(self):
        """
        Derleme istatistiklerini döndürür
        
        Returns:
            list: Derleme istatistikleri listesi
        """
        return self.compilation_history
    
    def get_last_compilation_stats(self):
        """
        Son derleme istatistiklerini döndürür
        
        Returns:
            dict: Son derleme istatistikleri
        """
        if not self.compilation_history:
            return None
        
        return self.compilation_history[-1]
    
    def reset_stats(self):
        """Derleme istatistiklerini sıfırlar"""
        self.compilation_history = []
        self.recycler.reset_stats()
        self.optimizer.reset_stats()
        self.mapper.reset_stats() if hasattr(self.mapper, 'reset_stats') else None
        self.scheduler.reset_stats() if hasattr(self.scheduler, 'reset_stats') else None 

    def _preprocessing(self, circuit):
        """
        Ön işleme aşaması
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Ön işleme tamamlanmış devre
        """
        # Devrenin kopyasını oluştur
        preprocessed_circuit = circuit.copy()
        
        # Temel kapı optimizasyonları ve sadeleştirmeler
        # Örneğin, I kapılarını kaldır, ardışık aynı kapıları sadeleştir
        cleaned_circuit = self.optimizer.simplify_gates(preprocessed_circuit)
        
        # Sort gates by time
        sorted_gates = sorted(enumerate(cleaned_circuit.gates), key=lambda x: x[1].time)
        
        return cleaned_circuit
    
    def _memory_planning(self, circuit):
        """
        Bellek planlama aşaması
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Bellek planlaması tamamlanmış devre
        """
        # Devrenin kopyasını oluştur
        memory_planned_circuit = circuit.copy()
        
        # 1. Qubit yaşam süreleri analizi
        qubit_lifetimes = memory_planned_circuit.calculate_qubit_usage()
        
        # 2. Bellek hiyerarşisi için qubit tahsisi planla
        allocation_plan = self.allocator.allocate(memory_planned_circuit, self.memory_hierarchy)
        
        # 3. Qubit geri dönüşümünü optimize et
        recycled_circuit, saved_qubits = self.recycler.optimize(memory_planned_circuit)
        
        self.logger.info(f"Memory planning: saved {saved_qubits} qubits through recycling")
        
        return recycled_circuit
    
    def _gate_optimization(self, circuit):
        """
        Kapı optimizasyonu aşaması
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Kapı optimizasyonu tamamlanmış devre
        """
        # Devrenin kopyasını oluştur
        optimized_circuit = circuit.copy()
        
        # Optimizasyon seviyesine göre farklı optimizasyonlar uygula
        if self.optimization_level >= 1:
            # Seviye 1: Temel optimizasyonlar
            optimized_circuit = self.optimizer.commute_gates(optimized_circuit)
            
        if self.optimization_level >= 2:
            # Seviye 2: Orta düzey optimizasyonlar
            optimized_circuit = self.optimizer.merge_rotations(optimized_circuit)
            
        if self.optimization_level >= 3:
            # Seviye 3: İleri düzey optimizasyonlar
            optimized_circuit = self.optimizer.template_matching(optimized_circuit)
        
        # Optimizasyon istatistiklerini raporla
        gate_reduction = len(circuit.gates) - len(optimized_circuit.gates)
        self.logger.info(f"Gate optimization: removed {gate_reduction} gates")
        
        return optimized_circuit
    
    def _qubit_mapping(self, circuit, hardware_model):
        """
        Qubit yerleşimi aşaması
        
        Args:
            circuit: İşlenecek devre
            hardware_model: Hedef donanım modeli
            
        Returns:
            Circuit: Qubit yerleşimi tamamlanmış devre
        """
        # Donanım modeli yoksa, bu aşamayı atla
        if hardware_model is None:
            return circuit.copy()
        
        # Qubit'leri fiziksel qubit'lere yerleştir
        mapped_circuit = self.mapper.map_qubits(circuit, hardware_model)
        
        # Yerleşim istatistiklerini raporla
        self.logger.info(f"Qubit mapping: mapped {mapped_circuit.width} logical qubits to physical qubits")
        
        return mapped_circuit
    
    def _gate_scheduling(self, circuit):
        """
        Kapı zamanlaması aşaması
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Kapı zamanlaması tamamlanmış devre
        """
        # Kapıları paralel yürütülecek şekilde yeniden zamanla
        scheduled_circuit = self.scheduler.schedule(circuit)
        
        # Zamanlama sonuçlarını raporla
        depth_reduction = circuit.depth - scheduled_circuit.depth
        self.logger.info(f"Gate scheduling: reduced depth by {depth_reduction} units")
        
        return scheduled_circuit
    
    def _qubit_routing(self, circuit, hardware_model):
        """
        Kapı yönlendirme aşaması
        
        Args:
            circuit: İşlenecek devre
            hardware_model: Hedef donanım modeli
            
        Returns:
            Circuit: Kapı yönlendirmesi tamamlanmış devre
        """
        # Donanım modeli yoksa, bu aşamayı atla
        if hardware_model is None:
            return circuit.copy()
        
        # Çok-qubitli kapılar için SWAP kapıları ekleyerek uyumlu hale getir
        routed_circuit = self.mapper.route_gates(circuit, hardware_model)
        
        # SWAP sayısını raporla
        swap_count = routed_circuit.swap_count
        self.logger.info(f"Qubit routing: inserted {swap_count} SWAP gates")
        
        return routed_circuit
    
    def _postprocessing(self, circuit):
        """
        Son işleme aşaması
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Son işleme tamamlanmış devre
        """
        # Devrenin kopyasını oluştur
        final_circuit = circuit.copy()
        
        # Gereksiz bariyer ve ID kapılarını kaldır
        final_circuit = self.optimizer.clean_circuit(final_circuit)
        
        # Son optimizasyonları uygula
        if self.optimization_level >= 1:
            final_circuit = self.optimizer.final_optimization(final_circuit)
        
        return final_circuit 