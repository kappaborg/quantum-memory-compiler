"""
Specific Quantum Gate Classes
============================

Specific implementations of common quantum gates.

Developer: kappasutra
"""

import numpy as np
from .gate import Gate, GateType


class HGate(Gate):
    """Hadamard Gate"""
    
    def __init__(self):
        super().__init__(GateType.H, [], [])
        self.name = 'H'


class XGate(Gate):
    """Pauli-X (NOT) Gate"""
    
    def __init__(self):
        super().__init__(GateType.X, [], [])
        self.name = 'X'


class YGate(Gate):
    """Pauli-Y Gate"""
    
    def __init__(self):
        super().__init__(GateType.Y, [], [])
        self.name = 'Y'


class ZGate(Gate):
    """Pauli-Z Gate"""
    
    def __init__(self):
        super().__init__(GateType.Z, [], [])
        self.name = 'Z'


class SGate(Gate):
    """S Gate (Phase)"""
    
    def __init__(self):
        super().__init__(GateType.S, [], [])
        self.name = 'S'


class TGate(Gate):
    """T Gate (π/8)"""
    
    def __init__(self):
        super().__init__(GateType.T, [], [])
        self.name = 'T'


class RXGate(Gate):
    """Rotation around X-axis Gate"""
    
    def __init__(self, theta):
        super().__init__(GateType.RX, [], [theta])
        self.name = 'RX'
        self.theta = theta


class RYGate(Gate):
    """Rotation around Y-axis Gate"""
    
    def __init__(self, theta):
        super().__init__(GateType.RY, [], [theta])
        self.name = 'RY'
        self.theta = theta


class RZGate(Gate):
    """Rotation around Z-axis Gate"""
    
    def __init__(self, theta):
        super().__init__(GateType.RZ, [], [theta])
        self.name = 'RZ'
        self.theta = theta


class CNOTGate(Gate):
    """Controlled-NOT Gate"""
    
    def __init__(self):
        super().__init__(GateType.CNOT, [], [])
        self.name = 'CNOT'


class CZGate(Gate):
    """Controlled-Z Gate"""
    
    def __init__(self):
        super().__init__(GateType.CZ, [], [])
        self.name = 'CZ'


class SWAPGate(Gate):
    """SWAP Gate"""
    
    def __init__(self):
        super().__init__(GateType.SWAP, [], [])
        self.name = 'SWAP'


class ToffoliGate(Gate):
    """Toffoli (CCNOT) Gate"""
    
    def __init__(self):
        super().__init__(GateType.TOFFOLI, [], [])
        self.name = 'TOFFOLI'


# Convenience aliases
IGate = lambda: Gate(GateType.I, [], [])
IGate.name = 'I' 