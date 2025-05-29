#!/usr/bin/env python3
"""
Quantum Memory Compiler - Advanced Memory-Aware Quantum Circuit Compilation
Copyright (c) 2025 Quantum Memory Compiler Project

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This file contains proprietary algorithms for quantum memory optimization.
Commercial use requires explicit permission.
"""

"""
Quantum Memory Compiler Cursor Extension
=======================================

This module enables the use of Quantum Memory Compiler within Cursor IDE.
Similar to VSCode extensions, it provides circuit visualization, simulation, 
compilation, and memory profiling features through the Cursor interface.

Developer: kappasutra
"""

import os
import sys
import json
import tempfile
from pathlib import Path
import subprocess
from typing import Any, Dict, List, Optional

# Import Cursor API
try:
    import cursor
    from cursor import api as cursor_api
    CURSOR_AVAILABLE = True
except ImportError:
    CURSOR_AVAILABLE = False
    print("⚠️  Cursor API not available - only VSCode compatible modes active")

# Extension state
extension_state = {
    "initialized": False,
    "temp_dir": None,
    "panels": {}
}

def activate(context: Any) -> None:
    """
    Activate the extension
    
    Args:
        context: Cursor extension context
    """
    if not CURSOR_AVAILABLE:
        print("❌ Quantum Memory Compiler extension could not be activated in Cursor.")
        return
    
    print("🚀 Activating Quantum Memory Compiler Cursor extension...")
    print("   Developer: kappasutra")
    
    # Create temporary directory
    extension_state["temp_dir"] = tempfile.mkdtemp(prefix="qmc_cursor_")
    extension_state["initialized"] = True
    
    # Register commands
    cursor_api.register_command("quantum-memory.visualize-circuit", visualize_circuit)
    cursor_api.register_command("quantum-memory.run-simulation", run_simulation)
    cursor_api.register_command("quantum-memory.compile-circuit", compile_circuit)
    cursor_api.register_command("quantum-memory.profile-memory", profile_memory)
    cursor_api.register_command("quantum-memory.run-examples", run_examples)
    cursor_api.register_command("quantum-memory.show-help", show_help)
    
    # Create sidebar menu
    create_sidebar_menu()
    
    print("✅ Quantum Memory Compiler Cursor extension activated successfully!")

def create_sidebar_menu() -> None:
    """Add Quantum Memory Compiler menu to Cursor sidebar"""
    if not CURSOR_AVAILABLE:
        return
    
    # Create sidebar menu
    menu_items = [
        {
            "id": "quantum-memory.visualize",
            "title": "🎨 Visualize Circuit",
            "command": "quantum-memory.visualize-circuit"
        },
        {
            "id": "quantum-memory.simulate",
            "title": "🔬 Run Simulation",
            "command": "quantum-memory.run-simulation"
        },
        {
            "id": "quantum-memory.compile",
            "title": "⚙️ Compile Circuit",
            "command": "quantum-memory.compile-circuit"
        },
        {
            "id": "quantum-memory.profile",
            "title": "💾 Memory Profile",
            "command": "quantum-memory.profile-memory"
        },
        {
            "id": "quantum-memory.examples",
            "title": "📚 Run Examples",
            "command": "quantum-memory.run-examples"
        },
        {
            "id": "quantum-memory.help",
            "title": "❓ Help",
            "command": "quantum-memory.show-help"
        }
    ]
    
    cursor_api.create_sidebar_menu("🚀 Quantum Memory (kappasutra)", menu_items)

