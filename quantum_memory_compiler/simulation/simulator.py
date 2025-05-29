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
Simulator modülü
=============

Kuantum devrelerini simüle eden sınıf.
"""

import numpy as np
from collections import defaultdict

from ..core.gate import GateType
from .error_mitigation import ErrorMitigation


class Simulator:
    """
    Kuantum devrelerini simüle eden sınıf
    
    Basit kuantum simülasyonu için state-vector yaklaşımını kullanır.
    Gelişmiş gürültü modelleri ve hata azaltma teknikleriyle entegre çalışır.
    """
    
    def __init__(self, noise_model=None, enable_error_mitigation=False):
        """
        Simulator nesnesini başlatır
        
        Args:
            noise_model: Simülasyonda kullanılacak gürültü modeli (opsiyonel)
            enable_error_mitigation: Hata azaltma yöntemlerini etkinleştir
        """
        self.noise_model = noise_model
        self.results = {}
        self.enable_error_mitigation = enable_error_mitigation
        
        # Hata azaltma modülü
        if self.enable_error_mitigation:
            self.error_mitigation = ErrorMitigation(self)
        else:
            self.error_mitigation = None
    
    def run(self, circuit, shots=1024, apply_error_mitigation=None):
        """
        Verilen devreyi simüle eder
        
        Args:
            circuit: Simüle edilecek devre
            shots: Simülasyon tekrar sayısı
            apply_error_mitigation: Hata azaltma uygula (None: varsayılan ayarı kullan)
            
        Returns:
            dict: Ölçüm sonuçları
        """
        print(f"🔬 Simulator.run called with {shots} shots")
        print(f"🔬 Circuit has {len(circuit.gates)} gates and {len(circuit.qubits)} qubits")
        
        # Hata azaltma ayarını belirle
        apply_mitigation = apply_error_mitigation if apply_error_mitigation is not None else self.enable_error_mitigation
        
        # Her shot için ayrı simülasyon çalıştır
        counts = defaultdict(int)
        
        for shot_idx in range(shots):
            # Qubit durumlarını hazırla
            qubit_states = {}
            for qubit in circuit.qubits:
                qubit.state.reset()  # |0⟩ durumuna sıfırla
                qubit_states[qubit.id] = qubit.state
            
            # Kapıları zamanlarına göre sırala ve uygula
            sorted_gates = sorted(circuit.gates, key=lambda g: g.time)
            
            if shot_idx == 0:  # Sadece ilk shot için debug
                print(f"🔬 Processing {len(sorted_gates)} gates")
                for i, gate in enumerate(sorted_gates):
                    print(f"🔬 Gate {i}: {gate.type.name} on qubits {[q.id for q in gate.qubits]}")
            
            # Ölçüm sonuçlarını sakla
            measurements = {}
            
            # Her kapıyı sırayla uygula
            for gate_idx, gate in enumerate(sorted_gates):
                # Ölçüm kapısı ise, sonucu kaydet
                if gate.type == GateType.MEASURE:
                    qubit = gate.qubits[0]
                    result = qubit.state.measure()
                    classical_bit = gate.parameters[0] if gate.parameters else qubit.id
                    measurements[classical_bit] = result
                    if shot_idx == 0:
                        print(f"🔬 Measured qubit {qubit.id} -> {result} (classical bit {classical_bit})")
                
                # Reset kapısı ise, qubit'i sıfırla
                elif gate.type == GateType.RESET:
                    qubit = gate.qubits[0]
                    qubit.state.reset()
                    
                # Diğer kapıları uygula
                else:
                    gate_qubits = [qubit_states[q.id] for q in gate.qubits]
                    
                    # Gürültü modeli varsa, kapıya gürültü ekle
                    if self.noise_model and gate.type != GateType.BARRIER:
                        self.noise_model.apply_noise(gate, gate_qubits, gate.time, gate_idx)
                    
                    # Kapıyı uygula
                    if gate.type != GateType.BARRIER:
                        try:
                            if gate.type == GateType.CNOT:
                                # CNOT kapısı özel olarak uygulanıyor
                                self._apply_cnot(gate_qubits[0], gate_qubits[1])
                            elif gate.type == GateType.CZ:
                                self._apply_cz(gate_qubits[0], gate_qubits[1])
                            else:
                                gate.apply(gate_qubits)
                        except NotImplementedError:
                            print(f"Uyarı: {gate.type.name} tipi kapı simülatörde tam olarak desteklenmiyor")
            
            # Bu simülasyonun sonucunu counts'a ekle
            if measurements:
                # Ölçüm sonuçları varsa, bunları kullan
                result_str = ''.join(str(measurements.get(i, 0)) for i in sorted(measurements.keys()))
                if shot_idx == 0:
                    print(f"🔬 Measurement results: {measurements}")
                    print(f"🔬 Result string: '{result_str}'")
            else:
                # Ölçüm sonuçları yoksa, tüm qubit'lerin son durumlarını ölç
                result_bits = []
                for qubit in circuit.qubits:
                    measurement_result = qubit.state.measure()
                    result_bits.append(str(measurement_result))
                result_str = ''.join(result_bits)
                if shot_idx == 0:
                    print(f"🔬 No explicit measurements, measuring final states: {result_bits}")
                    print(f"🔬 Result string: '{result_str}'")
            
            if result_str:
                counts[result_str] += 1
        
        print(f"🔬 Final counts: {dict(counts)}")
        
        # Sonuçları normalize et
        results = {}
        for key in counts:
            results[key] = counts[key] / shots
        
        print(f"🔬 Normalized results: {results}")
        
        self.results = dict(results)
        
        # Hata azaltma uygula
        if apply_mitigation and self.error_mitigation:
            try:
                # Ölçüm hatası azaltma uygula
                if hasattr(self.noise_model, 'active_mitigations') and "measurement_error_mitigation" in self.noise_model.active_mitigations:
                    mitigated_results = self.error_mitigation.apply_measurement_error_mitigation(
                        self.results, 
                        circuit.width
                    )
                    self.results = mitigated_results
            except Exception as e:
                print(f"Hata azaltma uygulanırken hata oluştu: {e}")
        
        # Return the results directly - use local results if no mitigation applied
        final_results = self.results if (apply_mitigation and self.error_mitigation) else results
        print(f"🔬 Final results to return: {final_results}")
        return final_results
    
    def run_with_error_mitigation(self, circuit, shots=1024, technique="measurement_error_mitigation"):
        """
        Belirtilen hata azaltma tekniği ile devreyi simüle eder
        
        Args:
            circuit: Simüle edilecek devre
            shots: Simülasyon tekrar sayısı
            technique: Kullanılacak hata azaltma tekniği
                      ("measurement_error_mitigation", "zne", "richardson", "pec")
            
        Returns:
            dict: Hata azaltma uygulanmış ölçüm sonuçları
        """
        if not self.error_mitigation:
            self.error_mitigation = ErrorMitigation(self)
        
        if not self.noise_model:
            print("Uyarı: Hata azaltma için gürültü modeli gereklidir")
            return self.run(circuit, shots)
        
        # Önce ölçüm hatası kalibrasyonu yap (gerekirse)
        if technique == "measurement_error_mitigation" and not self.error_mitigation.calibration_data:
            self.error_mitigation.calibrate_measurement_errors(circuit, shots=shots)
            self.noise_model.enable_error_mitigation(technique)
        
        # ZNE için gözlemlenebilir fonksiyon
        if technique == "zne":
            self.noise_model.enable_error_mitigation(technique)
            
            # Basit beklenen değer hesaplama fonksiyonu - farklı problem için özelleştirilebilir
            def expectation_z(results):
                # |0> durumu için +1, |1> durumu için -1 değeri ver
                exp_val = 0
                for bitstring, prob in results.items():
                    # Tek qubit durumu için basit hesaplama (çoklu qubit için genişletilebilir)
                    if len(bitstring) == 1:
                        exp_val += prob * (1 if bitstring == '0' else -1)
                    else:
                        # Çoklu qubit için ilk qubit'i dikkate al
                        exp_val += prob * (1 if bitstring[0] == '0' else -1)
                return exp_val
            
            mitigated_value = self.error_mitigation.zero_noise_extrapolation(
                circuit, expectation_z, shots
            )
            # ZNE yalnızca beklenen değer döndürür, bunu sonuç formatına dönüştür
            return {"ZNE_expectation_value": mitigated_value}
        
        # Richardson ekstrapolasyonu
        elif technique == "richardson":
            # Basit beklenen değer hesaplama fonksiyonu
            def expectation_z(results):
                exp_val = 0
                for bitstring, prob in results.items():
                    if len(bitstring) == 1:
                        exp_val += prob * (1 if bitstring == '0' else -1)
                    else:
                        exp_val += prob * (1 if bitstring[0] == '0' else -1)
                return exp_val
            
            mitigated_value = self.error_mitigation.richardson_extrapolation(
                circuit, expectation_z, shots
            )
            return {"Richardson_expectation_value": mitigated_value}
        
        # PEC (Probabilistic Error Cancellation)
        elif technique == "pec":
            mitigated_results = self.error_mitigation.probabilistic_error_cancellation(
                circuit, shots
            )
            return mitigated_results
        
        # Varsayılan: normal simülasyon ve sonra mitigation
        else:
            self.noise_model.enable_error_mitigation(technique)
            results = self.run(circuit, shots, apply_error_mitigation=True)
            return results
    
    def _apply_cnot(self, control_state, target_state):
        """
        CNOT kapısını uygular
        
        Args:
            control_state: Kontrol qubit durumu
            target_state: Hedef qubit durumu
        """
        # Kontrol qubit'i |1⟩ durumundaysa, hedef qubit'i çevir
        if abs(control_state.beta) > 0.5:  # |1⟩ durumuna daha yakın
            # X kapısı uygula
            alpha, beta = target_state.alpha, target_state.beta
            target_state.alpha = beta
            target_state.beta = alpha
    
    def _apply_cz(self, control_state, target_state):
        """
        CZ kapısı uygular: |11> durumunda hedef qubit'in fazını çevirir
        """
        # |11> durumunda hedef qubit'in fazını çevir
        # QubitState: alpha|0> + beta|1>
        # CZ: |11> -> -|11>
        # Sadece target_state.beta'ya -1 çarpanı uygula
        # (Bu basit modelde, iki qubitin de |1> olması durumunda faz çevirme yapılır)
        if abs(control_state.beta) > 0.5 and abs(target_state.beta) > 0.5:
            target_state.beta *= -1
    
    def get_statevector(self, circuit):
        """
        Verilen devrenin durum vektörünü hesaplar
        
        Not: Bu basit implementasyon tam bir state vector simülatörü değildir.
        Gerçek bir simülatör, tüm qubit'lerin birleşik durumunu temsil eden 
        2^n boyutunda bir durum vektörü kullanır.
        
        Args:
            circuit: Simüle edilecek devre
            
        Returns:
            dict: Her qubit için ayrı durum vektörleri
        """
        # Qubit durumlarını hazırla
        qubit_states = {}
        for qubit in circuit.qubits:
            qubit.state.reset()  # |0⟩ durumuna sıfırla
            qubit_states[qubit.id] = qubit.state
        
        # Kapıları zamanlarına göre sırala ve uygula
        sorted_gates = sorted(circuit.gates, key=lambda g: g.time)
        
        # Her kapıyı sırayla uygula
        for gate_idx, gate in enumerate(sorted_gates):
            if gate.type != GateType.BARRIER and gate.type != GateType.MEASURE:
                gate_qubits = [qubit_states[q.id] for q in gate.qubits]
                try:
                    if gate.type == GateType.CNOT:
                        # CNOT kapısı özel olarak uygulanıyor
                        self._apply_cnot(gate_qubits[0], gate_qubits[1])
                    elif gate.type == GateType.CZ:
                        self._apply_cz(gate_qubits[0], gate_qubits[1])
                    else:
                        gate.apply(gate_qubits)
                        
                    # Gürültü modeli varsa ve etkinse, statevector'a da gürültü uygula
                    if self.noise_model:
                        self.noise_model.apply_noise(gate, gate_qubits, gate.time, gate_idx)
                except NotImplementedError:
                    print(f"Uyarı: {gate.type.name} tipi kapı simülatörde tam olarak desteklenmiyor")
        
        # Her qubit için durum vektörünü döndür
        state_vectors = {}
        for qubit_id, state in qubit_states.items():
            state_vectors[qubit_id] = state.to_vector()
        
        return state_vectors
    
    def get_last_results(self):
        """
        Son çalıştırılan simülasyonun sonuçlarını döndürür
        
        Returns:
            dict: Ölçüm sonuçları
        """
        return self.results
    
    def simulate_with_multiple_noise_levels(self, circuit, shots=1024, noise_scales=[0.5, 1.0, 2.0]):
        """
        Farklı gürültü seviyelerinde simülasyon çalıştırır
        
        Args:
            circuit: Simüle edilecek devre
            shots: Simülasyon tekrar sayısı
            noise_scales: Gürültü ölçekleme faktörleri
            
        Returns:
            dict: Farklı gürültü seviyelerindeki simülasyon sonuçları
        """
        if not self.noise_model:
            raise ValueError("Bu özellik için gürültü modeli gereklidir")
            
        multi_results = {}
        
        # Orijinal gürültü modelini yedekle
        original_noise_model = self.noise_model
        
        for scale in noise_scales:
            # Gürültü modelinin kopyasını oluştur
            import copy
            temp_noise_model = copy.deepcopy(original_noise_model)
            
            # Gürültü parametrelerini ölçekle
            for attr_name in ["depolarizing_prob", "bit_flip_prob", "phase_flip_prob", 
                             "amplitude_damping_prob", "thermal_relaxation_prob"]:
                if hasattr(temp_noise_model, attr_name):
                    setattr(temp_noise_model, attr_name, 
                            getattr(temp_noise_model, attr_name) * scale)
            
            # Kapı hata oranlarını da ölçekle
            for gate_type in temp_noise_model.gate_error_rates:
                temp_noise_model.gate_error_rates[gate_type] *= scale
            
            # Ölçeklenmiş modeli kullan
            self.noise_model = temp_noise_model
            
            # Simülasyonu çalıştır
            results = self.run(circuit, shots)
            multi_results[f"scale_{scale}"] = results
        
        # Orijinal gürültü modelini geri yükle
        self.noise_model = original_noise_model
        
        return multi_results 