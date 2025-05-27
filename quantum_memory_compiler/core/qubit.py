import numpy as np
from enum import Enum, auto
from functools import lru_cache
import time as time_module


class QubitType(Enum):
    PHYSICAL = auto()  
    LOGICAL = auto()   
    ANCILLA = auto()   


class MemoryLevel(Enum):
    L1 = auto()  
    L2 = auto()  
    L3 = auto() 


class QubitState:    
    def __init__(self, alpha=1.0, beta=0.0):
       
        norm = np.abs(alpha)**2 + np.abs(beta)**2
        if not np.isclose(norm, 1.0):
            alpha = alpha / np.sqrt(norm)
            beta = beta / np.sqrt(norm)
            
        self._alpha = alpha
        self._beta = beta
        
        self._cache = {'vector': None, 'density_matrix': None, 'probabilities': None}
        self._cache_valid = False
    
    @property
    def alpha(self):
        """Alpha coefficient of the qubit state"""
        return self._alpha
    
    @alpha.setter
    def alpha(self, value):
        self._alpha = value
        self._invalidate_cache()
    
    @property
    def beta(self):
        return self._beta
    
    @beta.setter
    def beta(self, value):
        self._beta = value
        self._invalidate_cache()
    
    def _invalidate_cache(self):
        self._cache_valid = False
    
    def _update_cache(self):
        if not self._cache_valid:
            self._cache['vector'] = np.array([self._alpha, self._beta], dtype=complex)
            
            psi = self._cache['vector']
            self._cache['density_matrix'] = np.outer(psi, psi.conj())
            
            self._cache['probabilities'] = (np.abs(self._alpha)**2, np.abs(self._beta)**2)
            
            self._cache_valid = True
    
    def to_vector(self):
        self._update_cache()
        return self._cache['vector'].copy()
    
    def to_density_matrix(self):
        self._update_cache()
        return self._cache['density_matrix'].copy()
    
    def probabilities(self):
        self._update_cache()
        return self._cache['probabilities']
    
    def measure(self):
        
        prob_0, prob_1 = self.probabilities()
        result = np.random.choice([0, 1], p=[prob_0, prob_1])
        
        # Ölçüm sonrası durum çökmesi
        if result == 0:
            self._alpha = 1.0
            self._beta = 0.0
        else:
            self._alpha = 0.0
            self._beta = 1.0
            
        self._invalidate_cache()
        return result
    
    def reset(self):
        self._alpha = 1.0
        self._beta = 0.0
        self._invalidate_cache()
    
    def fidelity(self, target_state):
        
        this_dm = self.to_density_matrix()
        target_dm = target_state.to_density_matrix()
        
        # Calculate fidelity between density matrices
        sqrt_dm = np.sqrt(this_dm)
        prod = np.dot(sqrt_dm, np.dot(target_dm, sqrt_dm))
        return np.real(np.trace(np.sqrt(prod)))


