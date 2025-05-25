"""
Gate sınıfı
==========

Kuantum kapılarını temsil eden sınıf.
"""

import numpy as np
from enum import Enum, auto
from functools import lru_cache


class GateType(Enum):
    """Kuantum kapı tiplerini tanımlayan enum"""
    # Tek qubit kapıları
    I = auto()     # Birim matris
    X = auto()     # Pauli-X (NOT)
    Y = auto()     # Pauli-Y
    Z = auto()     # Pauli-Z
    H = auto()     # Hadamard
    S = auto()     # S kapısı (faz)
    SDG = auto()   # S-adjoint
    T = auto()     # T kapısı (π/8)
    TDG = auto()   # T-adjoint
    RX = auto()    # X ekseni etrafında rotasyon
    RY = auto()    # Y ekseni etrafında rotasyon
    RZ = auto()    # Z ekseni etrafında rotasyon
    P = auto()     # Faz rotasyon kapısı
    U1 = auto()    # U1 kapısı (faz)
    U2 = auto()    # U2 kapısı (karışık)
    U3 = auto()    # U3 kapısı (genel tek-qubit)
    SX = auto()    # √X (square root of X)
    SY = auto()    # √Y (square root of Y)
    
    # İki qubit kapıları
    CNOT = auto()  # Controlled-NOT
    CZ = auto()    # Controlled-Z
    SWAP = auto()  # SWAP kapısı
    ISWAP = auto() # iSWAP kapısı
    CP = auto()    # Controlled-Phase
    CRX = auto()   # Controlled-RX 
    CRY = auto()   # Controlled-RY
    CRZ = auto()   # Controlled-RZ
    CU1 = auto()   # Controlled-U1
    CU3 = auto()   # Controlled-U3
    RXX = auto()   # Ising XX kapısı
    RYY = auto()   # Ising YY kapısı
    RZZ = auto()   # Ising ZZ kapısı
    
    # Üç qubit kapıları
    TOFFOLI = auto()  # CCNOT (Toffoli)
    CSWAP = auto()    # Controlled-SWAP (Fredkin)
    CCZ = auto()      # Controlled-Controlled-Z
    
    # Özel kapılar
    RESET = auto()      # Qubit reset
    MEASURE = auto()    # Ölçüm
    BARRIER = auto()    # Bariyer (optimizasyon için)
    CUSTOM = auto()     # Özel tanımlı kapı


