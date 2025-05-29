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
Visualization Module
===================

This module provides visualization utilities for quantum circuits and memory usage.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from .circuit import Circuit
from .gate import GateType
from collections import defaultdict

class CircuitVisualizer:
    """
    Visualizer for quantum circuits
    """
    
    def __init__(self, figsize=(10, 6), fontsize=12):
        """
        Initialize the circuit visualizer
        
        Args:
            figsize: Figure size (width, height)
            fontsize: Font size for labels
        """
        self.figsize = figsize
        self.fontsize = fontsize
        
        # Color mapping for different gate types
        self.gate_colors = {
            GateType.X: "salmon",
            GateType.Y: "lightgreen",
            GateType.Z: "skyblue",
            GateType.H: "orange",
            GateType.CNOT: "violet",
            GateType.SWAP: "pink",
            GateType.MEASURE: "gray",
            GateType.RESET: "brown"
        }
        
        # Symbol mapping for different gate types
        self.gate_symbols = {
            GateType.X: "X",
            GateType.Y: "Y",
            GateType.Z: "Z",
            GateType.H: "H",
            GateType.CNOT: "•",
            GateType.SWAP: "×",
            GateType.MEASURE: "M",
            GateType.RESET: "R"
        }
    
    def visualize_circuit(self, circuit, filename=None):
        """
        Visualize a quantum circuit
        
        Args:
            circuit: The quantum circuit to visualize
            filename: Optional filename or file-like object to save the visualization
            
        Returns:
            matplotlib.figure: The figure object
        """
        # Create a figure
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Get circuit properties
        num_qubits = circuit.width
        max_time = max([gate.time for gate in circuit.gates]) if circuit.gates else 0
        
        # Draw qubit lines
        for i in range(num_qubits):
            ax.plot([0, max_time + 1], [i, i], 'k-', alpha=0.3)
            ax.text(-0.5, i, f"q{i}", fontsize=self.fontsize, 
                    horizontalalignment='right', verticalalignment='center')
        
        # Draw gates
        for gate in circuit.gates:
            gate_type = gate.type
            time = gate.time
            
            # Single-qubit gates
            if len(gate.qubits) == 1:
                qubit_id = gate.qubits[0].id
                color = self.gate_colors.get(gate_type, "gray")
                symbol = self.gate_symbols.get(gate_type, "?")
                
                # Draw gate box
                rect = plt.Rectangle((time - 0.4, qubit_id - 0.4), 0.8, 0.8, 
                                    color=color, alpha=0.7)
                ax.add_patch(rect)
                
                # Add gate symbol
                ax.text(time, qubit_id, symbol, fontsize=self.fontsize-2,
                       horizontalalignment='center', verticalalignment='center')
            
            # Two-qubit gates
            elif len(gate.qubits) == 2:
                q1, q2 = gate.qubits[0].id, gate.qubits[1].id
                q_min, q_max = min(q1, q2), max(q1, q2)
                
                if gate_type == GateType.CNOT:
                    # Draw control point
                    ax.plot(time, q1, 'ko', markersize=8)
                    
                    # Draw target point
                    circle = plt.Circle((time, q2), 0.2, color='white', ec='black')
                    ax.add_patch(circle)
                    ax.plot([time-0.2, time+0.2], [q2, q2], 'k-')
                    
                    # Draw connecting line
                    ax.plot([time, time], [q1, q2], 'k-')
                
                elif gate_type == GateType.SWAP:
                    # Draw swap points
                    ax.plot(time, q1, 'kx', markersize=8)
                    ax.plot(time, q2, 'kx', markersize=8)
                    
                    # Draw connecting line
                    ax.plot([time, time], [q1, q2], 'k-')
                
                else:
                    # Generic two-qubit gate
                    color = self.gate_colors.get(gate_type, "gray")
                    symbol = self.gate_symbols.get(gate_type, "?")
                    
                    # Draw connecting rectangle
                    rect = plt.Rectangle((time - 0.4, q_min - 0.4), 0.8, q_max - q_min + 0.8, 
                                       color=color, alpha=0.5)
                    ax.add_patch(rect)
                    
                    # Add gate symbol
                    ax.text(time, (q_min + q_max) / 2, symbol, fontsize=self.fontsize,
                           horizontalalignment='center', verticalalignment='center')
        
        # Set axis properties
        ax.set_xlim(-1, max_time + 1)
        ax.set_ylim(-0.5, num_qubits - 0.5)
        ax.set_title(f"Circuit: {circuit.name}", fontsize=self.fontsize+2)
        ax.set_xlabel("Time", fontsize=self.fontsize)
        ax.set_ylabel("Qubits", fontsize=self.fontsize)
        ax.invert_yaxis()  # Invert y-axis to match standard circuit notation
        ax.set_xticks(range(max_time + 1))
        ax.set_yticks(range(num_qubits))
        ax.set_yticklabels([f"|q{i}⟩" for i in range(num_qubits)])
        
        plt.tight_layout()
        
        # Save figure if filename is provided
        if filename:
            try:
                # Handle both file path and file-like objects (like BytesIO)
                if hasattr(filename, 'write'):
                    plt.savefig(filename, format='png', dpi=300, bbox_inches='tight')
                else:
                    # Get format from filename extension or default to PNG
                    fmt = filename.split('.')[-1] if '.' in filename else 'png'
                    plt.savefig(filename, format=fmt, dpi=300, bbox_inches='tight')
            except Exception as e:
                print(f"Error saving visualization: {e}")
        
        return fig

