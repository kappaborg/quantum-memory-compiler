# IBM Quantum Web Entegrasyonu Kullanım Kılavuzu

## 🚀 Genel Bakış

Bu kılavuz, Quantum Memory Compiler projesinde IBM Quantum bağlantısını web üzerinden nasıl kullanacağınızı açıklar. Web dashboard'u üzerinden IBM Quantum Network'e bağlanabilir, gerçek kuantum donanımlarında devrelerinizi çalıştırabilirsiniz.

## 📋 Gereksinimler

### 1. IBM Quantum Network Hesabı
- [IBM Quantum Network](https://quantum-computing.ibm.com/) hesabı oluşturun
- API token'ınızı alın (Account Settings > API Token)

### 2. Yazılım Gereksinimleri
- Python 3.8+ (Qiskit için)
- Node.js 16+ (React dashboard için)
- Qiskit kütüphanesi (`pip install qiskit`)

## 🔧 Kurulum ve Başlatma

### 1. API Sunucusunu Başlatın
```bash
# Proje ana dizininde
python -m quantum_memory_compiler.api
```
API sunucusu `http://localhost:5001` adresinde çalışacak.

### 2. Web Dashboard'unu Başlatın
```bash
# Web dashboard dizininde
cd web_dashboard/quantum-dashboard
npm install
npm start
```
Web uygulaması `http://localhost:3000` adresinde açılacak.

## 🌐 Web Arayüzünü Kullanma

### 1. IBM Quantum Sayfasına Erişim
- Web dashboard'unda sol menüden **"IBM Quantum"** seçeneğine tıklayın
- IBM Quantum bağlantı durumunu görebilirsiniz

### 2. API Token Ayarlama
1. **"Token Ayarla"** butonuna tıklayın
2. IBM Quantum Network'ten aldığınız API token'ı girin
3. **"Kaydet"** butonuna tıklayın
4. Sistem otomatik olarak bağlantıyı test edecek

### 3. Bağlantı Durumu Kontrolü
Bağlantı durumu kartında şu bilgileri görebilirsiniz:
- **Genel Durum**: Entegrasyonun genel durumu
- **Qiskit**: Qiskit kütüphanesinin versiyonu
- **API Token**: Token'ın mevcut olup olmadığı
- **IBM Quantum**: IBM Quantum Network bağlantısı

### 4. Backend'leri Görüntüleme
Token ayarlandıktan sonra:
- Mevcut IBM Quantum backend'leri tabloda listelenir
- Her backend için şu bilgiler gösterilir:
  - **İsim**: Backend adı
  - **Tip**: Simülatör veya gerçek donanım
  - **Qubit**: Qubit sayısı
  - **Durum**: Operasyonel durumu
  - **Bekleyen İş**: Kuyruktaki iş sayısı

### 5. Test Devresi Çalıştırma
1. Backend tablosunda istediğiniz backend'in yanındaki **▶️** butonuna tıklayın
2. Sistem otomatik olarak basit bir test devresi (H + CNOT) çalıştıracak
3. Sonuçlar popup pencerede gösterilecek:
   - Çalışma süresi
   - Kuyruk süresi
   - Ölçüm sonuçları (grafik olarak)

## 🔬 Özellikler

### Desteklenen İşlemler
- ✅ IBM Quantum Network bağlantısı
- ✅ Backend listesi görüntüleme
- ✅ Gerçek donanım ve simülatör desteği
- ✅ Test devresi çalıştırma
- ✅ Sonuçları grafik olarak görüntüleme
- ✅ Bağlantı durumu izleme

### Backend Türleri
- **Simülatörler**: `qasm_simulator`, `statevector_simulator`
- **Gerçek Donanım**: IBM Quantum işlemcileri (ibmq_lima, ibmq_belem, vb.)

### Güvenlik
- API token'lar güvenli şekilde localStorage'da saklanır
- Token'lar şifrelenerek backend'e gönderilir
- Hassas bilgiler loglanmaz

## 📊 Sonuçları Anlama

### Ölçüm Sonuçları
- **State**: Kuantum durumu (örn: "00", "01", "10", "11")
- **Count**: Bu durumun kaç kez ölçüldüğü
- **Probability**: Bu durumun olasılığı (%)

### Performans Metrikleri
- **Execution Time**: Devrenin çalışma süresi
- **Queue Time**: Kuyrukta bekleme süresi
- **Shots**: Toplam ölçüm sayısı

## 🛠️ Sorun Giderme

### Yaygın Sorunlar

#### 1. "Qiskit yüklü değil" Hatası
```bash
pip install qiskit
```

#### 2. "Token gerekli" Uyarısı
- IBM Quantum Network hesabınızdan API token alın
- Web arayüzünde token'ı ayarlayın

#### 3. "Bağlantı hatası"
- İnternet bağlantınızı kontrol edin
- API token'ın doğru olduğundan emin olun
- IBM Quantum Network servislerinin çalıştığını kontrol edin

#### 4. Backend'ler Görünmüyor
- Token'ın doğru ayarlandığından emin olun
- Sayfayı yenileyin (F5)
- "Yenile" butonuna tıklayın

### Debug Modu
Geliştirici konsolunda (F12) detaylı log mesajlarını görebilirsiniz.

## 🔗 API Endpoints

Web arayüzü şu API endpoint'lerini kullanır:

- `GET /api/ibm/status` - IBM Quantum durumu
- `GET /api/ibm/backends` - Mevcut backend'ler
- `POST /api/ibm/execute` - Devre çalıştırma
- `POST /api/ibm/transpile` - Devre transpile etme

## 📝 Örnek Kullanım Senaryosu

1. **Başlangıç**: Web dashboard'unu açın
2. **Bağlantı**: IBM Quantum sayfasına gidin
3. **Token**: API token'ınızı ayarlayın
4. **Backend Seçimi**: Uygun bir backend seçin
5. **Test**: Test devresi çalıştırın
6. **Sonuçlar**: Ölçüm sonuçlarını inceleyin

## 🎯 İleri Seviye Kullanım

### Özel Devre Çalıştırma
Gelecek güncellemelerde:
- Circuit Editor'den direkt IBM Quantum'a gönderme
- Özel devre parametreleri
- Batch işlem desteği

### Optimizasyon
- Transpilation seviyeleri
- Backend önerisi algoritması
- Maliyet optimizasyonu

## 📞 Destek

Sorunlarınız için:
1. Bu kılavuzu kontrol edin
2. GitHub Issues'da sorun bildirin
3. IBM Quantum Community'ye başvurun

---

**Developer**: kappasutra  
**Version**: 2.2.0  
**Last Updated**: 2024 