async def visualize_circuit() -> None:
    """Execute circuit visualization command"""
    if not CURSOR_AVAILABLE or not extension_state["initialized"]:
        return
    
    try:
        # Get active file
        active_file = cursor_api.get_active_file()
        if not active_file:
            cursor_api.show_error_message("Please open a Python file first.")
            return
        
        file_path = active_file.path
        
        # Temporary file for circuit output
        output_file = os.path.join(extension_state["temp_dir"], "circuit_visualization.png")
        
        # Prepare Python command
        python_path = sys.executable
        args = [
            "-c",
            f"""
import sys
sys.path.insert(0, '.')
from quantum_memory_compiler.cli import main
import sys
sys.argv = ['qmc', 'visualize', '{file_path}', '--output', '{output_file}']
main()
"""
        ]
        
        # Show progress
        cursor_api.show_information_message("🎨 Visualizing circuit... (kappasutra)")
        
        # Execute command
        process = subprocess.Popen(
            [python_path] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            if os.path.exists(output_file):
                # Show image panel
                show_image_panel("🎨 Quantum Circuit Visualization", output_file)
                cursor_api.show_information_message("✅ Circuit visualization completed!")
            else:
                cursor_api.show_error_message("❌ Visualization file could not be created.")
        else:
            cursor_api.show_error_message(f"❌ Visualization error: {stderr}")
            
    except Exception as e:
        cursor_api.show_error_message(f"❌ Error: {str(e)}")

async def run_simulation() -> None:
    """Execute simulation command"""
    if not CURSOR_AVAILABLE or not extension_state["initialized"]:
        return
    
    try:
        # Get active file
        active_file = cursor_api.get_active_file()
        if not active_file:
            cursor_api.show_error_message("Please open a Python file first.")
            return
        
        file_path = active_file.path
        
        # Ask for simulation parameters
        shots = await cursor_api.show_input_box(
            prompt="Number of simulation shots",
            placeholder="1024",
            value="1024"
        )
        
        if not shots:
            return  # User cancelled
        
        use_noise = await cursor_api.show_quick_pick(
            ["Yes", "No"],
            placeholder="Use noise model?"
        )
        
        if not use_noise:
            return  # User cancelled
        
        use_mitigation = await cursor_api.show_quick_pick(
            ["Yes", "No"],
            placeholder="Use error mitigation?"
        )
        
        if not use_mitigation:
            return  # User cancelled
        
        # Result file
        output_file = os.path.join(extension_state["temp_dir"], "simulation_results.json")
        
        # Prepare Python command
        python_path = sys.executable
        cmd_args = [
            "-c",
            f"""
import sys
sys.path.insert(0, '.')
from quantum_memory_compiler.cli import main
import sys
sys.argv = ['qmc', 'simulate', '{file_path}', '--shots', '{shots}']
if '{use_noise}' == 'Yes':
    sys.argv.extend(['--noise'])
if '{use_mitigation}' == 'Yes':
    sys.argv.extend(['--mitigation'])
sys.argv.extend(['--output', '{output_file}'])
main()
"""
        ]
        
        # Show progress
        cursor_api.show_information_message(f"🔬 Running simulation with {shots} shots... (kappasutra)")
        
        # Execute command
        process = subprocess.Popen(
            [python_path] + cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            if os.path.exists(output_file):
                # Load and show results
                with open(output_file, 'r') as f:
                    results = json.load(f)
                
                show_results_panel("🔬 Simulation Results", results)
                cursor_api.show_information_message("✅ Simulation completed successfully!")
            else:
                cursor_api.show_information_message("✅ Simulation completed! Check console for results.")
        else:
            cursor_api.show_error_message(f"❌ Simulation error: {stderr}")
            
    except Exception as e:
        cursor_api.show_error_message(f"❌ Error: {str(e)}")

async def compile_circuit() -> None:
    """Execute circuit compilation command"""
    if not CURSOR_AVAILABLE or not extension_state["initialized"]:
        return
    
    try:
        # Get active file
        active_file = cursor_api.get_active_file()
        if not active_file:
            cursor_api.show_error_message("Please open a Python file first.")
            return
        
        file_path = active_file.path
        
        # Ask for compilation strategy
        strategy = await cursor_api.show_quick_pick(
            ["balanced", "memory", "meta"],
            placeholder="Select compilation strategy"
        )
        
        if not strategy:
            return  # User cancelled
        
        # Output file
        output_file = os.path.join(extension_state["temp_dir"], "compiled_circuit.py")
        
        # Prepare Python command
        python_path = sys.executable
        cmd_args = [
            "-c",
            f"""
import sys
sys.path.insert(0, '.')
from quantum_memory_compiler.cli import main
import sys
sys.argv = ['qmc', 'compile', '{file_path}', '--strategy', '{strategy}', '--output', '{output_file}']
main()
"""
        ]
        
        # Show progress
        cursor_api.show_information_message(f"⚙️ Compiling circuit with {strategy} strategy... (kappasutra)")
        
        # Execute command
        process = subprocess.Popen(
            [python_path] + cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            if os.path.exists(output_file):
                # Open compiled circuit in new tab
                cursor_api.open_file(output_file)
                cursor_api.show_information_message("✅ Circuit compilation completed!")
            else:
                cursor_api.show_information_message("✅ Compilation completed! Check console for results.")
        else:
            cursor_api.show_error_message(f"❌ Compilation error: {stderr}")
            
    except Exception as e:
        cursor_api.show_error_message(f"❌ Error: {str(e)}")

async def profile_memory() -> None:
    """Execute memory profiling command"""
    if not CURSOR_AVAILABLE or not extension_state["initialized"]:
        return
    
    try:
        # Get active file
        active_file = cursor_api.get_active_file()
        if not active_file:
            cursor_api.show_error_message("Please open a Python file first.")
            return
        
        file_path = active_file.path
        
        # Output file for profile
        output_file = os.path.join(extension_state["temp_dir"], "memory_profile.png")
        
        # Prepare Python command
        python_path = sys.executable
        cmd_args = [
            "-c",
            f"""
import sys
sys.path.insert(0, '.')
from quantum_memory_compiler.cli import main
import sys
sys.argv = ['qmc', 'profile', '{file_path}', '--output', '{output_file}']
main()
"""
        ]
        
        # Show progress
        cursor_api.show_information_message("💾 Profiling memory usage... (kappasutra)")
        
        # Execute command
        process = subprocess.Popen(
            [python_path] + cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            if os.path.exists(output_file):
                # Show profile image
                show_image_panel("💾 Memory Profile", output_file)
                cursor_api.show_information_message("✅ Memory profiling completed!")
            else:
                cursor_api.show_information_message("✅ Profiling completed! Check console for results.")
        else:
            cursor_api.show_error_message(f"❌ Profiling error: {stderr}")
            
    except Exception as e:
        cursor_api.show_error_message(f"❌ Error: {str(e)}")

async def run_examples() -> None:
    """Execute example circuits"""
    if not CURSOR_AVAILABLE or not extension_state["initialized"]:
        return
    
    try:
        # Available examples
        examples = [
            "bell_state_example.py",
            "quantum_fourier_transform.py", 
            "grover_search.py",
            "error_mitigation_demo.py"
        ]
        
        # Ask user to select example
        selected_example = await cursor_api.show_quick_pick(
            examples,
            placeholder="Select an example to run"
        )
        
        if not selected_example:
            return  # User cancelled
        
        # Prepare Python command
        python_path = sys.executable
        cmd_args = [
            "-c",
            f"""
import sys
sys.path.insert(0, '.')
from quantum_memory_compiler.cli import main
import sys
sys.argv = ['qmc', 'examples', '{selected_example}']
main()
"""
        ]
        
        # Show progress
        cursor_api.show_information_message(f"📚 Running example: {selected_example}... (kappasutra)")
        
        # Execute command
        process = subprocess.Popen(
            [python_path] + cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            cursor_api.show_information_message(f"✅ Example {selected_example} completed successfully!")
            # Show output in new panel
            show_text_panel(f"📚 Example Output: {selected_example}", stdout)
        else:
            cursor_api.show_error_message(f"❌ Example error: {stderr}")
            
    except Exception as e:
        cursor_api.show_error_message(f"❌ Error: {str(e)}")

async def show_help() -> None:
    """Show help information"""
    if not CURSOR_AVAILABLE:
        return
    
    help_content = """
🚀 Quantum Memory Compiler Cursor Extension
Developer: kappasutra

Available Commands:
==================

🎨 Visualize Circuit
   - Visualizes quantum circuits from Python files
   - Generates circuit diagrams and saves as PNG

🔬 Run Simulation  
   - Simulates quantum circuits with customizable parameters
   - Supports noise models and error mitigation
   - Configurable shot count

⚙️ Compile Circuit
   - Compiles and optimizes quantum circuits
   - Multiple strategies: balanced, memory, meta
   - Memory-aware optimization

💾 Memory Profile
   - Profiles memory usage of quantum circuits
   - Visualizes memory hierarchy utilization
   - Identifies bottlenecks

📚 Run Examples
   - Execute built-in example circuits
   - Bell state, QFT, Grover's algorithm, etc.
   - Educational demonstrations

Usage:
======
1. Open a Python file containing quantum circuit code
2. Use the sidebar menu or command palette
3. Select desired operation
4. Follow the prompts for parameters
5. View results in new panels

Requirements:
=============
- Python file with quantum_memory_compiler imports
- Valid circuit definitions using QMC API
- Cursor IDE with extension support

For more information, visit the project repository.
"""
    
    show_text_panel("❓ Quantum Memory Compiler Help", help_content)

def show_image_panel(title: str, image_path: str) -> None:
    """Show image in a new panel"""
    if not CURSOR_AVAILABLE:
        return
    
    try:
        # Create webview panel for image
        panel_id = f"qmc_image_{len(extension_state['panels'])}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    background-color: #1e1e1e;
                    color: #ffffff;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #007acc;
                    padding-bottom: 10px;
                }}
                .developer {{
                    font-size: 12px;
                    color: #888;
                    margin-top: 5px;
                }}
                .image-container {{
                    text-align: center;
                    background-color: #2d2d30;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>{title}</h2>
                <div class="developer">Developer: kappasutra</div>
            </div>
            <div class="image-container">
                <img src="file://{image_path}" alt="Quantum Circuit Visualization" />
            </div>
        </body>
        </html>
        """
        
        panel = cursor_api.create_webview_panel(
            panel_id,
            title,
            cursor_api.ViewColumn.Beside,
            {"enableScripts": True}
        )
        
        panel.webview.html = html_content
        extension_state["panels"][panel_id] = panel
        
    except Exception as e:
        cursor_api.show_error_message(f"❌ Error showing image: {str(e)}")

def show_text_panel(title: str, content: str) -> None:
    """Show text content in a new panel"""
    if not CURSOR_AVAILABLE:
        return
    
    try:
        # Create webview panel for text
        panel_id = f"qmc_text_{len(extension_state['panels'])}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    background-color: #1e1e1e;
                    color: #ffffff;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    line-height: 1.6;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #007acc;
                    padding-bottom: 10px;
                }}
                .developer {{
                    font-size: 12px;
                    color: #888;
                    margin-top: 5px;
                }}
                .content {{
                    background-color: #2d2d30;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                    white-space: pre-wrap;
                    overflow-x: auto;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>{title}</h2>
                <div class="developer">Developer: kappasutra</div>
            </div>
            <div class="content">{content}</div>
        </body>
        </html>
        """
        
        panel = cursor_api.create_webview_panel(
            panel_id,
            title,
            cursor_api.ViewColumn.Beside,
            {"enableScripts": True}
        )
        
        panel.webview.html = html_content
        extension_state["panels"][panel_id] = panel
        
    except Exception as e:
        cursor_api.show_error_message(f"❌ Error showing text: {str(e)}")

def show_results_panel(title: str, results: Dict) -> None:
    """Show simulation results in a formatted panel"""
    if not CURSOR_AVAILABLE:
        return
    
    try:
        # Format results as HTML table
        results_html = "<table style='width: 100%; border-collapse: collapse;'>"
        results_html += "<tr style='background-color: #007acc; color: white;'>"
        results_html += "<th style='padding: 10px; border: 1px solid #555;'>State</th>"
        results_html += "<th style='padding: 10px; border: 1px solid #555;'>Probability</th>"
        results_html += "<th style='padding: 10px; border: 1px solid #555;'>Counts</th>"
        results_html += "</tr>"
        
        for state, prob in results.items():
            counts = int(prob * 1024)  # Assuming 1024 shots
            results_html += f"<tr style='background-color: #2d2d30;'>"
            results_html += f"<td style='padding: 8px; border: 1px solid #555; font-family: monospace;'>|{state}⟩</td>"
            results_html += f"<td style='padding: 8px; border: 1px solid #555;'>{prob:.4f}</td>"
            results_html += f"<td style='padding: 8px; border: 1px solid #555;'>{counts}</td>"
            results_html += "</tr>"
        
        results_html += "</table>"
        
        # Create panel with results
        panel_id = f"qmc_results_{len(extension_state['panels'])}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    background-color: #1e1e1e;
                    color: #ffffff;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #007acc;
                    padding-bottom: 10px;
                }}
                .developer {{
                    font-size: 12px;
                    color: #888;
                    margin-top: 5px;
                }}
                .results {{
                    background-color: #2d2d30;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>{title}</h2>
                <div class="developer">Developer: kappasutra</div>
            </div>
            <div class="results">
                {results_html}
            </div>
        </body>
        </html>
        """
        
        panel = cursor_api.create_webview_panel(
            panel_id,
            title,
            cursor_api.ViewColumn.Beside,
            {"enableScripts": True}
        )
        
        panel.webview.html = html_content
        extension_state["panels"][panel_id] = panel
        
    except Exception as e:
        cursor_api.show_error_message(f"❌ Error showing results: {str(e)}")

def deactivate() -> None:
    """Deactivate the extension"""
    if extension_state["initialized"]:
        # Clean up temporary directory
        if extension_state["temp_dir"] and os.path.exists(extension_state["temp_dir"]):
            import shutil
            shutil.rmtree(extension_state["temp_dir"])
        
        # Close all panels
        for panel in extension_state["panels"].values():
            panel.dispose()
        
        extension_state["initialized"] = False
        extension_state["temp_dir"] = None
        extension_state["panels"] = {}
        
        print("👋 Quantum Memory Compiler Cursor extension deactivated")
        print("   Developer: kappasutra") 