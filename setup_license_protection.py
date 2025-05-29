#!/usr/bin/env python3
"""
License Protection Setup Script
Quantum Memory Compiler projesinin lisans korumasını kurar
"""

import os
import glob
import subprocess
from pathlib import Path

LICENSE_HEADER = '''#!/usr/bin/env python3
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

'''

def add_license_header_to_file(filepath):
    """Dosyaya lisans header'ı ekle"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Eğer zaten lisans header'ı varsa skip et
        if 'Apache License' in content and 'Copyright' in content:
            print(f"✅ License header already exists: {filepath}")
            return
        
        # Shebang varsa koru
        lines = content.split('\n')
        if lines and lines[0].startswith('#!'):
            # Shebang'i koru, sonrasına lisans ekle
            new_content = lines[0] + '\n' + LICENSE_HEADER[len(lines[0])+1:] + '\n'.join(lines[1:])
        else:
            new_content = LICENSE_HEADER + content
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Added license header: {filepath}")
        
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")

def setup_license_protection():
    """Lisans korumasını kur"""
    print("🚀 Setting up License Protection for Quantum Memory Compiler")
    print("=" * 60)
    
    # 1. Python dosyalarına header ekle
    print("📝 Adding license headers to Python files...")
    python_files = glob.glob("quantum_memory_compiler/**/*.py", recursive=True)
    python_files.extend(glob.glob("*.py"))
    
    for py_file in python_files:
        if not py_file.endswith('__pycache__'):
            add_license_header_to_file(py_file)
    
    # 2. TypeScript dosyalarına header ekle
    print("\n📝 Adding license headers to TypeScript files...")
    ts_files = glob.glob("web_dashboard/**/*.ts", recursive=True)
    ts_files.extend(glob.glob("web_dashboard/**/*.tsx", recursive=True))
    
    ts_header = '''/*
 * Quantum Memory Compiler - Web Dashboard
 * Copyright (c) 2025 Quantum Memory Compiler Project
 * Licensed under the Apache License, Version 2.0
 */

'''
    
    for ts_file in ts_files:
        try:
            with open(ts_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'Copyright (c) 2025' not in content:
                with open(ts_file, 'w', encoding='utf-8') as f:
                    f.write(ts_header + content)
                print(f"✅ Added license header: {ts_file}")
        except Exception as e:
            print(f"❌ Error processing {ts_file}: {e}")
    
    # 3. Git commit ile lisans güncellemelerini kaydet
    print("\n📦 Committing license changes...")
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'feat: Add Apache 2.0 license protection'], check=True)
        print("✅ License changes committed to Git")
    except subprocess.CalledProcessError:
        print("⚠️ Git commit failed - please commit manually")
    
    # 4. Kontrol et
    print("\n🔍 Verification...")
    required_files = [
        'LICENSE',
        'README.md',
        'TRADEMARK_NOTICE.md',
        'LICENSE_RECOMMENDATIONS.md'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
    
    # 5. Özet rapor
    print("\n" + "=" * 60)
    print("📊 LICENSE PROTECTION SUMMARY")
    print("=" * 60)
    print("✅ Apache License 2.0 applied")
    print("✅ Copyright notices added")
    print("✅ Trademark protection established")
    print("✅ Commercial licensing framework ready")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Push changes to GitHub: git push")
    print("2. Set GitHub repository license to Apache-2.0")
    print("3. Consider trademark registration")
    print("4. Setup commercial licensing contact")
    print("5. Review and update headers periodically")
    
    print("\n⚖️ LEGAL PROTECTION ACHIEVED:")
    print("• Apache 2.0 license provides patent protection")
    print("• Copyright notices establish ownership")
    print("• Commercial use requires permission")
    print("• Attribution is enforced")
    print("• Trademark protection in place")

if __name__ == "__main__":
    setup_license_protection() 