class MemoryVisualizer:
    """
    Visualizer for memory usage
    """
    
    def __init__(self, figsize=(10, 6), fontsize=12):
        """
        Initialize the memory visualizer
        
        Args:
            figsize: Figure size (width, height)
            fontsize: Font size for labels
        """
        self.figsize = figsize
        self.fontsize = fontsize
        
        # Color mapping for different memory levels
        self.level_colors = {
            "L1": "red",
            "L2": "green",
            "L3": "blue"
        }
    
    def visualize_memory_usage(self, memory_hierarchy, filename=None):
        """
        Visualize memory hierarchy usage
        
        Args:
            memory_hierarchy: MemoryHierarchy object
            filename: Optional filename to save the visualization
            
        Returns:
            matplotlib.figure: The figure object
        """
        # Create a figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize)
        
        # Get memory levels
        levels = memory_hierarchy.levels
        level_names = list(levels.keys())
        capacities = [level.capacity for level in levels.values()]
        used = [level.used_qubits for level in levels.values()]
        free = [capacity - usage for capacity, usage in zip(capacities, used)]
        
        # Bar chart for capacity
        ax1.bar(level_names, capacities, color='lightgray', alpha=0.7, label='Total Capacity')
        ax1.bar(level_names, used, color=[self.level_colors[name] for name in level_names], 
                alpha=0.9, label='Used')
        
        # Set axis properties
        ax1.set_title("Memory Capacity and Usage", fontsize=self.fontsize+2)
        ax1.set_xlabel("Memory Level", fontsize=self.fontsize)
        ax1.set_ylabel("Number of Qubits", fontsize=self.fontsize)
        ax1.legend(fontsize=self.fontsize-2)
        
        # Pie chart for utilization
        total_capacity = sum(capacities)
        levels_data = [level.capacity / total_capacity for level in levels.values()]
        ax2.pie(levels_data, labels=level_names, colors=[self.level_colors[name] for name in level_names],
               autopct='%1.1f%%', shadow=True, startangle=90, wedgeprops={'alpha': 0.8})
        
        # Set axis properties
        ax2.set_title("Memory Hierarchy Distribution", fontsize=self.fontsize+2)
        
        plt.tight_layout()
        
        # Save figure if filename is provided
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        return fig

