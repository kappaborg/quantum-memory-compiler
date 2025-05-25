"""
Parallel Modülü
==============

Kuantum simülasyonları için paralelleştirme yetenekleri sağlayan modül.
"""

import multiprocessing
import concurrent.futures
import numpy as np
import time
from tqdm import tqdm
from typing import Dict, List, Callable, Any, Tuple
from .simulator import Simulator


class ParallelSimulator:
    """
    Paralel simülasyon işlemlerini sağlayan sınıf
    
    Birden fazla işlemci çekirdeği kullanarak simülasyon ve hesaplamaları
    paralelleştirmeyi sağlayarak büyük devrelerin verimli simülasyonunu destekler.
    """
    
    def __init__(self, max_workers=None):
        """
        ParallelSimulator nesnesini başlatır
        
        Args:
            max_workers: Maksimum iş parçacığı sayısı (None: otomatik)
        """
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.progress_bar = True
    
    def parallel_run(self, circuit, shots=1024, noise_model=None, enable_error_mitigation=False):
        """
        Bir kuantum devresini paralel olarak simüle eder
        
        Args:
            circuit: Simüle edilecek devre
            shots: Toplam simülasyon tekrar sayısı
            noise_model: Kullanılacak gürültü modeli
            enable_error_mitigation: Hata azaltma kullanılsın mı
            
        Returns:
            dict: Birleştirilmiş ölçüm sonuçları
        """
        # İşlemci sayısı
        num_workers = min(self.max_workers, shots)
        
        if num_workers <= 1:
            # Paralelleştirme gereksiz, normal simülatör ile çalıştır
            simulator = Simulator(noise_model=noise_model, enable_error_mitigation=enable_error_mitigation)
            return simulator.run(circuit, shots=shots)
        
        # Her iş parçacığına düşen shot sayısı
        shots_per_worker = shots // num_workers
        remaining_shots = shots % num_workers
        
        worker_shots = [shots_per_worker] * num_workers
        # Kalan shotları dağıt
        for i in range(remaining_shots):
            worker_shots[i] += 1
        
        # İş listesini oluştur
        worker_args = [(circuit, shot_count, noise_model, enable_error_mitigation) 
                      for shot_count in worker_shots]
        
        # Paralel çalıştır
        start_time = time.time()
        results = []
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
            if self.progress_bar:
                print(f"Paralel simülasyon başlatılıyor ({num_workers} işlemci)...")
                futures = list(tqdm(executor.map(self._run_simulation, worker_args), 
                                   total=num_workers, 
                                   desc="Simülasyon ilerlemesi"))
                results = futures
            else:
                futures = [executor.submit(self._run_simulation, args) for args in worker_args]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Sonuçları birleştir
        combined_results = self._combine_results(results, shots)
        
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"Paralel simülasyon tamamlandı ({elapsed:.2f} saniye)")
        
        return combined_results
    
    def _run_simulation(self, args):
        """
        Tek bir iş parçacığında simülasyon çalıştırır
        
        Args:
            args: (circuit, shots, noise_model, enable_error_mitigation) parametreleri
            
        Returns:
            dict: Simülasyon sonuçları
        """
        circuit, shots, noise_model, enable_error_mitigation = args
        
        simulator = Simulator(noise_model=noise_model, enable_error_mitigation=enable_error_mitigation)
        results = simulator.run(circuit, shots=shots)
        
        # Olasılık yerine, sayımları döndür
        count_results = {}
        for key, prob in results.items():
            count_results[key] = int(prob * shots)
        
        return count_results
    
    def _combine_results(self, results_list, total_shots):
        """
        Farklı iş parçacıklarından gelen sonuçları birleştirir
        
        Args:
            results_list: Simülasyon sonuçlarının listesi
            total_shots: Toplam shot sayısı
            
        Returns:
            dict: Birleştirilmiş sonuçlar
        """
        combined_counts = {}
        
        # Tüm sonuçları topla
        for result in results_list:
            for key, count in result.items():
                if key in combined_counts:
                    combined_counts[key] += count
                else:
                    combined_counts[key] = count
        
        # Olasılıklara dönüştür
        combined_probabilities = {}
        for key, count in combined_counts.items():
            combined_probabilities[key] = count / total_shots
            
        return combined_probabilities
    
    def parallel_expectation_value(self, circuit, observable, shots=1024, noise_model=None):
        """
        Bir devrenin beklenen değerini paralel olarak hesaplar
        
        Args:
            circuit: Değerlendirilecek devre
            observable: Beklenen değeri hesaplayacak gözlemlenebilir (fonksiyon)
            shots: Simülasyon tekrar sayısı
            noise_model: Kullanılacak gürültü modeli
            
        Returns:
            float: Hesaplanan beklenen değer
        """
        results = self.parallel_run(circuit, shots, noise_model)
        return observable(results)
    
    def parallel_parameter_sweep(self, circuit_generator, parameter_ranges, shots=1024, 
                               observable=None, noise_model=None):
        """
        Parametreli bir devreyi farklı parametre değerleriyle paralel olarak simüle eder
        
        Args:
            circuit_generator: Parametreleri alıp devre üreten fonksiyon
            parameter_ranges: Her parametre için değer aralıkları (dict)
            shots: Her parametre seti için simülasyon tekrar sayısı
            observable: Sonuçlardan beklenen değer hesaplayan fonksiyon (opsiyonel)
            noise_model: Kullanılacak gürültü modeli
            
        Returns:
            dict: Parametre değerlerine göre sonuçlar
        """
        # Parametre kombinasyonlarını oluştur
        from itertools import product
        
        parameter_keys = list(parameter_ranges.keys())
        parameter_values = list(parameter_ranges.values())
        
        parameter_combinations = []
        for combo in product(*parameter_values):
            params = {key: value for key, value in zip(parameter_keys, combo)}
            parameter_combinations.append(params)
        
        print(f"Toplam {len(parameter_combinations)} parametre kombinasyonu oluşturuldu")
        
        # Her kombinasyon için iş listesi oluştur
        worker_args = []
        for params in parameter_combinations:
            circuit = circuit_generator(params)
            worker_args.append((circuit, shots, noise_model, False))
        
        # Paralel çalıştır
        results = []
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            if self.progress_bar:
                futures = list(tqdm(executor.map(self._run_simulation, worker_args), 
                                   total=len(worker_args), 
                                   desc="Parametre taraması"))
                raw_results = futures
            else:
                futures = [executor.submit(self._run_simulation, args) for args in worker_args]
                raw_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Sonuçları işle
        if observable:
            # Eğer bir gözlemlenebilir fonksiyon belirtilmişse, beklenen değerleri hesapla
            results = []
            for params, raw_result in zip(parameter_combinations, raw_results):
                # Sayım sonuçlarını olasılıklara dönüştür
                prob_results = {k: v / shots for k, v in raw_result.items()}
                # Beklenen değeri hesapla
                exp_value = observable(prob_results)
                # Sonucu parametre değerleriyle birlikte kaydet
                results.append((params, exp_value))
            
            # Sonuçları sözlüğe çevir
            return dict(results)
        else:
            # Gözlemlenebilir belirtilmemişse, ham sonuçları döndür
            return dict(zip(parameter_combinations, raw_results))
    
    def parallel_noise_analysis(self, circuit, noise_scales=[0.0, 0.5, 1.0, 2.0, 5.0], 
                              shots=1024, observable=None):
        """
        Farklı gürültü seviyelerinde devreyi paralel olarak simüle eder
        
        Args:
            circuit: Simüle edilecek devre
            noise_scales: Gürültü ölçekleme faktörleri
            shots: Her ölçekleme için simülasyon tekrar sayısı
            observable: Sonuçlardan beklenen değer hesaplayan fonksiyon (opsiyonel)
            
        Returns:
            dict: Gürültü seviyelerine göre sonuçlar
        """
        from .noise_model import NoiseModel
        
        # Her gürültü seviyesi için iş listesi oluştur
        worker_args = []
        for scale in noise_scales:
            if scale == 0.0:
                # Gürültüsüz simülasyon
                worker_args.append((circuit, shots, None, False))
            else:
                # Ölçeklendirişmiş gürültü modeli
                noise_model = NoiseModel(
                    depolarizing_prob=0.01 * scale,
                    bit_flip_prob=0.005 * scale,
                    phase_flip_prob=0.005 * scale,
                    amplitude_damping_prob=0.003 * scale,
                    thermal_relaxation_prob=0.002 * scale,
                    measurement_error_prob=0.01 * scale
                )
                worker_args.append((circuit, shots, noise_model, False))
        
        # Paralel çalıştır
        results = []
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            if self.progress_bar:
                futures = list(tqdm(executor.map(self._run_simulation, worker_args), 
                                   total=len(worker_args), 
                                   desc="Gürültü analizi"))
                raw_results = futures
            else:
                futures = [executor.submit(self._run_simulation, args) for args in worker_args]
                raw_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Sonuçları işle
        if observable:
            # Eğer bir gözlemlenebilir fonksiyon belirtilmişse, beklenen değerleri hesapla
            results = []
            for scale, raw_result in zip(noise_scales, raw_results):
                # Sayım sonuçlarını olasılıklara dönüştür
                prob_results = {k: v / shots for k, v in raw_result.items()}
                # Beklenen değeri hesapla
                exp_value = observable(prob_results)
                # Sonucu gürültü seviyesiyle birlikte kaydet
                results.append((scale, exp_value))
            
            # Sonuçları sözlüğe çevir
            return dict(results)
        else:
            # Gözlemlenebilir belirtilmemişse, ham sonuçları döndür
            return dict(zip(noise_scales, raw_results))
    
    def set_progress_bar(self, enabled=True):
        """İlerleme çubuğunu etkinleştirir veya devre dışı bırakır"""
        self.progress_bar = enabled 