"""
Quantum Memory Compiler Magic Commands for Jupyter Notebook
===========================================================

This module provides Jupyter magic commands to interact with
Quantum Memory Compiler directly from Jupyter notebooks.

Developer: kappasutra

Usage:
    %load_ext quantum_memory_compiler_magic
    
    %qmc_version
    
    %%qmc_circuit
    # circuit code here
    
    %qmc_visualize circuit_name
    
    %qmc_simulate circuit_name
    
    %qmc_compile circuit_name
    
    %qmc_profile circuit_name
    
    %qmc_list
"""

import os
import sys
import json
import tempfile
import IPython
import IPython.display
from IPython.core.magic import Magics, magics_class, line_magic, cell_magic, line_cell_magic
from IPython.display import display, HTML, Image

# Try to import the library, warn if not available
try:
    import quantum_memory_compiler as qmc
    from quantum_memory_compiler.core import Circuit
    from quantum_memory_compiler.core.visualization import CircuitVisualizer
    from quantum_memory_compiler.simulation.simulator import Simulator
    from quantum_memory_compiler.compiler.compiler import QuantumCompiler
    from quantum_memory_compiler.memory.profiler import MemoryProfiler
    HAS_QMC = True
except ImportError:
    HAS_QMC = False
    

@magics_class
class QuantumMemoryCompilerMagics(Magics):
    """Jupyter magic commands for Quantum Memory Compiler"""
    
    def __init__(self, shell):
        """Initialize magic commands"""
        super(QuantumMemoryCompilerMagics, self).__init__(shell)
        self.circuits = {}  # Stored circuits
        
        # Check if QMC is loaded
        if not HAS_QMC:
            print("⚠️  Warning: quantum_memory_compiler library not installed.")
            print("   Install with: pip install quantum_memory_compiler")
        else:
            print("🚀 Quantum Memory Compiler Jupyter Extension loaded")
            print("   Developer: kappasutra")
    
    @line_magic
    def qmc_version(self, line):
        """Show Quantum Memory Compiler version"""
        if not HAS_QMC:
            return "❌ quantum_memory_compiler library not installed."
        
        return f"✅ Quantum Memory Compiler version: 2.1.0 | Developer: kappasutra"
    
    @cell_magic
    def qmc_circuit(self, line, cell):
        """
        Define and save a quantum circuit
        
        Usage:
            %%qmc_circuit [circuit_name]
            # Python code
        """
        if not HAS_QMC:
            return "❌ quantum_memory_compiler library not installed."
        
        # Get circuit name
        circuit_name = line.strip() or f"circuit_{len(self.circuits) + 1}"
        
        # Evaluate cell code
        local_ns = {}
        
        try:
            # Execute code
            exec(cell, self.shell.user_ns, local_ns)
            
            # Find Circuit object
            circuit = None
            for obj in local_ns.values():
                if isinstance(obj, Circuit):
                    circuit = obj
                    break
            
            if circuit is None:
                return "❌ Error: No Circuit object found in cell."
            
            # Save circuit
            self.circuits[circuit_name] = circuit
            
            # Show summary
            print(f"✅ Circuit '{circuit_name}' saved:")
            print(f"   • Width: {circuit.width} qubits")
            print(f"   • Gates: {len(circuit.gates)}")
            print(f"   • Developer: kappasutra")
            
            # Show circuit visualization
            visualizer = CircuitVisualizer()
            img_path = tempfile.NamedTemporaryFile(suffix='.png', delete=False).name
            visualizer.visualize_circuit(circuit, filename=img_path)
            
            display(Image(filename=img_path))
            os.remove(img_path)
            
            return None
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    @line_magic
    def qmc_visualize(self, line):
        """
        Visualize a saved circuit
        
        Usage:
            %qmc_visualize circuit_name
        """
        if not HAS_QMC:
            return "❌ quantum_memory_compiler library not installed."
        
        try:
            # Get circuit name
            circuit_name = line.strip()
            if not circuit_name:
                return "❌ Error: Circuit name not specified."
            
            # Find circuit
            if circuit_name not in self.circuits:
                return f"❌ Error: Circuit '{circuit_name}' not found."
            
            circuit = self.circuits[circuit_name]
            
            # Visualize
            print(f"🎨 Visualizing circuit '{circuit_name}'...")
            visualizer = CircuitVisualizer()
            img_path = tempfile.NamedTemporaryFile(suffix='.png', delete=False).name
            visualizer.visualize_circuit(circuit, filename=img_path)
            
            display(Image(filename=img_path))
            os.remove(img_path)
            
            return None
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    @line_magic
    def qmc_simulate(self, line):
        """
        Simulate a saved circuit
        
        Usage:
            %qmc_simulate circuit_name [shots=1024] [noise=True|False] [mitigation=True|False]
        """
        if not HAS_QMC:
            return "❌ quantum_memory_compiler library not installed."
        
        try:
            # Parse parameters
            args = line.split()
            if not args:
                return "❌ Error: Circuit name not specified."
            
            circuit_name = args[0]
            
            # Default values
            shots = 1024
            use_noise = False
            use_mitigation = False
            
            # Parameter parsing
            for arg in args[1:]:
                if arg.startswith("shots="):
                    shots = int(arg.split("=")[1])
                elif arg.startswith("noise="):
                    use_noise = arg.split("=")[1].lower() == "true"
                elif arg.startswith("mitigation="):
                    use_mitigation = arg.split("=")[1].lower() == "true"
            
            # Find circuit
            if circuit_name not in self.circuits:
                return f"❌ Error: Circuit '{circuit_name}' not found."
            
            circuit = self.circuits[circuit_name]
            
            # Simulate
            print(f"🔬 Simulating circuit '{circuit_name}'...")
            print(f"   • Shots: {shots}")
            print(f"   • Noise model: {'On' if use_noise else 'Off'}")
            print(f"   • Error mitigation: {'On' if use_mitigation else 'Off'}")
            print(f"   • Developer: kappasutra")
            
            # Noise model
            noise_model = None
            if use_noise:
                from quantum_memory_compiler.simulation.noise_model import NoiseModel
                noise_model = NoiseModel()
            
            # Simulator
            simulator = Simulator(noise_model=noise_model, enable_error_mitigation=use_mitigation)
            results = simulator.run(circuit, shots=shots)
            
            # Show results as table
            html = f"""
            <div style="margin-top: 20px; margin-bottom: 20px; font-family: Arial, sans-serif;">
                <h3 style="color: #2E86AB;">🔬 Simulation Results</h3>
                <p style="color: #666; font-size: 12px;">Developer: kappasutra</p>
                <table style="width: 60%; border-collapse: collapse; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <tr style="background-color: #2E86AB; color: white;">
                        <th style="padding: 12px; border: 1px solid #ddd;">Measurement Result</th>
                        <th style="padding: 12px; border: 1px solid #ddd;">Probability</th>
                        <th style="padding: 12px; border: 1px solid #ddd;">Counts</th>
                    </tr>
            """
            
            for bitstring, probability in sorted(results.items(), key=lambda x: -x[1]):
                counts = int(probability * shots)
                html += f"""
                    <tr style="background-color: {'#f8f9fa' if len(html.split('<tr>')) % 2 == 0 else 'white'};">
                        <td style="padding: 10px; border: 1px solid #ddd; font-family: monospace;">|{bitstring}⟩</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{probability:.4f}</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{counts}</td>
                    </tr>
                """
            
            html += """
                </table>
            </div>
            """
            
            display(HTML(html))
            
            return None
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    @line_magic
    def qmc_compile(self, line):
        """
        Compile a saved circuit
        
        Usage:
            %qmc_compile circuit_name [strategy=memory|balanced|meta]
        """
        if not HAS_QMC:
            return "❌ quantum_memory_compiler library not installed."
        
        try:
            # Parse parameters
            args = line.split()
            if not args:
                return "❌ Error: Circuit name not specified."
            
            circuit_name = args[0]
            
            # Default values
            strategy = "balanced"
            
            # Parameter parsing
            for arg in args[1:]:
                if arg.startswith("strategy="):
                    strategy = arg.split("=")[1].lower()
            
            # Find circuit
            if circuit_name not in self.circuits:
                return f"❌ Error: Circuit '{circuit_name}' not found."
            
            circuit = self.circuits[circuit_name]
            
            print(f"⚙️ Compiling circuit '{circuit_name}'...")
            print(f"   • Strategy: {strategy}")
            print(f"   • Developer: kappasutra")
            
            # Create memory hierarchy
            from quantum_memory_compiler.memory.hierarchy import MemoryHierarchy
            memory = MemoryHierarchy(l1_capacity=10, l2_capacity=20, l3_capacity=50)
            
            # Compiler
            if strategy == "meta":
                try:
                    from quantum_memory_compiler.compiler.meta_compiler import MetaCompiler
                    compiler = MetaCompiler(memory)
                    compiled_circuit = compiler.compile(circuit)
                    
                    print(f"   • Best strategy found: {getattr(compiler, 'best_strategy', 'Unknown')}")
                except ImportError:
                    print("   ⚠️ MetaCompiler not available, using balanced strategy")
                    compiler = QuantumCompiler(memory)
                    compiled_circuit = compiler.compile(circuit)
            else:
                compiler = QuantumCompiler(memory)
                compiled_circuit = compiler.compile(circuit)
            
            # Save result as new circuit
            compiled_name = f"{circuit_name}_compiled"
            self.circuits[compiled_name] = compiled_circuit
            
            print(f"✅ Circuit saved as '{compiled_name}':")
            print(f"   • Original qubits: {circuit.width} → Compiled: {compiled_circuit.width}")
            print(f"   • Original gates: {len(circuit.gates)} → Compiled: {len(compiled_circuit.gates)}")
            
            # Visualize
            visualizer = CircuitVisualizer()
            img_path = tempfile.NamedTemporaryFile(suffix='.png', delete=False).name
            visualizer.visualize_circuit(compiled_circuit, filename=img_path)
            
            display(Image(filename=img_path))
            os.remove(img_path)
            
            return None
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    @line_magic
    def qmc_profile(self, line):
        """
        Profile memory usage of a saved circuit
        
        Usage:
            %qmc_profile circuit_name
        """
        if not HAS_QMC:
            return "❌ quantum_memory_compiler library not installed."
        
        try:
            # Get circuit name
            circuit_name = line.strip()
            if not circuit_name:
                return "❌ Error: Circuit name not specified."
            
            # Find circuit
            if circuit_name not in self.circuits:
                return f"❌ Error: Circuit '{circuit_name}' not found."
            
            circuit = self.circuits[circuit_name]
            
            # Profile
            print(f"💾 Profiling circuit '{circuit_name}'...")
            print(f"   • Developer: kappasutra")
            
            profiler = MemoryProfiler()
            profile = profiler.profile_circuit_execution(circuit)
            
            # Show results
            html = f"""
            <div style="margin-top: 20px; margin-bottom: 20px; font-family: Arial, sans-serif;">
                <h3 style="color: #2E86AB;">💾 Memory Profile Results</h3>
                <p style="color: #666; font-size: 12px;">Developer: kappasutra</p>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #2E86AB;">
                    <p><strong>Circuit:</strong> {circuit_name}</p>
                    <p><strong>Total Qubits:</strong> {sum(profile.qubit_counts.values())}</p>
                    <p><strong>Average Qubit Lifetime:</strong> {profile.get_average_qubit_lifetime():.2f} time units</p>
                    <p><strong>Memory Usage Stats:</strong> {profile.get_memory_usage_stats()}</p>
                </div>
            </div>
            """
            
            display(HTML(html))
            
            # Create profile visualization
            try:
                from io import BytesIO
                import base64
                
                img_buf = BytesIO()
                profile.plot_memory_profile(img_buf)
                img_buf.seek(0)
                
                # Display the image
                display(Image(data=img_buf.read()))
            except Exception as viz_error:
                print(f"   ⚠️ Visualization error: {viz_error}")
            
            return None
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    @line_magic
    def qmc_list(self, line):
        """List saved circuits"""
        if not self.circuits:
            return "📋 No saved circuits."
        
        html = f"""
        <div style="margin-top: 20px; margin-bottom: 20px; font-family: Arial, sans-serif;">
            <h3 style="color: #2E86AB;">📋 Saved Circuits</h3>
            <p style="color: #666; font-size: 12px;">Developer: kappasutra</p>
            <table style="width: 80%; border-collapse: collapse; text-align: left; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <tr style="background-color: #2E86AB; color: white;">
                    <th style="padding: 12px; border: 1px solid #ddd;">Circuit Name</th>
                    <th style="padding: 12px; border: 1px solid #ddd;">Qubits</th>
                    <th style="padding: 12px; border: 1px solid #ddd;">Gates</th>
                    <th style="padding: 12px; border: 1px solid #ddd;">Depth</th>
                </tr>
        """
        
        for i, (name, circuit) in enumerate(self.circuits.items()):
            bg_color = "#f8f9fa" if i % 2 == 0 else "white"
            html += f"""
                <tr style="background-color: {bg_color};">
                    <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">{name}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{circuit.width}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{len(circuit.gates)}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{circuit.depth}</td>
                </tr>
            """
        
        html += """
            </table>
        </div>
        """
        
        display(HTML(html))
        
        return None
    
    @line_magic
    def qmc_help(self, line):
        """Show help for Quantum Memory Compiler magic commands"""
        help_html = """
        <div style="margin-top: 20px; margin-bottom: 20px; font-family: Arial, sans-serif;">
            <h2 style="color: #2E86AB;">🚀 Quantum Memory Compiler Magic Commands</h2>
            <p style="color: #666; font-size: 14px;"><strong>Developer:</strong> kappasutra</p>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 15px 0;">
                <h3 style="color: #2E86AB; margin-top: 0;">Available Commands:</h3>
                
                <div style="margin: 15px 0;">
                    <code style="background-color: #e9ecef; padding: 2px 6px; border-radius: 3px;">%qmc_version</code>
                    <p style="margin: 5px 0 15px 20px; color: #666;">Show version information</p>
                </div>
                
                <div style="margin: 15px 0;">
                    <code style="background-color: #e9ecef; padding: 2px 6px; border-radius: 3px;">%%qmc_circuit [name]</code>
                    <p style="margin: 5px 0 15px 20px; color: #666;">Define and save a quantum circuit</p>
                </div>
                
                <div style="margin: 15px 0;">
                    <code style="background-color: #e9ecef; padding: 2px 6px; border-radius: 3px;">%qmc_visualize circuit_name</code>
                    <p style="margin: 5px 0 15px 20px; color: #666;">Visualize a saved circuit</p>
                </div>
                
                <div style="margin: 15px 0;">
                    <code style="background-color: #e9ecef; padding: 2px 6px; border-radius: 3px;">%qmc_simulate circuit_name [shots=1024] [noise=True|False]</code>
                    <p style="margin: 5px 0 15px 20px; color: #666;">Simulate a quantum circuit</p>
                </div>
                
                <div style="margin: 15px 0;">
                    <code style="background-color: #e9ecef; padding: 2px 6px; border-radius: 3px;">%qmc_compile circuit_name [strategy=balanced|memory|meta]</code>
                    <p style="margin: 5px 0 15px 20px; color: #666;">Compile and optimize a circuit</p>
                </div>
                
                <div style="margin: 15px 0;">
                    <code style="background-color: #e9ecef; padding: 2px 6px; border-radius: 3px;">%qmc_profile circuit_name</code>
                    <p style="margin: 5px 0 15px 20px; color: #666;">Profile memory usage of a circuit</p>
                </div>
                
                <div style="margin: 15px 0;">
                    <code style="background-color: #e9ecef; padding: 2px 6px; border-radius: 3px;">%qmc_list</code>
                    <p style="margin: 5px 0 15px 20px; color: #666;">List all saved circuits</p>
                </div>
                
                <div style="margin: 15px 0;">
                    <code style="background-color: #e9ecef; padding: 2px 6px; border-radius: 3px;">%qmc_help</code>
                    <p style="margin: 5px 0 15px 20px; color: #666;">Show this help message</p>
                </div>
            </div>
            
            <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; border-left: 4px solid #2196f3;">
                <h4 style="margin-top: 0; color: #1976d2;">Example Usage:</h4>
                <pre style="background-color: white; padding: 10px; border-radius: 3px; overflow-x: auto;"><code>%%qmc_circuit bell_state
from quantum_memory_compiler.core import Circuit
from quantum_memory_compiler.core.gate import GateType

circuit = Circuit("bell_state")
q0 = circuit.add_qubit()
q1 = circuit.add_qubit()
circuit.add_gate(GateType.H, q0)
circuit.add_gate(GateType.CNOT, [q0, q1])

%qmc_simulate bell_state shots=1000
%qmc_compile bell_state strategy=balanced</code></pre>
            </div>
        </div>
        """
        
        display(HTML(help_html))
        return None


def load_ipython_extension(ipython):
    """Load the Quantum Memory Compiler magic extension"""
    ipython.register_magic_function(QuantumMemoryCompilerMagics)
    print("🚀 Quantum Memory Compiler Jupyter Extension loaded successfully!")
    print("   Use %qmc_help for available commands")
    print("   Developer: kappasutra")


def unload_ipython_extension(ipython):
    """Unload the extension"""
    print("👋 Quantum Memory Compiler Jupyter Extension unloaded")
    print("   Developer: kappasutra") 