def visualize_compilation_stats(compiler, original_circuit, compiled_circuit, filename=None):
    """
    Visualize compilation statistics
    
    Args:
        compiler: QuantumCompiler object
        original_circuit: Original circuit
        compiled_circuit: Compiled circuit
        filename: Optional filename to save the visualization
        
    Returns:
        matplotlib.figure: The figure object
    """
    # Get compilation stats
    stats = compiler.get_last_compilation_stats()
    
    # Create a figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Bar chart for qubit usage
    labels = ['Original', 'Compiled']
    qubit_counts = [original_circuit.width, compiled_circuit.width]
    gate_counts = [len(original_circuit.gates), len(compiled_circuit.gates)]
    
    x = np.arange(len(labels))
    width = 0.35
    
    ax1.bar(x - width/2, qubit_counts, width, label='Qubits', color='skyblue')
    ax1.bar(x + width/2, gate_counts, width, label='Gates', color='lightgreen')
    
    # Add labels and title
    ax1.set_title('Circuit Comparison', fontsize=14)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.legend()
    
    # Add text annotations
    for i, v in enumerate(qubit_counts):
        ax1.text(i - width/2, v + 0.1, str(v), ha='center')
    
    for i, v in enumerate(gate_counts):
        ax1.text(i + width/2, v + 0.1, str(v), ha='center')
    
    # Pie chart for memory level usage
    memory_data = [
        stats['memory_usage']['L1'],
        stats['memory_usage']['L2'], 
        stats['memory_usage']['L3']
    ]
    
    # Check if there's any usage
    if sum(memory_data) > 0:
        ax2.pie(memory_data, labels=['L1', 'L2', 'L3'], 
                colors=['red', 'green', 'blue'],
                autopct='%1.1f%%', shadow=True, startangle=90)
        ax2.set_title('Memory Level Usage', fontsize=14)
    else:
        ax2.text(0.5, 0.5, 'No memory usage data available', 
                 ha='center', va='center', fontsize=12)
        ax2.set_title('Memory Level Usage', fontsize=14)
        ax2.axis('off')
    
    plt.tight_layout()
    
    # Save figure if filename is provided
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
    
    return fig

def plot_circuit(circuit, filename=None, show_barriers=True, highlight_qubits=None):
    """
    Plots a quantum circuit diagram
    
    Args:
        circuit: Quantum circuit to plot
        filename: If specified, save the plot to this file
        show_barriers: Whether to show barrier gates in the plot
        highlight_qubits: List of qubits to highlight in the diagram
    """
    if not circuit.gates:
        print("No gates in circuit to plot")
        return
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, max(5, circuit.width * 0.5)))
    
    # Track which qubits are used in the circuit
    used_qubits = set()
    for gate in circuit.gates:
        for qubit in gate.qubits:
            used_qubits.add(qubit)
    
    # Map used qubits to consecutive row indices
    qubit_map = {qubit: i for i, qubit in enumerate(sorted(used_qubits, key=lambda q: q.id))}
    num_qubits = len(qubit_map)
    
    # Get max time in circuit
    max_time = max(gate.time + gate.duration for gate in circuit.gates)
    
    # Draw qubit lines
    for qubit, row in qubit_map.items():
        color = 'red' if highlight_qubits and qubit in highlight_qubits else 'black'
        ax.plot([0, max_time], [row, row], '-', color=color, alpha=0.5)
        
        # Add qubit label
        memory_level = qubit.memory_level.name if hasattr(qubit.memory_level, "name") else "L?"
        ax.text(-1, row, f"q{qubit.id}\n({memory_level})", ha='right', va='center')
    
    # Draw gates
    for gate in sorted(circuit.gates, key=lambda g: g.time):
        # Skip barriers if not showing them
        if not show_barriers and gate.type.name == 'BARRIER':
            continue
            
        # Get positions for this gate
        time = gate.time
        rows = [qubit_map[qubit] for qubit in gate.qubits]
        
        if len(rows) == 1:
            # Single-qubit gate
            row = rows[0]
            rect = patches.Rectangle((time-0.25, row-0.25), 0.5, 0.5, 
                                     edgecolor='black', facecolor='white', alpha=0.8)
            ax.add_patch(rect)
            
            # Add gate label
            gate_text = gate.type.name
            if gate.parameters:
                param_str = ",".join(f"{p:.2f}" for p in gate.parameters)
                gate_text += f"({param_str})"
            ax.text(time, row, gate_text, ha='center', va='center', fontsize=8)
            
        elif len(rows) == 2:
            # Two-qubit gate
            row1, row2 = min(rows), max(rows)
            
            # Draw vertical connector
            ax.plot([time, time], [row1, row2], 'k-')
            
            # Draw boxes at each end
            rect1 = patches.Rectangle((time-0.25, row1-0.25), 0.5, 0.5, 
                                     edgecolor='black', facecolor='white', alpha=0.8)
            rect2 = patches.Rectangle((time-0.25, row2-0.25), 0.5, 0.5, 
                                     edgecolor='black', facecolor='white', alpha=0.8)
            ax.add_patch(rect1)
            ax.add_patch(rect2)
            
            # Add gate label
            gate_text = gate.type.name
            if gate.parameters:
                param_str = ",".join(f"{p:.2f}" for p in gate.parameters)
                gate_text += f"({param_str})"
            ax.text(time, (row1 + row2) / 2, gate_text, ha='center', va='center', fontsize=8)
            
        elif len(rows) == 3:
            # Three-qubit gate
            row1, row2, row3 = sorted(rows)
            
            # Draw vertical connector
            ax.plot([time, time], [row1, row3], 'k-')
            
            # Draw boxes at each position
            rect1 = patches.Rectangle((time-0.25, row1-0.25), 0.5, 0.5, 
                                     edgecolor='black', facecolor='white', alpha=0.8)
            rect2 = patches.Rectangle((time-0.25, row2-0.25), 0.5, 0.5, 
                                     edgecolor='black', facecolor='white', alpha=0.8)
            rect3 = patches.Rectangle((time-0.25, row3-0.25), 0.5, 0.5, 
                                     edgecolor='black', facecolor='white', alpha=0.8)
            ax.add_patch(rect1)
            ax.add_patch(rect2)
            ax.add_patch(rect3)
            
            # Add gate label
            gate_text = gate.type.name
            ax.text(time, row2, gate_text, ha='center', va='center', fontsize=8)
    
    # Set axis properties
    ax.set_xlim(-1.5, max_time + 1)
    ax.set_ylim(-0.5, num_qubits - 0.5)
    ax.set_xlabel('Time')
    ax.set_ylabel('Qubits')
    ax.set_title(f'Quantum Circuit: {circuit.name}')
    
    # Invert y-axis to have qubit 0 at the top
    ax.invert_yaxis()
    
    # Set y-ticks to be invisible (we already labeled the qubits)
    ax.set_yticks([])
    
    # Save or show
    if filename:
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
    else:
        plt.tight_layout()
        plt.show()

