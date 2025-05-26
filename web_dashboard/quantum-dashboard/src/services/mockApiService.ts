/**
 * Mock API Service for Demo Mode
 * Provides simulated responses when real API is not available
 */

export interface MockCircuit {
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

export class MockApiService {
  private static delay(ms: number = 1000): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  static async visualizeCircuit(circuit: MockCircuit): Promise<{ success: boolean; message: string }> {
    await this.delay(1500);
    return {
      success: true,
      message: "🎨 Demo Mode: Circuit visualization would be generated here. In the full version, this creates a visual diagram of your quantum circuit."
    };
  }

  static async simulateCircuit(circuit: MockCircuit, params: any): Promise<any> {
    await this.delay(2000);
    
    // Generate mock simulation results
    const shots = params.shots || 1024;
    const numQubits = circuit.qubits;
    const numStates = Math.pow(2, numQubits);
    
    // Create realistic-looking results
    const results: Record<string, number> = {};
    
    if (circuit.gates.some(g => g.type === 'H' || g.type === 'CNOT')) {
      // Bell state or superposition-like results
      const state1 = '0'.repeat(numQubits);
      const state2 = '1'.repeat(numQubits);
      results[state1] = Math.floor(shots * 0.5 + (Math.random() - 0.5) * 100);
      results[state2] = shots - results[state1];
    } else {
      // Random distribution
      for (let i = 0; i < Math.min(numStates, 4); i++) {
        const state = i.toString(2).padStart(numQubits, '0');
        results[state] = Math.floor(Math.random() * shots / 4);
      }
      // Normalize to total shots
      const total = Object.values(results).reduce((sum, count) => sum + count, 0);
      const factor = shots / total;
      Object.keys(results).forEach(state => {
        results[state] = Math.floor(results[state] * factor);
      });
    }

    return {
      success: true,
      results,
      execution_time: 0.123 + Math.random() * 0.5,
      shots,
      backend: params.backend || 'demo_simulator',
      statevector: null,
      probabilities: Object.fromEntries(
        Object.entries(results).map(([state, count]) => [state, count / shots])
      ),
      fidelity: 0.95 + Math.random() * 0.05
    };
  }

  static async compileCircuit(circuit: MockCircuit, params: any): Promise<any> {
    await this.delay(1800);
    
    const originalGates = circuit.gates.length;
    const optimizedGates = Math.max(1, originalGates - Math.floor(Math.random() * 3));
    const originalDepth = Math.ceil(originalGates / 2);
    const optimizedDepth = Math.max(1, originalDepth - Math.floor(Math.random() * 2));
    
    return {
      success: true,
      compiled_circuit: {
        ...circuit,
        name: `${circuit.name} (Compiled)`,
        gates: circuit.gates.slice(0, optimizedGates) // Simulate optimization
      },
      metrics: {
        original_qubits: circuit.qubits,
        compiled_qubits: circuit.qubits,
        original_gates: originalGates,
        compiled_gates: optimizedGates,
        original_depth: originalDepth,
        compiled_depth: optimizedDepth,
        strategy: params.strategy || 'demo',
        meta_compiler_used: params.use_meta_compiler || false
      },
      execution_time: 0.234 + Math.random() * 0.3
    };
  }

  static async getIBMStatus(): Promise<any> {
    await this.delay(500);
    return {
      integration_ready: false,
      qiskit_available: true,
      token_provided: false,
      backends_available: 0,
      message: "🚀 Demo Mode: IBM Quantum integration is available in the full version. Please run the API server locally to connect with your IBM Quantum token."
    };
  }

  static async getIBMBackends(): Promise<any> {
    await this.delay(800);
    return {
      backends: [
        {
          name: "demo_simulator",
          type: "simulator",
          num_qubits: 32,
          coupling_map: [],
          basis_gates: ["cx", "id", "rz", "sx", "x"],
          max_shots: 8192,
          simulator: true,
          operational: true,
          pending_jobs: 0,
          least_busy: true
        }
      ],
      connected: false,
      count: 1
    };
  }

  static async executeIBMCircuit(circuit: MockCircuit, backend: string, shots: number): Promise<any> {
    await this.delay(3000); // Longer delay to simulate real quantum execution
    
    // Generate realistic quantum results
    const results: Record<string, number> = {};
    
    if (circuit.gates.some(g => g.type === 'H') && circuit.gates.some(g => g.type === 'CNOT')) {
      // Bell state results
      results['00'] = Math.floor(shots * 0.5 + (Math.random() - 0.5) * 50);
      results['11'] = shots - results['00'];
    } else if (circuit.gates.some(g => g.type === 'H')) {
      // Superposition
      results['0'] = Math.floor(shots * 0.5 + (Math.random() - 0.5) * 30);
      results['1'] = shots - results['0'];
    } else {
      // Default distribution
      results['00'] = Math.floor(shots * 0.7);
      results['01'] = Math.floor(shots * 0.1);
      results['10'] = Math.floor(shots * 0.1);
      results['11'] = shots - results['00'] - results['01'] - results['10'];
    }

    return {
      success: true,
      job_id: `demo_job_${Date.now()}`,
      status: 'COMPLETED',
      backend: backend,
      shots: shots,
      results: results,
      execution_time: 2.5 + Math.random() * 1.5,
      queue_time: 0.1 + Math.random() * 0.5,
      error_message: null
    };
  }
} 