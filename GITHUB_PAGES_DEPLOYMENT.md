# GitHub Pages Deployment Guide 🚀

Bu guide, Quantum Memory Compiler web dashboard'ını GitHub Pages'e deploy etmek için gerekli adımları açıklar.

## 🔐 **Güvenli Token Yönetimi**

### 1. **Local Development**

Local development için `.env` dosyası oluşturun:

```bash
# .env dosyası oluşturun (web_dashboard/quantum-dashboard/.env)
cp web_dashboard/quantum-dashboard/env.example web_dashboard/quantum-dashboard/.env
```

`.env` dosyasını düzenleyin:
```env
# IBM Quantum Configuration
REACT_APP_IBM_QUANTUM_TOKEN=your_actual_token_here
REACT_APP_IBM_QUANTUM_INSTANCE=ibm_quantum
REACT_APP_IBM_QUANTUM_CHANNEL=ibm_quantum

# API Configuration
REACT_APP_API_URL=http://localhost:5001
REACT_APP_DEMO_MODE=false
```

### 2. **GitHub Repository Secrets**

GitHub repository'nizde şu secrets'ları ekleyin:

1. **Repository Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** butonuna tıklayın
3. Şu secrets'ları ekleyin:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `IBM_QUANTUM_TOKEN` | `your_ibm_quantum_token` | IBM Quantum API token |
| `IBM_QUANTUM_INSTANCE` | `ibm_quantum` | IBM Quantum instance |
| `IBM_QUANTUM_CHANNEL` | `ibm_quantum` | IBM Quantum channel |
| `REACT_APP_API_URL` | `https://your-api-server.com` | API server URL (opsiyonel) |
| `REACT_APP_DEMO_MODE` | `false` | Demo mode (opsiyonel) |

## 🚀 **GitHub Pages Setup**

### 1. **Repository Settings**

1. **Repository Settings** → **Pages**
2. **Source**: GitHub Actions
3. **Custom domain** (opsiyonel): `your-domain.com`

### 2. **Automatic Deployment**

GitHub Actions workflow otomatik olarak:
- `main` veya `master` branch'e push edildiğinde
- Pull request oluşturulduğunda (build only)
- Web dashboard'ı build eder ve deploy eder

### 3. **Manual Deployment**

Manuel deployment için:

```bash
# Repository'yi clone edin
git clone https://github.com/your-username/quantum-memory-compiler.git
cd quantum-memory-compiler

# Dependencies'leri yükleyin
cd web_dashboard/quantum-dashboard
npm install

# Build edin
npm run build

# GitHub Pages'e deploy edin (gh-pages package gerekli)
npm install -g gh-pages
gh-pages -d build
```

## 🔧 **Configuration Options**

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_GITHUB_PAGES` | `false` | GitHub Pages mode |
| `REACT_APP_API_URL` | `http://localhost:5001` | API server URL |
| `REACT_APP_DEMO_MODE` | `false` | Demo mode |
| `REACT_APP_IBM_QUANTUM_TOKEN` | - | IBM Quantum token |
| `PUBLIC_URL` | `/` | Public URL path |

### Build Configuration

```json
{
  "homepage": "https://your-username.github.io/quantum-memory-compiler",
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d build"
  }
}
```

## 🔒 **Security Best Practices**

### 1. **Token Security**

- ✅ **DO**: Store tokens in GitHub Secrets
- ✅ **DO**: Use environment variables
- ✅ **DO**: Validate token format
- ❌ **DON'T**: Commit tokens to git
- ❌ **DON'T**: Share tokens publicly
- ❌ **DON'T**: Use production tokens in development

### 2. **Access Control**

- IBM Quantum token'ınızı minimal permissions ile oluşturun
- Sadece gerekli backend'lere erişim verin
- Token'ı düzenli olarak rotate edin

### 3. **Environment Separation**

```
Development → Local .env file
Staging     → GitHub Secrets (staging)
Production  → GitHub Secrets (production)
```

## 🌐 **Deployment URLs**

### GitHub Pages URL Format

```
https://your-username.github.io/quantum-memory-compiler/
```

### Custom Domain

```
https://your-domain.com/
```

## 🧪 **Testing Deployment**

### 1. **Local Testing**

```bash
# Build'i test edin
npm run build
npx serve -s build

# http://localhost:3000 adresinde test edin
```

### 2. **GitHub Pages Testing**

1. Repository'ye push edin
2. Actions tab'ında build'i kontrol edin
3. Deploy edilen URL'yi test edin
4. IBM Quantum token'ının çalıştığını doğrulayın

## 🔧 **Troubleshooting**

### Common Issues

1. **Build Fails**
   - Dependencies'leri kontrol edin
   - Environment variables'ları doğrulayın
   - Build logs'ları inceleyin

2. **IBM Quantum Token Not Working**
   - Token format'ını kontrol edin
   - GitHub Secrets'ları doğrulayın
   - Browser console'unu kontrol edin

3. **404 Errors**
   - `PUBLIC_URL` ayarını kontrol edin
   - Routing konfigürasyonunu doğrulayın
   - GitHub Pages settings'i kontrol edin

### Debug Commands

```bash
# Environment variables'ları kontrol edin
echo $REACT_APP_IBM_QUANTUM_TOKEN

# Build output'unu kontrol edin
ls -la build/

# GitHub Pages status'unu kontrol edin
curl -I https://your-username.github.io/quantum-memory-compiler/
```

## 📞 **Support**

Deployment ile ilgili sorunlar için:
1. GitHub Issues'da sorun açın
2. Build logs'ları paylaşın
3. Environment configuration'ınızı kontrol edin

---

**Son Güncelleme**: Ocak 2025  
**Versiyon**: 2.2.0 