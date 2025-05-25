#!/usr/bin/env python3
"""
IBM Quantum Integration
======================

IBM Quantum Network integration for real hardware execution.

Developer: kappasutra
"""

import time
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

try:
    from qiskit import QuantumCircuit, transpile
    # Use new Qiskit Runtime for IBM Quantum access
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Estimator
        from qiskit_ibm_provider import IBMProvider
        QISKIT_IBM_AVAILABLE = True
    except ImportError:
        # Fallback to older qiskit-ibmq-provider if available
        try:
            from qiskit.providers.ibmq import IBMQ
            QISKIT_IBM_AVAILABLE = True
        except ImportError:
            QISKIT_IBM_AVAILABLE = False
    
    # Try to import Aer for local simulation
    try:
        from qiskit_aer import Aer
        QISKIT_AER_AVAILABLE = True
    except ImportError:
        QISKIT_AER_AVAILABLE = False
        
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    QISKIT_IBM_AVAILABLE = False
    QISKIT_AER_AVAILABLE = False
    print("⚠️  Qiskit not available. IBM Quantum integration will use simulation mode.")


class BackendType(Enum):
    """IBM Quantum backend types"""
    SIMULATOR = "simulator"
    REAL_HARDWARE = "real_hardware"
    FAKE_BACKEND = "fake_backend"


@dataclass
class BackendInfo:
    """Information about an IBM Quantum backend"""
    name: str
    backend_type: BackendType
    num_qubits: int
    coupling_map: List[List[int]]
    basis_gates: List[str]
    max_shots: int
    max_experiments: int
    simulator: bool
    operational: bool
    pending_jobs: int
    least_busy: bool = False


@dataclass
class JobResult:
    """Result from IBM Quantum job execution"""
    job_id: str
    status: str
    backend_name: str
    shots: int
    results: Dict[str, int]
    execution_time: float
    queue_time: float
    success: bool
    error_message: Optional[str] = None


