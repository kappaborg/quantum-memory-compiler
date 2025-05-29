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
IBM Quantum Web Entegrasyonu Demo
=================================

Bu script IBM Quantum web entegrasyonunu test eder ve demo yapar.

Developer: kappasutra
"""

import time
import json
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

console = Console()

API_BASE_URL = "http://localhost:5001"

def check_api_server():
    """API sunucusunun çalışıp çalışmadığını kontrol et"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/info", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_ibm_status():
    """IBM Quantum durumunu al"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/ibm/status")
        return response.json()
    except Exception as e:
        console.print(f"[red]❌ IBM Quantum durumu alınamadı: {e}[/red]")
        return None

def get_backends():
    """IBM Quantum backend'lerini al"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/ibm/backends")
        return response.json()
    except Exception as e:
        console.print(f"[red]❌ Backend'ler alınamadı: {e}[/red]")
        return None

def execute_test_circuit(backend_name="qasm_simulator"):
    """Test devresi çalıştır"""
    test_circuit = {
        "name": "demo_circuit",
        "qubits": 2,
        "gates": [
            {"type": "H", "qubits": [0]},
            {"type": "CNOT", "qubits": [0, 1]}
        ],
        "measurements": [
            {"qubit": 0, "classical_bit": 0},
            {"qubit": 1, "classical_bit": 1}
        ]
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/ibm/execute", json={
            "circuit": test_circuit,
            "backend": backend_name,
            "shots": 1024,
            "optimization_level": 1,
            "monitor": False
        })
        return response.json()
    except Exception as e:
        console.print(f"[red]❌ Devre çalıştırılamadı: {e}[/red]")
        return None

def display_status(status):
    """IBM Quantum durumunu göster"""
    if not status:
        return
    
    table = Table(title="IBM Quantum Durumu")
    table.add_column("Özellik", style="cyan")
    table.add_column("Durum", style="green" if status.get('integration_ready') else "red")
    
    table.add_row("Qiskit Mevcut", "✅ Evet" if status.get('qiskit_available') else "❌ Hayır")
    if status.get('qiskit_version'):
        table.add_row("Qiskit Versiyonu", status['qiskit_version'])
    table.add_row("Token Sağlandı", "✅ Evet" if status.get('token_provided') else "❌ Hayır")
    table.add_row("IBM Quantum Bağlı", "✅ Evet" if status.get('connected') else "❌ Hayır")
    table.add_row("Entegrasyon Hazır", "✅ Evet" if status.get('integration_ready') else "❌ Hayır")
    
    console.print(table)

def display_backends(backends_data):
    """Backend'leri göster"""
    if not backends_data or not backends_data.get('backends'):
        console.print("[yellow]⚠️  Backend bulunamadı[/yellow]")
        return
    
    backends = backends_data['backends']
    
    table = Table(title=f"Mevcut Backend'ler ({len(backends)})")
    table.add_column("İsim", style="cyan")
    table.add_column("Tip", style="magenta")
    table.add_column("Qubit", justify="center")
    table.add_column("Durum", style="green")
    table.add_column("Bekleyen İş", justify="center")
    
    for backend in backends:
        backend_type = "🖥️  Simülatör" if backend['simulator'] else "⚛️  Donanım"
        status = "✅ Aktif" if backend['operational'] else "❌ Bakımda"
        
        table.add_row(
            backend['name'],
            backend_type,
            str(backend['num_qubits']),
            status,
            str(backend['pending_jobs'])
        )
    
    console.print(table)
    return backends

def display_results(result):
    """Çalıştırma sonuçlarını göster"""
    if not result:
        return
    
    if result.get('success'):
        console.print(Panel.fit(
            f"[green]✅ Başarılı![/green]\n\n"
            f"🆔 Job ID: {result.get('job_id', 'N/A')}\n"
            f"🖥️  Backend: {result.get('backend', 'N/A')}\n"
            f"🎯 Shots: {result.get('shots', 'N/A')}\n"
            f"⏱️  Çalışma Süresi: {result.get('execution_time', 0):.2f}s\n"
            f"⏳ Kuyruk Süresi: {result.get('queue_time', 0):.2f}s",
            title="Çalıştırma Sonucu"
        ))
        
        # Ölçüm sonuçlarını göster
        results = result.get('results', {})
        if results:
            table = Table(title="Ölçüm Sonuçları")
            table.add_column("Durum", style="cyan")
            table.add_column("Sayı", justify="center")
            table.add_column("Olasılık", justify="center", style="green")
            
            total_shots = sum(results.values())
            for state, count in sorted(results.items(), key=lambda x: x[1], reverse=True):
                probability = (count / total_shots) * 100
                table.add_row(state, str(count), f"{probability:.1f}%")
            
            console.print(table)
    else:
        console.print(Panel.fit(
            f"[red]❌ Başarısız![/red]\n\n"
            f"Hata: {result.get('error_message', 'Bilinmeyen hata')}",
            title="Çalıştırma Sonucu"
        ))

