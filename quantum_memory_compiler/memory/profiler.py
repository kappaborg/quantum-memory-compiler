"""
Memory Profiler modülü
=====================

Kuantum bellek kullanımını izleyen ve analiz eden araçlar.
"""

import time
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum, auto
from collections import defaultdict, deque
from ..core.qubit import MemoryLevel, QubitType


class ProfilingEvent(Enum):
    """Profil olayları"""
    ALLOCATE = auto()       # Qubit tahsisi
    DEALLOCATE = auto()     # Qubit serbest bırakma
    TRANSFER = auto()       # Qubit transferi
    GATE_APPLY = auto()     # Kapı uygulaması
    MEASUREMENT = auto()    # Ölçüm
    RESET = auto()          # Qubit sıfırlama
    SWAP = auto()           # Qubit değişimi


class MemoryProfile:
    """Bellek profili sınıfı, profil verilerini saklar"""
    
    def __init__(self, circuit_name=None):
        """
        MemoryProfile nesnesi oluşturur
        
        Args:
            circuit_name: Profili oluşturulan devrenin adı
        """
        self.circuit_name = circuit_name
        self.start_time = time.time()
        self.end_time = None
        self.events = []
        
        # Zaman içinde bellek kullanımı
        self.usage_timeline = defaultdict(list)  # {zaman_noktası: (L1_kullanım, L2_kullanım, L3_kullanım)}
        
        # Seviye başına qubit sayısı
        self.qubit_counts = {
            MemoryLevel.L1: 0,
            MemoryLevel.L2: 0,
            MemoryLevel.L3: 0
        }
        
        # Qubit ömür/yaşam süreleri
        self.qubit_lifetimes = defaultdict(lambda: {"allocated_at": None, "deallocated_at": None})
        
        # Darboğaz analizi için metrikler
        self.bottlenecks = []
        
        # Seviyeler arası transfer sayıları
        self.transfer_counts = defaultdict(int)  # {(source_level, target_level): count}
        
        # Operasyon sayaçları
        self.operation_counts = defaultdict(int)  # {operation_type: count}
        
        # Yoğun zamanlı bölgeler
        self.hotspots = []
    
    def add_event(self, event_type, time_point, qubit=None, level=None, source_level=None, target_level=None, gate=None):
        """
        Profil olayı ekler
        
        Args:
            event_type: Olay tipi (ProfilingEvent)
            time_point: Olayın zaman noktası
            qubit: İlgili qubit (opsiyonel)
            level: İlgili bellek seviyesi (opsiyonel)
            source_level: Transfer olayı için kaynak seviye (opsiyonel)
            target_level: Transfer olayı için hedef seviye (opsiyonel)
            gate: Uygulanan kapı (opsiyonel)
        """
        event = {
            "type": event_type,
            "time": time_point,
            "qubit_id": qubit.id if qubit else None,
            "memory_level": level.name if level else None,
            "source_level": source_level.name if source_level else None,
            "target_level": target_level.name if target_level else None,
            "gate_type": gate.type.name if gate else None
        }
        self.events.append(event)
        
        # Olay tipine göre sayaçları güncelle
        self.operation_counts[event_type] += 1
        
        # Olay tipine göre ek işlemler
        if event_type == ProfilingEvent.ALLOCATE:
            self.qubit_counts[qubit.memory_level] += 1
            self.qubit_lifetimes[qubit.id]["allocated_at"] = time_point
            
        elif event_type == ProfilingEvent.DEALLOCATE:
            self.qubit_counts[qubit.memory_level] -= 1
            self.qubit_lifetimes[qubit.id]["deallocated_at"] = time_point
            
        elif event_type == ProfilingEvent.TRANSFER:
            self.qubit_counts[source_level] -= 1
            self.qubit_counts[target_level] += 1
            self.transfer_counts[(source_level.name, target_level.name)] += 1
            
        # Zaman çizelgesini güncelle
        self.usage_timeline[time_point].append((
            self.qubit_counts[MemoryLevel.L1],
            self.qubit_counts[MemoryLevel.L2],
            self.qubit_counts[MemoryLevel.L3]
        ))
    
    def finalize(self):
        """Profili sonlandırır ve son analizleri yapar"""
        self.end_time = time.time()
        
        # Darboğaz analizi yap
        self._analyze_bottlenecks()
        
        # İlgili bölgeleri belirle
        self._identify_hotspots()
    
    def _analyze_bottlenecks(self):
        """Bellek kullanımındaki darboğazları analiz eder"""
        # Zaman noktalarını sırala
        time_points = sorted(self.usage_timeline.keys())
        
        if not time_points:
            return
        
        # Ardışık zaman noktaları arasında darboğazları belirle
        for i in range(len(time_points) - 1):
            t1, t2 = time_points[i], time_points[i+1]
            usage1 = self.usage_timeline[t1][-1]  # Son durum
            usage2 = self.usage_timeline[t2][-1]  # Son durum
            
            # Eğer herhangi bir bellek seviyesi %90'ın üzerinde doluysa, darboğaz olarak işaretle
            l1_capacity = 50  # Varsayılan değerler, gerçek kapasiteler hesaplanabilir
            l2_capacity = 100
            l3_capacity = 200
            
            if (usage1[0] > 0.9 * l1_capacity or 
                usage1[1] > 0.9 * l2_capacity or 
                usage1[2] > 0.9 * l3_capacity):
                self.bottlenecks.append({
                    "start_time": t1,
                    "end_time": t2,
                    "L1_usage": usage1[0],
                    "L2_usage": usage1[1],
                    "L3_usage": usage1[2],
                    "L1_utilization": usage1[0] / l1_capacity,
                    "L2_utilization": usage1[1] / l2_capacity,
                    "L3_utilization": usage1[2] / l3_capacity
                })
    
    def _identify_hotspots(self):
        """Yüksek yoğunluklu operasyon bölgelerini (hotspots) belirler"""
        # Zaman noktalarını sırala
        time_points = sorted(self.usage_timeline.keys())
        
        if not time_points:
            return
        
        # Operasyon yoğunluğunu hesapla
        op_density = {}
        window_size = max(5, len(time_points) // 20)  # 5 veya toplam noktaların %5'i
        
        for i in range(len(time_points) - window_size):
            window_end = min(i + window_size, len(time_points))
            window_events = sum(1 for event in self.events 
                              if time_points[i] <= event["time"] <= time_points[window_end-1])
            
            op_density[time_points[i]] = window_events / window_size
        
        # Ortalama ve standart sapma hesapla
        if op_density:
            mean_density = np.mean(list(op_density.values()))
            std_density = np.std(list(op_density.values()))
            
            # Ortalamadan 2 standart sapma üzerindeki bölgeleri hotspot olarak işaretle
            threshold = mean_density + 2 * std_density
            
            hotspot_start = None
            for t in sorted(op_density.keys()):
                if op_density[t] > threshold:
                    if hotspot_start is None:
                        hotspot_start = t
                elif hotspot_start is not None:
                    self.hotspots.append({
                        "start_time": hotspot_start,
                        "end_time": t,
                        "density": np.mean([op_density[x] for x in op_density 
                                          if hotspot_start <= x < t])
                    })
                    hotspot_start = None
    
    def get_average_qubit_lifetime(self):
        """
        Qubit'lerin ortalama ömrünü hesaplar
        
        Returns:
            float: Ortalama qubit ömrü
        """
        lifetimes = []
        for qubit_id, data in self.qubit_lifetimes.items():
            if data["allocated_at"] is not None and data["deallocated_at"] is not None:
                lifetime = data["deallocated_at"] - data["allocated_at"]
                lifetimes.append(lifetime)
        
        if not lifetimes:
            return 0
        
        return np.mean(lifetimes)
    
    def get_memory_usage_stats(self):
        """
        Bellek kullanım istatistiklerini hesaplar
        
        Returns:
            dict: Bellek kullanım istatistikleri
        """
        # Zaman noktalarını sırala
        time_points = sorted(self.usage_timeline.keys())
        
        if not time_points:
            return {
                "L1_avg": 0,
                "L2_avg": 0,
                "L3_avg": 0,
                "L1_max": 0,
                "L2_max": 0,
                "L3_max": 0,
                "L1_utilization": 0,
                "L2_utilization": 0,
                "L3_utilization": 0
            }
        
        # Her seviye için kullanım istatistiklerini hesapla
        l1_usage = [usage[0] for t in time_points for usage in self.usage_timeline[t]]
        l2_usage = [usage[1] for t in time_points for usage in self.usage_timeline[t]]
        l3_usage = [usage[2] for t in time_points for usage in self.usage_timeline[t]]
        
        # Varsayılan kapasiteler
        l1_capacity = 50
        l2_capacity = 100
        l3_capacity = 200
        
        return {
            "L1_avg": np.mean(l1_usage) if l1_usage else 0,
            "L2_avg": np.mean(l2_usage) if l2_usage else 0,
            "L3_avg": np.mean(l3_usage) if l3_usage else 0,
            "L1_max": np.max(l1_usage) if l1_usage else 0,
            "L2_max": np.max(l2_usage) if l2_usage else 0,
            "L3_max": np.max(l3_usage) if l3_usage else 0,
            "L1_utilization": np.mean(l1_usage) / l1_capacity if l1_usage else 0,
            "L2_utilization": np.mean(l2_usage) / l2_capacity if l2_usage else 0,
            "L3_utilization": np.mean(l3_usage) / l3_capacity if l3_usage else 0
        }
    
    def get_bottleneck_summary(self):
        """
        Darboğazların özetini döndürür
        
        Returns:
            dict: Darboğaz özeti
        """
        if not self.bottlenecks:
            return {
                "count": 0,
                "avg_duration": 0,
                "max_duration": 0,
                "total_duration": 0,
                "most_constrained_level": None
            }
        
        durations = [b["end_time"] - b["start_time"] for b in self.bottlenecks]
        
        # En çok kısıtlı olan bellek seviyesini belirle
        l1_bottlenecks = sum(1 for b in self.bottlenecks if b["L1_utilization"] > 0.9)
        l2_bottlenecks = sum(1 for b in self.bottlenecks if b["L2_utilization"] > 0.9)
        l3_bottlenecks = sum(1 for b in self.bottlenecks if b["L3_utilization"] > 0.9)
        
        most_constrained = "L1"
        if l2_bottlenecks > l1_bottlenecks:
            most_constrained = "L2"
        if l3_bottlenecks > max(l1_bottlenecks, l2_bottlenecks):
            most_constrained = "L3"
        
        return {
            "count": len(self.bottlenecks),
            "avg_duration": np.mean(durations) if durations else 0,
            "max_duration": np.max(durations) if durations else 0,
            "total_duration": np.sum(durations) if durations else 0,
            "most_constrained_level": most_constrained
        }
    
    def plot_memory_profile(self, circuit=None, output_file=None):
        """
        Bellek kullanımını görselleştirir
        
        Args:
            circuit: Profilleme yapılacak devre (None ise son profil sonuçları kullanılır)
            output_file: Çıktı dosyası yolu (None ise ekranda gösterilir)
            
        Returns:
            matplotlib.figure.Figure: Oluşturulan grafik figürü
        """
        try:
            if circuit is not None:
                # Yeni profil oluştur
                results = self.profile_circuit(circuit)
                if 'profile' in results:
                    profile = results['profile']
                else:
                    # Sonuçlar sözlüğünden profile nesnesi alınamıyorsa, bir MemoryProfile nesnesi oluştur
                    profile = MemoryProfile(getattr(circuit, 'name', 'unnamed'))
                    # Temel verileri doldur
                    profile.start_time = time.time()
                    profile.end_time = time.time()
                    profile.circuit_name = getattr(circuit, 'name', 'unnamed')
            else:
                # Son profil sonuçlarını kullan
                profile = self._last_profile
                if profile is None:
                    raise ValueError("Görselleştirme için bir devre verilmeli veya daha önce profilleme yapılmış olmalı")
            
            # Görselleştirmeyi oluştur
            if hasattr(profile, 'plot_memory_usage'):
                fig = profile.plot_memory_usage(output_file)
            else:
                # Varsayılan görselleştirme
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.set_title(f"Bellek Profili: {getattr(circuit, 'name', 'unnamed')}")
                ax.set_xlabel("Zaman")
                ax.set_ylabel("Qubit Sayısı")
                
                if output_file:
                    plt.savefig(output_file, dpi=300, bbox_inches='tight')
                    plt.close(fig)
                
            return fig
        except Exception as e:
            print(f"Bellek profili görselleştirme hatası: {e}")
            # Boş bir figür döndür
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, f"Görselleştirme hatası: {e}", 
                   horizontalalignment='center', verticalalignment='center')
            return fig