def plot_memory_usage(circuit, memory_hierarchy, timeline=None, filename=None):
    """
    Plots memory usage over time for a circuit
    
    Args:
        circuit: Quantum circuit to analyze
        memory_hierarchy: Memory hierarchy to consider
        timeline: Optional pre-computed usage timeline
        filename: If specified, save the plot to this file
    """
    if not timeline:
        # Create a timeline of memory usage
        timeline = defaultdict(lambda: {'L1': 0, 'L2': 0, 'L3': 0})
        
        # Calculate initial usage
        for level_name in ['L1', 'L2', 'L3']:
            level = memory_hierarchy.get_level(level_name)
            if level:
                timeline[0][level_name] = level.used_qubits
        
        # Determine all time points where memory usage changes
        time_points = set([0])
        for gate in circuit.gates:
            time_points.add(gate.time)
            time_points.add(gate.time + gate.duration)
        
        # Sort time points
        time_points = sorted(time_points)
        
        # Calculate memory usage at each time point
        for i, time in enumerate(time_points):
            if i > 0:
                # Start with previous state
                prev_time = time_points[i-1]
                timeline[time]['L1'] = timeline[prev_time]['L1']
                timeline[time]['L2'] = timeline[prev_time]['L2']
                timeline[time]['L3'] = timeline[prev_time]['L3']
            
            # Find all gates that start at this time
            gates_at_time = [g for g in circuit.gates if g.time == time]
            
            # Update memory usage based on gates
            for gate in gates_at_time:
                for qubit in gate.qubits:
                    level = qubit.memory_level.name if hasattr(qubit.memory_level, "name") else "L1"
                    if level in ['L1', 'L2', 'L3']:
                        # For simplicity, assume qubit is allocated if it's used at this time
                        if not qubit.is_allocated:
                            timeline[time][level] += 1
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Extract data for plotting
    times = sorted(timeline.keys())
    l1_usage = [timeline[t]['L1'] for t in times]
    l2_usage = [timeline[t]['L2'] for t in times]
    l3_usage = [timeline[t]['L3'] for t in times]
    
    # Plot memory usage
    ax.plot(times, l1_usage, 'r-', label='L1 Memory')
    ax.plot(times, l2_usage, 'g-', label='L2 Memory')
    ax.plot(times, l3_usage, 'b-', label='L3 Memory')
    
    # Get capacity limits
    l1_capacity = memory_hierarchy.get_level('L1').capacity
    l2_capacity = memory_hierarchy.get_level('L2').capacity
    l3_capacity = memory_hierarchy.get_level('L3').capacity
    
    # Draw capacity lines
    ax.axhline(y=l1_capacity, color='r', linestyle='--', alpha=0.5)
    ax.axhline(y=l2_capacity, color='g', linestyle='--', alpha=0.5)
    ax.axhline(y=l3_capacity, color='b', linestyle='--', alpha=0.5)
    
    # Add annotations for capacity limits
    ax.text(times[-1], l1_capacity, f'L1 Capacity: {l1_capacity}', va='bottom', ha='right', color='red')
    ax.text(times[-1], l2_capacity, f'L2 Capacity: {l2_capacity}', va='bottom', ha='right', color='green')
    ax.text(times[-1], l3_capacity, f'L3 Capacity: {l3_capacity}', va='bottom', ha='right', color='blue')
    
    # Set axis properties
    ax.set_xlim(0, max(times))
    ax.set_ylim(0, max(l1_capacity, l2_capacity, l3_capacity) * 1.1)
    ax.set_xlabel('Time')
    ax.set_ylabel('Number of Qubits')
    ax.set_title('Memory Usage Over Time')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # Save or show
    if filename:
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
    else:
        plt.tight_layout()
        plt.show()