def main():
    """Ana demo fonksiyonu"""
    console.print(Panel.fit(
        "[bold blue]🚀 IBM Quantum Web Entegrasyonu Demo[/bold blue]\n\n"
        "Bu demo IBM Quantum bağlantısını test eder ve\n"
        "web arayüzü özelliklerini gösterir.",
        title="Quantum Memory Compiler"
    ))
    
    # API sunucusu kontrolü
    console.print("\n[yellow]🔍 API sunucusu kontrol ediliyor...[/yellow]")
    if not check_api_server():
        console.print(Panel.fit(
            "[red]❌ API sunucusu çalışmıyor![/red]\n\n"
            "Lütfen önce API sunucusunu başlatın:\n"
            "[cyan]python -m quantum_memory_compiler.api[/cyan]",
            title="Hata"
        ))
        return
    
    console.print("[green]✅ API sunucusu çalışıyor[/green]")
    
    # IBM Quantum durumu
    console.print("\n[yellow]🔍 IBM Quantum durumu kontrol ediliyor...[/yellow]")
    status = get_ibm_status()
    display_status(status)
    
    if not status or not status.get('qiskit_available'):
        console.print(Panel.fit(
            "[red]❌ Qiskit yüklü değil![/red]\n\n"
            "Lütfen Qiskit'i yükleyin:\n"
            "[cyan]pip install qiskit[/cyan]",
            title="Gereksinim"
        ))
        return
    
    # Backend'leri al
    console.print("\n[yellow]🔍 Backend'ler yükleniyor...[/yellow]")
    backends_data = get_backends()
    backends = display_backends(backends_data)
    
    if not backends:
        console.print("[yellow]⚠️  Backend bulunamadı, simülasyon modu kullanılacak[/yellow]")
        backends = [{"name": "qasm_simulator", "simulator": True, "operational": True}]
    
    # Test devresi çalıştırma
    if Confirm.ask("\n🚀 Test devresi çalıştırmak ister misiniz?"):
        # Backend seçimi
        available_backends = [b for b in backends if b.get('operational', True)]
        
        if len(available_backends) > 1:
            console.print("\n📋 Mevcut backend'ler:")
            for i, backend in enumerate(available_backends):
                backend_type = "Simülatör" if backend.get('simulator') else "Donanım"
                console.print(f"  {i+1}. {backend['name']} ({backend_type})")
            
            choice = Prompt.ask(
                "Backend seçin",
                choices=[str(i+1) for i in range(len(available_backends))],
                default="1"
            )
            selected_backend = available_backends[int(choice)-1]['name']
        else:
            selected_backend = available_backends[0]['name']
        
        console.print(f"\n[cyan]🎯 Seçilen backend: {selected_backend}[/cyan]")
        
        # Çalıştırma
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Test devresi çalıştırılıyor...", total=None)
            result = execute_test_circuit(selected_backend)
        
        display_results(result)
    
    # Web arayüzü bilgisi
    console.print(Panel.fit(
        "[bold green]🌐 Web Arayüzü[/bold green]\n\n"
        "Web dashboard'unu kullanmak için:\n"
        "1. [cyan]http://localhost:3000[/cyan] adresini açın\n"
        "2. Sol menüden 'IBM Quantum' seçin\n"
        "3. API token'ınızı ayarlayın\n"
        "4. Backend'leri görüntüleyin ve test edin\n\n"
        "Detaylı kılavuz: [cyan]IBM_QUANTUM_WEB_GUIDE.md[/cyan]",
        title="Sonraki Adımlar"
    ))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Demo sonlandırıldı[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Beklenmeyen hata: {e}[/red]") 