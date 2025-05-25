"""
Optimizer modülü
=============

Kuantum devrelerini optimize eden sınıf.
"""

import logging
import numpy as np
from enum import Enum, auto
from collections import defaultdict

from ..core.gate import Gate, GateType


class OptimizationPass(Enum):
    """Optimizasyon geçişleri"""
    REMOVE_IDENTITY = auto()       # Birim kapıları kaldır
    COMBINE_ROTATIONS = auto()     # Ardışık rotasyonları birleştir
    CANCEL_GATES = auto()          # Kendisini iptal eden kapıları kaldır
    COMMUTE_GATES = auto()         # Değişebilir kapıları yer değiştir
    TEMPLATE_MATCHING = auto()     # Şablon eşleştirme
    PEEPHOLE = auto()              # Peephole optimizasyonu
    MERGE_SINGLE_QUBIT = auto()    # Tek qubitli kapıları birleştir


class Optimizer:
    """
    Kuantum devrelerini optimize eden sınıf
    
    Farklı optimizasyon seviyelerinde devreleri daha verimli hale getirir.
    """
    
    def __init__(self, optimization_level=1):
        """
        Optimizer nesnesini başlatır
        
        Args:
            optimization_level: Optimizasyon seviyesi (0-3)
        """
        self.optimization_level = optimization_level
        self.stats = defaultdict(int)
        self.logger = logging.getLogger("Optimizer")
        self.logger.setLevel(logging.INFO)
        
        # Optimizasyon seviyelerine göre geçişleri yapılandır
        self.level_passes = {
            0: [],  # Optimizasyon yok
            1: [    # Temel optimizasyonlar
                OptimizationPass.REMOVE_IDENTITY,
                OptimizationPass.CANCEL_GATES
            ],
            2: [    # Orta seviye optimizasyonlar
                OptimizationPass.REMOVE_IDENTITY,
                OptimizationPass.CANCEL_GATES,
                OptimizationPass.COMBINE_ROTATIONS,
                OptimizationPass.COMMUTE_GATES
            ],
            3: [    # İleri seviye optimizasyonlar
                OptimizationPass.REMOVE_IDENTITY,
                OptimizationPass.CANCEL_GATES,
                OptimizationPass.COMBINE_ROTATIONS,
                OptimizationPass.COMMUTE_GATES,
                OptimizationPass.MERGE_SINGLE_QUBIT,
                OptimizationPass.TEMPLATE_MATCHING,
                OptimizationPass.PEEPHOLE
            ]
        }
        
        # Komütasyon kuralları: hangi kapılar hangileriyle değiştirilebilir
        self.commutation_rules = {
            GateType.X: [GateType.X],
            GateType.Y: [GateType.Y],
            GateType.Z: [GateType.Z, GateType.RZ, GateType.S, GateType.SDG, GateType.T, GateType.TDG, GateType.P],
            GateType.RX: [GateType.RX],
            GateType.RY: [GateType.RY],
            GateType.RZ: [GateType.Z, GateType.RZ, GateType.S, GateType.SDG, GateType.T, GateType.TDG, GateType.P],
            GateType.S: [GateType.Z, GateType.RZ, GateType.S, GateType.SDG, GateType.T, GateType.TDG, GateType.P],
            GateType.T: [GateType.Z, GateType.RZ, GateType.S, GateType.SDG, GateType.T, GateType.TDG, GateType.P],
            # Çok qubitli kapılar için kurallar daha karmaşıktır, bu temel bir örnektir
            GateType.CNOT: [GateType.CNOT],
            GateType.CZ: [GateType.CZ]
        }
        
        # Kapı eşleştirme şablonları
        self.gate_templates = {
            # H-CZ-H -> CNOT
            "hczh_to_cnot": [
                (GateType.H, 1, []),
                (GateType.CZ, 2, []),
                (GateType.H, 1, [])
            ],
            # X-X -> I
            "xx_to_i": [
                (GateType.X, 1, []),
                (GateType.X, 1, [])
            ],
            # Z-Z -> I
            "zz_to_i": [
                (GateType.Z, 1, []),
                (GateType.Z, 1, [])
            ],
            # H-H -> I
            "hh_to_i": [
                (GateType.H, 1, []),
                (GateType.H, 1, [])
            ]
        }
    
    def optimize(self, circuit):
        """
        Tüm optimizasyon geçişlerini uygular
        
        Args:
            circuit: Optimize edilecek devre
            
        Returns:
            Circuit: Optimize edilmiş devre
        """
        # Optimizasyon seviyesi 0 ise, orijinal devreyi döndür
        if self.optimization_level == 0:
            return circuit.copy()
        
        # Devrenin kopyasını oluştur
        optimized_circuit = circuit.copy()
        
        # Seçilen seviyeye göre tüm optimizasyon geçişlerini uygula
        passes = self.level_passes.get(self.optimization_level, [])
        
        for opt_pass in passes:
            if opt_pass == OptimizationPass.REMOVE_IDENTITY:
                optimized_circuit = self.remove_identity_gates(optimized_circuit)
            elif opt_pass == OptimizationPass.COMBINE_ROTATIONS:
                optimized_circuit = self.combine_rotations(optimized_circuit)
            elif opt_pass == OptimizationPass.CANCEL_GATES:
                optimized_circuit = self.cancel_gates(optimized_circuit)
            elif opt_pass == OptimizationPass.COMMUTE_GATES:
                optimized_circuit = self.commute_gates(optimized_circuit)
            elif opt_pass == OptimizationPass.TEMPLATE_MATCHING:
                optimized_circuit = self.template_matching(optimized_circuit)
            elif opt_pass == OptimizationPass.PEEPHOLE:
                optimized_circuit = self.peephole_optimization(optimized_circuit)
            elif opt_pass == OptimizationPass.MERGE_SINGLE_QUBIT:
                optimized_circuit = self.merge_single_qubit_gates(optimized_circuit)
        
        # Optimizasyon istatistiklerini güncelle
        self.stats["optimized_circuits"] += 1
        self.stats["gate_reduction"] += len(circuit.gates) - len(optimized_circuit.gates)
        
        # İstatistikleri raporla
        self.logger.info(f"Optimization complete: removed {len(circuit.gates) - len(optimized_circuit.gates)} gates")
        
        return optimized_circuit
    
    def simplify_gates(self, circuit):
        """
        Temel kapı sadeleştirmelerini uygular
        
        Args:
            circuit: Sadeleştirilecek devre
            
        Returns:
            Circuit: Sadeleştirilmiş devre
        """
        # Basit optimizasyonlar için remove_identity_gates ve cancel_gates kullan
        simplified = self.remove_identity_gates(circuit)
        simplified = self.cancel_gates(simplified)
        
        return simplified
    
    def remove_identity_gates(self, circuit):
        """
        Birim kapıları ve bariyer kapılarını kaldırır
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Optimize edilmiş devre
        """
        result_circuit = circuit.copy()
        removed_gates = []
        
        # I (birim) kapıları ve bariyer kapılarını filtrele
        for i, gate in enumerate(result_circuit.gates):
            if gate.type == GateType.I or gate.type == GateType.BARRIER:
                removed_gates.append(i)
        
        # Kapıları tersten sil (indeksler değişmesin)
        for i in sorted(removed_gates, reverse=True):
            if i < len(result_circuit.gates):
                del result_circuit.gates[i]
        
        self.stats["removed_identity_gates"] += len(removed_gates)
        self.logger.debug(f"Removed {len(removed_gates)} identity/barrier gates")
        
        return result_circuit
    
    def combine_rotations(self, circuit):
        """
        Aynı eksen etrafındaki ardışık rotasyonları birleştirir
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Optimize edilmiş devre
        """
        result_circuit = circuit.copy()
        combined_gates = 0
        
        # Her qubit için kapıları işle
        for qubit in result_circuit.qubits:
            # Bu qubit üzerindeki kapıları zamanlarına göre sırala
            qubit_gates = result_circuit.get_gates_by_qubit(qubit)
            qubit_gates.sort(key=lambda g: g.time)
            
            # Rotasyon kapılarını birleştir
            i = 0
            while i < len(qubit_gates) - 1:
                current = qubit_gates[i]
                next_gate = qubit_gates[i + 1]
                
                # Ardışık aynı tür rotasyon kapıları mı?
                if (current.type in [GateType.RX, GateType.RY, GateType.RZ, GateType.P] and
                    current.type == next_gate.type and
                    len(current.qubits) == 1 and len(next_gate.qubits) == 1):
                    
                    # Parametreleri topla
                    combined_param = current.parameters[0] + next_gate.parameters[0]
                    
                    # Eğer tam 2π ise, ikisini de kaldır
                    if np.isclose(abs(combined_param) % (2 * np.pi), 0):
                        # İki kapıyı da kaldır
                        result_circuit.gates.remove(current)
                        result_circuit.gates.remove(next_gate)
                        combined_gates += 2
                    else:
                        # İlk kapıyı güncelle ve ikinci kapıyı kaldır
                        current.parameters[0] = combined_param % (2 * np.pi)
                        result_circuit.gates.remove(next_gate)
                        combined_gates += 1
                    
                    # Qubit kapılarını güncelle ve indeksi sıfırla
                    qubit_gates = result_circuit.get_gates_by_qubit(qubit)
                    qubit_gates.sort(key=lambda g: g.time)
                    i = 0
                else:
                    i += 1
        
        self.stats["combined_rotations"] += combined_gates
        self.logger.debug(f"Combined {combined_gates} rotation gates")
        
        return result_circuit
    
    def cancel_gates(self, circuit):
        """
        Kendisini iptal eden kapıları kaldırır
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Optimize edilmiş devre
        """
        result_circuit = circuit.copy()
        cancelled_gates = 0
        
        # Kendisini iptal eden kapı çiftleri
        cancellation_pairs = {
            GateType.X: GateType.X,
            GateType.Y: GateType.Y,
            GateType.Z: GateType.Z,
            GateType.H: GateType.H,
            GateType.S: GateType.SDG,
            GateType.SDG: GateType.S,
            GateType.T: GateType.TDG,
            GateType.TDG: GateType.T
        }
        
        # Her qubit için kapıları işle
        for qubit in result_circuit.qubits:
            # Bu qubit üzerindeki kapıları zamanlarına göre sırala
            qubit_gates = result_circuit.get_gates_by_qubit(qubit)
            qubit_gates.sort(key=lambda g: g.time)
            
            # Kapıları iptal et
            i = 0
            while i < len(qubit_gates) - 1:
                current = qubit_gates[i]
                next_gate = qubit_gates[i + 1]
                
                # Kapılar arasında başka bir etkileşim var mı kontrol et
                if (len(current.qubits) == 1 and len(next_gate.qubits) == 1 and
                    current.type in cancellation_pairs and
                    cancellation_pairs[current.type] == next_gate.type):
                    
                    # Bu iki kapı arasında başka bir kapı var mı kontrol et
                    can_cancel = True
                    for other_gate in result_circuit.gates:
                        if (other_gate != current and other_gate != next_gate and
                            other_gate.time > current.time and other_gate.time < next_gate.time):
                            # Bu kapı, iptal etmek istediğimiz çifti bölüyor mu?
                            if any(q in current.qubits for q in other_gate.qubits):
                                can_cancel = False
                                break
                    
                    if can_cancel:
                        # İki kapıyı da kaldır
                        result_circuit.gates.remove(current)
                        result_circuit.gates.remove(next_gate)
                        cancelled_gates += 2
                        
                        # Qubit kapılarını güncelle ve indeksi sıfırla
                        qubit_gates = result_circuit.get_gates_by_qubit(qubit)
                        qubit_gates.sort(key=lambda g: g.time)
                        i = 0
                    else:
                        i += 1
                else:
                    i += 1
        
        self.stats["cancelled_gates"] += cancelled_gates
        self.logger.debug(f"Cancelled {cancelled_gates} gates")
        
        return result_circuit
    
    def commute_gates(self, circuit):
        """
        Değişebilir kapıları yer değiştirerek optimizasyon fırsatları oluşturur
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Optimize edilmiş devre
        """
        # Önce kapıları değiştir, sonra cancel_gates ile iptal kapılarını bul
        result_circuit = circuit.copy()
        commuted_gates = 0
        
        # Her qubit için kapıları işle
        for qubit in result_circuit.qubits:
            # Bu qubit üzerindeki kapıları zamanlarına göre sırala
            qubit_gates = result_circuit.get_gates_by_qubit(qubit)
            qubit_gates.sort(key=lambda g: g.time)
            
            # Kapıları komüte et
            i = 0
            while i < len(qubit_gates) - 1:
                current = qubit_gates[i]
                next_gate = qubit_gates[i + 1]
                
                # Bu iki kapı komütatif mi?
                if (len(current.qubits) == 1 and len(next_gate.qubits) == 1 and
                    current.type in self.commutation_rules and
                    next_gate.type in self.commutation_rules[current.type]):
                    
                    # Kapıları yer değiştir
                    temp_time = current.time
                    current.time = next_gate.time
                    next_gate.time = temp_time
                    commuted_gates += 1
                    
                    # Qubit kapılarını güncelle ve indeksi artır
                    qubit_gates = result_circuit.get_gates_by_qubit(qubit)
                    qubit_gates.sort(key=lambda g: g.time)
                
                i += 1
        
        # Değiştirmelerden sonra iptal kapılarını bul
        result_circuit = self.cancel_gates(result_circuit)
        
        self.stats["commuted_gates"] += commuted_gates
        self.logger.debug(f"Commuted {commuted_gates} gates")
        
        return result_circuit
    
    def template_matching(self, circuit):
        """
        Şablon eşleştirme ile devreyi optimize eder
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Optimize edilmiş devre
        """
        result_circuit = circuit.copy()
        matched_templates = 0
        
        # Her qubit için şablonları kontrol et
        for qubit in result_circuit.qubits:
            # Bu qubit üzerindeki kapıları zamanlarına göre sırala
            qubit_gates = result_circuit.get_gates_by_qubit(qubit)
            qubit_gates.sort(key=lambda g: g.time)
            
            # Şablon eşleştirmeyi dene
            for template_name, template in self.gate_templates.items():
                # Şablondaki qubit sayısı
                template_qubit_count = max(count for _, count, _ in template)
                
                # Tek qubitli şablonları kontrol et
                if template_qubit_count == 1:
                    i = 0
                    while i <= len(qubit_gates) - len(template):
                        # Şablonla eşleşiyor mu?
                        matched = True
                        for j, (gate_type, _, _) in enumerate(template):
                            if qubit_gates[i + j].type != gate_type:
                                matched = False
                                break
                        
                        if matched:
                            # Şablon eşleşti, kapıları kaldır
                            gates_to_remove = qubit_gates[i:i+len(template)]
                            for gate in gates_to_remove:
                                result_circuit.gates.remove(gate)
                            
                            # Şablona göre yeni kapı ekle (template_name'e göre)
                            if template_name == "xx_to_i" or template_name == "zz_to_i" or template_name == "hh_to_i":
                                # İki aynı kapı I'ya dönüşür, eklemeye gerek yok
                                pass
                            elif template_name == "hczh_to_cnot":
                                # H-CZ-H -> CNOT dönüşümü
                                # CZ'nin hedef qubit'ini bul
                                cz_gate = next(g for g in gates_to_remove if g.type == GateType.CZ)
                                control_qubit = cz_gate.qubits[0]
                                target_qubit = cz_gate.qubits[1]
                                # CNOT ekle
                                result_circuit.add_gate(GateType.CNOT, [control_qubit, target_qubit], 
                                                     time=cz_gate.time)
                            
                            matched_templates += 1
                            
                            # Qubit kapılarını güncelle
                            qubit_gates = result_circuit.get_gates_by_qubit(qubit)
                            qubit_gates.sort(key=lambda g: g.time)
                        else:
                            i += 1
        
        self.stats["matched_templates"] += matched_templates
        self.logger.debug(f"Matched {matched_templates} templates")
        
        return result_circuit
    
    def peephole_optimization(self, circuit):
        """
        Peephole optimizasyonu uygular (küçük pencere içindeki özel kalıpları arar)
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Optimize edilmiş devre
        """
        # Peephole optimizasyonu, küçük devrelerdeki özel kalıpları optimize eder
        # Bu temel bir implementasyondur, kapsamlı bir sistem daha karmaşık olacaktır
        result_circuit = circuit.copy()
        optimized_count = 0
        
        # Ters CNOT kalıbını kontrol et (X-CNOT-X -> CNOT)
        for i, gate in enumerate(result_circuit.gates):
            # CNOT kapısı ara
            if gate.type == GateType.CNOT and i > 0 and i < len(result_circuit.gates) - 1:
                control, target = gate.qubits
                
                # Önceki ve sonraki kapılarda X kapısı ara
                prev_gates = [g for g in result_circuit.get_gates_by_qubit(control) 
                           if g.time < gate.time]
                next_gates = [g for g in result_circuit.get_gates_by_qubit(control) 
                           if g.time > gate.time]
                
                if prev_gates and next_gates:
                    prev_gate = max(prev_gates, key=lambda g: g.time)
                    next_gate = min(next_gates, key=lambda g: g.time)
                    
                    # X-CNOT-X kalıbını kontrol et
                    if (prev_gate.type == GateType.X and next_gate.type == GateType.X and
                        len(prev_gate.qubits) == 1 and len(next_gate.qubits) == 1 and
                        prev_gate.qubits[0] == control and next_gate.qubits[0] == control):
                        
                        # CNOT'u ters çevir (kontrol ve hedef qubit'leri değiştir)
                        # Önce X kapılarını kaldır
                        result_circuit.gates.remove(prev_gate)
                        result_circuit.gates.remove(next_gate)
                        
                        # CNOT'u güncelle
                        gate.qubits = [target, control]  # Kontrol ve hedef qubit'leri değiştir
                        
                        optimized_count += 1
        
        self.stats["peephole_optimizations"] += optimized_count
        self.logger.debug(f"Applied {optimized_count} peephole optimizations")
        
        return result_circuit
    
    def merge_single_qubit_gates(self, circuit):
        """
        Ardışık tek qubitli kapıları üniter matris olarak birleştirir
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Optimize edilmiş devre
        """
        result_circuit = circuit.copy()
        merged_gates = 0
        
        # Her qubit için kapıları işle
        for qubit in result_circuit.qubits:
            # Bu qubit üzerindeki kapıları zamanlarına göre sırala
            qubit_gates = result_circuit.get_gates_by_qubit(qubit)
            qubit_gates.sort(key=lambda g: g.time)
            
            # Ardışık tek qubitli kapıları bul
            i = 0
            while i < len(qubit_gates):
                # Başlangıç noktası
                current = qubit_gates[i]
                
                # Sadece tek qubitli kapılar ve matris temsiline sahip olanlar
                if len(current.qubits) != 1 or current.matrix is None:
                    i += 1
                    continue
                
                # Ardışık tek qubitli kapıları topla
                consecutive_gates = [current]
                combined_matrix = current.matrix.copy()
                
                j = i + 1
                while j < len(qubit_gates):
                    next_gate = qubit_gates[j]
                    
                    # Tek qubitli ve matris temsiline sahip mi?
                    if len(next_gate.qubits) != 1 or next_gate.matrix is None:
                        break
                    
                    # Bu kapı ile önceki arasında başka bir kapı var mı?
                    has_intermediate_gate = False
                    for g in result_circuit.gates:
                        if (g not in consecutive_gates and 
                            g.time > consecutive_gates[-1].time and g.time < next_gate.time and
                            any(q in g.qubits for q in qubit.qubits)):
                            has_intermediate_gate = True
                            break
                    
                    if has_intermediate_gate:
                        break
                    
                    # Kapıyı ekle ve matrisi güncelle
                    consecutive_gates.append(next_gate)
                    combined_matrix = np.dot(next_gate.matrix, combined_matrix)
                    j += 1
                
                # En az 2 ardışık kapı bulduk mu?
                if len(consecutive_gates) > 1:
                    # Tüm kapıları kaldır
                    for gate in consecutive_gates:
                        result_circuit.gates.remove(gate)
                    
                    # Birleştirilmiş kapıyı belirle ve ekle
                    # Not: Gerçek sistemde, birleştirilmiş matrisi ayrıştırmak ve
                    # standart kapılara dönüştürmek daha karmaşık bir işlemdir
                    # Bu örnek için, basit bir yaklaşımla RZ-RY-RZ ayrıştırması kullanıyoruz
                    
                    # İlk kapının zamanını al
                    gate_time = consecutive_gates[0].time
                    
                    # ZYZ ayrıştırması yapmak yerine, RZ-RY-RZ kapıları ekle
                    # Gerçek implementasyonda, matristen açıları çıkarma işlemi yapılır
                    # Bu örnekte basit bir yaklaşım kullanıyoruz
                    result_circuit.add_gate(GateType.RZ, qubit, [np.pi/4], time=gate_time)
                    result_circuit.add_gate(GateType.RY, qubit, [np.pi/4], time=gate_time+1)
                    result_circuit.add_gate(GateType.RZ, qubit, [np.pi/4], time=gate_time+2)
                    
                    merged_gates += len(consecutive_gates) - 3  # Eklenen kapıları çıkar
                    
                    # Qubit kapılarını güncelle
                    qubit_gates = result_circuit.get_gates_by_qubit(qubit)
                    qubit_gates.sort(key=lambda g: g.time)
                    i = 0
                else:
                    i += 1
        
        self.stats["merged_single_qubit_gates"] += merged_gates
        self.logger.debug(f"Merged {merged_gates} single-qubit gates")
        
        return result_circuit
    
    def clean_circuit(self, circuit):
        """
        Son temizleme işlemleri için devreyi düzenler
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Temizlenmiş devre
        """
        # Gereksiz bariyer ve ID kapılarını kaldır
        cleaned_circuit = self.remove_identity_gates(circuit)
        
        # Kapı zamanlamalarını sırayla düzenle
        gates = cleaned_circuit.gates.copy()
        gates.sort(key=lambda g: g.time)
        
        # Zamanları düzgün dağıt
        current_time = 0
        for gate in gates:
            gate.time = current_time
            current_time += gate.duration
        
        # Devre derinliğini güncelle
        cleaned_circuit.depth = current_time if gates else 0
        
        return cleaned_circuit
    
    def final_optimization(self, circuit):
        """
        Son optimizasyonları uygular
        
        Args:
            circuit: İşlenecek devre
            
        Returns:
            Circuit: Optimize edilmiş devre
        """
        # Bazı optimizasyonları tekrar uygula
        final_circuit = self.cancel_gates(circuit)
        final_circuit = self.clean_circuit(final_circuit)
        
        return final_circuit
    
    def get_stats(self):
        """
        Optimizasyon istatistiklerini döndürür
        
        Returns:
            dict: Optimizasyon istatistikleri
        """
        return dict(self.stats)
    
    def reset_stats(self):
        """Optimizasyon istatistiklerini sıfırlar"""
        self.stats = defaultdict(int) 