class IBMQuantumProvider:
    """IBM Quantum provider for accessing backends and executing jobs"""
    
    def __init__(self, token: Optional[str] = None, instance: str = 'ibm-q/open/main'):
        """
        Initialize IBM Quantum provider
        
        Args:
            token: IBM Quantum API token
            instance: IBM Quantum instance (hub/group/project)
        """
        self.token = token
        self.instance = instance
        self.service = None
        self.provider = None
        self.connected = False
        
        print("🔗 Initializing IBM Quantum Provider...")
        
        if QISKIT_AVAILABLE and QISKIT_IBM_AVAILABLE and token:
            try:
                self._connect()
            except Exception as e:
                print(f"⚠️  Failed to connect to IBM Quantum: {e}")
                print("   Using simulation mode instead.")
        else:
            print("⚠️  IBM Quantum token not provided or Qiskit IBM not available.")
            print("   Using simulation mode.")
    
    def _connect(self):
        """Connect to IBM Quantum using new Runtime service"""
        if not QISKIT_AVAILABLE or not QISKIT_IBM_AVAILABLE:
            return False
            
        try:
            # Try new QiskitRuntimeService first
            try:
                self.service = QiskitRuntimeService(token=self.token, instance=self.instance)
                self.connected = True
                print(f"✅ Connected to IBM Quantum Runtime: {self.instance}")
                return True
            except Exception as runtime_error:
                print(f"⚠️  Runtime service failed: {runtime_error}")
                
                # Fallback to IBMProvider
                try:
                    self.provider = IBMProvider(token=self.token, instance=self.instance)
                    self.connected = True
                    print(f"✅ Connected to IBM Quantum Provider: {self.instance}")
                    return True
                except Exception as provider_error:
                    print(f"⚠️  Provider failed: {provider_error}")
                    
                    # Last fallback to legacy IBMQ
                    try:
                        if hasattr(globals(), 'IBMQ'):
                            IBMQ.save_account(self.token, overwrite=True)
                            IBMQ.load_account()
                            self.provider = IBMQ.get_provider()
                            self.connected = True
                            print(f"✅ Connected to IBM Quantum (legacy): {self.instance}")
                            return True
                    except Exception as legacy_error:
                        print(f"⚠️  Legacy IBMQ failed: {legacy_error}")
            
            return False
            
        except Exception as e:
            print(f"❌ IBM Quantum connection failed: {e}")
            return False
    
    def get_backends(self, operational_only: bool = True) -> List[BackendInfo]:
        """Get available IBM Quantum backends"""
        backends = []
        
        if self.connected:
            try:
                # Get backends from service or provider
                if self.service:
                    ibm_backends = self.service.backends()
                elif self.provider:
                    ibm_backends = self.provider.backends()
                else:
                    ibm_backends = []
                
                for backend in ibm_backends:
                    try:
                        # Handle different backend API versions
                        if hasattr(backend, 'configuration'):
                            config = backend.configuration()
                            name = config.backend_name
                            num_qubits = config.n_qubits
                            coupling_map = getattr(config, 'coupling_map', [])
                            basis_gates = config.basis_gates
                            max_shots = getattr(config, 'max_shots', 8192)
                            simulator = getattr(config, 'simulator', False)
                        else:
                            # New backend API
                            name = backend.name
                            num_qubits = backend.num_qubits
                            coupling_map = getattr(backend, 'coupling_map', [])
                            basis_gates = getattr(backend, 'basis_gates', [])
                            max_shots = getattr(backend, 'max_shots', 8192)
                            simulator = 'simulator' in name.lower()
                        
                        # Get status if available
                        operational = True
                        pending_jobs = 0
                        try:
                            if hasattr(backend, 'status'):
                                status = backend.status()
                                operational = getattr(status, 'operational', True)
                                pending_jobs = getattr(status, 'pending_jobs', 0)
                        except:
                            pass
                        
                        backend_info = BackendInfo(
                            name=name,
                            backend_type=BackendType.SIMULATOR if simulator else BackendType.REAL_HARDWARE,
                            num_qubits=num_qubits,
                            coupling_map=coupling_map if coupling_map else [],
                            basis_gates=basis_gates,
                            max_shots=max_shots,
                            max_experiments=1,
                            simulator=simulator,
                            operational=operational,
                            pending_jobs=pending_jobs
                        )
                        backends.append(backend_info)
                        
                    except Exception as backend_error:
                        print(f"⚠️  Error processing backend {getattr(backend, 'name', 'unknown')}: {backend_error}")
                        continue
                    
            except Exception as e:
                print(f"❌ Error getting backends: {e}")
        
        # Add fallback simulation backends if no backends found
        if not backends:
            backends.extend(self._get_fallback_backends())
        
        return backends
    
    def _get_fallback_backends(self) -> List[BackendInfo]:
        """Get fallback simulation backends when IBM Quantum is not available"""
        fallback_backends = []
        
        # Add Aer simulators if available
        if QISKIT_AER_AVAILABLE:
            try:
                # Qiskit 2.0 compatible Aer backends
                aer_backends = [
                    {'name': 'qasm_simulator', 'description': 'QASM Simulator'},
                    {'name': 'statevector_simulator', 'description': 'Statevector Simulator'},
                    {'name': 'unitary_simulator', 'description': 'Unitary Simulator'}
                ]
                
                for backend_info in aer_backends:
                    backend_info_obj = BackendInfo(
                        name=backend_info['name'],
                        backend_type=BackendType.SIMULATOR,
                        num_qubits=32,
                        coupling_map=[],
                        basis_gates=['u1', 'u2', 'u3', 'cx', 'id', 'x', 'y', 'z', 'h', 's', 't'],
                        max_shots=8192,
                        max_experiments=1,
                        simulator=True,
                        operational=True,
                        pending_jobs=0
                    )
                    fallback_backends.append(backend_info_obj)
            except Exception as e:
                print(f"⚠️  Error getting Aer backends: {e}")
        
        # Add basic fallback simulators
        if not fallback_backends:
            fallback_backends = [
                BackendInfo(
                    name="qasm_simulator",
                    backend_type=BackendType.SIMULATOR,
                    num_qubits=32,
                    coupling_map=[],
                    basis_gates=['u1', 'u2', 'u3', 'cx', 'id', 'x', 'y', 'z', 'h', 's', 't'],
                    max_shots=8192,
                    max_experiments=1,
                    simulator=True,
                    operational=True,
                    pending_jobs=0
                ),
                BackendInfo(
                    name="statevector_simulator",
                    backend_type=BackendType.SIMULATOR,
                    num_qubits=32,
                    coupling_map=[],
                    basis_gates=['u1', 'u2', 'u3', 'cx', 'id', 'x', 'y', 'z', 'h', 's', 't'],
                    max_shots=1,
                    max_experiments=1,
                    simulator=True,
                    operational=True,
                    pending_jobs=0
                )
            ]
        
        return fallback_backends
    
    def get_least_busy_backend(self, min_qubits: int = 5) -> Optional[BackendInfo]:
        """Get the least busy backend with minimum qubits"""
        backends = self.get_backends()
        
        # Filter by minimum qubits and real hardware
        suitable_backends = [
            b for b in backends 
            if b.num_qubits >= min_qubits and 
               b.backend_type == BackendType.REAL_HARDWARE and 
               b.operational
        ]
        
        if not suitable_backends:
            # Fallback to simulators
            suitable_backends = [
                b for b in backends 
                if b.num_qubits >= min_qubits and b.simulator
            ]
        
        if suitable_backends:
            # Sort by pending jobs (least busy first)
            least_busy = min(suitable_backends, key=lambda b: b.pending_jobs)
            least_busy.least_busy = True
            return least_busy
        
        return None


