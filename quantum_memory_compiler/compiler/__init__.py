#!/usr/bin/env python3
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

"""
Compiler paketi
==============

Kuantum devrelerini bellek-bilinçli şekilde derleyen modüller.
"""

from .compiler import QuantumCompiler, QuantumCompiler as Compiler
from .optimizer import Optimizer
from .mapper import QubitMapper as Mapper
from .scheduler import GateScheduler as Scheduler

__all__ = ['QuantumCompiler', 'Compiler', 'Optimizer', 'Mapper', 'Scheduler'] 