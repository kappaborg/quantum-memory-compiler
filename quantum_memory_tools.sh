#!/bin/bash
# Quantum Memory Compiler Araçları
# Bu script, Quantum Memory Compiler'ın tüm temel komutlarını çalıştırır ve çıktılarını gösterir

echo "==============================================================="
echo "QUANTUM MEMORY COMPILER ARAÇLARI"
echo "==============================================================="
echo

# Remove unused files
echo ">> Cleaning process started..."
pkill -f "python -c.*run_api_server" 2>/dev/null || true
rm -f examples/test_circuit.qmc 2>/dev/null || true

# Create test circuit
echo -e "\n>> Test circuit creating..."
python create_test_circuit.py

# Visualizing
echo -e "\n>> Visualizing..."
echo "$ qmc visualize test_circuit.qmc --output circuit_visual.png"
qmc visualize test_circuit.qmc --output circuit_visual.png
echo "Görselleştirme dosyası: circuit_visual.png"

# Simulating
echo -e "\n>> Circuit simulating..."
echo "$ qmc simulate test_circuit.qmc"
qmc simulate test_circuit.qmc

# Compile
echo -e "\n>> Circuit compiling..."
echo "$ qmc compile test_circuit.qmc --output compiled_circuit.qmc"
qmc compile test_circuit.qmc --output compiled_circuit.qmc
echo "Derlenmiş devre dosyası: compiled_circuit.qmc"

# CPU USAGE 
echo -e "\n>> Circuit CPU usage..."
echo "$ qmc profile test_circuit.qmc --output memory_profile.png"
qmc profile test_circuit.qmc --output memory_profile.png 2>/dev/null || echo "Not: Bellek profilleme işlemi desteklenmiyor veya başarısız oldu."

# API Server
echo -e "\n>> API Starting (3 seconds)..."
# If we use 5000 we are taking error in mac ecosystem
echo "$ qmc api --port 5050 --debug"
qmc api --port 5050 --debug & 
API_PID=$!
sleep 3  

# API test requests
echo -e "\n>> Sending requests to API endpoints..."
echo "GET /api/info:"
curl -s http://localhost:5050/api/info | python -m json.tool

echo -e "\n>> POST /api/circuit/simulate endpoint'i test ediliyor:"
curl -s -X POST -H "Content-Type: application/json" -d @test_circuit.qmc http://localhost:5050/api/circuit/simulate | python -m json.tool

# Stop api by signal
echo -e "\n>> Killing API..."
kill $API_PID 2>/dev/null || true

# Örnek listesi
echo -e "\n>> Mevcut örnekler listeleniyor..."
echo "$ qmc examples --list"
qmc examples --list

echo -e "\n==============================================================="
echo "Process Completed"
echo "==============================================================="
echo "Created files:"
echo "- test_circuit.qmc (created circuit)"
echo "- circuit_visual.png (visualization output)"
echo "- compiled_circuit.qmc (compiled circuit)"
echo "- memory_profile.png (CPU profile)"
echo "===============================================================" 