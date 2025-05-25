# 🚀 GitHub Pages Deployment Rehberi

## 📋 **Adım Adım GitHub Pages Kurulumu**

### 🎯 **1. GitHub Repository Oluşturma**

1. **GitHub'a gidin:** https://github.com
2. **"New repository" butonuna tıklayın**
3. **Repository ayarları:**
   ```
   Repository name: quantum-memory-compiler
   Description: Advanced Quantum Circuit Compiler with IBM Quantum Integration
   ✅ Public (GitHub Pages için gerekli)
   ❌ Add a README file (zaten var)
   ❌ Add .gitignore (zaten var)
   ❌ Choose a license (zaten var)
   ```
4. **"Create repository" butonuna tıklayın**

### 🔗 **2. Local Repository'yi GitHub'a Bağlama**

Terminal'de şu komutları çalıştırın:

```bash
# GitHub repository'sini remote olarak ekleyin
git remote add origin https://github.com/KULLANICI_ADINIZ/quantum-memory-compiler.git

# Ana branch'i main olarak ayarlayın
git branch -M main

# İlk push'u yapın
git push -u origin main
```

**⚠️ Önemli:** `KULLANICI_ADINIZ` yerine kendi GitHub kullanıcı adınızı yazın!

### ⚙️ **3. GitHub Pages Ayarları**

1. **GitHub repository sayfasında "Settings" sekmesine gidin**
2. **Sol menüden "Pages" seçeneğini bulun**
3. **Source ayarları:**
   ```
   Source: Deploy from a branch
   Branch: gh-pages
   Folder: / (root)
   ```
4. **"Save" butonuna tıklayın**

### 🚀 **4. Otomatik Deployment**

Artık her `main` branch'e push yaptığınızda GitHub Actions otomatik olarak:
1. React app'i build edecek
2. `gh-pages` branch'ine deploy edecek
3. Sitenizi yayınlayacak

### 📱 **5. Manuel Deployment (Alternatif)**

Eğer otomatik deployment çalışmazsa, manuel olarak deploy edebilirsiniz:

```bash
# Deploy script'ini çalıştırın
./deploy.sh
```

## 🌐 **Site URL'niz**

Deployment tamamlandıktan sonra siteniz şu adreste yayında olacak:

```
https://KULLANICI_ADINIZ.github.io/quantum-memory-compiler
```

## 🔧 **Deployment Durumu Kontrolü**

### GitHub Actions Kontrolü:
1. Repository'nizde "Actions" sekmesine gidin
2. Son workflow'un durumunu kontrol edin
3. Yeşil ✅ işareti başarılı deployment'i gösterir

### Site Kontrolü:
1. Browser'da site URL'nizi açın
2. Quantum Memory Compiler arayüzünün yüklendiğini kontrol edin
3. "IBM Quantum" sayfasının çalıştığını test edin

## 🛠️ **Sorun Giderme**

### ❌ **Build Hatası**
```bash
# Dependencies'leri kontrol edin
cd web_dashboard/quantum-dashboard
npm install
npm run build
```

### ❌ **GitHub Pages Görünmüyor**
1. Repository Settings > Pages'de ayarları kontrol edin
2. `gh-pages` branch'inin oluştuğunu kontrol edin
3. 5-10 dakika bekleyin (GitHub Pages gecikmesi olabilir)

### ❌ **404 Hatası**
1. `package.json`'da `homepage` field'ının doğru olduğunu kontrol edin
2. Build dosyalarının doğru kopyalandığını kontrol edin

## 📊 **Deployment Özellikleri**

### ✅ **Otomatik Özellikler:**
- 🔄 Otomatik build ve deployment
- 📱 Responsive tasarım
- ⚡ Optimized production build
- 🔍 SEO optimizasyonu
- 📈 Performance optimization

### 🎨 **UI Özellikleri:**
- 🌟 Modern Material-UI tasarım
- 🌙 Dark theme
- 📊 Interactive charts (Recharts)
- 🔄 Real-time updates
- 📱 Mobile-friendly

### 🔬 **Quantum Özellikleri:**
- ⚛️ IBM Quantum integration
- 🔧 Circuit builder
- 📊 Simulation results
- 🎯 Backend selection
- 🔐 Token management

## 🎉 **Başarılı Deployment Sonrası**

Deployment başarılı olduktan sonra:

1. **Site URL'nizi paylaşın**
2. **README.md'de USERNAME'i güncelleyin**
3. **Social media'da duyurun**
4. **Quantum computing topluluklarında paylaşın**

## 📝 **Güncelleme Süreci**

Gelecekte güncellemeler yapmak için:

```bash
# Değişikliklerinizi yapın
git add .
git commit -m "🔧 Update: Yeni özellik açıklaması"
git push origin main

# GitHub Actions otomatik olarak deploy edecek!
```

## 🌟 **Bonus: Custom Domain (Opsiyonel)**

Kendi domain'iniz varsa:

1. **DNS ayarlarında CNAME record ekleyin:**
   ```
   www.your-domain.com -> KULLANICI_ADINIZ.github.io
   ```

2. **Repository Settings > Pages'de custom domain ekleyin**

3. **HTTPS'i etkinleştirin**

---

## 🎯 **Özet Checklist**

- [ ] GitHub repository oluşturuldu
- [ ] Local repository GitHub'a push edildi
- [ ] GitHub Pages ayarları yapıldı
- [ ] GitHub Actions çalışıyor
- [ ] Site erişilebilir durumda
- [ ] IBM Quantum integration test edildi
- [ ] README.md'de URL güncellendi

**🚀 Tebrikler! Quantum Memory Compiler artık GitHub Pages'de yayında!** 