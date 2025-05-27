import axios, { AxiosInstance, AxiosResponse } from 'axios';
import envService from './envService';

/**
 * API Service for Quantum Memory Compiler
 * Handles all API communications with automatic fallback to demo mode
 */

interface CircuitData {
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

interface SimulationParams {
  shots?: number;
  noise?: boolean;
  mitigation?: boolean;
  backend?: string;
}

interface CompilationParams {
  strategy?: string;
  use_meta_compiler?: boolean;
}

class ApiServiceClass {
  private axiosInstance: AxiosInstance;
  private baseUrl: string;
  private isDemoMode: boolean;

  constructor() {
    const config = envService.getConfig();
    this.baseUrl = config.apiUrl;
    this.isDemoMode = config.isDemoMode;
    
    this.axiosInstance = axios.create({
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    this.updateBaseUrl();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.axiosInstance.interceptors.request.use(
      (config) => {
        // Skip actual requests in demo mode
        if (this.isDemoMode || this.baseUrl.startsWith('demo://')) {
          console.log('🎭 Demo Mode: Intercepting API request:', config.url);
          return Promise.reject(new Error('DEMO_MODE_INTERCEPT'));
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.message === 'DEMO_MODE_INTERCEPT') {
          // Return demo response
          return this.getDemoResponse(error.config);
        }
        
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  private getDemoResponse(config: any): Promise<AxiosResponse> {
    const url = config.url || '';
    const method = config.method || 'get';
    
    // Simulate network delay
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          data: this.generateDemoData(url, method, config.data),
          status: 200,
          statusText: 'OK',
          headers: {},
          config,
        } as AxiosResponse);
      }, 300 + Math.random() * 700); // 300-1000ms delay
    });
  }

  private generateDemoData(url: string, method: string, requestData?: any): any {
    if (url.includes('/api/info')) {
      return {
        success: true,
        name: 'Quantum Memory Compiler API (Demo)',
        version: '2.2.0',
        system_info: {
          platform: 'Demo Environment',
          python_version: '3.9.0',
          memory: '4.0 GB'
        },
        gpu_support: true,
        endpoints: ['simulation', 'compilation', 'visualization', 'ibm_quantum']
      };
    }

    if (url.includes('/api/circuit/simulate')) {
      const shots = requestData?.shots || 1024;
      return {
        success: true,
        results: {
          '00': Math.floor(shots * 0.5 + Math.random() * shots * 0.1),
          '01': Math.floor(shots * 0.1 + Math.random() * shots * 0.1),
          '10': Math.floor(shots * 0.1 + Math.random() * shots * 0.1),
          '11': Math.floor(shots * 0.3 + Math.random() * shots * 0.1)
        },
        execution_time: 0.1 + Math.random() * 0.5,
        shots,
        backend: 'demo_simulator'
      };
    }

    if (url.includes('/api/circuit/compile')) {
      return {
        success: true,
        compiled_circuit: {
          name: 'Compiled Circuit (Demo)',
          qubits: requestData?.circuit?.qubits || 2,
          gates: requestData?.circuit?.gates || []
        },
        metrics: {
          original_qubits: requestData?.circuit?.qubits || 2,
          compiled_qubits: requestData?.circuit?.qubits || 2,
          original_gates: requestData?.circuit?.gates?.length || 0,
          compiled_gates: Math.max(1, (requestData?.circuit?.gates?.length || 0) - 1),
          original_depth: requestData?.circuit?.gates?.length || 0,
          compiled_depth: Math.max(1, (requestData?.circuit?.gates?.length || 0) - 1),
          strategy: requestData?.strategy || 'demo',
          meta_compiler_used: requestData?.use_meta_compiler || false
        },
        execution_time: 0.2 + Math.random() * 0.3
      };
    }

    if (url.includes('/api/circuit/visualize')) {
      return {
        success: true,
        image: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
        message: 'Demo visualization generated'
      };
    }

    if (url.includes('/api/health')) {
      return {
        success: true,
        status: 'healthy',
        timestamp: new Date().toISOString()
      };
    }

    // Default demo response
    return {
      success: true,
      message: 'Demo mode response',
      data: {}
    };
  }

