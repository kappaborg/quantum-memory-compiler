"""
Bellek Yöneticisi modülü
=====================

Kuantum bellek hiyerarşisini yöneten ve qubit tahsisini optimize eden sınıf.
"""

import logging
from collections import defaultdict

from ..core.qubit import Qubit, QubitType, MemoryLevel as QubitMemLevel
from .hierarchy import MemoryHierarchy
from .allocation import QubitAllocator


class MemoryManager:
    """Kuantum bellek hiyerarşisini yöneten ve qubit'leri tahsis eden sınıf"""
    
    def __init__(self, memory_hierarchy, allocator_strategy="lifetime"):
        """
        MemoryManager nesnesini başlatır
        
        Args:
            memory_hierarchy: MemoryHierarchy nesnesi
            allocator_strategy: Kullanılacak tahsis stratejisi ("static", "lifetime", "dynamic")
        """
        self.memory_hierarchy = memory_hierarchy
        self.allocator_strategy = allocator_strategy
        
        # Qubit tahsis stratejisini oluştur
        self.allocator = QubitAllocator.create(allocator_strategy)
        
        # Qubit izleme verileri
        self.active_qubits = set()        # Şu anda aktif olan qubit'ler
        self.qubit_levels = {}            # Qubit -> bellek seviyesi eşleştirmesi
        self.qubit_usage_times = {}       # Qubit -> (başlangıç zamanı, son kullanım zamanı)
        self.qubit_access_frequency = {}  # Qubit -> erişim sayısı
        
        # Bellek optimizasyonu verileri
        self.transfer_queue = []       # Yaklaşan transferler listesi: (qubit, hedef seviye, zaman)
        self.current_time = 0          # Simülasyon zamanı
        self.optimization_interval = 10 # Bellek optimizasyonu aralığı (simülasyon zaman birimi)
        self.last_optimization_time = 0 # Son optimizasyon zamanı
        
        # Loglar
        self.logger = logging.getLogger("MemoryManager")
        self.logger.setLevel(logging.INFO)
    
    def allocate_qubit(self, level_name="L1"):
        """
        Yeni bir qubit tahsis eder ve belirtilen bellek seviyesine yerleştirir
        
        Args:
            level_name: Bellek seviyesi adı (varsayılan: L1)
            
        Returns:
            Qubit: Tahsis edilen qubit veya None (başarısızsa)
        """
        # Yeni qubit oluştur
        qubit_id = len(self.active_qubits)
        qubit = Qubit(qubit_id, QubitType.LOGICAL, getattr(QubitMemLevel, level_name))
        
        # Bellek seviyesinde tahsis et
        if self.memory_hierarchy.allocate_qubit(qubit, level_name):
            # Başarılı tahsis
            self.active_qubits.add(qubit)
            self.qubit_levels[qubit] = level_name
            self.qubit_usage_times[qubit] = (self.current_time, self.current_time)
            self.qubit_access_frequency[qubit] = 1
            
            self.logger.debug(f"Qubit {qubit.id} allocated at level {level_name}")
            return qubit
        
        self.logger.warning(f"Failed to allocate qubit at level {level_name}")
        return None
    
    def allocate_qubits(self, n, level_name="L1"):
        """
        Birden çok qubit tahsis eder
        
        Args:
            n: Tahsis edilecek qubit sayısı
            level_name: Bellek seviyesi adı
            
        Returns:
            list: Tahsis edilen qubit'ler listesi
        """
        return [self.allocate_qubit(level_name) for _ in range(n)]
    
    def deallocate_qubit(self, qubit):
        """
        Qubit'i serbest bırakır
        
        Args:
            qubit: Serbest bırakılacak qubit
            
        Returns:
            bool: İşlem başarılı oldu mu?
        """
        if qubit not in self.active_qubits:
            self.logger.warning(f"Qubit {qubit.id} is not active, cannot deallocate")
            return False
        
        if self.memory_hierarchy.deallocate_qubit(qubit):
            # Başarılı serbest bırakma
            self.active_qubits.remove(qubit)
            
            if qubit in self.qubit_levels:
                del self.qubit_levels[qubit]
            if qubit in self.qubit_usage_times:
                del self.qubit_usage_times[qubit]
            if qubit in self.qubit_access_frequency:
                del self.qubit_access_frequency[qubit]
            
            self.logger.debug(f"Qubit {qubit.id} deallocated")
            return True
        
        self.logger.warning(f"Failed to deallocate qubit {qubit.id}")
        return False
    
    def get_qubit_memory_level(self, qubit):
        """
        Qubit'in bulunduğu bellek seviyesini döndürür
        
        Args:
            qubit: Sorgulanacak qubit
            
        Returns:
            str: Bellek seviyesi adı veya None
        """
        return self.qubit_levels.get(qubit)
    
    def update_qubit_usage(self, qubit, time):
        """
        Qubit kullanımını günceller
        
        Args:
            qubit: Güncellenen qubit
            time: Kullanım zamanı
        """
        if qubit not in self.active_qubits:
            self.logger.warning(f"Qubit {qubit.id} is not active, cannot update usage")
            return
        
        # Qubit'in son kullanım zamanını güncelle
        start_time, _ = self.qubit_usage_times.get(qubit, (time, time))
        self.qubit_usage_times[qubit] = (start_time, time)
        
        # Erişim frekansını artır
        self.qubit_access_frequency[qubit] = self.qubit_access_frequency.get(qubit, 0) + 1
        
        # Qubit'in son kullanım zamanını güncelle
        qubit.update_usage_time(time)
    
    def transfer_qubit(self, qubit, target_level):
        """
        Qubit'i farklı bir bellek seviyesine taşır
        
        Args:
            qubit: Taşınacak qubit
            target_level: Hedef bellek seviyesi adı
            
        Returns:
            tuple: (başarı durumu, transfer süresi)
        """
        if qubit not in self.active_qubits:
            self.logger.warning(f"Qubit {qubit.id} is not active, cannot transfer")
            return False, 0
        
        current_level = self.qubit_levels.get(qubit)
        if current_level == target_level:
            return True, 0
        
        self.logger.debug(f"Transferring qubit {qubit.id} from {current_level} to {target_level}")
        
        # Transferi gerçekleştir
        success, transfer_time = self.memory_hierarchy.transfer_qubit(qubit, target_level)
        
        if success:
            # Qubit'in bellek seviyesini güncelle
            self.qubit_levels[qubit] = target_level
            self.logger.debug(f"Qubit {qubit.id} transferred to {target_level} in {transfer_time} time units")
        else:
            self.logger.warning(f"Failed to transfer qubit {qubit.id} to {target_level}")
        
        return success, transfer_time
    
    def queue_transfer(self, qubit, target_level, scheduled_time):
        """
        Belirli bir zamanda gerçekleşecek transfer işlemini kuyruğa ekler
        
        Args:
            qubit: Taşınacak qubit
            target_level: Hedef bellek seviyesi
            scheduled_time: Transfer zamanı
        """
        self.transfer_queue.append((qubit, target_level, scheduled_time))
        self.transfer_queue.sort(key=lambda x: x[2])  # Zamana göre sırala
        
        self.logger.debug(f"Queued transfer of qubit {qubit.id} to {target_level} at time {scheduled_time}")
    
    def process_transfers(self, current_time):
        """
        Belirli bir zamana kadar olan transfer işlemlerini gerçekleştirir
        
        Args:
            current_time: Şu anki zaman
            
        Returns:
            int: Gerçekleştirilen transfer sayısı
        """
        self.current_time = current_time
        transfers_processed = 0
        
        # Transfer kuyruğundaki işlemleri kontrol et
        pending_transfers = []
        
        for qubit, target_level, scheduled_time in self.transfer_queue:
            if scheduled_time <= current_time:
                # Transferi gerçekleştir
                success, transfer_time = self.transfer_qubit(qubit, target_level)
                if success:
                    transfers_processed += 1
            else:
                # Henüz zamanı gelmemiş transferler
                pending_transfers.append((qubit, target_level, scheduled_time))
        
        # Kuyruğu güncelle
        self.transfer_queue = pending_transfers
        
        return transfers_processed
    
    def optimize_memory(self, circuit, current_time):
        """
        Bellek kullanımını optimize eder
        
        Args:
            circuit: Optimize edilecek devre
            current_time: Şu anki zaman
            
        Returns:
            int: Kuyruğa eklenen transfer sayısı
        """
        self.current_time = current_time
        
        # Optimize etmek için henüz erken mi?
        if current_time - self.last_optimization_time < self.optimization_interval:
            return 0
        
        self.logger.info(f"Optimizing memory at time {current_time}")
        self.last_optimization_time = current_time
        
        # Her qubit için yaşam süresi analizi
        queued_transfers = 0
        qubit_lifetimes = {}
        
        for qubit in self.active_qubits:
            # Devreden qubit yaşam süresi bilgisini al
            start_time, end_time = circuit.get_qubit_lifetime(qubit)
            
            # Devrede kullanılmayan qubit'ler için yöneticiden yaşam süresi bilgisini al
            if start_time == end_time == 0:
                start_time, end_time = self.qubit_usage_times.get(qubit, (current_time, current_time))
            
            qubit_lifetimes[qubit] = (start_time, end_time)
            
            # Qubit yaşam süresine göre en uygun bellek seviyesini belirle
            remaining_lifetime = max(0, end_time - current_time)
            best_level = self.memory_hierarchy.get_best_level_for_qubit(qubit, remaining_lifetime)
            current_level = self.qubit_levels.get(qubit)
            
            # Eğer farklı bir seviyeye taşınması gerekiyorsa, transferi planla
            if best_level != current_level:
                # Taşıma zamanını belirle (şimdi veya biraz sonra)
                transfer_time = current_time
                
                # Transferi kuyruğa ekle
                self.queue_transfer(qubit, best_level, transfer_time)
                queued_transfers += 1
                
                self.logger.debug(f"Optimization: Qubit {qubit.id} should move from {current_level} to {best_level} "
                                 f"(remaining lifetime: {remaining_lifetime})")
        
        return queued_transfers
    
    def update_time(self, time):
        """
        Bellek yöneticisinin zamanını günceller ve bekleyen transferleri işler
        
        Args:
            time: Yeni zaman
            
        Returns:
            int: İşlenen transfer sayısı
        """
        if time < self.current_time:
            self.logger.warning(f"Cannot update time backward from {self.current_time} to {time}")
            return 0
        
        # Bekleyen transferleri işle
        return self.process_transfers(time)
    
    def get_memory_stats(self):
        """
        Bellek kullanım istatistiklerini döndürür
        
        Returns:
            dict: Bellek kullanım istatistikleri
        """
        stats = {
            "active_qubits": len(self.active_qubits),
            "level_stats": self.memory_hierarchy.get_utilization_stats(),
            "transfer_stats": self.memory_hierarchy.get_transfer_stats(),
            "pending_transfers": len(self.transfer_queue)
        }
        
        # Seviye başına qubit dağılımı
        level_distribution = defaultdict(int)
        for level in self.qubit_levels.values():
            level_distribution[level] += 1
        stats["level_distribution"] = dict(level_distribution)
        
        return stats
    
    def reset(self):
        """Bellek yöneticisini sıfırlar"""
        # Tüm aktif qubit'leri serbest bırak
        for qubit in list(self.active_qubits):
            self.deallocate_qubit(qubit)
        
        # Bellek hiyerarşisini sıfırla
        self.memory_hierarchy.reset()
        
        # İç durumu sıfırla
        self.active_qubits.clear()
        self.qubit_levels.clear()
        self.qubit_usage_times.clear()
        self.qubit_access_frequency.clear()
        self.transfer_queue.clear()
        self.current_time = 0
        self.last_optimization_time = 0
        
        self.logger.info("Memory manager reset")
    
    def __str__(self):
        """Bellek yöneticisinin string temsilini döndürür"""
        active_count = len(self.active_qubits)
        pending_count = len(self.transfer_queue)
        
        return (f"MemoryManager(strategy={self.allocator_strategy}, "
                f"active_qubits={active_count}, pending_transfers={pending_count})") 