def plot_memory_hierarchy(memory_hierarchy, filename=None):
    """
    Visualizes the memory hierarchy structure
    
    Args:
        memory_hierarchy: Memory hierarchy to visualize
        filename: If specified, save the plot to this file
    """
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Get memory levels
    levels = ['L1', 'L2', 'L3']
    level_objects = [memory_hierarchy.get_level(level) for level in levels]
    level_objects = [l for l in level_objects if l is not None]
    
    # Define colors and positions
    colors = ['#ff9999', '#99ff99', '#9999ff']
    positions = [1, 2, 3]
    
    # Draw rectangles for each level
    for i, (level, color) in enumerate(zip(level_objects, colors)):
        # Size rectangle based on capacity
        width = np.sqrt(level.capacity) * 0.5
        height = np.sqrt(level.capacity) * 0.3
        
        # Position rectangle
        pos = positions[i]
        
        # Draw rectangle
        rect = patches.Rectangle((pos-width/2, 1-height/2), width, height, 
                                edgecolor='black', facecolor=color, alpha=0.7)
        ax.add_patch(rect)
        
        # Add label
        ax.text(pos, 1, f"{level.name}\nCapacity: {level.capacity}\nUsed: {level.used_qubits}\nCoh. Time: {level.coherence_time}", 
                ha='center', va='center', fontsize=10)
    
    # Draw arrows for transfers
    arrow_props = dict(arrowstyle='->', lw=1.5, color='gray')
    
    # L1 <-> L2
    ax.annotate('', xy=(positions[0]+0.3, 1), xytext=(positions[1]-0.3, 1), 
                arrowprops=arrow_props)
    ax.annotate('', xy=(positions[1]-0.3, 0.9), xytext=(positions[0]+0.3, 0.9), 
                arrowprops=arrow_props)
    
    # L2 <-> L3
    if len(positions) >= 3:
        ax.annotate('', xy=(positions[1]+0.3, 1), xytext=(positions[2]-0.3, 1), 
                    arrowprops=arrow_props)
        ax.annotate('', xy=(positions[2]-0.3, 0.9), xytext=(positions[1]+0.3, 0.9), 
                    arrowprops=arrow_props)
    
    # Add transfer costs
    for i in range(len(positions)-1):
        src, dst = levels[i], levels[i+1]
        transfer_key = (src, dst)
        
        # Get transfer time and error rate
        transfer_time = memory_hierarchy.transfer_times.get(transfer_key, 0)
        error_rate = memory_hierarchy.transfer_error_rates.get(transfer_key, 0)
        
        # Add label at midpoint
        midpoint = (positions[i] + positions[i+1]) / 2
        ax.text(midpoint, 1.1, f"T: {transfer_time} | E: {error_rate:.3f}", 
                ha='center', va='center', fontsize=8)
    
    # Set axis properties
    ax.set_xlim(0, positions[-1] + 1)
    ax.set_ylim(0, 2)
    ax.set_title('Quantum Memory Hierarchy')
    ax.axis('off')  # Hide axes
    
    # Save or show
    if filename:
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
    else:
        plt.tight_layout()
        plt.show()