class MemoryProfiler:
    """Bellek profilini oluşturan ve yöneten sınıf"""
    
    def __init__(self, memory_hierarchy=None, circuit=None):
        """
        MemoryProfiler nesnesini oluşturur
        
        Args:
            memory_hierarchy: Profillenecek bellek hiyerarşisi
            circuit: Profillenecek devre
        """
        self.memory_hierarchy = memory_hierarchy
        self.circuit = circuit
        self._active_profile = None
        self._last_profile = None
        self.profiles = []  # Birden fazla profil saklamak için
        self.is_profiling = False
    
    def start_profiling(self, circuit_name=None):
        """
        Profillemeyi başlatır
        
        Args:
            circuit_name: Profili oluşturulan devrenin adı
        """
        if self.is_profiling:
            self.stop_profiling()
            
        self._active_profile = MemoryProfile(circuit_name)
        self.is_profiling = True
        
        return self._active_profile
    
    def stop_profiling(self):
        """
        Profillemeyi sonlandırır
        
        Returns:
            MemoryProfile: Oluşturulan profil
        """
        if not self.is_profiling or self._active_profile is None:
            return None
            
        self._active_profile.finalize()
        self._last_profile = self._active_profile
        self.profiles.append(self._active_profile)
        
        profile = self._active_profile
        self._active_profile = None
        self.is_profiling = False
        
        return profile
    
    def profile_event(self, event_type, time_point, qubit=None, level=None, 
                     source_level=None, target_level=None, gate=None):
        """
        Bellek olayını profiller
        
        Args:
            event_type: Olay tipi (ProfilingEvent)
            time_point: Olayın zaman noktası
            qubit: İlgili qubit (opsiyonel)
            level: İlgili bellek seviyesi (opsiyonel)
            source_level: Transfer olayı için kaynak seviye (opsiyonel)
            target_level: Transfer olayı için hedef seviye (opsiyonel)
            gate: Uygulanan kapı (opsiyonel)
            
        Returns:
            bool: Profilleme başarılı oldu mu
        """
        if not self.is_profiling or self._active_profile is None:
            return False
            
        self._active_profile.add_event(event_type, time_point, qubit, level, 
                                      source_level, target_level, gate)
        return True
    
    def profile_circuit_execution(self, circuit=None, max_time=1000):
        """
        Bir devrenin yürütülmesini profiller
        
        Args:
            circuit: Profil oluşturulacak devre
            max_time: Maksimum simülasyon zamanı (varsayılan: 1000)
            
        Returns:
            MemoryProfile: Oluşturulan profil
        """
        if circuit is None:
            circuit = self.circuit
            
        if circuit is None:
            raise ValueError("Profil için bir devre belirtilmelidir")
            
        # Profilciyi başlat
        profile = self.start_profiling(circuit.name)
        
        # Simülasyon zamanını hızlandır
        for time_point in range(max_time):
            # Gerçek bir simülasyonda, bu her kapının zamanında uygulama alacaktır
            for gate in [g for g in circuit.gates if g.time <= time_point <= g.end_time]:
                qubits = gate.qubits
                # Kapı uygulamasını profil et
                self.profile_event(
                    event_type=ProfilingEvent.GATE_APPLY,
                    time_point=time_point,
                    qubit=qubits[0] if qubits else None,
                    gate=gate
                )
                
                # Ölçüm işlemlerini profil et
                if gate.type.name == "MEASURE":
                    self.profile_event(
                        event_type=ProfilingEvent.MEASUREMENT,
                        time_point=time_point,
                        qubit=qubits[0] if qubits else None
                    )
        
        # Profilciyi durdur
        self.stop_profiling()
        
        return profile
        
    def profile_circuit(self, circuit=None, max_time=1000):
        """
        Devre profillemesi yapar
        
        Args:
            circuit: Profilleme yapılacak devre
            max_time: Maksimum simülasyon süresi
            
        Returns:
            dict: Profilleme sonuçları
        """
        if circuit is None and self.circuit is None:
            raise ValueError("Profilleme için bir devre belirtilmelidir")
        
        if circuit:
            self.circuit = circuit
        
        # Devre yürütme profillemesi
        profile = self.profile_circuit_execution(self.circuit, max_time)
        
        # Darboğaz analizi
        bottlenecks = self.analyze_bottlenecks(profile)
        
        # Sonuçları derle
        results = {
            'max_qubits': profile.get_memory_usage_stats().get('max_total_qubits', 0),
            'avg_lifetime': profile.get_average_qubit_lifetime() or 0,
            'bottlenecks': bottlenecks,
            'profile': profile,
            'circuit_name': self.circuit.name if hasattr(self.circuit, 'name') else 'unnamed',
            'circuit_width': self.circuit.width if hasattr(self.circuit, 'width') else 0,
            'transfer_counts': dict(profile.transfer_counts),
            'operation_counts': {str(k.name): v for k, v in profile.operation_counts.items()},
            'execution_time': profile.end_time - profile.start_time if profile.end_time else 0,
            'memory_usage': profile.get_memory_usage_stats(),
            'recommendations': self.recommend_optimizations(profile)
        }
        
        return results
    
    def analyze_bottlenecks(self, profile=None):
        """
        Bellek darboğazlarını analiz eder
        
        Args:
            profile: Analiz edilecek profil (None ise en son profil kullanılır)
            
        Returns:
            list: Tespit edilen darboğazlar
        """
        profile = profile or (self.profiles[-1] if self.profiles else None)
        if profile is None:
            return []
            
        return profile.bottlenecks
    
    def recommend_optimizations(self, profile=None):
        """
        Bellek kullanımını iyileştirmek için öneriler sunar
        
        Args:
            profile: Analiz edilecek profil (None ise en son profil kullanılır)
            
        Returns:
            list: Optimizasyon önerileri
        """
        profile = profile or (self.profiles[-1] if self.profiles else None)
        if profile is None:
            return []
            
        recommendations = []
        memory_stats = profile.get_memory_usage_stats()
        bottleneck_summary = profile.get_bottleneck_summary()
        
        # Bellek seviyesi dengesizliği kontrolü
        if memory_stats["L1_utilization"] > 0.8 and memory_stats["L3_utilization"] < 0.3:
            recommendations.append("Consider offloading qubits from L1 to L3 memory for long-term storage")
            
        if memory_stats["L2_utilization"] < 0.2 and (memory_stats["L1_utilization"] > 0.7 or memory_stats["L3_utilization"] > 0.7):
            recommendations.append("L2 memory is underutilized. Consider using it as a buffer between L1 and L3")
        
        # Darboğaz analizi
        if bottleneck_summary["count"] > 0:
            if bottleneck_summary["most_constrained_level"] == "L1":
                recommendations.append("L1 memory is a bottleneck. Consider using more aggressive recycling or offloading to L2/L3")
            elif bottleneck_summary["most_constrained_level"] == "L2":
                recommendations.append("L2 memory is a bottleneck. Consider bypassing L2 for some transfers or increasing L2 capacity")
            elif bottleneck_summary["most_constrained_level"] == "L3":
                recommendations.append("L3 memory is a bottleneck. Consider more aggressive qubit deallocation or increasing L3 capacity")
        
        # Transfer analizi
        high_l1_l3_transfers = profile.transfer_counts.get(("L1", "L3"), 0) + profile.transfer_counts.get(("L3", "L1"), 0)
        if high_l1_l3_transfers > 10:
            recommendations.append("High number of direct L1<->L3 transfers. Consider using L2 as intermediate buffer to reduce transfer errors")
        
        # Hotspot analizi
        if profile.hotspots:
            recommendations.append(f"Found {len(profile.hotspots)} hotspots with high operation density. Consider spreading operations more evenly")
        
        return recommendations
    
    def compare_profiles(self, profile1, profile2):
        """
        İki profili karşılaştırır
        
        Args:
            profile1: Birinci profil
            profile2: İkinci profil
            
        Returns:
            dict: Karşılaştırma sonuçları
        """
        if profile1 is None or profile2 is None:
            return None
            
        stats1 = profile1.get_memory_usage_stats()
        stats2 = profile2.get_memory_usage_stats()
        
        bottleneck1 = profile1.get_bottleneck_summary()
        bottleneck2 = profile2.get_bottleneck_summary()
        
        return {
            "name1": profile1.circuit_name or "Profile 1",
            "name2": profile2.circuit_name or "Profile 2",
            
            "L1_avg_diff": stats2["L1_avg"] - stats1["L1_avg"],
            "L2_avg_diff": stats2["L2_avg"] - stats1["L2_avg"],
            "L3_avg_diff": stats2["L3_avg"] - stats1["L3_avg"],
            
            "L1_max_diff": stats2["L1_max"] - stats1["L1_max"],
            "L2_max_diff": stats2["L2_max"] - stats1["L2_max"],
            "L3_max_diff": stats2["L3_max"] - stats1["L3_max"],
            
            "L1_util_diff": stats2["L1_utilization"] - stats1["L1_utilization"],
            "L2_util_diff": stats2["L2_utilization"] - stats1["L2_utilization"],
            "L3_util_diff": stats2["L3_utilization"] - stats1["L3_utilization"],
            
            "bottleneck_count_diff": bottleneck2["count"] - bottleneck1["count"],
            "bottleneck_time_diff": bottleneck2["total_duration"] - bottleneck1["total_duration"],
            
            "qubit_lifetime_diff": profile2.get_average_qubit_lifetime() - profile1.get_average_qubit_lifetime()
        } 