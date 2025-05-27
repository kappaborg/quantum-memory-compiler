/**
 * Real API Service for Quantum Memory Compiler
 * Connects to the actual backend API server
 */

export interface Circuit {
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

export interface SimulationParams {
  shots?: number;
  noise?: boolean;
  mitigation?: boolean;
  backend?: string;
}

export interface CompilationParams {
  strategy?: string;
  use_meta_compiler?: boolean;
}

export class ApiService {
  private static baseUrl = 'http://localhost:5001/api';
  
  private static async request(endpoint: string, options: RequestInit = {}): Promise<any> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };
    
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
  }

  static async getApiInfo(): Promise<any> {
    return this.request('/info');
  }

  static async visualizeCircuit(circuit: Circuit, format: string = 'base64'): Promise<any> {
    return this.request('/circuit/visualize', {
      method: 'POST',
      body: JSON.stringify({
        circuit,
        format
      }),
    });
  }

  static async simulateCircuit(circuit: Circuit, params: SimulationParams = {}): Promise<any> {
    return this.request('/circuit/simulate', {
      method: 'POST',
      body: JSON.stringify({
        circuit,
        shots: params.shots || 1024,
        noise: params.noise || false,
        mitigation: params.mitigation || false
      }),
    });
  }

  static async compileCircuit(circuit: Circuit, params: CompilationParams = {}): Promise<any> {
    return this.request('/circuit/compile', {
      method: 'POST',
      body: JSON.stringify({
        circuit,
        strategy: params.strategy || 'balanced',
        use_meta_compiler: params.use_meta_compiler || false
      }),
    });
  }

  static async profileMemory(circuit: Circuit): Promise<any> {
    return this.request('/memory/profile', {
      method: 'POST',
      body: JSON.stringify({
        circuit
      }),
    });
  }

  static async getExamples(): Promise<any> {
    return this.request('/examples');
  }

  static async uploadCircuit(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.request('/circuit/upload', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set Content-Type for FormData
    });
  }

  static async downloadCircuit(circuit: Circuit, format: string = 'json', filename?: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/circuit/download`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        circuit,
        format,
        filename: filename || 'quantum_circuit'
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Download failed: ${response.status} ${response.statusText}`);
    }
    
    return response.blob();
  }

  // IBM Quantum Integration
  static async getIBMStatus(token?: string): Promise<any> {
    const params = token ? `?token=${encodeURIComponent(token)}` : '';
    return this.request(`/ibm/status${params}`);
  }

  static async getIBMBackends(token?: string): Promise<any> {
    const params = token ? `?token=${encodeURIComponent(token)}` : '';
    return this.request(`/ibm/backends${params}`);
  }

  static async executeIBMCircuit(
    circuit: Circuit, 
    backend: string, 
    shots: number = 1024,
    token?: string
  ): Promise<any> {
    return this.request('/ibm/execute', {
      method: 'POST',
      body: JSON.stringify({
        circuit,
        backend,
        shots,
        token
      }),
    });
  }

  static async transpileIBMCircuit(
    circuit: Circuit, 
    backend: string,
    optimization_level: number = 1,
    token?: string
  ): Promise<any> {
    return this.request('/ibm/transpile', {
      method: 'POST',
      body: JSON.stringify({
        circuit,
        backend,
        optimization_level,
        token
      }),
    });
  }

  // GPU Acceleration
  static async getAccelerationStatus(): Promise<any> {
    return this.request('/acceleration/status');
  }

  static async analyzeCircuitAcceleration(circuit: Circuit): Promise<any> {
    return this.request('/acceleration/analyze', {
      method: 'POST',
      body: JSON.stringify({
        circuit
      }),
    });
  }

  static async runAcceleratedSimulation(
    circuit: Circuit, 
    shots: number = 1024,
    method: string = 'auto',
    optimize_memory: boolean = true
  ): Promise<any> {
    return this.request('/acceleration/simulate', {
      method: 'POST',
      body: JSON.stringify({
        circuit,
        shots,
        method,
        optimize_memory
      }),
    });
  }

  static async runAccelerationBenchmark(
    qubit_range: number[] = [4, 6],
    gate_counts: number[] = [50, 100],
    shots: number = 100
  ): Promise<any> {
    return this.request('/acceleration/benchmark', {
      method: 'POST',
      body: JSON.stringify({
        qubit_range,
        gate_counts,
        shots
      }),
    });
  }

  static async getMemoryReport(): Promise<any> {
    return this.request('/acceleration/memory/report');
  }

  static async cleanupMemory(force_gc: boolean = true): Promise<any> {
    return this.request('/acceleration/memory/cleanup', {
      method: 'POST',
      body: JSON.stringify({
        force_gc
      }),
    });
  }

  // Cache Management
  static async getCacheStats(): Promise<any> {
    return this.request('/cache/stats');
  }

  static async clearCache(cache_type?: string): Promise<any> {
    return this.request('/cache/clear', {
      method: 'POST',
      body: JSON.stringify({
        cache_type
      }),
    });
  }

  static async cleanupCache(): Promise<any> {
    return this.request('/cache/cleanup', {
      method: 'POST',
    });
  }

  // Health Check
  static async healthCheck(): Promise<boolean> {
    try {
      await this.getApiInfo();
      return true;
    } catch (error) {
      console.error('API health check failed:', error);
      return false;
    }
  }

  // Set API base URL (for different environments)
  static setBaseUrl(url: string): void {
    this.baseUrl = url.endsWith('/api') ? url : `${url}/api`;
  }
} 