class Qubit:
    
    DEFAULT_COHERENCE_TIMES = {
        MemoryLevel.L1: 50,      
        MemoryLevel.L2: 200,     
        MemoryLevel.L3: 1000     
    }
    
    DEFAULT_ERROR_RATES = {
        MemoryLevel.L1: 0.01,    
        MemoryLevel.L2: 0.005,   
        MemoryLevel.L3: 0.001    
    }
    
    def __init__(self, qubit_id, qubit_type=QubitType.LOGICAL, memory_level=MemoryLevel.L1):
        """
        Qubit nesnesini başlatır
        
        Args:
            qubit_id: Qubit'in benzersiz kimliği
            qubit_type: Qubit'in tipi (PHYSICAL, LOGICAL, ANCILLA)
            memory_level: Qubit'in bellek hiyerarşisindeki seviyesi
        """
        self.id = qubit_id
        self.type = qubit_type
        self._memory_level = memory_level
        self.state = QubitState()  
        
        self.creation_time = 0
        self.last_usage_time = 0
        self.is_allocated = False
        self.is_active = False
        
        # Fiziksel özellikler - MemoryLevel'a bağlı varsayılan değerler ile başlatılır
        self._coherence_time = self.DEFAULT_COHERENCE_TIMES[memory_level]
        self._error_rate = self.DEFAULT_ERROR_RATES[memory_level]
        
        # Eşleme bilgileri (mantıksal-fiziksel eşleme için)
        self.mapped_to = None  # Mantıksal qubit fiziksel qubit'e eşlenmişse
        self.mapped_from = None  # Fiziksel qubit mantıksal qubit'den eşlenmişse
        
        # Memory usage tracking
        self.usage_history = []  # List of (start_time, end_time, operation) tuples
        self.gate_count = 0  # Number of gates applied to this qubit
        self.transfer_count = 0  # Number of times this qubit was transferred between memory levels
    
    def __str__(self):
        """Qubit'in string temsilini döndürür"""
        return f"Qubit(id={self.id}, type={self.type.name}, level={self.memory_level.name})"
    
    @property
    def memory_level(self):
        """Returns the memory level of the qubit"""
        return self._memory_level
    
    @memory_level.setter
    def memory_level(self, level):
        """Sets the memory level and updates associated properties"""
        old_level = self._memory_level
        self._memory_level = level
        
        # Update coherence time and error rate based on the new memory level
        if self._coherence_time == self.DEFAULT_COHERENCE_TIMES[old_level]:
            self._coherence_time = self.DEFAULT_COHERENCE_TIMES[level]
        
        if self._error_rate == self.DEFAULT_ERROR_RATES[old_level]:
            self._error_rate = self.DEFAULT_ERROR_RATES[level]
        
        # Track the transfer between memory levels
        if old_level != level and self.is_active:
            self.transfer_count += 1
    
    @property
    def coherence_time(self):
        """Returns the coherence time of the qubit"""
        return self._coherence_time
    
    @coherence_time.setter
    def coherence_time(self, value):
        """Sets the coherence time"""
        if value <= 0:
            raise ValueError("Coherence time must be positive")
        self._coherence_time = value
    
    @property
    def error_rate(self):
        """Returns the error rate of the qubit"""
        return self._error_rate
    
    @error_rate.setter
    def error_rate(self, value):
        """Sets the error rate"""
        if value < 0 or value > 1:
            raise ValueError("Error rate must be between 0 and 1")
        self._error_rate = value
    
    @property
    def is_coherent(self):
        """
        Checks if the qubit is still coherent based on the time since last usage
        
        Returns:
            bool: True if the qubit is likely still coherent
        """
        if not self.is_active:
            return False
            
        current_time = time_module.time()
        elapsed_time = current_time - self.last_usage_time
        
        # Simple coherence model: probability decreases exponentially
        coherence_prob = np.exp(-elapsed_time / self._coherence_time)
        return coherence_prob > 0.5  # Threshold for considering still coherent
    
    @property
    def lifetime(self):
        """
        Returns the lifetime of the qubit from creation to last usage
        
        Returns:
            float: Lifetime in time units
        """
        if not self.is_allocated:
            return 0
        return self.last_usage_time - self.creation_time
    
    @property
    @lru_cache(maxsize=1)
    def usage_statistics(self):
        """
        Calculates and returns usage statistics for this qubit
        
        Returns:
            dict: Statistics including idle_time, active_time, etc.
        """
        if not self.usage_history:
            return {
                "idle_time": 0,
                "active_time": 0,
                "utilization": 0,
                "operation_count": 0
            }
        
        # Sort history by start time
        sorted_history = sorted(self.usage_history, key=lambda x: x[0])
        
        active_time = sum(end - start for start, end, _ in sorted_history)
        total_time = sorted_history[-1][1] - sorted_history[0][0]
        idle_time = total_time - active_time
        
        return {
            "idle_time": idle_time,
            "active_time": active_time,
            "utilization": active_time / total_time if total_time > 0 else 0,
            "operation_count": len(sorted_history)
        }
    
    def allocate(self, time):
        """
        Qubit'i tahsis eder
        
        Args:
            time: Tahsis zamanı
        """
        self.is_allocated = True
        self.is_active = True
        self.creation_time = time
        self.last_usage_time = time
        self.reset()
        
        # Clear history on re-allocation
        self.usage_history = []
        self.gate_count = 0
        self.transfer_count = 0
    
    def deallocate(self):
        """Qubit'i serbest bırakır"""
        self.is_allocated = False
        self.is_active = False
        self.mapped_to = None
        self.mapped_from = None
    
    def reset(self):
        """Qubit'i |0⟩ durumuna sıfırlar"""
        self.state.reset()
    
    def measure(self):
        """Qubit'i ölçer ve sonucu döndürür"""
        # Record usage
        self._record_operation("measure")
        return self.state.measure()
    
    def update_usage_time(self, time):
        """Qubit'in son kullanım zamanını günceller"""
        # Only record if time has advanced
        if time > self.last_usage_time and self.is_active:
            time_diff = time - self.last_usage_time
            self.last_usage_time = time
    
    def _record_operation(self, operation_name, start_time=None, end_time=None):
        """
        Records an operation in the usage history
        
        Args:
            operation_name: Name of the operation
            start_time: Start time of the operation (defaults to current time)
            end_time: End time of the operation (defaults to start_time)
        """
        if not self.is_active:
            return
            
        if start_time is None:
            start_time = self.last_usage_time
            
        if end_time is None:
            end_time = start_time
            
        self.usage_history.append((start_time, end_time, operation_name))
        self.gate_count += 1
        self.last_usage_time = end_time
    
    def apply_gate(self, gate_name, start_time, end_time):
        """
        Records a gate application in the usage history
        
        Args:
            gate_name: Name of the gate
            start_time: Start time of the gate application
            end_time: End time of the gate application
        """
        self._record_operation(f"gate:{gate_name}", start_time, end_time)
    
    def set_memory_level(self, level):
        """
        Qubit'in bellek seviyesini değiştirir
        
        Args:
            level: Yeni bellek seviyesi (MemoryLevel)
        """
        self.memory_level = level
        self._record_operation(f"transfer_to_{level.name}")
    
    def map_to(self, physical_qubit):
        """
        Mantıksal qubit'i fiziksel qubit'e eşler
        
        Args:
            physical_qubit: Eşlenecek fiziksel qubit
        """
        if self.type != QubitType.LOGICAL or physical_qubit.type != QubitType.PHYSICAL:
            raise ValueError("Eşleme sadece mantıksal qubit'den fiziksel qubit'e yapılabilir")
        
        self.mapped_to = physical_qubit
        physical_qubit.mapped_from = self
        self._record_operation(f"map_to_physical_{physical_qubit.id}")
    
    def unmap(self):
        """Qubit eşlemesini kaldırır"""
        if self.mapped_to:
            physical_id = self.mapped_to.id
            self.mapped_to.mapped_from = None
            self.mapped_to = None
            self._record_operation(f"unmap_from_physical_{physical_id}")
        elif self.mapped_from:
            logical_id = self.mapped_from.id
            self.mapped_from.mapped_to = None
            self.mapped_from = None
            self._record_operation(f"unmap_from_logical_{logical_id}")
    
    def estimate_decoherence(self, time):
        """
        Estimates decoherence probability at a given time
        
        Args:
            time: Time to estimate decoherence at
            
        Returns:
            float: Probability that the qubit has decohered (0-1)
        """
        if not self.is_active:
            return 1.0
            
        time_since_last_use = time - self.last_usage_time
        if time_since_last_use <= 0:
            return 0.0
            
        # Simple exponential decoherence model
        return 1.0 - np.exp(-time_since_last_use / self._coherence_time)
    
    def serialize(self):
        """
        Serializes the qubit state and properties to a dictionary
        
        Returns:
            dict: Serialized representation of the qubit
        """
        return {
            "id": self.id,
            "type": self.type.name,
            "memory_level": self.memory_level.name,
            "state": {"alpha": self.state.alpha, "beta": self.state.beta},
            "is_allocated": self.is_allocated,
            "is_active": self.is_active,
            "creation_time": self.creation_time,
            "last_usage_time": self.last_usage_time,
            "coherence_time": self.coherence_time,
            "error_rate": self.error_rate,
            "gate_count": self.gate_count,
            "transfer_count": self.transfer_count
        }
    
    @classmethod
    def deserialize(cls, data):
        """
        Creates a qubit from serialized data
        
        Args:
            data: Dictionary containing serialized qubit data
            
        Returns:
            Qubit: Reconstructed qubit object
        """
        qubit_type = QubitType[data["type"]]
        memory_level = MemoryLevel[data["memory_level"]]
        
        qubit = cls(data["id"], qubit_type, memory_level)
        qubit.state = QubitState(data["state"]["alpha"], data["state"]["beta"])
        qubit.is_allocated = data["is_allocated"]
        qubit.is_active = data["is_active"]
        qubit.creation_time = data["creation_time"]
        qubit.last_usage_time = data["last_usage_time"]
        qubit.coherence_time = data["coherence_time"]
        qubit.error_rate = data["error_rate"]
        qubit.gate_count = data["gate_count"]
        qubit.transfer_count = data["transfer_count"]
        
        return qubit 