"""
ErrorVisualization modülü
=====================

Gürültü etkilerini ve hata azaltma sonuçlarını görselleştiren sınıf.
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict


class ErrorVisualization:
    """
    Gürültü etkilerini ve hata azaltma sonuçlarını görselleştiren sınıf
    
    Simülasyon sonuçlarını ve hata istatistiklerini görselleştirmek için kullanılır.
    """
    
    def __init__(self, simulator):
        """
        ErrorVisualization nesnesini başlatır
        
        Args:
            simulator: Simülatör nesnesi
        """
        self.simulator = simulator
        self.figure_count = 0
    
    def plot_results_comparison(self, ideal_results, noisy_results, mitigated_results=None, 
                               title="Simülasyon Sonuçları Karşılaştırması", 
                               save_path=None):
        """
        İdeal, gürültülü ve hata azaltma uygulanmış sonuçları karşılaştırır
        
        Args:
            ideal_results: İdeal (gürültüsüz) simülasyon sonuçları
            noisy_results: Gürültülü simülasyon sonuçları
            mitigated_results: Hata azaltma uygulanmış sonuçları (opsiyonel)
            title: Grafik başlığı
            save_path: Grafiğin kaydedileceği dosya yolu (opsiyonel)
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Tüm sonuçlardaki durum etiketlerini topla ve sırala
        all_states = sorted(set(list(ideal_results.keys()) + 
                               list(noisy_results.keys()) + 
                               (list(mitigated_results.keys()) if mitigated_results else [])))
        
        x = np.arange(len(all_states))
        width = 0.25  # Çubuk genişliği
        
        # Gürültüsüz sonuçlar
        ideal_vals = [ideal_results.get(state, 0) for state in all_states]
        rects1 = ax.bar(x - width, ideal_vals, width, label='İdeal')
        
        # Gürültülü sonuçlar
        noisy_vals = [noisy_results.get(state, 0) for state in all_states]
        rects2 = ax.bar(x, noisy_vals, width, label='Gürültülü')
        
        # Hata azaltma uygulanmış sonuçlar
        if mitigated_results:
            mitigated_vals = [mitigated_results.get(state, 0) for state in all_states]
            rects3 = ax.bar(x + width, mitigated_vals, width, label='Hata Azaltmalı')
        
        # Grafik düzenlemeleri
        ax.set_title(title)
        ax.set_xlabel('Ölçüm sonuçları')
        ax.set_ylabel('Olasılık')
        ax.set_xticks(x)
        ax.set_xticklabels(all_states)
        ax.legend()
        
        # Grafik sınırları ayarla
        ax.set_ylim(0, 1.1)
        
        fig.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
            
        self.figure_count += 1
        plt.close(fig)
    
    def plot_error_distribution(self, noise_model, gate_runs=1000, 
                              title="Gürültü Dağılımı", save_path=None):
        """
        Gürültü modelinin farklı hata tiplerinin dağılımını görselleştir
        
        Args:
            noise_model: Gürültü modeli
            gate_runs: Simüle edilecek kapı sayısı
            title: Grafik başlığı
            save_path: Grafiğin kaydedileceği dosya yolu (opsiyonel)
        """
        if not hasattr(noise_model, 'get_error_statistics'):
            print("Bu gürültü modeli hata istatistiklerini desteklemiyor.")
            return
            
        # Gürültü modelinin geçmiş verilerini temizle
        if hasattr(noise_model, 'reset_error_history'):
            noise_model.reset_error_history()
        
        # Rastgele kapılar için gürültü uygula
        from ..core.gate import Gate, GateType
        from ..core.qubit import Qubit, QubitState
        
        error_counts = defaultdict(int)
        gate_types = [GateType.X, GateType.Y, GateType.Z, GateType.H, 
                      GateType.CNOT, GateType.S, GateType.T, 
                      GateType.RX, GateType.RY, GateType.RZ]
        
        for i in range(gate_runs):
            # Rastgele bir kapı seç
            gate_type = np.random.choice(gate_types)
            
            # Gerekli qubit sayısını belirle
            if gate_type == GateType.CNOT:
                num_qubits = 2
            else:
                num_qubits = 1
                
            # Kapı ve qubit durumlarını oluştur
            qubits = [Qubit(j) for j in range(num_qubits)]
            qubit_states = [q.state for q in qubits]
            gate = Gate(gate_type, qubits)
            
            # Gürültü uygula
            noise_model.apply_noise(gate, qubit_states, time=i, circuit_idx=i)
        
        # Hata istatistiklerini al
        error_stats = noise_model.get_error_statistics()
        
        if not error_stats:
            print("Hiç hata istatistiği toplanmadı.")
            return
            
        # Grafik çiz
        fig, ax = plt.subplots(figsize=(10, 6))
        
        error_types = list(error_stats.keys())
        error_counts = list(error_stats.values())
        
        ax.bar(error_types, error_counts)
        
        # Grafik düzenlemeleri
        ax.set_title(title)
        ax.set_xlabel('Hata Tipi')
        ax.set_ylabel('Sayı')
        
        plt.xticks(rotation=45)
        fig.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
            
        self.figure_count += 1
        plt.close(fig)
    
    def plot_zne_extrapolation(self, error_mitigation, circuit_name=None, 
                             title="Zero-Noise Extrapolation", save_path=None):
        """
        Sıfır Gürültü Ekstrapolasyonu (ZNE) sonuçlarını görselleştir
        
        Args:
            error_mitigation: Hata azaltma nesnesi
            circuit_name: Görselleştirilecek devre adı (opsiyonel)
            title: Grafik başlığı
            save_path: Grafiğin kaydedileceği dosya yolu (opsiyonel)
        """
        if not hasattr(error_mitigation, 'get_extrapolation_data'):
            print("Bu hata azaltma modeli ekstrapolasyon verilerini desteklemiyor.")
            return
            
        # Ekstrapolasyon verilerini al
        extrapolation_data = error_mitigation.get_extrapolation_data(circuit_name)
        
        if not extrapolation_data:
            print("Hiçbir ekstrapolasyon verisi bulunamadı.")
            return
            
        # Düzeltme: Eğer doğrudan bir liste dönerse, onu kullan
        if isinstance(extrapolation_data, list):
            data_points = extrapolation_data
        elif isinstance(extrapolation_data, dict):
            if circuit_name is None:
                circuit_name = list(extrapolation_data.keys())[0]
            data_points = extrapolation_data[circuit_name]
        else:
            print("Beklenmeyen ekstrapolasyon veri tipi.")
            return
        
        # Veri noktalarını ayır
        scales = [p[0] for p in data_points]
        expectations = [p[2] for p in data_points]
        
        # Ekstrapolasyon için polinom uydurma
        degree = min(len(scales) - 1, 2)  # 2. dereceden fazla gitme
        coeffs = np.polyfit(scales, expectations, degree)
        poly = np.poly1d(coeffs)
        
        # Düzgün bir eğri için daha fazla nokta
        x_smooth = np.linspace(0, max(scales)*1.1, 100)
        y_smooth = poly(x_smooth)
        
        # Sıfır gürültü değeri (ekstrapolasyon)
        zero_noise_value = poly(0.0)
        
        # Grafik çiz
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Veri noktalarını çiz
        ax.scatter(scales, expectations, color='blue', label='Simülasyon Sonuçları')
        
        # Ekstrapolasyon eğrisini çiz
        ax.plot(x_smooth, y_smooth, 'r-', label=f'{degree}. Derece Polinom Ekstrapolasyonu')
        
        # Sıfır gürültü noktasını vurgula
        ax.plot(0, zero_noise_value, 'go', markersize=10, label=f'Ekstrapolasyon: {zero_noise_value:.4f}')
        
        # Grafik düzenlemeleri
        ax.set_title(f"{title} - {circuit_name}")
        ax.set_xlabel('Gürültü Ölçeği')
        ax.set_ylabel('Beklenen Değer')
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        fig.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
            
        self.figure_count += 1
        plt.close(fig)
    
    def plot_error_scaling_comparison(self, circuit, shots=1024, noise_scales=[0.5, 1.0, 1.5, 2.0],
                                    observable_fn=None, title="Gürültü Ölçekleme Karşılaştırması",
                                    save_path=None):
        """
        Farklı gürültü seviyelerinde simülasyon sonuçlarını karşılaştırır
        
        Args:
            circuit: Simüle edilecek devre
            shots: Simülasyon tekrar sayısı
            noise_scales: Gürültü ölçekleme faktörleri
            observable_fn: Gözlemlenebilir fonksiyon (opsiyonel)
            title: Grafik başlığı
            save_path: Grafiğin kaydedileceği dosya yolu (opsiyonel)
        """
        if not hasattr(self.simulator, 'simulate_with_multiple_noise_levels'):
            print("Bu simülatör birden çok gürültü seviyesinde simülasyonu desteklemiyor.")
            return
            
        # Varsayılan gözlemlenebilir fonksiyon
        if observable_fn is None:
            def observable_fn(results):
                # İlk qubit'in |0⟩ olma olasılığı
                zero_prob = sum(prob for state, prob in results.items() 
                                if len(state) > 0 and state[0] == '0')
                return zero_prob
        
        # Çeşitli gürültü seviyelerinde simülasyon çalıştır
        multi_results = self.simulator.simulate_with_multiple_noise_levels(
            circuit, shots, noise_scales
        )
        
        # Gözlemlenebilir değerleri hesapla
        expectation_values = {}
        for scale_key, results in multi_results.items():
            expectation_values[scale_key] = observable_fn(results)
        
        # Grafik çiz
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Veri noktalarını çiz
        scales = [float(key.split('_')[1]) for key in expectation_values.keys()]
        values = list(expectation_values.values())
        
        ax.plot(scales, values, 'bo-', label='Gözlemlenebilir Değer')
        
        # İdeal değer (gürültüsüz) - eğer mümkünse
        if hasattr(self.simulator, 'noise_model') and self.simulator.noise_model is not None:
            # Gürültü modelini geçici olarak kapat
            temp_noise_model = self.simulator.noise_model
            self.simulator.noise_model = None
            
            # İdeal simülasyon
            ideal_results = self.simulator.run(circuit, shots)
            ideal_value = observable_fn(ideal_results)
            
            # Gürültü modelini geri yükle
            self.simulator.noise_model = temp_noise_model
            
            # İdeal değeri göster
            ax.axhline(y=ideal_value, color='green', linestyle='--', 
                      label=f'İdeal Değer: {ideal_value:.4f}')
        
        # Grafik düzenlemeleri
        ax.set_title(title)
        ax.set_xlabel('Gürültü Ölçeği')
        ax.set_ylabel('Gözlemlenebilir Değer')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        fig.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
            
        self.figure_count += 1
        plt.close(fig)
    
    def plot_readout_calibration_matrix(self, error_mitigation, num_qubits, 
                                      title="Ölçüm Hatası Kalibrasyon Matrisi", 
                                      save_path=None):
        """
        Ölçüm hatası kalibrasyon matrisini görselleştir
        
        Args:
            error_mitigation: Hata azaltma nesnesi
            num_qubits: Qubit sayısı
            title: Grafik başlığı
            save_path: Grafiğin kaydedileceği dosya yolu (opsiyonel)
        """
        if not hasattr(error_mitigation, 'correction_matrices') or num_qubits not in error_mitigation.correction_matrices:
            print(f"{num_qubits} qubit için kalibrasyon matrisi bulunamadı.")
            return
        
        # Kalibrasyon verileri
        if hasattr(error_mitigation, 'calibration_data') and error_mitigation.calibration_data:
            # Kalibrasyon matrisini oluştur
            basis_states = [format(i, f'0{num_qubits}b') for i in range(2**num_qubits)]
            n = len(basis_states)
            cal_matrix = np.zeros((n, n))
            
            for i, prepared_state in enumerate(basis_states):
                results = error_mitigation.calibration_data.get(prepared_state, {})
                for j, measured_state in enumerate(basis_states):
                    cal_matrix[i, j] = results.get(measured_state, 0.0)
            
            # Kalibrasyon matrisini görselleştir
            fig, ax = plt.subplots(figsize=(8, 6))
            
            im = ax.imshow(cal_matrix, cmap='viridis')
            
            # Renk skalası
            cbar = ax.figure.colorbar(im, ax=ax)
            cbar.ax.set_ylabel('Olasılık', rotation=-90, va="bottom")
            
            # Eksen etiketleri
            ax.set_xticks(np.arange(n))
            ax.set_yticks(np.arange(n))
            ax.set_xticklabels(basis_states)
            ax.set_yticklabels(basis_states)
            
            # Eksen başlıkları
            ax.set_xlabel('Ölçülen Durum')
            ax.set_ylabel('Hazırlanan Durum')
            
            # Başlık
            ax.set_title(title)
            
            # Etiketleri döndür
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            
            # Metin değerlerini göster
            for i in range(n):
                for j in range(n):
                    text = ax.text(j, i, f"{cal_matrix[i, j]:.2f}",
                                 ha="center", va="center", color="w" if cal_matrix[i, j] < 0.5 else "black")
            
            fig.tight_layout()
            
            if save_path:
                plt.savefig(save_path)
            else:
                plt.show()
                
            self.figure_count += 1
            plt.close(fig)
        else:
            print("Kalibrasyon verileri bulunamadı.")
    
    def plot_all_error_statistics(self, noise_model, circuit, shots=1024, 
                                title_prefix="Gürültü ve Hata Analizi", 
                                save_dir=None):
        """
        Kapsamlı hata istatistikleri raporları oluştur
        
        Args:
            noise_model: Gürültü modeli
            circuit: Simüle edilecek devre
            shots: Simülasyon tekrar sayısı
            title_prefix: Grafik başlığı öneki
            save_dir: Grafiklerin kaydedileceği dizin (opsiyonel)
        """
        # 1. Gürültü Dağılımı
        save_path = f"{save_dir}/error_distribution.png" if save_dir else None
        self.plot_error_distribution(
            noise_model, gate_runs=1000, 
            title=f"{title_prefix} - Gürültü Dağılımı",
            save_path=save_path
        )
        
        # Geçici olarak gürültü modelini ayarla
        orig_noise_model = self.simulator.noise_model
        self.simulator.noise_model = noise_model
        
        # 2. İdeal vs Gürültülü Sonuçlar
        # İdeal simülasyon (gürültüsüz)
        self.simulator.noise_model = None
        ideal_results = self.simulator.run(circuit, shots)
        
        # Gürültülü simülasyon
        self.simulator.noise_model = noise_model
        noisy_results = self.simulator.run(circuit, shots)
        
        # Hata azaltma uygulanmış simülasyon
        if hasattr(self.simulator, 'run_with_error_mitigation'):
            mitigated_results = self.simulator.run_with_error_mitigation(
                circuit, shots, technique="measurement_error_mitigation"
            )
            
            # Sonuçları karşılaştır
            save_path = f"{save_dir}/results_comparison.png" if save_dir else None
            self.plot_results_comparison(
                ideal_results, noisy_results, mitigated_results,
                title=f"{title_prefix} - Sonuç Karşılaştırması",
                save_path=save_path
            )
        else:
            # Mitigasyon olmadan karşılaştır
            save_path = f"{save_dir}/results_comparison.png" if save_dir else None
            self.plot_results_comparison(
                ideal_results, noisy_results,
                title=f"{title_prefix} - Sonuç Karşılaştırması",
                save_path=save_path
            )
        
        # 3. Gürültü ölçekleme karşılaştırması
        save_path = f"{save_dir}/noise_scaling.png" if save_dir else None
        self.plot_error_scaling_comparison(
            circuit, shots, 
            title=f"{title_prefix} - Gürültü Ölçekleme Analizi",
            save_path=save_path
        )
        
        # 4. ZNE analizi (eğer mümkünse)
        if (hasattr(self.simulator, 'error_mitigation') and 
            self.simulator.error_mitigation is not None and 
            hasattr(self.simulator.error_mitigation, 'zero_noise_extrapolation')):
            
            # Basit gözlemlenebilir fonksiyon
            def expectation_z(results):
                exp_val = 0
                for bitstring, prob in results.items():
                    if len(bitstring) > 0:
                        exp_val += prob * (1 if bitstring[0] == '0' else -1)
                return exp_val
            
            # ZNE çalıştır
            self.simulator.error_mitigation.zero_noise_extrapolation(
                circuit, expectation_z, shots
            )
            
            # ZNE grafiği
            save_path = f"{save_dir}/zne_extrapolation.png" if save_dir else None
            self.plot_zne_extrapolation(
                self.simulator.error_mitigation,
                title=f"{title_prefix} - Sıfır Gürültü Ekstrapolasyonu",
                save_path=save_path
            )
        
        # Orijinal gürültü modelini geri yükle
        self.simulator.noise_model = orig_noise_model 