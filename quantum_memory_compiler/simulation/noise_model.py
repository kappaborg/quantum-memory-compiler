"""
NoiseModel modülü
==============

Kuantum gürültü modellerini temsil eden sınıf.
"""

import numpy as np
from collections import defaultdict
from ..core.gate import GateType


class NoiseModel:
    """
    Kuantum gürültü modellerini temsil eden sınıf
    
    Bit-flip, phase-flip, depolarizasyon, termal etki, ölçüm hatası, ve koherans 
    kaybı gibi gerçekçi hata modellerini destekler.
    """
    
    def __init__(self, depolarizing_prob=0.01, bit_flip_prob=0.005, phase_flip_prob=0.005,
                 amplitude_damping_prob=0.003, thermal_relaxation_prob=0.002, 
                 measurement_error_prob=0.01, crosstalk_prob=0.001):
        """
        NoiseModel nesnesini başlatır
        
        Args:
            depolarizing_prob: Depolarizasyon hatası olasılığı
            bit_flip_prob: Bit-flip hatası olasılığı
            phase_flip_prob: Phase-flip hatası olasılığı
            amplitude_damping_prob: Genlik sönümlenmesi hatası (T1 dekoherans)
            thermal_relaxation_prob: Termal relaksasyon hatası
            measurement_error_prob: Ölçüm hatası olasılığı
            crosstalk_prob: Çapraz etkileşim (crosstalk) hatası olasılığı
        """
        self.depolarizing_prob = depolarizing_prob
        self.bit_flip_prob = bit_flip_prob
        self.phase_flip_prob = phase_flip_prob
        self.amplitude_damping_prob = amplitude_damping_prob
        self.thermal_relaxation_prob = thermal_relaxation_prob
        self.measurement_error_prob = measurement_error_prob
        self.crosstalk_prob = crosstalk_prob
        
        # Hata kayıtları
        self.error_history = defaultdict(list)
        
        # Özel kapı hata oranları
        self.gate_error_rates = {
            GateType.X: bit_flip_prob,
            GateType.Y: bit_flip_prob + phase_flip_prob,
            GateType.Z: phase_flip_prob,
            GateType.H: (bit_flip_prob + phase_flip_prob) / 2,
            GateType.S: phase_flip_prob * 1.2,
            GateType.T: phase_flip_prob * 1.5,
            GateType.RX: bit_flip_prob * 1.2,
            GateType.RY: bit_flip_prob * 1.2,
            GateType.RZ: phase_flip_prob * 1.2,
            GateType.CNOT: depolarizing_prob * 2,  # İki qubitli kapılar daha hatalı
            GateType.CZ: depolarizing_prob * 2,
            GateType.SWAP: depolarizing_prob * 3,  # SWAP 3 CNOT'a eşdeğer
            GateType.MEASURE: measurement_error_prob
        }
        
        # Mitigation teknikleri
        self.active_mitigations = set()
    
    def apply_noise(self, gate, qubit_states, time=None, circuit_idx=None):
        """
        Kapıya gürültü ekler
        
        Args:
            gate: Gürültü eklenecek kapı
            qubit_states: Etkilenen qubit durumları
            time: Kapının uygulandığı zaman (opsiyonel)
            circuit_idx: Devredeki kapı indeksi (opsiyonel)
            
        Returns:
            bool: Gürültü uygulandıysa True
        """
        if not qubit_states:
            return False
            
        # Kapı tipine uygun hata oranını belirle
        error_rate = self.gate_error_rates.get(gate.type, self.depolarizing_prob)
        applied_errors = []
        
        # Her qubit için rastgele hata uygula
        for i, qubit_state in enumerate(qubit_states):
            error_applied = False
            
            # Depolarizasyon hatası
            if np.random.random() < error_rate:
                self._apply_depolarizing_error(qubit_state)
                applied_errors.append(("depolarizing", i))
                error_applied = True
                
            # Bit-flip hatası
            elif np.random.random() < self.bit_flip_prob:
                self._apply_bit_flip(qubit_state)
                applied_errors.append(("bit_flip", i))
                error_applied = True
                
            # Phase-flip hatası
            elif np.random.random() < self.phase_flip_prob:
                self._apply_phase_flip(qubit_state)
                applied_errors.append(("phase_flip", i))
                error_applied = True
                
            # Genlik sönümlenmesi (amplitude damping)
            elif np.random.random() < self.amplitude_damping_prob:
                self._apply_amplitude_damping(qubit_state)
                applied_errors.append(("amplitude_damping", i))
                error_applied = True
                
            # Termal relaksasyon
            elif np.random.random() < self.thermal_relaxation_prob:
                self._apply_thermal_relaxation(qubit_state)
                applied_errors.append(("thermal_relaxation", i))
                error_applied = True
            
            # Hata tarihçesini kaydet
            if error_applied and circuit_idx is not None:
                self.error_history[circuit_idx].append((gate.type.name, i, time, applied_errors[-1][0]))
                
        # İki qubitli kapılar için çapraz etkileşim hatası
        if len(qubit_states) > 1 and np.random.random() < self.crosstalk_prob:
            self._apply_crosstalk(qubit_states)
            applied_errors.append(("crosstalk", -1))
            
        # Aktif hata azaltma teknikleri uygulanıyorsa
        if "measurement_error_mitigation" in self.active_mitigations and gate.type == GateType.MEASURE:
            self._mitigate_measurement_error(qubit_states[0])
            
        if "zne" in self.active_mitigations:
            # Zero Noise Extrapolation için hata verilerini sakla
            if circuit_idx is not None and applied_errors:
                self.error_history[circuit_idx].extend(applied_errors)
                
        return len(applied_errors) > 0
    
    def _apply_bit_flip(self, qubit_state):
        """
        Bit-flip hatası uygular (X kapısı)
        
        Args:
            qubit_state: Hata uygulanacak qubit durumu
        """
        # X matrisi: [[0, 1], [1, 0]]
        alpha, beta = qubit_state.alpha, qubit_state.beta
        qubit_state.alpha = beta
        qubit_state.beta = alpha
    
    def _apply_phase_flip(self, qubit_state):
        """
        Phase-flip hatası uygular (Z kapısı)
        
        Args:
            qubit_state: Hata uygulanacak qubit durumu
        """
        # Z matrisi: [[1, 0], [0, -1]]
        qubit_state.beta *= -1
    
    def _apply_depolarizing_error(self, qubit_state):
        """
        Depolarizasyon hatası uygular (rastgele Pauli hatası)
        
        Args:
            qubit_state: Hata uygulanacak qubit durumu
        """
        # Rastgele bir Pauli hatası seç
        error_type = np.random.choice(["I", "X", "Y", "Z"])
        
        if error_type == "X":
            # X hatası
            self._apply_bit_flip(qubit_state)
        elif error_type == "Z":
            # Z hatası
            self._apply_phase_flip(qubit_state)
        elif error_type == "Y":
            # Y hatası (X ve Z'nin bileşimi)
            self._apply_bit_flip(qubit_state)
            self._apply_phase_flip(qubit_state)
        # "I" için hiçbir şey yapma
    
    def _apply_amplitude_damping(self, qubit_state):
        """
        Genlik sönümlenmesi (amplitude damping) hatası uygular (T1 dekoherans)
        
        Args:
            qubit_state: Hata uygulanacak qubit durumu
        """
        # T1 bozunması: |1⟩ durumundan |0⟩ durumuna geçiş
        if abs(qubit_state.beta) > 0:
            # Bozunma olasılığına bağlı olarak |0⟩ durumuna geçiş
            damping_probability = np.random.random()
            if damping_probability < self.amplitude_damping_prob * 2:  # 2 ile çarpma daha belirgin etki için
                # |0⟩ durumuna kısmi geçiş
                damping_factor = 1 - damping_probability
                qubit_state.beta *= damping_factor
                # Normalizasyon
                norm = np.sqrt(abs(qubit_state.alpha)**2 + abs(qubit_state.beta)**2)
                qubit_state.alpha /= norm
                qubit_state.beta /= norm
    
    def _apply_thermal_relaxation(self, qubit_state):
        """
        Termal relaksasyon hatası uygular
        
        Args:
            qubit_state: Hata uygulanacak qubit durumu
        """
        # Termal denge durumuna yaklaşma
        # Sıcaklığa bağlı olarak |0⟩ ve |1⟩ arasında denge oluşur
        thermal_prob = 0.1  # Termal denge durumunda |1⟩ olma olasılığı
        
        if np.random.random() < self.thermal_relaxation_prob * 2:  # 2 ile çarpma daha belirgin etki için
            # Termal dengeye doğru kısmi değişim
            relaxation_rate = np.random.random() * self.thermal_relaxation_prob
            
            # Mevcut olasılık dağılımı
            p0 = abs(qubit_state.alpha)**2
            p1 = abs(qubit_state.beta)**2
            
            # Yeni olasılık dağılımı
            new_p0 = p0 * (1 - relaxation_rate) + (1 - thermal_prob) * relaxation_rate
            new_p1 = p1 * (1 - relaxation_rate) + thermal_prob * relaxation_rate
            
            # Yeni durum vektörü
            qubit_state.alpha = np.sqrt(new_p0) * np.exp(1j * np.angle(qubit_state.alpha))
            qubit_state.beta = np.sqrt(new_p1) * np.exp(1j * np.angle(qubit_state.beta))
    
    def _apply_crosstalk(self, qubit_states):
        """
        Çapraz etkileşim (crosstalk) hatası uygular
        
        Args:
            qubit_states: Etkileşen qubit durumları
        """
        if len(qubit_states) < 2:
            return
            
        # Rastgele iki qubit seç
        q1_idx, q2_idx = np.random.choice(range(len(qubit_states)), 2, replace=False)
        q1, q2 = qubit_states[q1_idx], qubit_states[q2_idx]
        
        # Küçük bir fazlı etkileşim uygula
        phase_shift = np.random.random() * np.pi / 8  # Küçük bir faz kayması
        
        # q1'in durumu q2'nin durumunu etkiler
        if abs(q1.beta) > 0.5:  # q1 |1⟩ durumuna yakınsa
            q2.beta *= np.exp(1j * phase_shift)  # q2'ye faz kayması uygula
        
        # q2'nin durumu q1'in durumunu etkiler
        if abs(q2.beta) > 0.5:  # q2 |1⟩ durumuna yakınsa
            q1.beta *= np.exp(1j * phase_shift)  # q1'e faz kayması uygula
    
    def _mitigate_measurement_error(self, qubit_state):
        """
        Ölçüm hatalarını azaltan basit bir teknik uygular
        
        Args:
            qubit_state: Ölçülecek qubit durumu
        """
        # Belirsiz bölgelerde daha kesin bir ölçüm yapmak için durumu güçlendir
        alpha_mag = abs(qubit_state.alpha)
        beta_mag = abs(qubit_state.beta)
        
        # Eğer durum |0⟩ veya |1⟩'e çok yakınsa, ölçüm hatasını azalt
        threshold = 0.15
        if alpha_mag > 1 - threshold:  # Çok |0⟩'a yakın
            qubit_state.alpha = 1.0
            qubit_state.beta = 0.0
        elif beta_mag > 1 - threshold:  # Çok |1⟩'e yakın
            qubit_state.alpha = 0.0
            qubit_state.beta = 1.0
    
    def enable_error_mitigation(self, technique):
        """
        Hata azaltma tekniğini etkinleştirir
        
        Args:
            technique: Etkinleştirilecek hata azaltma tekniği
                      ('zne', 'measurement_error_mitigation', 'qec', 'richardson')
        """
        self.active_mitigations.add(technique)
        
    def disable_error_mitigation(self, technique):
        """
        Hata azaltma tekniğini devre dışı bırakır
        
        Args:
            technique: Devre dışı bırakılacak hata azaltma tekniği
        """
        if technique in self.active_mitigations:
            self.active_mitigations.remove(technique)
    
    def reset_error_history(self):
        """Hata geçmişini temizler"""
        self.error_history = defaultdict(list)
    
    def get_error_statistics(self):
        """
        Hata istatistiklerini döndürür
        
        Returns:
            dict: Hata tiplerine göre istatistikler
        """
        stats = defaultdict(int)
        for gate_errors in self.error_history.values():
            for _, _, _, error_type in gate_errors:
                stats[error_type] += 1
                
        return dict(stats)
    
    def __str__(self):
        return (f"NoiseModel(depolarizing={self.depolarizing_prob}, "
                f"bit_flip={self.bit_flip_prob}, phase_flip={self.phase_flip_prob}, "
                f"amplitude_damping={self.amplitude_damping_prob}, "
                f"thermal_relaxation={self.thermal_relaxation_prob}, "
                f"measurement_error={self.measurement_error_prob}, "
                f"crosstalk={self.crosstalk_prob})") 