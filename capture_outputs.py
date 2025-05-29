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
Quantum Memory Compiler - Output Capture Script
Projedeki tüm önemli çıktıları yakalar ve rapor için organize eder.
"""

import os
import json
import subprocess
import time
import psutil
import matplotlib.pyplot as plt
from datetime import datetime
import requests
from pathlib import Path

class OutputCapture:
    def __init__(self):
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def capture_system_info(self):
        """Sistem bilgilerini yakala"""
        print("📋 Capturing system information...")
        
        uname_info = os.uname()
        system_info = {
            "timestamp": datetime.now().isoformat(),
            "python_version": subprocess.check_output(["python", "--version"]).decode().strip(),
            "platform": {
                "system": uname_info.sysname,
                "node": uname_info.nodename,
                "release": uname_info.release,
                "version": uname_info.version,
                "machine": uname_info.machine
            },
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "disk_space": psutil.disk_usage('/').total
        }
        
        with open(self.output_dir / f"system_info_{self.timestamp}.json", 'w') as f:
            json.dump(system_info, f, indent=2)
        
        return system_info
    
    def capture_cli_outputs(self):
        """CLI komut çıktılarını yakala"""
        print("🖥️ Capturing CLI outputs...")
        
        cli_commands = [
            ("help", ["python", "-m", "quantum_memory_compiler.cli.main", "--help"]),
            ("version", ["python", "-c", "import quantum_memory_compiler; print(quantum_memory_compiler.__version__)"]),
        ]
        
        cli_results = {}
        for name, cmd in cli_commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                cli_results[name] = {
                    "command": " ".join(cmd),
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
                
                # Ayrı dosyalara kaydet
                with open(self.output_dir / f"cli_{name}_{self.timestamp}.txt", 'w') as f:
                    f.write(f"Command: {' '.join(cmd)}\n")
                    f.write(f"Return Code: {result.returncode}\n")
                    f.write("--- STDOUT ---\n")
                    f.write(result.stdout)
                    f.write("\n--- STDERR ---\n")
                    f.write(result.stderr)
                    
            except Exception as e:
                cli_results[name] = {"error": str(e)}
        
        with open(self.output_dir / f"cli_results_{self.timestamp}.json", 'w') as f:
            json.dump(cli_results, f, indent=2)
        
        return cli_results
    
    def capture_api_status(self):
        """API endpoint durumlarını yakala"""
        print("🔗 Capturing API status...")
        
        api_endpoints = [
            ("status", "http://localhost:5000/api/status"),
            ("health", "http://localhost:5000/api/health"),
            ("gpu", "http://localhost:5000/api/gpu/status"),
        ]
        
        api_results = {}
        for name, url in api_endpoints:
            try:
                response = requests.get(url, timeout=5)
                api_results[name] = {
                    "url": url,
                    "status_code": response.status_code,
                    "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                    "headers": dict(response.headers)
                }
            except Exception as e:
                api_results[name] = {
                    "url": url,
                    "error": str(e)
                }
        
        with open(self.output_dir / f"api_status_{self.timestamp}.json", 'w') as f:
            json.dump(api_results, f, indent=2)
        
        return api_results
    
    def capture_performance_metrics(self):
        """Performance metriklerini yakala"""
        print("📊 Capturing performance metrics...")
        
        # Memory usage tracking
        memory_data = []
        cpu_data = []
        
        print("  - Monitoring system for 30 seconds...")
        for i in range(30):
            memory_data.append(psutil.virtual_memory().percent)
            cpu_data.append(psutil.cpu_percent())
            time.sleep(1)
        
        # Plot memory usage
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 1, 1)
        plt.plot(memory_data, 'b-', linewidth=2)
        plt.title('Memory Usage Over Time')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Memory Usage (%)')
        plt.grid(True)
        
        plt.subplot(2, 1, 2)
        plt.plot(cpu_data, 'r-', linewidth=2)
        plt.title('CPU Usage Over Time')
        plt.xlabel('Time (seconds)')
        plt.ylabel('CPU Usage (%)')
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / f"performance_metrics_{self.timestamp}.png", dpi=300)
        plt.close()
        
        # Save raw data
        performance_data = {
            "timestamp": datetime.now().isoformat(),
            "memory_usage": memory_data,
            "cpu_usage": cpu_data,
            "avg_memory": sum(memory_data) / len(memory_data),
            "avg_cpu": sum(cpu_data) / len(cpu_data),
            "max_memory": max(memory_data),
            "max_cpu": max(cpu_data)
        }
        
        with open(self.output_dir / f"performance_data_{self.timestamp}.json", 'w') as f:
            json.dump(performance_data, f, indent=2)
        
        return performance_data
    
    def capture_build_results(self):
        """Build sonuçlarını yakala"""
        print("🏗️ Capturing build results...")
        
        build_commands = [
            ("react_build", ["npm", "run", "build"], "web_dashboard/quantum-dashboard"),
            ("python_test", ["python", "-m", "pytest", "tests/", "-v"], "."),
        ]
        
        build_results = {}
        for name, cmd, cwd in build_commands:
            try:
                print(f"  - Running {name}...")
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=300,
                    cwd=cwd if os.path.exists(cwd) else None
                )
                
                build_results[name] = {
                    "command": " ".join(cmd),
                    "cwd": cwd,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                    "success": result.returncode == 0
                }
                
                # Ayrı dosyalara kaydet
                with open(self.output_dir / f"build_{name}_{self.timestamp}.txt", 'w') as f:
                    f.write(f"Command: {' '.join(cmd)}\n")
                    f.write(f"Working Directory: {cwd}\n")
                    f.write(f"Return Code: {result.returncode}\n")
                    f.write("--- STDOUT ---\n")
                    f.write(result.stdout)
                    f.write("\n--- STDERR ---\n")
                    f.write(result.stderr)
                    
            except Exception as e:
                build_results[name] = {"error": str(e)}
        
        with open(self.output_dir / f"build_results_{self.timestamp}.json", 'w') as f:
            json.dump(build_results, f, indent=2)
        
        return build_results
    
    def capture_file_structure(self):
        """Proje dosya yapısını yakala"""
        print("📁 Capturing file structure...")
        
        def get_tree_structure(path, prefix="", max_depth=3, current_depth=0):
            if current_depth > max_depth:
                return []
            
            items = []
            try:
                path_obj = Path(path)
                if not path_obj.exists():
                    return items
                
                entries = sorted(path_obj.iterdir(), key=lambda x: (x.is_file(), x.name))
                
                for i, entry in enumerate(entries):
                    if entry.name.startswith('.') and entry.name not in ['.github', '.gitignore']:
                        continue
                    
                    is_last = i == len(entries) - 1
                    current_prefix = "└── " if is_last else "├── "
                    items.append(f"{prefix}{current_prefix}{entry.name}")
                    
                    if entry.is_dir() and entry.name not in ['venv', '__pycache__', 'node_modules', '.git', 'build']:
                        extension = "    " if is_last else "│   "
                        items.extend(get_tree_structure(
                            entry, 
                            prefix + extension, 
                            max_depth, 
                            current_depth + 1
                        ))
            except PermissionError:
                pass
            
            return items
        
        tree_structure = get_tree_structure(".")
        
        with open(self.output_dir / f"file_structure_{self.timestamp}.txt", 'w') as f:
            f.write("Quantum Memory Compiler - Project Structure\n")
            f.write("=" * 50 + "\n\n")
            f.write(".\n")
            for line in tree_structure:
                f.write(line + "\n")
        
        return tree_structure
    
    def generate_summary_report(self, all_results):
        """Özet rapor oluştur"""
        print("📋 Generating summary report...")
        
        report = []
        report.append("# Quantum Memory Compiler - Output Capture Summary")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Timestamp:** {self.timestamp}")
        report.append("")
        
        # System info
        if 'system_info' in all_results:
            info = all_results['system_info']
            report.append("## 🖥️ System Information")
            report.append(f"- **Python Version:** {info.get('python_version', 'Unknown')}")
            report.append(f"- **Platform:** {info.get('platform', {}).get('system', 'Unknown')}")
            report.append(f"- **CPU Cores:** {info.get('cpu_count', 'Unknown')}")
            report.append(f"- **Memory:** {info.get('memory_total', 0) // (1024**3)} GB")
            report.append("")
        
        # CLI Results
        if 'cli_results' in all_results:
            report.append("## 🖥️ CLI Output Status")
            for name, result in all_results['cli_results'].items():
                status = "✅ Success" if result.get('returncode') == 0 else "❌ Failed"
                report.append(f"- **{name.title()}:** {status}")
            report.append("")
        
        # API Status
        if 'api_results' in all_results:
            report.append("## 🔗 API Endpoint Status")
            for name, result in all_results['api_results'].items():
                if 'error' in result:
                    status = "❌ Error"
                elif result.get('status_code') == 200:
                    status = "✅ Online"
                else:
                    status = f"⚠️ Status {result.get('status_code', 'Unknown')}"
                report.append(f"- **{name.title()}:** {status}")
            report.append("")
        
        # Performance
        if 'performance_data' in all_results:
            perf = all_results['performance_data']
            report.append("## 📊 Performance Metrics")
            report.append(f"- **Average Memory Usage:** {perf.get('avg_memory', 0):.1f}%")
            report.append(f"- **Average CPU Usage:** {perf.get('avg_cpu', 0):.1f}%")
            report.append(f"- **Peak Memory Usage:** {perf.get('max_memory', 0):.1f}%")
            report.append(f"- **Peak CPU Usage:** {perf.get('max_cpu', 0):.1f}%")
            report.append("")
        
        # Build Results
        if 'build_results' in all_results:
            report.append("## 🏗️ Build Status")
            for name, result in all_results['build_results'].items():
                if 'error' in result:
                    status = "❌ Error"
                elif result.get('success'):
                    status = "✅ Success"
                else:
                    status = "❌ Failed"
                report.append(f"- **{name.replace('_', ' ').title()}:** {status}")
            report.append("")
        
        # File list
        report.append("## 📁 Generated Files")
        output_files = list(self.output_dir.glob(f"*{self.timestamp}*"))
        for file in sorted(output_files):
            size = file.stat().st_size
            size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
            report.append(f"- `{file.name}` ({size_str})")
        report.append("")
        
        report.append("## 📋 Usage Instructions")
        report.append("Bu dosyalar raporunuzda şu şekilde kullanılabilir:")
        report.append("- JSON dosyaları → Kod blokları olarak")
        report.append("- PNG dosyaları → Görsel olarak")
        report.append("- TXT dosyaları → Terminal çıktıları olarak")
        
        with open(self.output_dir / f"SUMMARY_REPORT_{self.timestamp}.md", 'w') as f:
            f.write("\n".join(report))
        
        return report

def main():
    """Ana capture fonksiyonu"""
    print("🚀 Quantum Memory Compiler - Output Capture Started")
    print("=" * 60)
    
    capture = OutputCapture()
    all_results = {}
    
    try:
        # Sırayla tüm çıktıları yakala
        all_results['system_info'] = capture.capture_system_info()
        all_results['cli_results'] = capture.capture_cli_outputs()
        all_results['api_results'] = capture.capture_api_status()
        all_results['performance_data'] = capture.capture_performance_metrics()
        all_results['build_results'] = capture.capture_build_results()
        all_results['file_structure'] = capture.capture_file_structure()
        
        # Özet rapor oluştur
        summary = capture.generate_summary_report(all_results)
        
        print("\n" + "=" * 60)
        print("✅ Output capture completed successfully!")
        print(f"📁 Results saved in: {capture.output_dir}")
        print(f"📋 Summary report: SUMMARY_REPORT_{capture.timestamp}.md")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during capture: {e}")
        return False

if __name__ == "__main__":
    main() 