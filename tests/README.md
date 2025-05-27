# Quantum Memory Compiler - Test Suite 🧪

Bu klasör Quantum Memory Compiler projesinin test dosyalarını içerir.

## 📋 Test Dosyaları

### 🔧 API Tests
- **`test_api_simulation_fix.py`** - API simulation ve compilation endpoint'lerini test eder
- **`simple_api_test.py`** - Basit API test server (Port 5002)
- **`test_api_client.py`** - API client fonksiyonlarını test eder

### 🧪 Core Tests
- **`test_simulator_direct.py`** - Simulator'ı doğrudan test eder
- **`test_logging_system.py`** - Logging sistemini test eder
- **`test_version_2_2_0.py`** - v2.2.0 özelliklerini kapsamlı test eder

### ⚡ Performance Tests
- **`test_gpu_acceleration.py`** - GPU acceleration'ı test eder
- **`comprehensive_gpu_test.py`** - Kapsamlı GPU performans testleri

### 🌐 Integration Tests
- **`test_ibm_quantum_simple.py`** - IBM Quantum entegrasyonunu test eder

### 📊 Test Data
- **`test_logs_export.json`** - Test log verileri
- **`test_logs/`** - Test log dosyaları

## 🚀 Test Çalıştırma

### API Testleri
```bash
# API server'ın çalıştığından emin olun (Port 5001)
python tests/test_api_simulation_fix.py

# Basit API test server
python tests/simple_api_test.py
```

### Core Testleri
```bash
# Simulator testleri
python tests/test_simulator_direct.py

# Logging sistem testleri
python tests/test_logging_system.py

# Kapsamlı v2.2.0 testleri
python tests/test_version_2_2_0.py
```

### Performance Testleri
```bash
# GPU acceleration testleri
python tests/test_gpu_acceleration.py

# Kapsamlı GPU testleri
python tests/comprehensive_gpu_test.py
```

### Integration Testleri
```bash
# IBM Quantum testleri (Token gerekli)
python tests/test_ibm_quantum_simple.py
```

## 📝 Test Sonuçları

Test sonuçları `test_logs/` klasöründe saklanır. JSON formatında export edilen loglar `test_logs_export.json` dosyasında bulunur.

## 🔧 Test Geliştirme

Yeni test dosyaları eklerken:
1. `test_` prefix'i kullanın
2. Açıklayıcı docstring'ler ekleyin
3. Error handling ekleyin
4. Test sonuçlarını logla

---

**Son Güncelleme**: Ocak 2025  
**Test Coverage**: 85%+ 