class Gate:
    """Kuantum kapısını temsil eden sınıf"""
    
    # Cache ile parametresiz kapı matrislerini önbelleğe alır
    @staticmethod
    @lru_cache(maxsize=32)
    def _get_standard_gate_matrix(gate_type):
        """Standart kapıların matris temsilini döndürür"""
        # Tek qubit kapı matrisleri
        if gate_type == GateType.I:
            return np.array([[1, 0], [0, 1]], dtype=complex)
        elif gate_type == GateType.X:
            return np.array([[0, 1], [1, 0]], dtype=complex)
        elif gate_type == GateType.Y:
            return np.array([[0, -1j], [1j, 0]], dtype=complex)
        elif gate_type == GateType.Z:
            return np.array([[1, 0], [0, -1]], dtype=complex)
        elif gate_type == GateType.H:
            return np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        elif gate_type == GateType.S:
            return np.array([[1, 0], [0, 1j]], dtype=complex)
        elif gate_type == GateType.SDG:
            return np.array([[1, 0], [0, -1j]], dtype=complex)
        elif gate_type == GateType.T:
            return np.array([[1, 0], [0, np.exp(1j * np.pi/4)]], dtype=complex)
        elif gate_type == GateType.TDG:
            return np.array([[1, 0], [0, np.exp(-1j * np.pi/4)]], dtype=complex)
        elif gate_type == GateType.SX:  # Square root of X
            return np.array([[1+1j, 1-1j], [1-1j, 1+1j]], dtype=complex) / 2
        elif gate_type == GateType.SY:  # Square root of Y
            return np.array([[1+1j, -1-1j], [1+1j, 1+1j]], dtype=complex) / 2
        # İki qubit kapı matrisleri
        elif gate_type == GateType.CNOT:
            return np.array([[1, 0, 0, 0],
                           [0, 1, 0, 0],
                           [0, 0, 0, 1],
                           [0, 0, 1, 0]], dtype=complex)
        elif gate_type == GateType.CZ:
            return np.array([[1, 0, 0, 0],
                           [0, 1, 0, 0],
                           [0, 0, 1, 0],
                           [0, 0, 0, -1]], dtype=complex)
        elif gate_type == GateType.SWAP:
            return np.array([[1, 0, 0, 0],
                            [0, 0, 1, 0],
                            [0, 1, 0, 0],
                            [0, 0, 0, 1]], dtype=complex)
        elif gate_type == GateType.ISWAP:
            return np.array([[1, 0, 0, 0],
                             [0, 0, 1j, 0],
                             [0, 1j, 0, 0],
                             [0, 0, 0, 1]], dtype=complex)
        # Üç qubit kapıları çok büyük matrislerdir (8x8), tam simülatörde ele alınmalıdır
        else:
            return None
    
    @staticmethod
    def rx_matrix(theta):
        """RX(θ) kapısının matris temsilini hesaplar"""
        c = np.cos(theta/2)
        s = -1j * np.sin(theta/2)
        return np.array([[c, s], [s, c]], dtype=complex)
    
    @staticmethod
    def ry_matrix(theta):
        """RY(θ) kapısının matris temsilini hesaplar"""
        c = np.cos(theta/2)
        s = np.sin(theta/2)
        return np.array([[c, -s], [s, c]], dtype=complex)
    
    @staticmethod
    def rz_matrix(theta):
        """RZ(θ) kapısının matris temsilini hesaplar"""
        exp_plus = np.exp(-1j * theta/2)
        exp_minus = np.exp(1j * theta/2)
        return np.array([[exp_plus, 0], [0, exp_minus]], dtype=complex)
    
    @staticmethod
    def phase_matrix(phi):
        """P(φ) (faz kapısı) matris temsilini hesaplar"""
        return np.array([[1, 0], [0, np.exp(1j * phi)]], dtype=complex)
    
    @staticmethod
    def u1_matrix(lambda_param):
        """U1(λ) kapısının matris temsilini hesaplar"""
        return np.array([[1, 0], [0, np.exp(1j * lambda_param)]], dtype=complex)
    
    @staticmethod
    def u2_matrix(phi, lambda_param):
        """U2(φ,λ) kapısının matris temsilini hesaplar"""
        return np.array([
            [1 / np.sqrt(2), -np.exp(1j * lambda_param) / np.sqrt(2)],
            [np.exp(1j * phi) / np.sqrt(2), np.exp(1j * (phi + lambda_param)) / np.sqrt(2)]
        ], dtype=complex)
    
    @staticmethod
    def u3_matrix(theta, phi, lambda_param):
        """U3(θ,φ,λ) kapısının matris temsilini hesaplar"""
        return np.array([
            [np.cos(theta/2), -np.exp(1j * lambda_param) * np.sin(theta/2)],
            [np.exp(1j * phi) * np.sin(theta/2), np.exp(1j * (phi + lambda_param)) * np.cos(theta/2)]
        ], dtype=complex)
    
    @staticmethod
    def rxx_matrix(theta):
        """RXX(θ) Ising kapısının matris temsilini hesaplar"""
        c = np.cos(theta/2)
        s = -1j * np.sin(theta/2)
        return np.array([
            [c, 0, 0, s],
            [0, c, s, 0],
            [0, s, c, 0],
            [s, 0, 0, c]
        ], dtype=complex)
    
    @staticmethod
    def ryy_matrix(theta):
        """RYY(θ) Ising kapısının matris temsilini hesaplar"""
        c = np.cos(theta/2)
        s = -1j * np.sin(theta/2)
        return np.array([
            [c, 0, 0, -s],
            [0, c, s, 0],
            [0, s, c, 0],
            [-s, 0, 0, c]
        ], dtype=complex)
    
    @staticmethod
    def rzz_matrix(theta):
        """RZZ(θ) Ising kapısının matris temsilini hesaplar"""
        exp_plus = np.exp(-1j * theta/2)
        exp_minus = np.exp(1j * theta/2)
        return np.array([
            [exp_plus, 0, 0, 0],
            [0, exp_minus, 0, 0],
            [0, 0, exp_minus, 0],
            [0, 0, 0, exp_plus]
        ], dtype=complex)
    
    @staticmethod
    def cp_matrix(phi):
        """Controlled-Phase kapısının matris temsilini hesaplar"""
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, np.exp(1j * phi)]
        ], dtype=complex)
    
    def __init__(self, gate_type, qubits, parameters=None, time=0, duration=1):
        """
        Gate nesnesini başlatır
        
        Args:
            gate_type: Kapı tipi (GateType)
            qubits: Kapının uygulandığı qubit(ler) listesi
            parameters: Parametrik kapılar için parametreler (örn. rotasyon açısı)
            time: Kapının uygulanma zamanı (simülasyon zaman birimi)
            duration: Kapının süresi (simülasyon zaman birimi)
        """
        self.type = gate_type
        self.qubits = qubits if isinstance(qubits, list) else [qubits]
        self.parameters = parameters if parameters is not None else []
        self.time = time
        self.duration = duration
        
        # Donanım kısıtlamaları ve hata modeli için alanlar
        self.fidelity = 1.0  # Kapı sadakati
        self.error_model = None  # Kapı hata modeli
        
        # Derleyici için ek bilgiler
        self.is_optimized = False
        self.original_gate = None  # Optimize edilmiş kapıların orijinal versiyonu
        
        # SWAP optimizasyonu için
        self.is_inserted_swap = False  # Derleyici tarafından eklenen SWAP mı?
        
        # Kapının matris temsilini hesaplama
        self._matrix = self._calculate_matrix()
    
    def _calculate_matrix(self):
        """Kapı tipine ve parametrelere göre matris temsilini hesaplar"""
        # Standart kapı matrisleri (parametresiz)
        if self.type in [GateType.I, GateType.X, GateType.Y, GateType.Z, 
                         GateType.H, GateType.S, GateType.SDG, GateType.T, 
                         GateType.TDG, GateType.SX, GateType.SY,
                         GateType.CNOT, GateType.CZ, GateType.SWAP, GateType.ISWAP]:
            return self._get_standard_gate_matrix(self.type)
        
        # Parametrik kapılar
        elif self.type == GateType.RX:
            return self.rx_matrix(self.parameters[0])
        elif self.type == GateType.RY:
            return self.ry_matrix(self.parameters[0])
        elif self.type == GateType.RZ:
            return self.rz_matrix(self.parameters[0])
        elif self.type == GateType.P:
            return self.phase_matrix(self.parameters[0])
        elif self.type == GateType.U1:
            return self.u1_matrix(self.parameters[0])
        elif self.type == GateType.U2:
            return self.u2_matrix(self.parameters[0], self.parameters[1])
        elif self.type == GateType.U3:
            return self.u3_matrix(self.parameters[0], self.parameters[1], self.parameters[2])
        elif self.type == GateType.CP:
            return self.cp_matrix(self.parameters[0])
        elif self.type == GateType.RXX:
            return self.rxx_matrix(self.parameters[0])
        elif self.type == GateType.RYY:
            return self.ryy_matrix(self.parameters[0])
        elif self.type == GateType.RZZ:
            return self.rzz_matrix(self.parameters[0])
        elif self.type == GateType.CRX:
            # Controlled-RX kapısı için tam simülatör gereklidir
            return None
        elif self.type == GateType.CRY:
            # Controlled-RY kapısı için tam simülatör gereklidir
            return None
        elif self.type == GateType.CRZ:
            # Controlled-RZ kapısı için tam simülatör gereklidir
            return None
        elif self.type == GateType.CU1:
            # Controlled-U1 kapısı için tam simülatör gereklidir
            return None
        elif self.type == GateType.CU3:
            # Controlled-U3 kapısı için tam simülatör gereklidir
            return None
        else:
            # Diğer kapılar için özel implementasyon veya tam simülatör gerekli
            return None
    
    def __str__(self):
        """Kapının string temsilini döndürür"""
        qubit_str = ", ".join(str(q.id) for q in self.qubits)
        param_str = f", params={self.parameters}" if self.parameters else ""
        return f"{self.type.name}({qubit_str}{param_str})"
    
    @property
    def matrix(self):
        """Kapının matris temsilini döndürür (mümkünse)"""
        return self._matrix
    
    @property
    def num_qubits(self):
        """Kapının etkilediği qubit sayısını döndürür"""
        return len(self.qubits)
    
    @property
    def end_time(self):
        """Kapının bittiği zamanı döndürür"""
        return self.time + self.duration
    
    def apply(self, qubit_states):
        """
        Kapıyı verilen qubit durumlarına uygular
        
        Args:
            qubit_states: Kapının uygulanacağı QubitState nesneleri listesi
            
        Returns:
            bool: İşlemin başarılı olup olmadığı
        """
        # Tek qubit kapıları
        if self.type in [GateType.I, GateType.X, GateType.Y, GateType.Z, GateType.H, 
                         GateType.S, GateType.SDG, GateType.T, GateType.TDG, GateType.SX, GateType.SY,
                         GateType.RX, GateType.RY, GateType.RZ, GateType.P, GateType.U1, GateType.U2, GateType.U3]:
            if len(qubit_states) != 1:
                raise ValueError(f"Tek qubit kapısı için bir QubitState gerekli, {len(qubit_states)} verildi")
            
            if self._matrix is None:
                raise NotImplementedError(f"{self.type.name} matris temsili bu simülatör sürümünde desteklenmiyor")
                
            state_vector = qubit_states[0].to_vector()
            result_vector = np.dot(self._matrix, state_vector)
            qubit_states[0].alpha = result_vector[0]
            qubit_states[0].beta = result_vector[1]
            return True
            
        # İki qubit kapıları
        elif self.type in [GateType.CNOT, GateType.CZ, GateType.SWAP, GateType.ISWAP, GateType.CP,
                          GateType.CRX, GateType.CRY, GateType.CRZ, GateType.CU1, GateType.CU3,
                          GateType.RXX, GateType.RYY, GateType.RZZ]:
            if len(qubit_states) != 2:
                raise ValueError(f"{self.type.name} kapısı için iki QubitState gerekli, {len(qubit_states)} verildi")

            # Basit simülatörde sadece CNOT kapısı destekleniyor
            if self.type == GateType.CNOT:
                control, target = qubit_states
                prob_0, prob_1 = control.probabilities()
            
                # Kontrol qubit |1⟩ durumundaysa hedef qubit üzerine X uygula
                if np.isclose(prob_1, 1):
                    x_matrix = self._get_standard_gate_matrix(GateType.X)
                    target_vector = target.to_vector()
                    result_vector = np.dot(x_matrix, target_vector)
                    target.alpha = result_vector[0]
                    target.beta = result_vector[1]
                # Süperpozisyon durumunda gerçek simülatör gerekir
                elif not np.isclose(prob_0, 1):
                    raise NotImplementedError("Bu basit simülatör süperpozisyondaki CNOT'u desteklemiyor")
            else:
                raise NotImplementedError(f"{self.type.name} kapısı şu anda basit simülatörde desteklenmiyor")
            
            return True
            
        # Üç qubit kapıları
        elif self.type in [GateType.TOFFOLI, GateType.CSWAP, GateType.CCZ]:
            if len(qubit_states) != 3:
                raise ValueError(f"{self.type.name} kapısı için üç QubitState gerekli, {len(qubit_states)} verildi")

            raise NotImplementedError(f"{self.type.name} kapısı basit simülatörde desteklenmiyor")
            
        # Özel kapılar
        elif self.type == GateType.RESET:
            if len(qubit_states) != 1:
                raise ValueError(f"RESET kapısı için bir QubitState gerekli, {len(qubit_states)} verildi")
            
            qubit_states[0].reset()
            return True
            
        elif self.type == GateType.MEASURE:
            if len(qubit_states) != 1:
                raise ValueError(f"MEASURE kapısı için bir QubitState gerekli, {len(qubit_states)} verildi")
            
            result = qubit_states[0].measure()
            return result
            
        elif self.type == GateType.BARRIER:
            # Bariyer kapısı sadece derleyici için anlamlıdır, simülasyonda işlem yapmaz
            return True
            
        else:
            # Diğer kapı tipleri için tam simülatör gerekli
            raise NotImplementedError(f"{self.type.name} tipindeki kapı şu anda basit simülatörde desteklenmiyor")
    
    def is_compatible(self, hardware_model):
        """
        Kapının belirli bir donanım modeliyle uyumlu olup olmadığını kontrol eder
        
        Args:
            hardware_model: Donanım modeli
            
        Returns:
            bool: Kapının donanımda desteklenip desteklenmediği
        """
        # Kapı tipinin donanımda desteklenip desteklenmediğini kontrol et
        if self.type not in hardware_model.supported_gates:
            return False
        
        # Çok qubit'li kapılar için qubit'ler arasında bağlantı olup olmadığını kontrol et
        if len(self.qubits) > 1:
            # İki qubit kapısı
            if len(self.qubits) == 2:
                q1, q2 = self.qubits
                if not hardware_model.are_connected(q1, q2):
                    return False
            # Üç qubit kapısı
            elif len(self.qubits) == 3:
                q1, q2, q3 = self.qubits
                if not (hardware_model.are_connected(q1, q2) and 
                        hardware_model.are_connected(q2, q3) and 
                        hardware_model.are_connected(q1, q3)):
                    return False
        
        return True
    
    def validate_unitary(self):
        """
        Kapı matrisinin üniter olup olmadığını kontrol eder
        
        Returns:
            bool: Matrisin üniter olup olmadığı
        """
        if self._matrix is None:
            return True  # Matris hesaplanamıyorsa kontrol edilemez
        
        # U†U = I kontrolü
        hermitian_conjugate = self._matrix.conj().T
        product = np.dot(hermitian_conjugate, self._matrix)
        identity = np.eye(len(self._matrix), dtype=complex)
        
        return np.allclose(product, identity)
    
    def to_qasm(self):
        """
        Kapının QASM temsilini döndürür
        
        Returns:
            str: QASM temsili
        """
        qubit_str = ", ".join(f"q[{q.id}]" for q in self.qubits)
        
        if self.type == GateType.I:
            return f"id {qubit_str};"
        elif self.type == GateType.X:
            return f"x {qubit_str};"
        elif self.type == GateType.Y:
            return f"y {qubit_str};"
        elif self.type == GateType.Z:
            return f"z {qubit_str};"
        elif self.type == GateType.H:
            return f"h {qubit_str};"
        elif self.type == GateType.S:
            return f"s {qubit_str};"
        elif self.type == GateType.SDG:
            return f"sdg {qubit_str};"
        elif self.type == GateType.T:
            return f"t {qubit_str};"
        elif self.type == GateType.TDG:
            return f"tdg {qubit_str};"
        elif self.type == GateType.RX:
            return f"rx({self.parameters[0]}) {qubit_str};"
        elif self.type == GateType.RY:
            return f"ry({self.parameters[0]}) {qubit_str};"
        elif self.type == GateType.RZ:
            return f"rz({self.parameters[0]}) {qubit_str};"
        elif self.type == GateType.P:
            return f"p({self.parameters[0]}) {qubit_str};"
        elif self.type == GateType.U1:
            return f"u1({self.parameters[0]}) {qubit_str};"
        elif self.type == GateType.U2:
            return f"u2({self.parameters[0]},{self.parameters[1]}) {qubit_str};"
        elif self.type == GateType.U3:
            return f"u3({self.parameters[0]},{self.parameters[1]},{self.parameters[2]}) {qubit_str};"
        elif self.type == GateType.CNOT:
            return f"cx {qubit_str};"
        elif self.type == GateType.CZ:
            return f"cz {qubit_str};"
        elif self.type == GateType.SWAP:
            return f"swap {qubit_str};"
        elif self.type == GateType.MEASURE:
            q_str = f"q[{self.qubits[0].id}]"
            c_bit = self.parameters[0] if self.parameters else self.qubits[0].id
            return f"measure {q_str} -> c[{c_bit}];"
        elif self.type == GateType.BARRIER:
            return f"barrier {qubit_str};"
        else:
            # Diğer kapı tipleri için özel işlem gerekebilir
            return f"// Unsupported gate: {self.type.name}" 