"""
Qubit Geri Dönüşüm modülü
======================

Qubit'lerin sıfırlanması ve yeniden kullanımı ile ilgili stratejileri içerir.
"""

import logging
from enum import Enum, auto
import numpy as np

from ..core.gate import GateType


class RecyclingStrategy(Enum):
    """Qubit geri dönüşüm stratejileri"""
    NONE = auto()           # Geri dönüşüm yok
    RESET_BASED = auto()    # Reset tabanlı geri dönüşüm
    TELEPORT = auto()       # Teleport tabanlı geri dönüşüm
    ADAPTIVE = auto()       # Adaptif geri dönüşüm
    DYNAMIC = auto()        # Dinamik yaşam süresi analizi ile geri dönüşüm
    PREDICTIVE = auto()     # Çalışma zamanı tahminlerine dayalı geri dönüşüm


class QubitRecycler:
    """
    Qubit geri dönüşümünü yöneten sınıf
    
    Reset tabanlı ve teleport tabanlı geri dönüşüm stratejilerini uygular.
    """
    
    def __init__(self, strategy=RecyclingStrategy.RESET_BASED):
        """
        QubitRecycler nesnesini başlatır
        
        Args:
            strategy: Geri dönüşüm stratejisi
        """
        self.strategy = strategy
        self.logger = logging.getLogger("QubitRecycler")
        self.logger.setLevel(logging.INFO)
        
        # İstatistikler
        self.total_reset_count = 0
        self.total_teleport_count = 0
        self.total_dynamic_recycles = 0
        self.total_predictive_recycles = 0
        self.saved_qubits = 0
        
        # Son yaşam süresi analizi sonuçlarını önbelleğe alma
        self._last_lifetime_analysis = None
    
    def optimize(self, circuit, qubit_usage_analysis=None):
        """
        Devre için qubit geri dönüşümünü optimize eder
        
        Args:
            circuit: Optimize edilecek devre
            qubit_usage_analysis: Önceden yapılmış qubit kullanım analizi (opsiyonel)
            
        Returns:
            tuple: (optimize edilmiş devre, tasarruf edilen qubit sayısı)
        """
        if self.strategy == RecyclingStrategy.NONE:
            return circuit, 0
        
        # Devrenin kopyasını oluştur
        optimized_circuit = circuit.copy()
        
        # Kullanım analizini yap veya verilen analizi kullan
        usage_analysis = qubit_usage_analysis
        if usage_analysis is None:
            usage_analysis = self._analyze_qubit_usage(optimized_circuit)
        
        # Strateji seçimi
        if self.strategy == RecyclingStrategy.RESET_BASED:
            saved = self._apply_reset_based_recycling(optimized_circuit, usage_analysis)
        elif self.strategy == RecyclingStrategy.TELEPORT:
            saved = self._apply_teleport_based_recycling(optimized_circuit, usage_analysis)
        elif self.strategy == RecyclingStrategy.ADAPTIVE:
            saved = self._apply_adaptive_recycling(optimized_circuit, usage_analysis)
        elif self.strategy == RecyclingStrategy.DYNAMIC:
            saved = self._apply_dynamic_recycling(optimized_circuit, usage_analysis)
        elif self.strategy == RecyclingStrategy.PREDICTIVE:
            saved = self._apply_predictive_recycling(optimized_circuit, usage_analysis)
        else:
            saved = 0
        
        self.saved_qubits += saved
        return optimized_circuit, saved
    
    def _analyze_qubit_usage(self, circuit):
        """
        Devredeki qubit kullanımını analiz eder
        
        Args:
            circuit: Analiz edilecek devre
            
        Returns:
            dict: Qubit kullanım analizi
                {qubit: {
                    'first_use': ilk_kullanım_zamanı,
                    'last_use': son_kullanım_zamanı,
                    'usage_intervals': [(başlangıç1, bitiş1), (başlangıç2, bitiş2), ...],
                    'gates': [kapı1, kapı2, ...],
                    'is_entangled_at_end': son_kullanımda_dolanık_mı
                }}
        """
        analysis = {}
        for qubit in circuit.qubits:
            qubit_gates = circuit.get_gates_by_qubit(qubit)
            
            if not qubit_gates:
                # Bu qubit hiç kullanılmamış
                analysis[qubit] = {
                    'first_use': 0,
                    'last_use': 0,
                    'usage_intervals': [],
                    'gates': [],
                    'is_entangled_at_end': False
                }
                continue
            
            # Zamanları sırala
            gate_times = [(gate.time, gate) for gate in qubit_gates]
            gate_times.sort(key=lambda x: x[0])  # Sort only by time value
            
            first_use = gate_times[0][0]
            last_use = gate_times[-1][0] + gate_times[-1][1].duration
            
            # Kullanım aralıklarını belirle
            current_interval_start = first_use
            current_interval_end = current_interval_start
            usage_intervals = []
            
            for time, gate in gate_times:
                # Eğer arada boşluk varsa, yeni aralık başlat
                if time > current_interval_end + 10:  # 10 birim boşluk toleransı
                    usage_intervals.append((current_interval_start, current_interval_end))
                    current_interval_start = time
                
                current_interval_end = max(current_interval_end, time + gate.duration)
            
            # Son aralığı ekle
            usage_intervals.append((current_interval_start, current_interval_end))
            
            # Son kullanımda dolanıklık durumunu belirle
            is_entangled_at_end = False
            for gate in reversed(qubit_gates):
                if len(gate.qubits) > 1 and gate.type not in [GateType.MEASURE, GateType.RESET, GateType.BARRIER]:
                    # Bu bir çok-qubitli kapı ve ölçüm/reset değil, bu nedenle dolanıklık oluşturabilir
                    is_entangled_at_end = True
                    break
                
                if gate.type == GateType.MEASURE or gate.type == GateType.RESET:
                    # Ölçüm veya reset dolanıklığı bozar
                    is_entangled_at_end = False
                    break
            
            analysis[qubit] = {
                'first_use': first_use,
                'last_use': last_use,
                'usage_intervals': usage_intervals,
                'gates': [gate for _, gate in gate_times],
                'is_entangled_at_end': is_entangled_at_end
            }
        
        return analysis
    
    def _analyze_qubit_lifetime(self, circuit, usage_analysis=None):
        """
        Performs a dynamic analysis of qubit lifetimes
        
        Args:
            circuit: The quantum circuit to analyze
            usage_analysis: Pre-computed usage analysis (optional)
            
        Returns:
            dict: Lifetime analysis with the following structure:
                {qubit: {
                    'lifetime': total_lifetime,
                    'active_periods': [(start1, end1), (start2, end2), ...],
                    'idle_time': total_idle_time,
                    'active_time': total_active_time,
                    'idle_periods': [(start1, end1), (start2, end2), ...],
                    'utilization': active_time / total_lifetime,
                    'operation_count': number_of_gates,
                    'operation_density': operations_per_time_unit
                }}
        """
        # If usage analysis isn't provided, compute it
        if usage_analysis is None:
            usage_analysis = self._analyze_qubit_usage(circuit)
            
        lifetime_analysis = {}
        
        for qubit, analysis in usage_analysis.items():
            # Skip qubits that aren't used
            if not analysis['gates']:
                lifetime_analysis[qubit] = {
                    'lifetime': 0,
                    'active_periods': [],
                    'idle_time': 0,
                    'active_time': 0,
                    'idle_periods': [],
                    'utilization': 0,
                    'operation_count': 0,
                    'operation_density': 0
                }
                continue
                
            # Extract active periods (usage intervals) from the analysis
            active_periods = analysis['usage_intervals']
            
            # Calculate total lifetime (from first to last use)
            total_lifetime = analysis['last_use'] - analysis['first_use']
            
            # Calculate active time (sum of active periods)
            active_time = sum(end - start for start, end in active_periods)
            
            # Calculate idle periods (gaps between active periods)
            idle_periods = []
            for i in range(len(active_periods) - 1):
                curr_end = active_periods[i][1]
                next_start = active_periods[i + 1][0]
                if next_start > curr_end:
                    idle_periods.append((curr_end, next_start))
            
            # Calculate total idle time
            idle_time = sum(end - start for start, end in idle_periods)
            
            # Calculate utilization (active time / total lifetime)
            utilization = active_time / total_lifetime if total_lifetime > 0 else 0
            
            # Count operations (gates) on this qubit
            operation_count = len(analysis['gates'])
            
            # Calculate operation density (operations per time unit)
            operation_density = operation_count / active_time if active_time > 0 else 0
            
            # Store all analysis data
            lifetime_analysis[qubit] = {
                'lifetime': total_lifetime,
                'active_periods': active_periods,
                'idle_time': idle_time,
                'active_time': active_time,
                'idle_periods': idle_periods,
                'utilization': utilization,
                'operation_count': operation_count,
                'operation_density': operation_density
            }
        
        # Cache the analysis for later use
        self._last_lifetime_analysis = lifetime_analysis
            
        return lifetime_analysis
    
    def _apply_dynamic_recycling(self, circuit, usage_analysis):
        """
        Applies dynamic lifetime-based recycling strategy
        
        This strategy identifies qubits with long idle periods and inserts reset operations
        to allow them to be recycled during those periods. It also considers qubit operation
        density to prioritize recycling qubits that are used less frequently.
        
        Args:
            circuit: Circuit to be optimized
            usage_analysis: Qubit usage analysis
            
        Returns:
            int: Number of qubits saved
        """
        self.logger.info("Applying dynamic lifetime-based recycling strategy")
        
        # Perform lifetime analysis
        lifetime_analysis = self._analyze_qubit_lifetime(circuit, usage_analysis)
        
        reset_count = 0
        saved_qubits = 0
        circuit_depth = circuit.calculate_depth()
        
        # Identify qubits with long idle periods
        candidates = []
        for qubit, analysis in lifetime_analysis.items():
            # Skip qubits without idle periods
            if not analysis['idle_periods']:
                continue
                
            # Consider qubits with long idle periods and low utilization
            for idle_start, idle_end in analysis['idle_periods']:
                idle_duration = idle_end - idle_start
                # If idle period is significant and qubit isn't entangled at that point
                if idle_duration > 20 and not self._is_qubit_entangled_at(circuit, qubit, idle_start):
                    priority = idle_duration * (1 - analysis['utilization'])
                    candidates.append((qubit, idle_start, idle_end, priority))
        
        # Sort candidates by priority (higher priority first)
        candidates.sort(key=lambda x: x[3], reverse=True)
        
        # Apply resets to selected candidates
        for qubit, idle_start, idle_end, _ in candidates:
            # Find all gates on this qubit
            qubit_gates = circuit.get_gates_by_qubit(qubit)
            
            # Find the last gate before the idle period
            last_gate_before = max(
                (g for g in qubit_gates if g.time + g.duration <= idle_start), 
                key=lambda g: g.time + g.duration, 
                default=None
            )
            
            # Find the first gate after the idle period
            first_gate_after = min(
                (g for g in qubit_gates if g.time >= idle_end),
                key=lambda g: g.time,
                default=None
            )
            
            # Skip if we couldn't find the appropriate gates
            if not last_gate_before or not first_gate_after:
                continue
                
            # Skip if the last gate is already a reset or measure
            if last_gate_before.type in [GateType.RESET, GateType.MEASURE]:
                continue
                
            # Add reset after the last gate
            reset_time = last_gate_before.time + last_gate_before.duration + 1
            circuit.add_gate(GateType.RESET, qubit, time=reset_time)
            reset_count += 1
            
            # If we can reuse this qubit during the idle period, count it as saved
            if self._can_reuse_qubit_during_period(circuit, qubit, reset_time + 1, idle_end - 5):
                saved_qubits += 1
        
        self.logger.info(f"Added {reset_count} dynamic reset operations, potentially saving {saved_qubits} qubits")
        self.total_dynamic_recycles += reset_count
        
        return saved_qubits
    
    def _is_qubit_entangled_at(self, circuit, qubit, time_point):
        """
        Determines if a qubit is entangled at a specific time point
        
        Args:
            circuit: The quantum circuit
            qubit: The qubit to check
            time_point: The time point to check
            
        Returns:
            bool: True if the qubit is likely entangled, False otherwise
        """
        # Get all gates on this qubit before the time point
        qubit_gates = [g for g in circuit.get_gates_by_qubit(qubit) if g.time < time_point]
        
        if not qubit_gates:
            return False
            
        # Start from the last gate applied before the time point
        last_gate = max(qubit_gates, key=lambda g: g.time)
        
        # If the last gate is a measure or reset, the qubit is not entangled
        if last_gate.type in [GateType.MEASURE, GateType.RESET]:
            return False
            
        # If the last gate is a multi-qubit gate, the qubit might be entangled
        if len(last_gate.qubits) > 1:
            # Check if any other qubit involved in this gate is used after this gate
            for other_qubit in last_gate.qubits:
                if other_qubit == qubit:
                    continue
                    
                other_gates = circuit.get_gates_by_qubit(other_qubit)
                later_gates = [g for g in other_gates if g.time > last_gate.time]
                
                if later_gates:
                    return True
                    
        # For simplicity, if we've reached this point, assume the qubit is not entangled
        return False
    
    def _can_reuse_qubit_during_period(self, circuit, qubit, start_time, end_time):
        """
        Determines if a qubit can be reused during a specific time period
        
        Args:
            circuit: The quantum circuit
            qubit: The qubit to check
            start_time: The start time of the period
            end_time: The end time of the period
            
        Returns:
            bool: True if the qubit can be reused, False otherwise
        """
        # Check if the period is long enough to be useful
        if end_time - start_time < 10:
            return False
            
        # Count the number of qubits that are active during this period
        active_qubits = 0
        for other_qubit in circuit.qubits:
            if other_qubit == qubit:
                continue
                
            # Get gates for this qubit within the time period
            time_range_gates = [g for g in circuit.get_gates_by_qubit(other_qubit)
                             if g.time >= start_time and g.time <= end_time]
                             
            if time_range_gates:
                active_qubits += 1
                
        # If a significant number of qubits are active, there's potential for reuse
        # (this is a heuristic and could be adjusted)
        return active_qubits > len(circuit.qubits) / 4
    
    def _apply_predictive_recycling(self, circuit, usage_analysis):
        """
        Applies predictive recycling based on runtime patterns
        
        This strategy analyzes circuit execution patterns to predict when qubits will
        be needed in the future, allowing for more aggressive recycling of qubits that
        won't be needed for a long time.
        
        Args:
            circuit: Circuit to be optimized
            usage_analysis: Qubit usage analysis
            
        Returns:
            int: Number of qubits saved
        """
        self.logger.info("Applying predictive recycling strategy")
        
        # First, analyze overall circuit structure
        circuit_depth = circuit.calculate_depth()
        all_gates = sorted(circuit.gates, key=lambda g: g.time)
        
        # Identify execution phases (initialization, computation, measurement)
        phase_boundaries = self._identify_circuit_phases(circuit, all_gates)
        
        # Analyze qubit usage patterns in each phase
        phase_usage = self._analyze_phase_usage(circuit, phase_boundaries)
        
        reset_count = 0
        saved_qubits = 0
        
        # For each phase transition, identify qubits that won't be used in the next phase
        for i in range(len(phase_boundaries) - 1):
            current_phase_end = phase_boundaries[i]
            next_phase_start = phase_boundaries[i+1]
            
            # Find qubits that are not used in the next phase
            for qubit in circuit.qubits:
                # Skip if qubit is not in the usage analysis
                if qubit not in usage_analysis:
                    continue
                    
                # Check if the qubit is used in the current phase but not in the next
                current_phase_usage = any(gate.time <= current_phase_end for gate in usage_analysis[qubit]['gates'])
                next_phase_usage = any(gate.time >= next_phase_start for gate in usage_analysis[qubit]['gates'])
                
                if current_phase_usage and not next_phase_usage and not usage_analysis[qubit]['is_entangled_at_end']:
                    # This qubit can be reset at the phase transition
                    reset_time = current_phase_end + 1
                    
                    # Check if the qubit doesn't already have a reset or measurement
                    existing_ops = [g for g in circuit.get_gates_by_qubit(qubit) 
                                  if g.time >= current_phase_end - 5 and g.time <= current_phase_end + 5]
                                  
                    if not any(g.type in [GateType.RESET, GateType.MEASURE] for g in existing_ops):
                        circuit.add_gate(GateType.RESET, qubit, time=reset_time)
                        reset_count += 1
                        
                        # If the qubit is not used again for a significant period, count it as saved
                        if not any(gate.time < next_phase_start + (circuit_depth / 4) 
                                 for gate in usage_analysis[qubit]['gates'] 
                                 if gate.time > reset_time):
                            saved_qubits += 1
        
        self.logger.info(f"Added {reset_count} predictive reset operations, potentially saving {saved_qubits} qubits")
        self.total_predictive_recycles += reset_count
        
        return saved_qubits
    
    def _identify_circuit_phases(self, circuit, all_gates):
        """
        Identifies execution phases in the circuit
        
        Args:
            circuit: The quantum circuit
            all_gates: All gates in the circuit, sorted by time
            
        Returns:
            list: Time points marking phase boundaries
        """
        circuit_depth = circuit.calculate_depth()
        
        # Simple phase identification based on gate density
        time_points = [g.time for g in all_gates]
        phase_boundaries = [0]  # Start with the beginning of the circuit
        
        if not time_points:
            return [0, circuit_depth]
        
        # Use a sliding window to identify changes in gate density
        window_size = max(10, len(time_points) // 20)  # 10 or 5% of all gates
        densities = []
        
        for i in range(0, len(time_points) - window_size, window_size // 2):
            window = time_points[i:i+window_size]
            time_span = window[-1] - window[0] if len(window) > 1 else 1
            density = len(window) / time_span
            densities.append((window[0], density))
        
        # Identify significant changes in density
        if densities:
            avg_density = np.mean([d for _, d in densities])
            std_density = np.std([d for _, d in densities])
            threshold = avg_density + std_density
            
            for time, density in densities:
                if abs(density - avg_density) > threshold:
                    phase_boundaries.append(time)
        
        # Add measurement phase if not already identified
        measurement_gates = [g for g in all_gates if g.type == GateType.MEASURE]
        if measurement_gates:
            first_measure_time = min(g.time for g in measurement_gates)
            if not any(abs(b - first_measure_time) < 10 for b in phase_boundaries):
                phase_boundaries.append(first_measure_time)
        
        # Add the end of the circuit
        phase_boundaries.append(circuit_depth)
        
        # Sort and remove duplicates
        phase_boundaries = sorted(set(phase_boundaries))
        
        return phase_boundaries
    
    def _analyze_phase_usage(self, circuit, phase_boundaries):
        """
        Analyzes qubit usage patterns in each circuit phase
        
        Args:
            circuit: The quantum circuit
            phase_boundaries: Time points marking phase boundaries
            
        Returns:
            list: Qubit usage analysis for each phase
        """
        phase_usage = []
        
        for i in range(len(phase_boundaries) - 1):
            phase_start = phase_boundaries[i]
            phase_end = phase_boundaries[i+1]
            
            # Count which qubits are used in this phase
            phase_qubits = set()
            for gate in circuit.gates:
                if phase_start <= gate.time <= phase_end:
                    phase_qubits.update(gate.qubits)
            
            # Count gate types in this phase
            gate_types = {}
            for gate in circuit.gates:
                if phase_start <= gate.time <= phase_end:
                    gate_types[gate.type] = gate_types.get(gate.type, 0) + 1
            
            phase_usage.append({
                'start': phase_start,
                'end': phase_end,
                'qubits': phase_qubits,
                'gate_types': gate_types,
                'qubit_count': len(phase_qubits),
                'is_measurement_phase': GateType.MEASURE in gate_types
            })
        
        return phase_usage
        
    def _apply_reset_based_recycling(self, circuit, usage_analysis):
        """
        Reset tabanlı geri dönüşüm stratejisini uygular
        
        Args:
            circuit: Optimize edilecek devre
            usage_analysis: Qubit kullanım analizi
            
        Returns:
            int: Tasarruf edilen qubit sayısı
        """
        self.logger.info("Applying reset-based recycling strategy")
        reset_count = 0
        saved_qubits = 0
        circuit_depth = circuit.calculate_depth()
        
        # Sort qubits by last use time
        sorted_qubits = sorted(circuit.qubits, key=lambda q: usage_analysis[q]['last_use'])
        
        # Her qubit için son kullanımdan sonra reset uygulayıp uygulayamayacağımızı kontrol et
        for qubit in sorted_qubits:
            analysis = usage_analysis[qubit]
            last_use = analysis['last_use']
            
            # Eğer son kullanımdan sonra devre hala devam ediyorsa ve qubit dolanık değilse
            if last_use < circuit_depth - 10 and not analysis['is_entangled_at_end']:
                # Reset ekle
                circuit.add_gate(GateType.RESET, qubit, time=last_use + 1)
                reset_count += 1
                
                # Eğer bu qubit'in kullanılabilir hale gelmesi başka qubit tasarrufu sağlarsa
                if self._can_reuse_qubit_save_allocation(circuit, qubit, last_use + 2, usage_analysis):
                    saved_qubits += 1
        
        self.logger.info(f"Added {reset_count} reset operations, potentially saving {saved_qubits} qubits")
        self.total_reset_count += reset_count
        
        return saved_qubits
    
    def _apply_teleport_based_recycling(self, circuit, usage_analysis):
        """
        Teleport tabanlı geri dönüşüm stratejisini uygular
        
        Args:
            circuit: Optimize edilecek devre
            usage_analysis: Qubit kullanım analizi
            
        Returns:
            int: Tasarruf edilen qubit sayısı
        """
        self.logger.info("Applying teleport-based recycling strategy")
        teleport_count = 0
        saved_qubits = 0
        
        # Dolanık qubit çiftlerini bul
        entangled_pairs = self._find_entangled_qubit_pairs(circuit, usage_analysis)
        
        for qubit_a, qubit_b in entangled_pairs:
            # Eğer bu dolanık çifti teleport ile optimize edebilirsek
            if self._can_apply_teleport(circuit, qubit_a, qubit_b, usage_analysis):
                # Teleport protokolü ekle
                success = self._add_teleport_protocol(circuit, qubit_a, qubit_b, usage_analysis)
                
                if success:
                    teleport_count += 1
                    # Teleport genellikle 1 qubit tasarrufu sağlar
                    saved_qubits += 1
        
        self.logger.info(f"Added {teleport_count} teleport operations, potentially saving {saved_qubits} qubits")
        self.total_teleport_count += teleport_count
        
        return saved_qubits
    
    def _apply_adaptive_recycling(self, circuit, usage_analysis):
        """
        Adaptif geri dönüşüm stratejisini uygular (reset ve teleport kombinasyonu)
        
        Args:
            circuit: Optimize edilecek devre
            usage_analysis: Qubit kullanım analizi
            
        Returns:
            int: Tasarruf edilen qubit sayısı
        """
        self.logger.info("Applying adaptive recycling strategy")
        
        # Önce reset tabanlı stratejiyi uygula
        saved_by_reset = self._apply_reset_based_recycling(circuit, usage_analysis)
        
        # Analizi güncelle
        updated_analysis = self._analyze_qubit_usage(circuit)
        
        # Sonra teleport tabanlı stratejiyi uygula
        saved_by_teleport = self._apply_teleport_based_recycling(circuit, updated_analysis)
        
        return saved_by_reset + saved_by_teleport
    
    def _can_reuse_qubit_save_allocation(self, circuit, qubit, available_time, analysis):
        """
        Qubit'in yeniden kullanılması başka bir qubit tahsisinden tasarruf sağlar mı?
        
        Args:
            circuit: Devre
            qubit: Yeniden kullanılabilir hale gelen qubit
            available_time: Qubit'in yeniden kullanılabilir olduğu zaman
            analysis: Qubit kullanım analizi
            
        Returns:
            bool: Yeniden kullanım tasarruf sağlarsa True
        """
        # Diğer qubit'lerin ilk kullanım zamanlarını kontrol et
        # Eğer available_time sonra başlayan başka bir qubit varsa,
        # onun yerine bu qubit'i yeniden kullanabiliriz
        for other_qubit in circuit.qubits:
            if other_qubit == qubit:
                continue
                
            other_analysis = analysis.get(other_qubit)
            if not other_analysis:
                continue
                
            first_use = other_analysis['first_use']
            
            # Eğer diğer qubit'in ilk kullanımı, bu qubit'in yeniden kullanılabilir olduğu zamandan sonraysa
            if first_use > available_time:
                return True
        
        return False
    
    def _find_entangled_qubit_pairs(self, circuit, analysis):
        """
        Devredeki dolanık qubit çiftlerini bulur
        
        Args:
            circuit: Devre
            analysis: Qubit kullanım analizi
            
        Returns:
            list: Dolanık qubit çiftleri [(qubit_a, qubit_b), ...]
        """
        entangled_pairs = []
        
        # Devredeki çok-qubitli kapıları kontrol et
        multi_qubit_gates = [gate for gate in circuit.gates if len(gate.qubits) > 1 and 
                            gate.type not in [GateType.MEASURE, GateType.RESET, GateType.BARRIER]]
        
        for gate in multi_qubit_gates:
            if len(gate.qubits) == 2:
                qubit_a, qubit_b = gate.qubits
                # Eğer bu çift zaten eklenmemişse
                if (qubit_a, qubit_b) not in entangled_pairs and (qubit_b, qubit_a) not in entangled_pairs:
                    entangled_pairs.append((qubit_a, qubit_b))
        
        return entangled_pairs
    
    def _can_apply_teleport(self, circuit, qubit_a, qubit_b, analysis):
        """
        İki qubit arasında teleport uygulanabilir mi kontrol eder
        
        Args:
            circuit: Devre
            qubit_a: Birinci qubit
            qubit_b: İkinci qubit
            analysis: Qubit kullanım analizi
            
        Returns:
            bool: Teleport uygulanabilirse True
        """
        # Teleport için basit bir kontrol - gelişmiş bir uygulamada daha detaylı olabilir
        # Bu basitleştirilmiş versiyonda, eğer qubits dolanıksa ve biri diğerinden
        # çok daha uzun süre kullanılıyorsa teleport uygulanabilir kabul ediyoruz
        
        analysis_a = analysis[qubit_a]
        analysis_b = analysis[qubit_b]
        
        last_use_a = analysis_a['last_use']
        last_use_b = analysis_b['last_use']
        
        # Eğer bir qubit diğerinden çok daha uzun süre kullanılıyorsa
        if abs(last_use_a - last_use_b) > 20:
            return True
        
        return False
    
    def _add_teleport_protocol(self, circuit, source_qubit, target_qubit, analysis):
        """
        İki qubit arasında teleport protokolü ekler
        
        Args:
            circuit: Devre
            source_qubit: Kaynak qubit
            target_qubit: Hedef qubit
            analysis: Qubit kullanım analizi
            
        Returns:
            bool: Teleport başarılı eklendiyse True
        """
        # Not: Gerçek bir teleport protokolü çok daha karmaşıktır.
        # Bu örnek, sadece teleport işleminin simüle edildiğini göstermek içindir.
        
        analysis_source = analysis[source_qubit]
        analysis_target = analysis[target_qubit]
        
        # Hangi qubit önce kullanımını bitirecek?
        if analysis_source['last_use'] < analysis_target['last_use']:
            early_qubit = source_qubit
            late_qubit = target_qubit
        else:
            early_qubit = target_qubit
            late_qubit = source_qubit
        
        early_last_use = min(analysis_source['last_use'], analysis_target['last_use'])
        
        # Yardımcı qubit gerekir
        ancilla = circuit.add_qubit(None, QubitType.ANCILLA)
        
        # Teleport için kapılar
        # Bell durumu oluştur
        circuit.h(ancilla)
        circuit.cnot(ancilla, early_qubit)
        
        # Teleport ölçümleri
        circuit.cnot(late_qubit, ancilla)
        circuit.h(late_qubit)
        circuit.add_gate(GateType.MEASURE, ancilla, time=early_last_use + 3)
        circuit.add_gate(GateType.MEASURE, late_qubit, time=early_last_use + 4)
        
        # Klasik sonuçlara göre düzeltme kapılarını eklemek gerekir
        # Bu basitleştirilmiş versiyonda atlanmıştır
        
        return True
    
    def get_stats(self):
        """
        Geri dönüşüm istatistiklerini döndürür
        
        Returns:
            dict: Geri dönüşüm istatistikleri
        """
        return {
            'strategy': self.strategy.name,
            'total_reset_count': self.total_reset_count,
            'total_teleport_count': self.total_teleport_count,
            'total_dynamic_recycles': self.total_dynamic_recycles,
            'total_predictive_recycles': self.total_predictive_recycles,
            'saved_qubits': self.saved_qubits
        }
    
    def reset_stats(self):
        """Geri dönüşüm istatistiklerini sıfırlar"""
        self.total_reset_count = 0
        self.total_teleport_count = 0
        self.total_dynamic_recycles = 0
        self.total_predictive_recycles = 0
        self.saved_qubits = 0 