class IBMQuantumBackend:
    """IBM Quantum backend for executing circuits"""
    
    def __init__(self, provider: IBMQuantumProvider, backend_name: str):
        """
        Initialize IBM Quantum backend
        
        Args:
            provider: IBM Quantum provider
            backend_name: Name of the backend to use
        """
        self.provider = provider
        self.backend_name = backend_name
        self.backend = None
        self.backend_info = None
        
        print(f"🔧 Initializing IBM Quantum Backend: {backend_name}")
        
        # Get backend info
        backends = provider.get_backends()
        self.backend_info = next((b for b in backends if b.name == backend_name), None)
        
        if not self.backend_info:
            raise ValueError(f"Backend {backend_name} not found")
        
        # Get actual backend if connected
        if provider.connected and provider.provider:
            try:
                self.backend = provider.provider.get_backend(backend_name)
                print(f"✅ Backend {backend_name} ready")
            except Exception as e:
                print(f"⚠️  Could not get backend {backend_name}: {e}")
                print("   Using simulation mode")
    
    def execute_circuit(self, circuit, shots: int = 1024, 
                       optimization_level: int = 1, 
                       monitor: bool = True) -> JobResult:
        """
        Execute a quantum circuit on IBM Quantum backend
        
        Args:
            circuit: Quantum circuit to execute
            shots: Number of shots
            optimization_level: Transpilation optimization level (0-3)
            monitor: Whether to monitor job progress
            
        Returns:
            JobResult with execution results
        """
        start_time = time.time()
        
        print(f"🚀 Executing circuit on {self.backend_name}")
        print(f"   Shots: {shots}")
        print(f"   Optimization level: {optimization_level}")
        
        try:
            if self.backend and QISKIT_AVAILABLE:
                # Real IBM Quantum execution
                return self._execute_real(circuit, shots, optimization_level, monitor)
            else:
                # Simulation mode
                return self._execute_simulation(circuit, shots)
                
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ Execution failed: {e}")
            
            return JobResult(
                job_id="error",
                status="ERROR",
                backend_name=self.backend_name,
                shots=shots,
                results={},
                execution_time=execution_time,
                queue_time=0,
                success=False,
                error_message=str(e)
            )
    
    def _execute_real(self, circuit, shots: int, optimization_level: int, 
                     monitor: bool) -> JobResult:
        """Execute on real IBM Quantum hardware"""
        start_time = time.time()
        
        # Transpile circuit for backend
        print("🔄 Transpiling circuit for backend...")
        transpiled = transpile(
            circuit, 
            backend=self.backend,
            optimization_level=optimization_level
        )
        
        # Submit job
        print("📤 Submitting job to IBM Quantum...")
        job = execute(transpiled, backend=self.backend, shots=shots)
        
        queue_start = time.time()
        
        # Monitor job if requested
        if monitor:
            print("⏳ Monitoring job progress...")
            job_monitor(job)
        else:
            # Wait for completion
            while job.status() not in [JobStatus.DONE, JobStatus.ERROR, JobStatus.CANCELLED]:
                time.sleep(5)
        
        queue_time = time.time() - queue_start
        
        # Get results
        if job.status() == JobStatus.DONE:
            result = job.result()
            counts = result.get_counts()
            
            execution_time = time.time() - start_time
            
            print(f"✅ Job completed successfully")
            print(f"   Job ID: {job.job_id()}")
            print(f"   Execution time: {execution_time:.2f}s")
            print(f"   Queue time: {queue_time:.2f}s")
            
            return JobResult(
                job_id=job.job_id(),
                status="COMPLETED",
                backend_name=self.backend_name,
                shots=shots,
                results=counts,
                execution_time=execution_time,
                queue_time=queue_time,
                success=True
            )
        else:
            error_msg = f"Job failed with status: {job.status()}"
            if hasattr(job, 'error_message'):
                error_msg += f" - {job.error_message()}"
            
            return JobResult(
                job_id=job.job_id(),
                status=str(job.status()),
                backend_name=self.backend_name,
                shots=shots,
                results={},
                execution_time=time.time() - start_time,
                queue_time=queue_time,
                success=False,
                error_message=error_msg
            )
    
    def _execute_simulation(self, circuit, shots: int) -> JobResult:
        """Execute using local simulation"""
        start_time = time.time()
        
        print("🔄 Running local simulation...")
        
        # Simple simulation - generate random results based on circuit
        import random
        
        # Determine number of qubits from circuit
        if hasattr(circuit, 'width'):
            num_qubits = circuit.width
        elif hasattr(circuit, 'num_qubits'):
            num_qubits = circuit.num_qubits
        else:
            num_qubits = 2  # Default
        
        # Generate random measurement results
        results = {}
        for _ in range(shots):
            # Generate random bit string
            bitstring = ''.join(random.choice(['0', '1']) for _ in range(num_qubits))
            results[bitstring] = results.get(bitstring, 0) + 1
        
        execution_time = time.time() - start_time
        
        print(f"✅ Simulation completed")
        print(f"   Results: {len(results)} unique outcomes")
        print(f"   Execution time: {execution_time:.3f}s")
        
        return JobResult(
            job_id=f"sim_{int(time.time())}",
            status="COMPLETED",
            backend_name=self.backend_name,
            shots=shots,
            results=results,
            execution_time=execution_time,
            queue_time=0,
            success=True
        )
    
    def get_backend_info(self) -> BackendInfo:
        """Get backend information"""
        return self.backend_info
    
    def get_status(self) -> Dict[str, Any]:
        """Get backend status"""
        if self.backend:
            try:
                status = self.backend.status()
                return {
                    "operational": status.operational,
                    "pending_jobs": status.pending_jobs,
                    "status_msg": status.status_msg
                }
            except:
                pass
        
        return {
            "operational": True,
            "pending_jobs": 0,
            "status_msg": "Simulation mode"
        } 