import axios from 'axios';
import { MockApiService } from './mockApiService';

// Function to get API configuration from localStorage
const getApiConfig = () => {
  const savedConfig = localStorage.getItem('quantum_api_config');
  if (savedConfig) {
    try {
      return JSON.parse(savedConfig);
    } catch (e) {
      console.error('Failed to parse API config:', e);
    }
  }
  return {
    mode: 'demo',
    apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:5001',
    isDemo: process.env.REACT_APP_DEMO_MODE === 'true' || process.env.REACT_APP_API_URL?.includes('demo') || false
  };
};

const config = getApiConfig();
const API_BASE_URL = config.apiUrl;
const IS_DEMO_MODE = config.isDemo;

// Debug logging
console.log('🔧 IBMQuantumService Config:', {
  mode: config.mode,
  API_BASE_URL,
  IS_DEMO_MODE,
  REACT_APP_API_URL: process.env.REACT_APP_API_URL,
  REACT_APP_DEMO_MODE: process.env.REACT_APP_DEMO_MODE
});

export interface IBMBackend {
  name: string;
  type: string;
  num_qubits: number;
  coupling_map: number[][];
  basis_gates: string[];
  max_shots: number;
  simulator: boolean;
  operational: boolean;
  pending_jobs: number;
  least_busy?: boolean;
}

export interface IBMExecutionResult {
  success: boolean;
  job_id: string;
  status: string;
  backend: string;
  shots: number;
  results: Record<string, number>;
  execution_time: number;
  queue_time: number;
  error_message?: string;
}

export interface IBMStatus {
  qiskit_available: boolean;
  qiskit_version?: string;
  token_provided: boolean;
  connected: boolean;
  integration_ready: boolean;
}

export interface CircuitData {
  name: string;
  qubits: number;
  gates: Array<{
    type: string;
    qubits: number[];
    parameters?: number[];
  }>;
  measurements?: Array<{
    qubit: number;
    classical_bit: number;
  }>;
}

class IBMQuantumService {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
    // Store in localStorage for persistence
    localStorage.setItem('ibm_quantum_token', token);
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('ibm_quantum_token');
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('ibm_quantum_token');
  }

  async getStatus(): Promise<IBMStatus> {
    try {
      if (IS_DEMO_MODE) {
        return await MockApiService.getIBMStatus();
      }
      
      const token = this.getToken();
      const response = await axios.get(`${API_BASE_URL}/api/ibm/status`, {
        params: token ? { token } : {}
      });
      return response.data;
    } catch (error) {
      console.error('Error getting IBM Quantum status:', error);
      throw error;
    }
  }

  async getBackends(): Promise<{ backends: IBMBackend[]; connected: boolean; count: number }> {
    try {
      if (IS_DEMO_MODE) {
        return await MockApiService.getIBMBackends();
      }
      
      const token = this.getToken();
      const response = await axios.get(`${API_BASE_URL}/api/ibm/backends`, {
        params: token ? { token } : {}
      });
      return response.data;
    } catch (error) {
      console.error('Error getting IBM Quantum backends:', error);
      throw error;
    }
  }

  async executeCircuit(
    circuit: CircuitData,
    backend: string = 'qasm_simulator',
    shots: number = 1024,
    optimizationLevel: number = 1,
    monitor: boolean = true
  ): Promise<IBMExecutionResult> {
    try {
      if (IS_DEMO_MODE) {
        return await MockApiService.executeIBMCircuit(circuit, backend, shots);
      }
      
      const token = this.getToken();
      const response = await axios.post(`${API_BASE_URL}/api/ibm/execute`, {
        circuit,
        backend,
        shots,
        optimization_level: optimizationLevel,
        monitor,
        token
      });
      return response.data;
    } catch (error) {
      console.error('Error executing circuit on IBM Quantum:', error);
      throw error;
    }
  }

  async transpileCircuit(
    circuit: CircuitData,
    backend: string = 'qasm_simulator',
    optimizationLevel: number = 1
  ): Promise<{
    success: boolean;
    original_circuit: any;
    transpiled_circuit: any;
    optimization_level: number;
    backend: string;
    error?: string;
  }> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/ibm/transpile`, {
        circuit,
        backend,
        optimization_level: optimizationLevel
      });
      return response.data;
    } catch (error) {
      console.error('Error transpiling circuit:', error);
      throw error;
    }
  }

  // Helper method to create a simple test circuit
  createTestCircuit(): CircuitData {
    return {
      name: 'test_circuit',
      qubits: 2,
      gates: [
        { type: 'H', qubits: [0] },
        { type: 'CNOT', qubits: [0, 1] }
      ],
      measurements: [
        { qubit: 0, classical_bit: 0 },
        { qubit: 1, classical_bit: 1 }
      ]
    };
  }

  // Helper method to format execution results for display
  formatResults(results: Record<string, number>): Array<{ state: string; count: number; probability: number }> {
    const totalShots = Object.values(results).reduce((sum, count) => sum + count, 0);
    
    return Object.entries(results)
      .map(([state, count]) => ({
        state,
        count,
        probability: count / totalShots
      }))
      .sort((a, b) => b.count - a.count);
  }
}

const ibmQuantumService = new IBMQuantumService();
export default ibmQuantumService; 