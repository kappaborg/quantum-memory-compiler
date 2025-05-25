"""
ErrorMitigation modülü
===================

Kuantum hata azaltma tekniklerini gerçekleştiren sınıf.
"""

import numpy as np
from collections import defaultdict, Counter
import copy
import matplotlib
matplotlib.use('Agg')

class ErrorMitigation:
    """
    Kuantum hata azaltma tekniklerini gerçekleştiren sınıf
    
    Ölçüm hatası azaltma, sıfır gürültü ekstrapolasyonu (ZNE), Richardson ekstrapolasyonu 
    ve daha fazlasını destekler.
    """
    
    def __init__(self, simulator):
        """
        ErrorMitigation nesnesini başlatır
        
        Args:
            simulator: Simülatör nesnesi
        """
        self.simulator = simulator
        self.calibration_data = {}
        self.correction_matrices = {}
        self.extrapolation_scales = [1.0, 1.5, 2.0, 3.0]  # ZNE için ölçekleme faktörleri
        self.ansatz_results = defaultdict(list)  # ZNE sonuçları için
    
    def calibrate_measurement_errors(self, circuit, shots=1024):
        """
        Ölçüm hatalarını kalibre eder
        
        Args:
            circuit: Kalibrasyon devreleri oluşturmak için kullanılacak temel devre
            shots: Her kalibrasyon devresi için simülasyon tekrar sayısı
            
        Returns:
            dict: Kalibrasyon verileri
        """
        from ..core.circuit import Circuit
        from ..core.gate import Gate, GateType
        
        num_qubits = circuit.width
        basis_states = [format(i, f'0{num_qubits}b') for i in range(2**num_qubits)]
        
        # Her temel durum için bir kalibrasyon devresi oluştur
        cal_results = {}
        
        for basis_state in basis_states:
            # Hazırlık devresi oluştur
            cal_circuit = Circuit()
            
            # Tüm qubit'leri ekle
            for i in range(num_qubits):
                cal_circuit.add_qubit(circuit.qubits[i])
            
            # İlgili temel durumu hazırla
            for i, bit in enumerate(basis_state):
                if bit == '1':
                    # |1⟩ durumu için X kapısı uygula
                    cal_circuit.add_gate(GateType.X, circuit.qubits[i])
            
            # Tüm qubit'leri ölç
            for i in range(num_qubits):
                cal_circuit.add_measurement(circuit.qubits[i], i)
            
            # Devreyi çalıştır ve sonuçları kaydet
            results = self.simulator.run(cal_circuit, shots=shots)
            cal_results[basis_state] = results
        
        # Kalibrasyon verilerini sakla
        self.calibration_data = cal_results
        
        # Düzeltme matrislerini hesapla
        self._compute_correction_matrices(num_qubits)
        
        return cal_results
    
    def _compute_correction_matrices(self, num_qubits):
        """
        Ölçüm hatası düzeltme matrislerini hesaplar
        
        Args:
            num_qubits: Qubit sayısı
        """
        if not self.calibration_data:
            raise ValueError("Kalibrasyon verileri mevcut değil. Önce calibrate_measurement_errors işlevini çağırın.")
        
        basis_states = [format(i, f'0{num_qubits}b') for i in range(2**num_qubits)]
        n = len(basis_states)
        
        # Kalibrasyon matrisini oluştur
        cal_matrix = np.zeros((n, n))
        
        for i, prepared_state in enumerate(basis_states):
            results = self.calibration_data.get(prepared_state, {})
            
            for j, measured_state in enumerate(basis_states):
                cal_matrix[i, j] = results.get(measured_state, 0.0)
        
        # Matrisin tersini al (düzeltme matrisi)
        try:
            correction_matrix = np.linalg.inv(cal_matrix)
            self.correction_matrices[num_qubits] = correction_matrix
        except np.linalg.LinAlgError:
            # Matris tekil veya kötü koşullu ise, sözde-ters (pseudo-inverse) kullan
            correction_matrix = np.linalg.pinv(cal_matrix)
            self.correction_matrices[num_qubits] = correction_matrix
            print(f"Uyarı: {num_qubits} qubit için düzeltme matrisi oluştururken tersini alamadık. Sözde-ters kullanıldı.")
    
    def apply_measurement_error_mitigation(self, results, num_qubits):
        """
        Ölçüm hatası azaltma tekniğini uygular
        
        Args:
            results: Ham simülasyon sonuçları
            num_qubits: Qubit sayısı
            
        Returns:
            dict: Düzeltilmiş sonuçlar
        """
        if num_qubits not in self.correction_matrices:
            raise ValueError(f"{num_qubits} qubit için düzeltme matrisi bulunamadı.")
        
        basis_states = [format(i, f'0{num_qubits}b') for i in range(2**num_qubits)]
        n = len(basis_states)
        
        # Sonuçları bir vektöre dönüştür
        count_vector = np.zeros(n)
        for i, state in enumerate(basis_states):
            count_vector[i] = results.get(state, 0.0)
        
        # Düzeltme matrisini uygula
        corrected_vector = np.dot(self.correction_matrices[num_qubits], count_vector)
        
        # Negatif değerleri sıfırla ve normalizasyon
        corrected_vector = np.maximum(0, corrected_vector)
        if np.sum(corrected_vector) > 0:
            corrected_vector /= np.sum(corrected_vector)
        
        # Düzeltilmiş sonuçları oluştur
        corrected_results = {}
        for i, state in enumerate(basis_states):
            if corrected_vector[i] > 1e-10:  # Çok küçük değerleri atla
                corrected_results[state] = corrected_vector[i]
        
        return corrected_results
    
    def zero_noise_extrapolation(self, circuit, observable_fn, shots=1024, scale_noise=True):
        """
        Sıfır Gürültü Ekstrapolasyonu (ZNE) uygular
        
        Args:
            circuit: Simüle edilecek devre
            observable_fn: Gözlemlenebilir fonksiyon (sonuçlardan beklenen değer hesaplar)
            shots: Simülasyon tekrar sayısı
            scale_noise: Gürültüyü ölçeklemek için etkin olmalı
            
        Returns:
            float: Gürültüsüz tahmin edilen beklenen değer
        """
        if self.simulator.noise_model is None:
            raise ValueError("ZNE için gürültü modeli gereklidir.")
        
        self.simulator.noise_model.enable_error_mitigation("zne")
        
        # Farklı gürültü seviyelerinde devreyi çalıştır
        scale_results = []
        
        for scale in self.extrapolation_scales:
            # Simülatörün bir kopyasını al
            # Mevcut noise_model'i kopyala
            temp_noise_model = copy.deepcopy(self.simulator.noise_model)
            
            if scale_noise:
                # Gürültü parametrelerini ölçekle
                temp_noise_model.depolarizing_prob *= scale
                temp_noise_model.bit_flip_prob *= scale
                temp_noise_model.phase_flip_prob *= scale
                temp_noise_model.amplitude_damping_prob *= scale
                temp_noise_model.thermal_relaxation_prob *= scale
                # Kapı hata oranlarını da güncelle
                for gate_type in temp_noise_model.gate_error_rates:
                    temp_noise_model.gate_error_rates[gate_type] *= scale
            
            # Devreyi çalıştır
            temp_simulator = copy.deepcopy(self.simulator)
            temp_simulator.noise_model = temp_noise_model
            results = temp_simulator.run(circuit, shots=shots)
            
            # Gözlemlenebilir değeri hesapla
            expectation = observable_fn(results)
            scale_results.append((scale, expectation))
            
            # Ansatz sonuçlarını sakla
            self.ansatz_results[circuit.name if hasattr(circuit, 'name') else 'unnamed'].append(
                (scale, results, expectation)
            )
        
        # Gürültüsüz değeri tahmin et (ölçekleme faktörü 0'a ekstrapolasyon)
        # Polinom ekstrapolasyonu kullan
        scales = np.array([s for s, _ in scale_results])
        expectations = np.array([e for _, e in scale_results])
        
        # Polynomial fit order (degree)
        degree = min(len(scales) - 1, 2)  # 2. dereceden fazla gitme
        
        # Polynomial ekstrapolasyonu
        coeffs = np.polyfit(scales, expectations, degree)
        poly = np.poly1d(coeffs)
        
        # 0 gürültü seviyesine ekstrapolasyon
        extrapolated_value = poly(0.0)
        
        return extrapolated_value
    
    def richardson_extrapolation(self, circuit, observable_fn, shots=1024):
        """
        Richardson ekstrapolasyonu uygular (gate folding ile)
        
        Args:
            circuit: Simüle edilecek devre
            observable_fn: Gözlemlenebilir fonksiyon (sonuçlardan beklenen değer hesaplar)
            shots: Simülasyon tekrar sayısı
            
        Returns:
            float: Gürültüsüz tahmin edilen beklenen değer
        """
        from ..core.gate import Gate
        from ..core.circuit import Circuit
        
        # Gate folding için katsayılar - identity insertion ile gürültüyü artır
        fold_factors = [1, 3, 5]  # 1x, 3x, 5x gate count
        results = []
        
        for factor in fold_factors:
            if factor == 1:
                # Orijinal devre
                folded_circuit = circuit
            else:
                # Kapı katlama: Her kapıyı kendisi+ters+kendisi şeklinde değiştir
                folded_circuit = Circuit()
                
                # Tüm qubit'leri ekle
                for qubit in circuit.qubits:
                    folded_circuit.add_qubit(qubit)
                
                # Her kapı için katlama uygula
                for gate in circuit.gates:
                    if gate.type.name in ["MEASURE", "RESET", "BARRIER"]:
                        # Ölçüm ve reset kapıları katlanmaz
                        folded_circuit.add_gate(copy.deepcopy(gate))
                    else:
                        # Kapıyı ekle
                        folded_circuit.add_gate(copy.deepcopy(gate))
                        
                        # factor-1 kez kapı+ters_kapı ekle
                        for _ in range((factor - 1) // 2):
                            # Kapının tersini ekle (I'ye çevir)
                            inverse_gate = gate.inverse() if hasattr(gate, 'inverse') else gate
                            folded_circuit.add_gate(copy.deepcopy(inverse_gate))
                            
                            # Orijinal kapıyı tekrar ekle
                            folded_circuit.add_gate(copy.deepcopy(gate))
            
            # Devreyi çalıştır
            sim_results = self.simulator.run(folded_circuit, shots=shots)
            
            # Gözlemlenebilir değeri hesapla
            expectation = observable_fn(sim_results)
            results.append((factor, expectation))
        
        # Richardson ekstrapolasyonu
        # 1. dereceden lineer ekstrapolasyon (basit)
        if len(results) >= 2:
            x0, y0 = results[0]
            x1, y1 = results[1]
            slope = (y1 - y0) / (x1 - x0)
            extrapolated = y0 - slope * x0  # x=0'a ekstrapolasyon
            
            # Daha fazla veri noktası varsa, 2. derece polinom
            if len(results) >= 3:
                factors = np.array([f for f, _ in results])
                expectations = np.array([e for _, e in results])
                coeffs = np.polyfit(factors, expectations, 2)
                extrapolated = coeffs[2]  # x=0 için sabit terim
            
            return extrapolated
        else:
            return results[0][1]  # Yeterli veri yoksa, ilk sonucu döndür
    
    def probabilistic_error_cancellation(self, circuit, shots=1024):
        """
        Olasılıksal Hata İptali (PEC) tekniğini uygular
        
        Bu teknik karmaşıktır ve bu basit implementasyon yalnızca konsepti gösterir
        
        Args:
            circuit: Simüle edilecek devre
            shots: Simülasyon tekrar sayısı
            
        Returns:
            dict: Düzeltilmiş sonuçlar
        """
        # Bu basit uygulamada, her ölçüm sonucunu farklı gürültü örnekleri ile çeşitlendireceğiz
        # ve sonra ağırlıklı ortalamasını alacağız
        
        # Farklı gürültü seviyelerinde multiple simülasyonlar çalıştır
        combined_results = Counter()
        total_weight = 0
        
        # Farklı gürültü seviyeleri (0.8, 0.9, 1.0, 1.1, 1.2) ile simülasyonlar çalıştır
        noise_scales = [0.8, 0.9, 1.0, 1.1, 1.2]
        for scale in noise_scales:
            # Gürültü modelinin bir kopyasını al ve ölçekle
            if self.simulator.noise_model:
                temp_noise_model = copy.deepcopy(self.simulator.noise_model)
                
                # Tüm hata olasılıklarını ölçekle
                for attr in ['depolarizing_prob', 'bit_flip_prob', 'phase_flip_prob', 
                             'amplitude_damping_prob', 'thermal_relaxation_prob']:
                    if hasattr(temp_noise_model, attr):
                        setattr(temp_noise_model, attr, getattr(temp_noise_model, attr) * scale)
                
                # Kapı hata oranlarını da ölçekle
                for gate_type in temp_noise_model.gate_error_rates:
                    temp_noise_model.gate_error_rates[gate_type] *= scale
                
                # Geçici simülatör oluştur ve kullan
                temp_simulator = copy.deepcopy(self.simulator)
                temp_simulator.noise_model = temp_noise_model
                results = temp_simulator.run(circuit, shots=shots)
                
                # Ağırlık hesapla - 1.0'a daha yakın scalelere daha çok ağırlık ver
                weight = 1.0 / (abs(scale - 1.0) + 0.5)
                
                # Ağırlıklı sonuçları topla
                for state, prob in results.items():
                    combined_results[state] += prob * weight
                    
                total_weight += weight
        
        # Sonuçları normalize et
        normalized_results = {}
        for state, count in combined_results.items():
            normalized_results[state] = count / total_weight
        
        return normalized_results
    
    def create_readout_calibration_circuits(self, circuit):
        """
        Readout kalibrasyonu için gerekli devreleri oluşturur
        
        Args:
            circuit: Temel devre
            
        Returns:
            list: Kalibrasyon devreleri
        """
        # Bu kısım calibrate_measurement_errors içinde kullanılır
        pass
    
    def reset_calibration_data(self):
        """Kalibrasyon verilerini temizler"""
        self.calibration_data = {}
        self.correction_matrices = {}
        self.ansatz_results = defaultdict(list)
    
    def get_extrapolation_data(self, circuit_name=None):
        """
        ZNE ekstrapolasyon verilerini döndürür
        
        Args:
            circuit_name: Devre adı (opsiyonel)
            
        Returns:
            list: Ekstrapolasyon verileri
        """
        if circuit_name is None:
            return dict(self.ansatz_results)
            
        return self.ansatz_results.get(circuit_name, []) 