  public setBaseUrl(url: string): void {
    this.baseUrl = url;
    this.isDemoMode = url.startsWith('demo://') || envService.isDemoMode();
    this.updateBaseUrl();
  }

  private updateBaseUrl(): void {
    if (!this.isDemoMode && !this.baseUrl.startsWith('demo://')) {
      this.axiosInstance.defaults.baseURL = this.baseUrl;
    }
  }

  // Health check
  public async healthCheck(): Promise<boolean> {
    try {
      const response = await this.axiosInstance.get('/api/health');
      return response.data.success === true;
    } catch (error) {
      console.log('Health check failed, using demo mode');
      return this.isDemoMode; // Return true in demo mode
    }
  }

  // Get API info
  public async getApiInfo(): Promise<any> {
    try {
      const response = await this.axiosInstance.get('/api/info');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get API info');
    }
  }

  // Circuit simulation
  public async simulateCircuit(circuit: CircuitData, params: SimulationParams = {}): Promise<any> {
    try {
      const response = await this.axiosInstance.post('/api/circuit/simulate', {
        circuit,
        ...params
      });
      return response.data;
    } catch (error) {
      throw new Error('Simulation failed');
    }
  }

  // Circuit compilation
  public async compileCircuit(circuit: CircuitData, params: CompilationParams = {}): Promise<any> {
    try {
      const response = await this.axiosInstance.post('/api/circuit/compile', {
        circuit,
        ...params
      });
      return response.data;
    } catch (error) {
      throw new Error('Compilation failed');
    }
  }

  // Circuit visualization
  public async visualizeCircuit(circuit: CircuitData, format: string = 'base64'): Promise<any> {
    try {
      const response = await this.axiosInstance.post('/api/circuit/visualize', {
        circuit,
        format
      });
      return response.data;
    } catch (error) {
      throw new Error('Visualization failed');
    }
  }

  // Circuit upload
  public async uploadCircuit(file: File): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await this.axiosInstance.post('/api/circuit/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error('Upload failed');
    }
  }

  // Circuit download
  public async downloadCircuit(circuit: CircuitData, format: string): Promise<any> {
    try {
      const response = await this.axiosInstance.post('/api/circuit/download', {
        circuit,
        format
      });
      return response.data;
    } catch (error) {
      throw new Error('Download failed');
    }
  }

  // IBM Quantum status
  public async getIBMQuantumStatus(): Promise<any> {
    try {
      const response = await this.axiosInstance.get('/api/ibm/status');
      return response.data;
    } catch (error) {
      throw new Error('IBM Quantum status check failed');
    }
  }

  // IBM Quantum backends
  public async getIBMQuantumBackends(): Promise<any> {
    try {
      const response = await this.axiosInstance.get('/api/ibm/backends');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get IBM Quantum backends');
    }
  }

  // IBM Quantum execution
  public async executeOnIBMQuantum(circuit: CircuitData, backend: string, shots: number): Promise<any> {
    try {
      const response = await this.axiosInstance.post('/api/ibm/execute', {
        circuit,
        backend,
        shots
      });
      return response.data;
    } catch (error) {
      throw new Error('IBM Quantum execution failed');
    }
  }

  // GPU acceleration status
  public async getGPUStatus(): Promise<any> {
    try {
      const response = await this.axiosInstance.get('/api/gpu/status');
      return response.data;
    } catch (error) {
      throw new Error('GPU status check failed');
    }
  }

  // Memory profiling
  public async getMemoryProfile(): Promise<any> {
    try {
      const response = await this.axiosInstance.get('/api/memory/profile');
      return response.data;
    } catch (error) {
      throw new Error('Memory profiling failed');
    }
  }

  // Cache management
  public async clearCache(): Promise<any> {
    try {
      const response = await this.axiosInstance.delete('/api/cache/clear');
      return response.data;
    } catch (error) {
      throw new Error('Cache clear failed');
    }
  }

  // Get cache status
  public async getCacheStatus(): Promise<any> {
    try {
      const response = await this.axiosInstance.get('/api/cache/status');
      return response.data;
    } catch (error) {
      throw new Error('Cache status check failed');
    }
  }
}

// Create singleton instance
export const ApiService = new ApiServiceClass();

// Export for React components
export default ApiService; 