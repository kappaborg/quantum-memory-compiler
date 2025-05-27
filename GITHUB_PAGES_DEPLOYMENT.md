# GitHub Pages Deployment Guide

## 🚀 **Automated Deployment Setup**

This guide explains how to deploy the Quantum Memory Compiler dashboard to GitHub Pages with automated CI/CD.

## 📋 **Prerequisites**

1. GitHub repository with the quantum memory compiler code
2. GitHub Pages enabled for the repository
3. Proper repository permissions configured

## ⚙️ **Repository Settings Configuration**

### 1. **Enable GitHub Pages**

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Under **Source**, select **GitHub Actions**
4. Save the settings

### 2. **Configure Repository Permissions**

1. Go to **Settings** → **Actions** → **General**
2. Under **Workflow permissions**, select:
   - ✅ **Read and write permissions**
   - ✅ **Allow GitHub Actions to create and approve pull requests**
3. Click **Save**

### 3. **Set Environment Secrets (Optional)**

If you want to use real IBM Quantum integration:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add the following repository secrets:
   - `IBM_QUANTUM_TOKEN`: Your IBM Quantum token
3. Click **Add secret**

## 🔧 **Workflow Configuration**

The deployment workflow (`.github/workflows/deploy-github-pages.yml`) is configured to:

- ✅ Build the React application with production optimizations
- ✅ Automatically enable demo mode for GitHub Pages
- ✅ Handle CORS and HTTPS issues
- ✅ Deploy to GitHub Pages using official GitHub Actions

### **Environment Variables**

The workflow automatically sets:

```yaml
# GitHub Pages Configuration
REACT_APP_GITHUB_PAGES: true
PUBLIC_URL: /quantum-memory-compiler

# API Configuration (Demo Mode)
REACT_APP_API_URL: demo://api.quantum-memory-compiler.local
REACT_APP_DEMO_MODE: true
REACT_APP_ENV: production

# IBM Quantum Configuration
REACT_APP_IBM_QUANTUM_TOKEN: ${{ secrets.IBM_QUANTUM_TOKEN }}
REACT_APP_IBM_QUANTUM_INSTANCE: ibm_quantum
REACT_APP_IBM_QUANTUM_CHANNEL: ibm_quantum
```

## 🚀 **Deployment Process**

### **Automatic Deployment**

1. Push changes to the `main` branch
2. GitHub Actions automatically triggers the workflow
3. The application is built with production settings
4. Artifacts are uploaded to GitHub Pages
5. The site is deployed and accessible

### **Manual Deployment**

If you need to manually trigger deployment:

1. Go to **Actions** tab in your repository
2. Select **Deploy to GitHub Pages** workflow
3. Click **Run workflow**
4. Select the `main` branch
5. Click **Run workflow**

## 🌐 **Accessing Your Deployed Site**

After successful deployment, your site will be available at:
- `https://[username].github.io/quantum-memory-compiler/`

Replace `[username]` with your GitHub username.

## 🔍 **Troubleshooting**

### **Common Issues and Solutions**

#### **1. Permission Denied Error (403)**

**Error:** `Permission to [username]/quantum-memory-compiler.git denied to github-actions[bot]`

**Solution:**
1. Go to **Settings** → **Actions** → **General**
2. Under **Workflow permissions**, select **Read and write permissions**
3. Enable **Allow GitHub Actions to create and approve pull requests**
4. Save and re-run the workflow

#### **2. Pages Build Failed**

**Error:** Build or deployment fails

**Solution:**
1. Check the **Actions** tab for detailed error logs
2. Ensure all dependencies are properly listed in `package.json`
3. Verify the build completes locally with `npm run build`
4. Check that the `PUBLIC_URL` matches your repository name

#### **3. Site Not Loading Properly**

**Error:** Site loads but features don't work

**Solution:**
1. Check browser console for errors
2. Verify that demo mode is enabled (should show "Demo Mode" in API status)
3. Ensure the `PUBLIC_URL` is correctly set in the workflow

#### **4. IBM Quantum Token Issues**

**Error:** IBM Quantum features not working

**Solution:**
1. Verify the token is correctly set in repository secrets
2. Check that the token has proper permissions
3. The token should be set as `IBM_QUANTUM_TOKEN` in repository secrets

### **Workflow Status Checks**

Monitor deployment status:

1. **Actions Tab**: Shows workflow execution status
2. **Environments**: Shows deployment history and status
3. **Pages Settings**: Shows current deployment source and status

## 📊 **Features Available in Demo Mode**

When deployed to GitHub Pages, the following features are available:

- ✅ **Circuit Editor**: Full circuit design capabilities
- ✅ **Simulation**: Simulated quantum circuit execution
- ✅ **Compilation**: Circuit optimization and compilation
- ✅ **Visualization**: Circuit diagram generation
- ✅ **Live User Counter**: Real-time user activity simulation
- ✅ **IBM Quantum Integration**: Token management (with real token)
- ✅ **Memory Profiling**: Simulated memory usage statistics
- ✅ **GPU Acceleration**: Simulated acceleration metrics

## 🔐 **Security Considerations**

- ✅ Environment variables are properly secured
- ✅ IBM Quantum tokens are stored as encrypted secrets
- ✅ No sensitive data is exposed in the client-side code
- ✅ Demo mode provides full functionality without backend dependencies

## 📝 **Updating the Deployment**

To update your deployed site:

1. Make changes to your code
2. Commit and push to the `main` branch
3. GitHub Actions will automatically rebuild and redeploy
4. Changes will be live within 2-5 minutes

## 🎯 **Performance Optimization**

The deployment includes:

- ✅ Production build optimization
- ✅ Code splitting and lazy loading
- ✅ Gzip compression
- ✅ Source map generation disabled for smaller bundle size
- ✅ Efficient caching strategies

## 📞 **Support**

If you encounter issues:

1. Check the **Actions** tab for detailed logs
2. Review this troubleshooting guide
3. Ensure repository permissions are correctly configured
4. Verify GitHub Pages is enabled with **GitHub Actions** as source

---

**Last Updated:** December 2024
**Workflow Version:** 2.0
**Compatibility:** GitHub Pages, React 18, Node.js 18+ 