# Quantum Memory Compiler

Memory-aware compiler and simulator system for quantum computers to enable more efficient program development.

## 🎯 Overview

Quantum Memory Compiler is a comprehensive tool that optimizes quantum circuits in terms of memory usage and provides simulation, compilation, and visualization features all in one place. With memory hierarchy awareness, qubit recycling, and meta-compiler features, it enables you to create more efficient quantum circuits.

## ✨ Features

- **🧠 Memory-aware compilation**: Optimizes quantum circuits in terms of memory usage
- **♻️ Qubit recycling**: Reuses qubits after quantum states are released
- **🏗️ Memory hierarchy**: Simulates different memory levels with various access times and coherence times
- **🤖 Meta-compiler**: Evaluates various compilation strategies to find the best result
- **📊 Visualization tools**: Visualizes circuits and memory usage
- **🔊 Noise models**: Simulation with realistic noise effects
- **🛠️ Error mitigation**: Implements various error mitigation techniques
- **🖥️ Multi-interface**: CLI, API, Jupyter, VSCode, Cursor extensions, and Web Dashboard

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/kappaborg/quantum_memory_compiler.git
cd quantum_memory_compiler

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install the package
pip install -e .
```

### Run Demo

```bash
# Run comprehensive demo
python demo_presentation.py
```

This demo shows all features and creates visualizations in the `demo_outputs/` directory.

## 📖 Usage

### 🌐 Web Dashboard (NEW!)

```bash
# Start API server
qmc api --port 5000 --debug

# In another terminal, start web dashboard
cd web_dashboard/quantum-dashboard
npm install
npm start
```

Open `http://localhost:3000` for the modern web interface featuring:
- **Interactive Circuit Editor**: Visual quantum gate placement
- **Real-time Monitoring**: System status and statistics
- **Circuit Visualization**: Live circuit diagrams
- **Responsive Design**: Works on desktop, tablet, and mobile

### 🖥️ Command Line Interface (CLI)

```bash
# Show help
qmc --help

# Visualize circuit
qmc visualize circuit.qmc --output circuit.png

# Compile circuit
qmc compile circuit.qmc --output compiled_circuit.qmc --strategy memory

# Simulate circuit
qmc simulate circuit.qmc --shots 1024 --noise --mitigation

# Create memory profile
qmc profile circuit.qmc --output profile.png

# Run examples
qmc examples --list
qmc examples --run bell_state
```

### 🔌 Cursor IDE Extension

```bash
# Install Cursor extension
qmc cursor --install

# Check status
qmc cursor --status
```

### 🌐 API Server

```bash
# Start API server
qmc api --port 5000 --debug
```

### 📓 Jupyter Notebook Integration

```python
# Load magic commands
%load_ext quantum_memory_compiler_magic

# Define circuit
%%qmc_circuit bell_state
from quantum_memory_compiler.core import Circuit, GateType
circuit = Circuit(2)
circuit.add_gate(GateType.H, 0)
circuit.add_gate(GateType.CNOT, [0, 1])

# Simulate
%qmc_simulate bell_state shots=2048 noise=True mitigation=True

# Compile
%qmc_compile bell_state strategy=meta
```

## 🏗️ Architecture Overview

```
📦 Core (Base Components)
├── Circuit: Quantum circuit structure
├── Gate: Quantum gates
├── Qubit: Quantum bits
└── Visualization: Visualization tools

⚙️ Compiler
├── QuantumCompiler: Main compiler
├── Optimizer: Gate optimization
├── Mapper: Physical qubit mapping
└── MetaCompiler: Strategy evaluation

💾 Memory (Memory Management)
├── Hierarchy: Memory level definitions
├── Manager: Qubit allocation and recycling
└── Profiler: Memory usage analysis

🔬 Simulation
├── Simulator: Quantum circuit simulator
├── NoiseModel: Noise modeling
└── ErrorMitigation: Error mitigation

🖥️ Interface
├── CLI: Command line interface
├── API: REST API server
├── Web Dashboard: React-based web interface
├── Jupyter: Notebook integration
└── Cursor: IDE extension
```

## 📚 Examples

The project includes the following example circuits:

- **Bell State**: Basic quantum entanglement example
- **Grover Search**: Quantum search algorithm
- **Quantum Fourier Transform**: QFT implementation
- **Error Mitigation Demo**: Error mitigation techniques

```bash
# Run examples
python -c "from quantum_memory_compiler.examples import bell_state_example; bell_state_example.main()"
python -c "from quantum_memory_compiler.examples import quantum_fourier_transform; quantum_fourier_transform.main()"
```

## 🗺️ Development Roadmap

For detailed information about completed features and future development plans, see our comprehensive [Development Roadmap](ROADMAP.md).

### Current Status (v2.1.0)
- ✅ Core quantum circuit framework
- ✅ Memory-aware compilation system
- ✅ Advanced CLI with rich interface
- ✅ REST API server
- ✅ **Web Dashboard with React + TypeScript** 🆕
- ✅ Jupyter and Cursor IDE integrations
- ✅ Complete English localization

### Upcoming Features
- ⚡ GPU acceleration for simulations
- 🔗 IBM Quantum hardware integration
- 🤖 AI-powered circuit optimization
- 📱 Mobile application
- 🌍 Distributed computing support

## 🛠️ Development

### Running Tests

```bash
# Run all tests
python -m pytest quantum_memory_compiler/tests/

# Run specific test file
python -m pytest quantum_memory_compiler/tests/test_circuit.py
```

### Code Quality

```bash
# Linting
pylint quantum_memory_compiler/

# Formatting
black quantum_memory_compiler/
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

For those who want to contribute, please create a pull request. For major changes, we recommend opening an issue first to discuss.

For detailed contribution guidelines and development roadmap, see [ROADMAP.md](ROADMAP.md).

## 📞 Contact

**Developer:** kappasutra  
**Email:** kappasutra@quantum.dev  
**GitHub:** https://github.com/kappasutra/quantum_memory_compiler

For questions and support, please use GitHub Issues or contact the developer directly. 