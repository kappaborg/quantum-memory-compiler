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
Quantum Memory Compiler - Logging System
========================================

Kapsamlı logging ve error handling sistemi.

Developer: kappasutra
"""

import logging
import sys
import os
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
from enum import Enum

class LogLevel(Enum):
    """Log seviyeleri"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogCategory(Enum):
    """Log kategorileri"""
    SIMULATION = "SIMULATION"
    COMPILATION = "COMPILATION"
    MEMORY = "MEMORY"
    API = "API"
    VISUALIZATION = "VISUALIZATION"
    ACCELERATION = "ACCELERATION"
    SYSTEM = "SYSTEM"
    USER = "USER"

class QuantumLogger:
    """
    Quantum Memory Compiler için özelleştirilmiş logger
    """
    
    def __init__(self, name: str = "QuantumMemoryCompiler", log_dir: str = "logs"):
        """
        Logger'ı initialize eder
        
        Args:
            name: Logger adı
            log_dir: Log dosyalarının saklanacağı dizin
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Ana logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Formatter
        self.formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handlers
        self._setup_handlers()
        
        # Session info
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_start = datetime.now()
        
        # Statistics
        self.stats = {
            "total_logs": 0,
            "errors": 0,
            "warnings": 0,
            "simulations": 0,
            "compilations": 0
        }
        
        self.info("🚀 Quantum Memory Compiler Logger initialized", LogCategory.SYSTEM)
    
    def _setup_handlers(self):
        """Handler'ları setup eder"""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)
        
        # File handler - genel log
        general_log = self.log_dir / f"quantum_compiler_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(general_log)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
        
        # Error handler - sadece error'lar
        error_log = self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(error_log)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self.formatter)
        self.logger.addHandler(error_handler)
    
    def _log(self, level: LogLevel, message: str, category: LogCategory = LogCategory.SYSTEM, 
             extra_data: Optional[Dict[str, Any]] = None):
        """
        Internal log metodu
        
        Args:
            level: Log seviyesi
            message: Log mesajı
            category: Log kategorisi
            extra_data: Ek veri
        """
        # Statistics güncelle
        self.stats["total_logs"] += 1
        if level == LogLevel.ERROR:
            self.stats["errors"] += 1
        elif level == LogLevel.WARNING:
            self.stats["warnings"] += 1
        
        if category == LogCategory.SIMULATION:
            self.stats["simulations"] += 1
        elif category == LogCategory.COMPILATION:
            self.stats["compilations"] += 1
        
        # Log mesajını formatla
        formatted_message = f"[{category.value}] {message}"
        
        if extra_data:
            formatted_message += f" | Data: {json.dumps(extra_data, default=str)}"
        
        # Log seviyesine göre log
        if level == LogLevel.DEBUG:
            self.logger.debug(formatted_message)
        elif level == LogLevel.INFO:
            self.logger.info(formatted_message)
        elif level == LogLevel.WARNING:
            self.logger.warning(formatted_message)
        elif level == LogLevel.ERROR:
            self.logger.error(formatted_message)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(formatted_message)
    
    def debug(self, message: str, category: LogCategory = LogCategory.SYSTEM, 
              extra_data: Optional[Dict[str, Any]] = None):
        """Debug log"""
        self._log(LogLevel.DEBUG, message, category, extra_data)
    
    def info(self, message: str, category: LogCategory = LogCategory.SYSTEM, 
             extra_data: Optional[Dict[str, Any]] = None):
        """Info log"""
        self._log(LogLevel.INFO, message, category, extra_data)
    
    def warning(self, message: str, category: LogCategory = LogCategory.SYSTEM, 
                extra_data: Optional[Dict[str, Any]] = None):
        """Warning log"""
        self._log(LogLevel.WARNING, message, category, extra_data)
    
    def error(self, message: str, category: LogCategory = LogCategory.SYSTEM, 
              extra_data: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None):
        """Error log"""
        if exception:
            extra_data = extra_data or {}
            extra_data["exception"] = str(exception)
            extra_data["traceback"] = traceback.format_exc()
        
        self._log(LogLevel.ERROR, message, category, extra_data)
    
    def critical(self, message: str, category: LogCategory = LogCategory.SYSTEM, 
                 extra_data: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None):
        """Critical log"""
        if exception:
            extra_data = extra_data or {}
            extra_data["exception"] = str(exception)
            extra_data["traceback"] = traceback.format_exc()
        
        self._log(LogLevel.CRITICAL, message, category, extra_data)
    
    def log_simulation_start(self, circuit_name: str, shots: int, qubits: int):
        """Simulation başlangıcını log'lar"""
        self.info(f"🔬 Simulation started: {circuit_name} ({qubits} qubits, {shots} shots)", 
                 LogCategory.SIMULATION, 
                 {"circuit_name": circuit_name, "shots": shots, "qubits": qubits})
    
    def log_simulation_end(self, circuit_name: str, execution_time: float, results: Dict[str, Any]):
        """Simulation sonunu log'lar"""
        self.info(f"✅ Simulation completed: {circuit_name} ({execution_time:.3f}s)", 
                 LogCategory.SIMULATION,
                 {"circuit_name": circuit_name, "execution_time": execution_time, "results": results})
    
    def log_compilation_start(self, circuit_name: str, strategy: str):
        """Compilation başlangıcını log'lar"""
        self.info(f"⚙️ Compilation started: {circuit_name} (strategy: {strategy})", 
                 LogCategory.COMPILATION,
                 {"circuit_name": circuit_name, "strategy": strategy})
    
    def log_compilation_end(self, circuit_name: str, execution_time: float, metrics: Dict[str, Any]):
        """Compilation sonunu log'lar"""
        self.info(f"✅ Compilation completed: {circuit_name} ({execution_time:.3f}s)", 
                 LogCategory.COMPILATION,
                 {"circuit_name": circuit_name, "execution_time": execution_time, "metrics": metrics})
    
    def log_api_request(self, endpoint: str, method: str, client_ip: str = "unknown"):
        """API request'ini log'lar"""
        self.info(f"📡 API Request: {method} {endpoint} from {client_ip}", 
                 LogCategory.API,
                 {"endpoint": endpoint, "method": method, "client_ip": client_ip})
    
    def log_memory_usage(self, component: str, memory_mb: float, peak_memory_mb: float = None):
        """Memory usage'ı log'lar"""
        extra_data = {"component": component, "memory_mb": memory_mb}
        if peak_memory_mb:
            extra_data["peak_memory_mb"] = peak_memory_mb
        
        self.debug(f"💾 Memory usage: {component} - {memory_mb:.2f} MB", 
                  LogCategory.MEMORY, extra_data)
    
    def log_acceleration_status(self, gpu_available: bool, device_count: int, memory_gb: float):
        """GPU acceleration status'unu log'lar"""
        status = "enabled" if gpu_available else "disabled"
        self.info(f"🚀 GPU Acceleration: {status} ({device_count} devices, {memory_gb:.1f} GB)", 
                 LogCategory.ACCELERATION,
                 {"gpu_available": gpu_available, "device_count": device_count, "memory_gb": memory_gb})
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Session istatistiklerini döndürür"""
        session_duration = (datetime.now() - self.session_start).total_seconds()
        
        return {
            "session_id": self.session_id,
            "session_start": self.session_start.isoformat(),
            "session_duration_seconds": session_duration,
            "statistics": self.stats.copy()
        }
    
    def export_logs(self, output_file: str = None) -> str:
        """Log'ları export eder"""
        if not output_file:
            output_file = f"quantum_logs_export_{self.session_id}.json"
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "session_info": self.get_session_stats(),
            "log_files": [
                str(f) for f in self.log_dir.glob("*.log")
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.info(f"📤 Logs exported to {output_file}", LogCategory.SYSTEM)
        return output_file

# Global logger instance
_global_logger = None

def get_logger() -> QuantumLogger:
    """Global logger instance'ını döndürür"""
    global _global_logger
    if _global_logger is None:
        _global_logger = QuantumLogger()
    return _global_logger

def setup_logging(log_dir: str = "logs", log_level: str = "INFO"):
    """Logging sistemini setup eder"""
    global _global_logger
    _global_logger = QuantumLogger(log_dir=log_dir)
    
    # Log level'ı ayarla
    if hasattr(logging, log_level.upper()):
        _global_logger.logger.setLevel(getattr(logging, log_level.upper()))
    
    return _global_logger

# Convenience functions
def log_info(message: str, category: LogCategory = LogCategory.SYSTEM, extra_data: Dict[str, Any] = None):
    """Convenience function for info logging"""
    get_logger().info(message, category, extra_data)

def log_error(message: str, category: LogCategory = LogCategory.SYSTEM, 
              extra_data: Dict[str, Any] = None, exception: Exception = None):
    """Convenience function for error logging"""
    get_logger().error(message, category, extra_data, exception)

def log_warning(message: str, category: LogCategory = LogCategory.SYSTEM, extra_data: Dict[str, Any] = None):
    """Convenience function for warning logging"""
    get_logger().warning(message, category, extra_data)

def log_debug(message: str, category: LogCategory = LogCategory.SYSTEM, extra_data: Dict[str, Any] = None):
    """Convenience function for debug logging"""
    get_logger().debug(message, category, extra_data) 