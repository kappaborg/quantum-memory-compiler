#!/bin/bash

# GitHub Pages Deployment Script for Quantum Memory Compiler
# Developer: kappasutra

echo "🚀 Starting GitHub Pages Deployment..."

# Check if we're in the right directory
if [ ! -d "web_dashboard/quantum-dashboard" ]; then
    echo "❌ Error: web_dashboard/quantum-dashboard directory not found!"
    echo "   Please run this script from the project root directory."
    exit 1
fi

# Navigate to React app directory
cd web_dashboard/quantum-dashboard

echo "📦 Installing dependencies..."
npm install

echo "🔧 Building React app for production..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build successful!"

# Navigate back to project root
cd ../..

# Check if gh-pages branch exists
if git show-ref --verify --quiet refs/heads/gh-pages; then
    echo "🔄 Switching to gh-pages branch..."
    git checkout gh-pages
else
    echo "🆕 Creating gh-pages branch..."
    git checkout --orphan gh-pages
fi

# Clear the branch
git rm -rf . 2>/dev/null || true

# Copy build files
echo "📋 Copying build files..."
cp -r web_dashboard/quantum-dashboard/build/* .

# Create CNAME file if you have a custom domain (optional)
# echo "your-domain.com" > CNAME

# Create .nojekyll file to bypass Jekyll processing
touch .nojekyll

# Add all files
git add .

# Commit
git commit -m "Deploy to GitHub Pages - $(date)"

echo "🚀 Pushing to GitHub Pages..."
git push origin gh-pages

# Switch back to main branch
git checkout main

echo "✅ Deployment complete!"
echo "🌐 Your site will be available at: https://USERNAME.github.io/REPOSITORY_NAME"
echo "   (Replace USERNAME and REPOSITORY_NAME with your actual values)" 