#!/usr/bin/env python3
"""
Logging System Test
==================

Quantum Memory Compiler logging sistemini test eder.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'quantum_memory_compiler'))

from quantum_memory_compiler.utils.logger import (
    QuantumLogger, LogCategory, get_logger, setup_logging,
    log_info, log_error, log_warning, log_debug
)

def test_logging_system():
    """Logging sistemini test eder"""
    
    print("🧪 Testing Quantum Memory Compiler Logging System")
    print("=" * 60)
    
    # Setup logging
    logger = setup_logging(log_dir="test_logs", log_level="DEBUG")
    
    # Test basic logging
    print("\n📝 Testing basic logging...")
    log_info("This is an info message", LogCategory.SYSTEM)
    log_warning("This is a warning message", LogCategory.API)
    log_debug("This is a debug message", LogCategory.SIMULATION)
    
    # Test error logging with exception
    print("\n❌ Testing error logging...")
    try:
        raise ValueError("Test exception for logging")
    except Exception as e:
        log_error("Test error occurred", LogCategory.SYSTEM, exception=e)
    
    # Test simulation logging
    print("\n🔬 Testing simulation logging...")
    logger.log_simulation_start("Bell State Circuit", 1024, 2)
    logger.log_simulation_end("Bell State Circuit", 0.125, {"00": 0.5, "11": 0.5})
    
    # Test compilation logging
    print("\n⚙️ Testing compilation logging...")
    logger.log_compilation_start("Test Circuit", "balanced")
    logger.log_compilation_end("Test Circuit", 0.089, {
        "original_gates": 10,
        "compiled_gates": 8,
        "reduction": "20%"
    })
    
    # Test API logging
    print("\n📡 Testing API logging...")
    logger.log_api_request("/api/circuit/simulate", "POST", "127.0.0.1")
    
    # Test memory logging
    print("\n💾 Testing memory logging...")
    logger.log_memory_usage("Simulator", 256.5, 512.0)
    
    # Test acceleration logging
    print("\n🚀 Testing acceleration logging...")
    logger.log_acceleration_status(True, 1, 4.0)
    
    # Test with extra data
    print("\n📊 Testing with extra data...")
    log_info("Circuit created successfully", LogCategory.SIMULATION, {
        "circuit_name": "Test Circuit",
        "qubits": 4,
        "gates": 15,
        "depth": 8
    })
    
    # Get session stats
    print("\n📈 Session Statistics:")
    stats = logger.get_session_stats()
    for key, value in stats.items():
        if key == "statistics":
            print(f"  {key}:")
            for stat_key, stat_value in value.items():
                print(f"    {stat_key}: {stat_value}")
        else:
            print(f"  {key}: {value}")
    
    # Export logs
    print("\n📤 Exporting logs...")
    export_file = logger.export_logs("test_logs_export.json")
    print(f"✅ Logs exported to: {export_file}")
    
    print("\n🎉 Logging system test completed!")
    print("📁 Check the 'test_logs' directory for log files")

if __name__ == "__main__":
    test_logging_system() 