def plot_memory_transfers(memory_hierarchy, timeline=None, filename=None):
    """
    Visualizes memory transfers over time
    
    Args:
        memory_hierarchy: Memory hierarchy to visualize
        timeline: Optional list of transfer events [(time, qubit, source, target), ...]
        filename: If specified, save the plot to this file
    """
    if not timeline:
        print("No transfer timeline provided")
        return
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Extract data for plotting
    times = [t[0] for t in timeline]
    qubits = [t[1].id for t in timeline]
    sources = [t[2].name if hasattr(t[2], "name") else t[2] for t in timeline]
    targets = [t[3].name if hasattr(t[3], "name") else t[3] for t in timeline]
    
    # Define colors for different levels
    level_colors = {'L1': 'red', 'L2': 'green', 'L3': 'blue'}
    
    # Plot transfer markers
    for i, (time, qubit, source, target) in enumerate(zip(times, qubits, sources, targets)):
        # Draw a line from source to target
        y_source = {'L1': 1, 'L2': 2, 'L3': 3}[source]
        y_target = {'L1': 1, 'L2': 2, 'L3': 3}[target]
        
        ax.plot([time, time], [y_source, y_target], '-', 
                color=level_colors[target], alpha=0.6, lw=1.5)
        
        # Mark the start and end points
        ax.plot(time, y_source, 'o', color=level_colors[source], markersize=5)
        ax.plot(time, y_target, 'o', color=level_colors[target], markersize=5)
        
        # Add qubit label
        ax.text(time, (y_source + y_target) / 2, f"q{qubit}", ha='left', va='center', fontsize=8)
    
    # Draw level lines
    ax.axhline(y=1, color=level_colors['L1'], linestyle='-', alpha=0.3, label='L1')
    ax.axhline(y=2, color=level_colors['L2'], linestyle='-', alpha=0.3, label='L2')
    ax.axhline(y=3, color=level_colors['L3'], linestyle='-', alpha=0.3, label='L3')
    
    # Set axis properties
    if times:
        ax.set_xlim(min(times) - 1, max(times) + 1)
    ax.set_ylim(0.5, 3.5)
    ax.set_xlabel('Time')
    ax.set_ylabel('Memory Level')
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(['L1', 'L2', 'L3'])
    ax.set_title('Memory Transfers Over Time')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    # Save or show
    if filename:
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
    else:
        plt.tight_layout()
        plt.show()

def generate_memory_report(circuit, memory_hierarchy, filename=None):
    """
    Generates a comprehensive visual report on memory usage
    
    Args:
        circuit: Quantum circuit to analyze
        memory_hierarchy: Memory hierarchy to consider
        filename: Base filename for the report images
    """
    # Create a directory for the reports if filename is specified
    import os
    if filename:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Plot the circuit
    circuit_filename = f"{filename}_circuit.png" if filename else None
    plot_circuit(circuit, filename=circuit_filename)
    
    # Plot memory hierarchy
    hierarchy_filename = f"{filename}_hierarchy.png" if filename else None
    plot_memory_hierarchy(memory_hierarchy, filename=hierarchy_filename)
    
    # Plot memory usage over time
    usage_filename = f"{filename}_usage.png" if filename else None
    plot_memory_usage(circuit, memory_hierarchy, filename=usage_filename)
    
    # If there are no transfers in the circuit, we can't plot them
    transfers = []
    for gate in circuit.gates:
        if hasattr(gate, 'is_transfer') and gate.is_transfer:
            transfers.append((gate.time, gate.qubits[0], gate.source_level, gate.target_level))
    
    if transfers:
        transfers_filename = f"{filename}_transfers.png" if filename else None
        plot_memory_transfers(memory_hierarchy, timeline=transfers, filename=transfers_filename)
    
    # Print a summary of what was generated
    if filename:
        print(f"Generated memory report with base filename: {filename}")
        print(f"- Circuit diagram: {circuit_filename}")
        print(f"- Memory hierarchy: {hierarchy_filename}")
        print(f"- Memory usage: {usage_filename}")
        if transfers:
            print(f"- Memory transfers: {transfers_filename}")
    
    # Return the list of generated files
    generated_files = []
    if filename:
        generated_files = [circuit_filename, hierarchy_filename, usage_filename]
        if transfers:
            generated_files.append(transfers_filename)
    
    return generated_files 