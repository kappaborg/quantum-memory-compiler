# Quantum Memory Compiler 🚀

**Advanced Quantum Circuit Compiler with IBM Quantum Integration**

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Demo-blue)](https://USERNAME.github.io/quantum-memory-compiler)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)

## 🌟 Features

### 🔬 **Quantum Circuit Compilation**
- Advanced quantum circuit optimization
- Memory-aware compilation strategies
- GPU-accelerated simulation
- Real-time circuit visualization

### 🌐 **IBM Quantum Integration**
- Direct connection to IBM Quantum Network
- Real hardware execution
- Backend status monitoring
- Token-based authentication

### 💻 **Modern Web Interface**
- React + TypeScript frontend
- Material-UI components
- Real-time WebSocket updates
- Interactive circuit builder

### ⚡ **Performance Optimization**
- GPU acceleration with JAX
- Parallel processing (8 workers)
- Memory optimization (4GB limit)
- JIT compilation with Numba

## 🚀 Live Demo

**Try it now:** [https://USERNAME.github.io/quantum-memory-compiler](https://USERNAME.github.io/quantum-memory-compiler)

*Replace USERNAME with your GitHub username*

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
# Clone the repository
git clone https://github.com/USERNAME/quantum-memory-compiler.git
cd quantum-memory-compiler

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Start API server
python -m quantum_memory_compiler.api --port 5001
```

### Frontend Setup
```bash
# Navigate to React app
cd web_dashboard/quantum-dashboard

# Install dependencies
npm install

# Start development server
npm start
```

## 🔧 Usage

### 1. **Start the Services**
```bash
# Terminal 1 - API Server
python -m quantum_memory_compiler.api --port 5001

# Terminal 2 - Web Dashboard
cd web_dashboard/quantum-dashboard && npm start
```

### 2. **Access the Web Interface**
- Open: http://localhost:3001
- Navigate to "IBM Quantum" page
- Set your IBM Quantum token
- Start building and executing circuits!

### 3. **IBM Quantum Setup**
1. Get your token from [IBM Quantum](https://quantum.ibm.com/)
2. Click "Token Ayarla" in the web interface
3. Paste your token and save
4. Access real quantum backends!

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Web     │    │   Flask API     │    │  IBM Quantum    │
│   Dashboard     │◄──►│    Server       │◄──►│   Network       │
│  (Port 3001)    │    │  (Port 5001)    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Components
- **Frontend**: React + TypeScript + Material-UI
- **Backend**: Flask + SocketIO + Qiskit
- **Integration**: IBM Quantum Runtime
- **Acceleration**: JAX + Numba + GPU

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/info` | GET | API information |
| `/api/circuit/visualize` | POST | Circuit visualization |
| `/api/circuit/simulate` | POST | Circuit simulation |
| `/api/circuit/compile` | POST | Circuit compilation |
| `/api/ibm/status` | GET | IBM Quantum status |
| `/api/ibm/backends` | GET | Available backends |
| `/api/ibm/execute` | POST | Execute on IBM Quantum |

## 🚀 Deployment

### GitHub Pages Deployment
```bash
# Make sure you're on main branch
git checkout main

# Run deployment script
./deploy.sh
```

The script will:
1. Build the React app for production
2. Create/update gh-pages branch
3. Deploy to GitHub Pages
4. Your site will be live at: `https://USERNAME.github.io/REPOSITORY_NAME`

### Manual Deployment
```bash
# Build React app
cd web_dashboard/quantum-dashboard
npm run build

# Deploy build folder to your hosting service
```

## 🔬 Examples

### Bell State Circuit
```python
from quantum_memory_compiler.core.circuit import Circuit
from quantum_memory_compiler.core.gates import HGate, CNOTGate

# Create Bell state
circuit = Circuit(2)
circuit.add_gate(HGate(), 0)
circuit.add_gate(CNOTGate(), 0, 1)

# Visualize and simulate
circuit.visualize()
results = circuit.simulate(shots=1024)
```

### IBM Quantum Execution
```javascript
// Web interface - IBM Quantum execution
const circuit = {
  name: "bell_state",
  qubits: 2,
  gates: [
    { type: "H", qubits: [0] },
    { type: "CNOT", qubits: [0, 1] }
  ]
};

const result = await ibmQuantumService.executeCircuit(
  circuit, 
  "ibm_brisbane", 
  1024
);
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Developer

**kappasutra**
- GitHub: [@kappasutra](https://github.com/kappasutra)
- Quantum Computing Enthusiast
- Full-Stack Developer

## 🙏 Acknowledgments

- IBM Quantum Network for quantum computing access
- Qiskit team for quantum computing framework
- React and Material-UI communities
- Open source quantum computing community

## 📈 Project Stats

- **Languages**: Python, TypeScript, JavaScript
- **Frameworks**: React, Flask, Qiskit
- **Features**: 20+ quantum gates, GPU acceleration, real-time updates
- **Backends**: 3+ simulators, IBM Quantum hardware
- **Performance**: 8-worker parallel processing, 4GB memory optimization

---

**⭐ Star this repository if you find it useful!**

**🚀 Try the live demo:** [https://USERNAME.github.io/quantum-memory-compiler](https://USERNAME.github.io/quantum-memory-compiler) 