# Quantum Memory Compiler CLI Usage Guide

## Installation

Ensure you have Python 3.7+ installed. Then install the package:

```bash
pip install -e .
```

## Basic Usage

The Quantum Memory Compiler comes with a command-line interface (CLI) tool called `qmc`. Here are the available commands:

### Compiling a Circuit

```bash
qmc compile sample_circuit.json --output compiled_circuit.json --memory_config memory_config.json --verbose
```

### Visualizing a Circuit

```bash
qmc visualize sample_circuit.json --output circuit_visualization.png --memory
```

### Simulating a Circuit

```bash
qmc simulate sample_circuit.json --shots 1024 --output simulation_results.json
```

### Profiling Memory Usage

```bash
qmc profile sample_circuit.json --output memory_profile.png
```

### Memory Management

```bash
qmc memory --config memory_config.json --visualize --output memory_hierarchy.png
```

### List and Run Examples

```bash
qmc examples --list
qmc examples --run bell_state
```

## Project Structure

The project is organized into the following modules:

- **core/**: Contains fundamental quantum computing constructs
  - `circuit.py`: Circuit representation
  - `gate.py`: Quantum gates
  - `qubit.py`: Qubit abstraction
  - `visualization.py`: Circuit visualization tools

- **compiler/**: Memory-aware compilation components
  - `compiler.py`: Main compiler class
  - `optimizer.py`: Gate optimization
  - `mapper.py`: Qubit mapping
  - `scheduler.py`: Gate scheduling

- **memory/**: Memory management functionality  
  - `hierarchy.py`: Memory hierarchy
  - `manager.py`: Memory manager
  - `allocation.py`: Qubit allocation
  - `recycling.py`: Qubit recycling
  - `profiler.py`: Memory profiling

- **simulation/**: Quantum circuit simulation
  - `simulator.py`: Circuit simulator
  - `noise_model.py`: Noise models

## Running Tests

To run tests:

```bash
# Run all tests
pytest

# Run specific test file
pytest quantum_memory_compiler/tests/test_circuit.py

# Run with verbose output
pytest -v
```

## Typical Usage Patterns

### Compile-Simulate Workflow

1. Create a circuit or use a sample circuit
2. Compile the circuit with memory optimizations:
   ```bash
   qmc compile my_circuit.json --output compiled.json --memory_config memory_config.json --verbose
   ```
3. Simulate the compiled circuit:
   ```bash
   qmc simulate compiled.json --shots 1000 --output results.json
   ```
4. Analyze the results

### Memory Profiling Workflow

1. Profile your circuit's memory usage:
   ```bash
   qmc profile my_circuit.json --output memory_profile.png
   ```
2. Identify memory bottlenecks
3. Adjust your circuit design or memory configuration
4. Recompile and profile again to see improvements

## Circuit File Format

Circuit files should be in JSON format as follows:

```json
{
  "name": "Circuit Name",
  "qubits": 2,
  "gates": [
    {
      "type": "H",
      "qubits": [0],
      "params": []
    },
    {
      "type": "CNOT",
      "qubits": [0, 1],
      "params": []
    }
  ],
  "measurements": [
    {
      "qubit": 0,
      "register": "c",
      "bit": 0
    },
    {
      "qubit": 1,
      "register": "c",
      "bit": 1
    }
  ]
}
```

## Memory Configuration Format

Memory configuration files should be in JSON format as follows:

```json
{
  "hierarchy": {
    "levels": [
      {
        "name": "fast_memory",
        "capacity": 10,
        "access_time": 1,
        "error_rate": 0.001
      },
      {
        "name": "slow_memory",
        "capacity": 50,
        "access_time": 10,
        "error_rate": 0.01
      }
    ]
  },
  "allocation_strategy": "lifetime",
  "recycling_strategy": "reset_based",
  "optimization_level": 2
}
``` 