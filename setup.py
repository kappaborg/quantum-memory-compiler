#!/usr/bin/env python
"""
Setup script for Quantum Memory Compiler
========================================

Developer: kappasutra
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="quantum_memory_compiler",
    version="2.1.0",
    author="kappasutra",
    author_email="kappasutra@quantum.dev",
    description="Memory-aware compiler and simulator system for quantum computers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kappasutra/quantum_memory_compiler",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Compilers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "jupyter": [
            "jupyter>=1.0",
            "ipython>=7.0",
            "notebook>=6.0",
        ],
        "advanced-cli": [
            "rich>=12.0.0",
            "click>=8.0",
        ],
        "visualization": [
            "matplotlib>=3.3.0",
            "seaborn>=0.11.0",
            "plotly>=5.0.0",
        ],
        "all": [
            "pytest>=6.0", "pytest-cov>=2.0", "black>=21.0", "flake8>=3.8", "mypy>=0.800",
            "jupyter>=1.0", "ipython>=7.0", "notebook>=6.0",
            "rich>=12.0.0", "click>=8.0",
            "matplotlib>=3.3.0", "seaborn>=0.11.0", "plotly>=5.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "qmc=quantum_memory_compiler.cli:main",
            "quantum-memory-compiler=quantum_memory_compiler.cli:main",
        ],
        "jupyter_extensions": [
            "quantum_memory_compiler_magic=jupyter_extension.quantum_memory_compiler_magic:load_ipython_extension",
        ],
        "cursor_extensions": [
            "quantum_memory=quantum_memory_compiler.cursor_extension:activate",
        ],
    },
    include_package_data=True,
    package_data={
        "quantum_memory_compiler": [
            "examples/*.py",
            "docs/*.md",
            "*.md",
        ],
        "jupyter_extension": [
            "*.py",
            "*.ipynb",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/kappasutra/quantum_memory_compiler/issues",
        "Source": "https://github.com/kappasutra/quantum_memory_compiler",
        "Documentation": "https://github.com/kappasutra/quantum_memory_compiler/wiki",
    },
    keywords="quantum computing, compiler, memory management, simulation, optimization",
) 