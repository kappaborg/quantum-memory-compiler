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
Bellek Hiyerarşisi modülü
========================

Kuantum bellek hiyerarşisini ve farklı bellek seviyelerini temsil eden sınıf.
"""

from ..core.qubit import MemoryLevel, QubitType


class MemoryLevelManager:
    """Bellek hiyerarşisindeki bir seviyeyi temsil eden sınıf"""
    
    def __init__(self, name, capacity, coherence_time, access_time=1, error_rate=0.001):
        """
        MemoryLevelManager nesnesini başlatır
        
        Args:
            name: Bellek seviyesinin adı (L1, L2, L3, vs.)
            capacity: Seviyedeki maksimum qubit sayısı
            coherence_time: Qubit'lerin bu seviyedeki koherans süreleri (simülasyon zaman birimi)
            access_time: Qubit durumlarına erişim süresi (simülasyon zaman birimi)
            error_rate: Bu seviyedeki qubit'lerin hata oranı
        """
        self.name = name
        self.capacity = capacity
        self.coherence_time = coherence_time
        self.access_time = access_time
        self.error_rate = error_rate
        
        # İzleme değişkenleri
        self.used_qubits = 0
        self.active_qubits = []
    
    @property
    def available_capacity(self):
        """Kullanılabilir qubit sayısını döndürür"""
        return self.capacity - self.used_qubits
    
    @property
    def utilization(self):
        """Kullanım oranını döndürür (0-1 arası)"""
        return self.used_qubits / self.capacity if self.capacity > 0 else 0
    
    def allocate_qubit(self, qubit):
        """
        Bu seviyede qubit tahsis eder
        
        Args:
            qubit: Tahsis edilecek qubit
            
        Returns:
            bool: Tahsis başarılı oldu mu?
        """
        if self.available_capacity <= 0:
            return False
        
        self.used_qubits += 1
        self.active_qubits.append(qubit)
        
        # Qubit'in fiziksel özelliklerini bu seviyeye göre ayarla
        qubit.coherence_time = self.coherence_time
        qubit.error_rate = self.error_rate
        
        return True
    
    def deallocate_qubit(self, qubit):
        """
        Qubit'i serbest bırakır
        
        Args:
            qubit: Serbest bırakılacak qubit
            
        Returns:
            bool: İşlem başarılı oldu mu?
        """
        if qubit in self.active_qubits:
            self.active_qubits.remove(qubit)
            self.used_qubits -= 1
            return True
        return False
    
    def __str__(self):
        return (f"MemoryLevelManager({self.name}, cap={self.capacity}, "
                f"used={self.used_qubits}, coh_time={self.coherence_time})")


class MemoryHierarchy:
    """Kuantum bellek hiyerarşisi sınıfı"""
    
    def __init__(self, l1_capacity=50, l2_capacity=100, l3_capacity=200):
        """
        MemoryHierarchy nesnesini başlatır
        
        Args:
            l1_capacity: L1 bellek kapasitesi (işlem qubit'leri)
            l2_capacity: L2 bellek kapasitesi (ara bellek)
            l3_capacity: L3 bellek kapasitesi (uzun süreli bellek)
        """
        # Bellek seviyeleri
        self.levels = {
            "L1": MemoryLevelManager("L1", l1_capacity, coherence_time=100, access_time=1, error_rate=0.001),
            "L2": MemoryLevelManager("L2", l2_capacity, coherence_time=500, access_time=5, error_rate=0.0005),
            "L3": MemoryLevelManager("L3", l3_capacity, coherence_time=2000, access_time=20, error_rate=0.0001)
        }
        
        # Transfer süreleri: (kaynak, hedef) -> süre
        self.transfer_times = {
            ("L1", "L2"): 5,
            ("L2", "L1"): 5,
            ("L2", "L3"): 15,
            ("L3", "L2"): 15,
            ("L1", "L3"): 20,
            ("L3", "L1"): 20
        }
        
        # Transfer hata oranları: (kaynak, hedef) -> hata oranı
        self.transfer_error_rates = {
            ("L1", "L2"): 0.005,
            ("L2", "L1"): 0.005,
            ("L2", "L3"): 0.01,
            ("L3", "L2"): 0.01,
            ("L1", "L3"): 0.015,
            ("L3", "L1"): 0.015
        }
        
        # İzleme değişkenleri
        self.total_transfers = 0
        self.transfer_stats = {key: 0 for key in self.transfer_times.keys()}
    
    @classmethod
    def from_config(cls, config_data):
        """
        Konfigürasyon verisinden MemoryHierarchy nesnesi oluşturur
        
        Args:
            config_data: Bellek konfigürasyon verisi (sözlük olarak)
            
        Returns:
            MemoryHierarchy: Oluşturulan bellek hiyerarşisi
        """
        # Varsayılan kapasiteler
        l1_capacity = 50
        l2_capacity = 100
        l3_capacity = 200
        
        # Konfigürasyondan kapasiteleri güncelle
        if isinstance(config_data, dict) and 'hierarchy' in config_data:
            hierarchy_data = config_data['hierarchy']
            
            # Eğer levels tanımlanmışsa, özel kapasiteleri kullan
            if 'levels' in hierarchy_data and isinstance(hierarchy_data['levels'], list):
                for level in hierarchy_data['levels']:
                    if isinstance(level, dict) and 'name' in level and 'capacity' in level:
                        name = level['name'].upper()
                        capacity = level['capacity']
                        
                        if name == 'L1' or name == 'FAST_MEMORY':
                            l1_capacity = capacity
                        elif name == 'L2' or name == 'BUFFER_MEMORY':
                            l2_capacity = capacity
                        elif name == 'L3' or name == 'SLOW_MEMORY':
                            l3_capacity = capacity
        
        # Yeni hiyerarşi oluştur
        hierarchy = cls(l1_capacity, l2_capacity, l3_capacity)
        
        # Eğer özel seviyeler tanımlanmışsa, bunları ekle
        if isinstance(config_data, dict) and 'hierarchy' in config_data:
            hierarchy_data = config_data['hierarchy']
            
            if 'levels' in hierarchy_data and isinstance(hierarchy_data['levels'], list):
                for level in hierarchy_data['levels']:
                    if isinstance(level, dict) and 'name' in level:
                        # Eğer standart L1, L2, L3 değilse, özel seviye olarak ekle
                        name = level['name']
                        if name.upper() not in ('L1', 'L2', 'L3'):
                            hierarchy.add_level(
                                name=name,
                                capacity=level.get('capacity', 50),
                                access_time=level.get('access_time', 5),
                                error_rate=level.get('error_rate', 0.001),
                                coherence_time=level.get('coherence_time', 100)
                            )
        
        return hierarchy
    
    def add_level(self, name, capacity, access_time=1, error_rate=0.001, coherence_time=100):
        """
        Bellek hiyerarşisine yeni bir seviye ekler
        
        Args:
            name: Bellek seviyesinin adı (örn. "fast_memory")
            capacity: Seviyedeki maksimum qubit sayısı
            access_time: Qubit durumlarına erişim süresi (simülasyon zaman birimi)
            error_rate: Bu seviyedeki qubit'lerin hata oranı
            coherence_time: Qubit'lerin bu seviyedeki koherans süreleri (simülasyon zaman birimi)
            
        Returns:
            bool: Ekleme başarılı oldu mu?
        """
        if name in self.levels:
            return False
            
        # Yeni seviyeyi ekle
        self.levels[name] = MemoryLevelManager(name, capacity, coherence_time, access_time, error_rate)
        
        # Varsayılan transfer sürelerini ve hata oranlarını diğer seviyelerle ayarla
        for existing_level in [lvl for lvl in self.levels if lvl != name]:
            # Yeni seviyeden mevcut seviyeye
            self.transfer_times[(name, existing_level)] = max(5, access_time * 5)
            self.transfer_error_rates[(name, existing_level)] = max(0.005, error_rate * 5)
            
            # Mevcut seviyeden yeni seviyeye
            self.transfer_times[(existing_level, name)] = max(5, access_time * 5)
            self.transfer_error_rates[(existing_level, name)] = max(0.005, error_rate * 5)
            
            # Transfer istatistiklerini güncelle
            self.transfer_stats[(name, existing_level)] = 0
            self.transfer_stats[(existing_level, name)] = 0
            
        return True
    
    def get_level(self, level_name):
        """
        Bellek seviyesini ismine göre döndürür
        
        Args:
            level_name: Bellek seviyesi adı (L1, L2, L3 veya MemoryLevel enum)
            
        Returns:
            MemoryLevelManager: Bellek seviyesi
        """
        if isinstance(level_name, str):
            return self.levels.get(level_name)
        
        # MemoryLevel enum'u kullanıldıysa
        if hasattr(level_name, "name"):
            return self.levels.get(level_name.name)
        
        return None
    
    def allocate_qubit(self, qubit, level_name):
        """
        Belirli bir seviyede qubit tahsis eder
        
        Args:
            qubit: Tahsis edilecek qubit
            level_name: Bellek seviyesi adı
            
        Returns:
            bool: Tahsis başarılı oldu mu?
        """
        level = self.get_level(level_name)
        if not level:
            return False
        
        result = level.allocate_qubit(qubit)
        if result:
            # Qubit'in memory_level'ini uygun bellek seviyesine ayarla
            if level_name == "L1":
                qubit.set_memory_level(MemoryLevel.L1)
            elif level_name == "L2":
                qubit.set_memory_level(MemoryLevel.L2)
            elif level_name == "L3":
                qubit.set_memory_level(MemoryLevel.L3)
        
        return result
    
    def deallocate_qubit(self, qubit):
        """
        Qubit'i serbest bırakır
        
        Args:
            qubit: Serbest bırakılacak qubit
            
        Returns:
            bool: İşlem başarılı oldu mu?
        """
        level_name = qubit.memory_level.name if hasattr(qubit.memory_level, "name") else qubit.memory_level
        level = self.get_level(level_name)
        if not level:
            return False
        
        return level.deallocate_qubit(qubit)
    
    def transfer_qubit(self, qubit, target_level_name):
        """
        Qubit'i bir bellek seviyesinden diğerine taşır
        
        Args:
            qubit: Taşınacak qubit
            target_level_name: Hedef bellek seviyesi adı
            
        Returns:
            tuple: (başarı durumu, transfer süresi)
        """
        # Qubit'in şu anki bellek seviyesini belirle
        current_level_name = qubit.memory_level.name if hasattr(qubit.memory_level, "name") else qubit.memory_level
        
        # Hedef seviye ile aynıysa, transfer gerekmez
        if current_level_name == target_level_name:
            return True, 0
        
        # Şu anki ve hedef bellek seviyelerini al
        current_level = self.get_level(current_level_name)
        target_level = self.get_level(target_level_name)
        
        if not current_level or not target_level:
            return False, 0
        
        # Hedef seviyede yer var mı?
        if target_level.available_capacity <= 0:
            return False, 0
        
        # Transfer süresini belirle
        transfer_key = (current_level_name, target_level_name)
        transfer_time = self.transfer_times.get(transfer_key, 10)  # Varsayılan 10 birim
        
        # Qubit'i şu anki seviyeden çıkar
        current_level.deallocate_qubit(qubit)
        
        # Qubit'i hedef seviyeye ekle
        success = target_level.allocate_qubit(qubit)
        
        if success:
            # Qubit'in bellek seviyesini güncelle
            if target_level_name == "L1":
                qubit.set_memory_level(MemoryLevel.L1)
            elif target_level_name == "L2":
                qubit.set_memory_level(MemoryLevel.L2)
            elif target_level_name == "L3":
                qubit.set_memory_level(MemoryLevel.L3)
            
            # Transfer istatistiklerini güncelle
            self.total_transfers += 1
            self.transfer_stats[transfer_key] = self.transfer_stats.get(transfer_key, 0) + 1
        else:
            # Transfer başarısız olduysa, qubit'i orijinal seviyeye geri koy
            current_level.allocate_qubit(qubit)
        
        return success, transfer_time
    
    def get_best_level_for_qubit(self, qubit, lifetime):
        """
        Verilen yaşam süresine göre bir qubit için en uygun bellek seviyesini belirler
        
        Args:
            qubit: Değerlendirilecek qubit
            lifetime: Beklenen qubit yaşam süresi
            
        Returns:
            str: Önerilen bellek seviyesi adı
        """
        if lifetime <= self.levels["L1"].coherence_time * 0.7:
            return "L1"
        elif lifetime <= self.levels["L2"].coherence_time * 0.7:
            return "L2"
        else:
            return "L3"
    
    def get_total_capacity(self):
        """Tüm bellek hiyerarşisinin toplam kapasitesini döndürür"""
        return sum(level.capacity for level in self.levels.values())
    
    def get_total_used(self):
        """Tüm bellek hiyerarşisinde kullanılan toplam qubit sayısını döndürür"""
        return sum(level.used_qubits for level in self.levels.values())
    
    def get_utilization_stats(self):
        """Her bellek seviyesinin kullanım oranını döndürür"""
        return {name: level.utilization for name, level in self.levels.items()}
    
    def get_transfer_stats(self):
        """Bellek seviyeleri arasındaki transferlerin istatistiklerini döndürür"""
        return {
            "total_transfers": self.total_transfers,
            "transfer_counts": self.transfer_stats,
            "transfer_ratios": {key: count / self.total_transfers if self.total_transfers > 0 else 0 
                              for key, count in self.transfer_stats.items()}
        }
    
    def reset(self):
        """Bellek hiyerarşisini sıfırlar"""
        for level in self.levels.values():
            level.used_qubits = 0
            level.active_qubits = []
        
        self.total_transfers = 0
        self.transfer_stats = {key: 0 for key in self.transfer_times.keys()}
    
    def __str__(self):
        """Bellek hiyerarşisinin string temsilini döndürür"""
        level_strs = [str(level) for level in self.levels.values()]
        return f"MemoryHierarchy({', '.join(level_strs)})"

    def get_transfer_cost(self, source_level, target_level, qubit=None):
        """
        Calculates the cost of transferring a qubit between memory levels
        
        Args:
            source_level: Source memory level (name or MemoryLevel enum)
            target_level: Target memory level (name or MemoryLevel enum)
            qubit: Optional qubit to consider qubit-specific costs
            
        Returns:
            float: Cost value (higher is more expensive)
        """
        # Normalize level names
        source_name = source_level.name if hasattr(source_level, "name") else source_level
        target_name = target_level.name if hasattr(target_level, "name") else target_level
        
        # Get basic transfer time
        transfer_key = (source_name, target_name)
        base_time_cost = self.transfer_times.get(transfer_key, 10)
        
        # Get error rate for this transfer
        error_cost = self.transfer_error_rates.get(transfer_key, 0.01) * 100  # Scale up for cost calculation
        
        # Consider target memory level utilization (higher utilization = higher cost)
        target_level_obj = self.get_level(target_name)
        utilization_cost = target_level_obj.utilization * 5 if target_level_obj else 0
        
        # If qubit is provided, consider qubit-specific factors
        qubit_specific_cost = 0
        if qubit:
            # Consider coherence time of the qubit compared to target level
            target_coherence = target_level_obj.coherence_time if target_level_obj else 100
            coherence_ratio = target_coherence / qubit.coherence_time if qubit.coherence_time else 1
            
            # If the target coherence is much higher than needed, it's wasteful (higher cost)
            if coherence_ratio > 5:
                qubit_specific_cost += (coherence_ratio - 5) * 0.5
                
            # If the qubit has high activity, L1 is preferred (lower cost)
            if target_name == "L1" and hasattr(qubit, "gate_count") and qubit.gate_count > 10:
                qubit_specific_cost -= 2
        
        # Calculate total cost
        total_cost = base_time_cost + error_cost + utilization_cost + qubit_specific_cost
        
        return max(0, total_cost)  # Ensure cost is non-negative
    
    def find_optimal_level(self, qubit, current_operation=None, future_operations=None):
        """
        Determines the optimal memory level for a qubit based on its usage pattern
        
        Args:
            qubit: The qubit to analyze
            current_operation: Optional current operation being performed
            future_operations: Optional list of future operations on this qubit
            
        Returns:
            str: Name of the optimal memory level for this qubit
        """
        # Get current level
        current_level = qubit.memory_level.name if hasattr(qubit.memory_level, "name") else qubit.memory_level
        
        # If no future operations, keep qubit in current level
        if not future_operations:
            return current_level
            
        # Count operations by type
        op_counts = {}
        for op in future_operations:
            op_type = getattr(op, "type", None)
            if op_type:
                op_counts[op_type] = op_counts.get(op_type, 0) + 1
        
        # Calculate idle time until next operation
        idle_time = 0
        if future_operations and hasattr(future_operations[0], "time") and current_operation and hasattr(current_operation, "time"):
            idle_time = future_operations[0].time - (current_operation.time + getattr(current_operation, "duration", 0))
        
        # Determine best level based on operations and idle time
        if idle_time > 100:
            # Long idle time, prefer L3 for storage
            return "L3"
        elif idle_time > 20:
            # Medium idle time, prefer L2
            return "L2"
        elif sum(op_counts.values()) > 5:
            # Many upcoming operations, prefer L1 for fast access
            return "L1"
        
        # By default, keep in current level
        return current_level
    
    def smart_transfer(self, qubit, recommended_level=None, context=None):
        """
        Intelligently transfers a qubit to the optimal memory level
        
        Args:
            qubit: Qubit to transfer
            recommended_level: Optional recommended level (if known)
            context: Optional operation context (current and future operations)
            
        Returns:
            tuple: (success, transfer_time, target_level)
        """
        # Get current level
        current_level = qubit.memory_level.name if hasattr(qubit.memory_level, "name") else qubit.memory_level
        
        # If recommended level is provided, use it, otherwise find optimal level
        if recommended_level:
            target_level = recommended_level
        else:
            current_op = context["current_operation"] if context and "current_operation" in context else None
            future_ops = context["future_operations"] if context and "future_operations" in context else None
            target_level = self.find_optimal_level(qubit, current_op, future_ops)
        
        # Check if transfer is necessary
        if current_level == target_level:
            return True, 0, target_level
        
        # Calculate direct transfer cost
        direct_cost = self.get_transfer_cost(current_level, target_level, qubit)
        
        # Check if indirect transfer through intermediate level is more efficient
        indirect_costs = {}
        for intermediate in ["L1", "L2", "L3"]:
            if intermediate != current_level and intermediate != target_level:
                first_leg_cost = self.get_transfer_cost(current_level, intermediate, qubit)
                second_leg_cost = self.get_transfer_cost(intermediate, target_level, qubit)
                indirect_costs[intermediate] = first_leg_cost + second_leg_cost
        
        # Find minimum cost path
        min_indirect_cost = min(indirect_costs.values()) if indirect_costs else float('inf')
        best_intermediate = min(indirect_costs, key=indirect_costs.get) if indirect_costs else None
        
        # Compare direct vs indirect
        if min_indirect_cost < direct_cost * 0.8:  # Only use indirect if significantly better
            # First transfer to intermediate level
            success1, time1 = self.transfer_qubit(qubit, best_intermediate)
            if not success1:
                return False, 0, current_level
                
            # Then transfer to final target
            success2, time2 = self.transfer_qubit(qubit, target_level)
            return success2, time1 + time2, target_level
        else:
            # Direct transfer is optimal
            success, time = self.transfer_qubit(qubit, target_level)
            return success, time, target_level
    
    def optimize_memory_allocation(self, circuit, time_point=None):
        """
        Optimizes memory allocation for a circuit at a given time point
        
        Args:
            circuit: The quantum circuit
            time_point: The time point to optimize for (default: current)
            
        Returns:
            dict: Summary of optimization actions taken
        """
        if time_point is None:
            time_point = circuit.current_time
            
        actions = {
            "transfers": 0,
            "qubits_affected": 0,
            "total_transfer_time": 0,
            "total_cost_saved": 0
        }
        
        # For each qubit, determine if it's in the optimal level
        processed_qubits = set()
        for qubit in circuit.qubits:
            if qubit in processed_qubits or not qubit.is_active:
                continue
                
            # Get upcoming operations for this qubit
            future_gates = [g for g in circuit.get_gates_by_qubit(qubit) if g.time > time_point]
            future_gates.sort(key=lambda g: g.time)
            
            # Find most recent operation
            prev_gates = [g for g in circuit.get_gates_by_qubit(qubit) if g.time <= time_point]
            current_op = max(prev_gates, key=lambda g: g.time) if prev_gates else None
            
            # Build context for decision making
            context = {
                "current_operation": current_op,
                "future_operations": future_gates,
                "time_point": time_point
            }
            
            # Determine optimal level based on operation pattern
            current_level = qubit.memory_level.name if hasattr(qubit.memory_level, "name") else qubit.memory_level
            optimal_level = self.find_optimal_level(qubit, current_op, future_gates)
            
            # If qubit isn't in optimal level, transfer it
            if current_level != optimal_level:
                current_cost = self.get_transfer_cost(current_level, "L1", qubit) if future_gates else 0
                optimal_cost = self.get_transfer_cost(optimal_level, "L1", qubit) if future_gates else 0
                
                # Only transfer if there's significant benefit
                if optimal_cost < current_cost * 0.7:
                    success, transfer_time, actual_level = self.smart_transfer(qubit, optimal_level, context)
                    
                    if success:
                        actions["transfers"] += 1
                        actions["qubits_affected"] += 1
                        actions["total_transfer_time"] += transfer_time
                        actions["total_cost_saved"] += (current_cost - optimal_cost)
                        
            processed_qubits.add(qubit)
            
        return actions 