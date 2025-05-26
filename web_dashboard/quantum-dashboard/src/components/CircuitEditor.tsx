import {
    AccountTree as CircuitIcon,
    Clear as ClearIcon,
    Build as CompileIcon,
    Download as DownloadIcon,
    Save as SaveIcon,
    PlayArrow as SimulateIcon,
    Visibility as VisualizeIcon
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Grid,
    LinearProgress,
    Menu,
    MenuItem,
    Paper,
    TextField,
    Typography
} from '@mui/material';
import axios from 'axios';
import React, { useCallback, useState } from 'react';

interface Gate {
  id: string;
  type: string;
  qubits: number[];
  parameters?: number[];
  position: { x: number; y: number };
  column: number;
}

interface Circuit {
  name: string;
  qubits: number;
  gates: Gate[];
  measurements?: Array<{ qubit: number; classical_bit: number }>;
}

const GATE_TYPES = [
  { name: 'H', label: 'Hadamard', qubits: 1, color: '#2E86AB', symbol: 'H' },
  { name: 'X', label: 'Pauli-X', qubits: 1, color: '#A23B72', symbol: 'X' },
  { name: 'Y', label: 'Pauli-Y', qubits: 1, color: '#F18F01', symbol: 'Y' },
  { name: 'Z', label: 'Pauli-Z', qubits: 1, color: '#C73E1D', symbol: 'Z' },
  { name: 'CNOT', label: 'CNOT', qubits: 2, color: '#4CAF50', symbol: '⊕' },
  { name: 'CZ', label: 'Controlled-Z', qubits: 2, color: '#FF9800', symbol: 'CZ' },
  { name: 'RX', label: 'Rotation-X', qubits: 1, color: '#9C27B0', hasParams: true, symbol: 'RX' },
  { name: 'RY', label: 'Rotation-Y', qubits: 1, color: '#673AB7', hasParams: true, symbol: 'RY' },
  { name: 'RZ', label: 'Rotation-Z', qubits: 1, color: '#3F51B5', hasParams: true, symbol: 'RZ' },
  { name: 'S', label: 'S Gate', qubits: 1, color: '#009688', symbol: 'S' },
  { name: 'T', label: 'T Gate', qubits: 1, color: '#795548', symbol: 'T' },
];

const CircuitEditor: React.FC = () => {
  const [circuit, setCircuit] = useState<Circuit>({
    name: 'New Circuit',
    qubits: 3,
    gates: [],
    measurements: []
  });
  
  const [selectedGate, setSelectedGate] = useState<string | null>(null);
  const [selectedQubits, setSelectedQubits] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [exportMenuAnchor, setExportMenuAnchor] = useState<null | HTMLElement>(null);
  const [gateParams, setGateParams] = useState<{ [key: string]: number }>({});
  const [hoveredQubit, setHoveredQubit] = useState<number | null>(null);

  const getNextColumn = useCallback(() => {
    if (circuit.gates.length === 0) return 0;
    return Math.max(...circuit.gates.map(g => g.column)) + 1;
  }, [circuit.gates]);

  const addGate = useCallback((qubitIndex: number) => {
    if (!selectedGate) return;
    
    const gateInfo = GATE_TYPES.find(g => g.name === selectedGate);
    if (!gateInfo) return;

    let targetQubits: number[] = [];
    
    if (gateInfo.qubits === 1) {
      targetQubits = [qubitIndex];
    } else if (gateInfo.qubits === 2) {
      if (selectedQubits.length === 0) {
        // First qubit selection for 2-qubit gate
        setSelectedQubits([qubitIndex]);
        return;
      } else if (selectedQubits.length === 1 && selectedQubits[0] !== qubitIndex) {
        // Second qubit selection
        targetQubits = [selectedQubits[0], qubitIndex].sort((a, b) => a - b);
        setSelectedQubits([]);
      } else {
        // Same qubit clicked twice, reset
        setSelectedQubits([]);
        return;
      }
    }

    if (targetQubits.length === gateInfo.qubits) {
      const column = getNextColumn();
      const newGate: Gate = {
        id: `gate_${Date.now()}_${Math.random()}`,
        type: selectedGate,
        qubits: targetQubits,
        position: { x: column * 80 + 100, y: targetQubits[0] * 60 + 30 },
        parameters: gateInfo.hasParams ? [gateParams[selectedGate] || 0] : undefined,
        column
      };

      setCircuit(prev => ({
        ...prev,
        gates: [...prev.gates, newGate]
      }));
      
      if (gateInfo.qubits === 1) {
        setSelectedGate(null);
      }
    }
  }, [selectedGate, selectedQubits, gateParams, getNextColumn]);

  const removeGate = useCallback((gateId: string) => {
    setCircuit(prev => ({
      ...prev,
      gates: prev.gates.filter(g => g.id !== gateId)
    }));
  }, []);

  const clearCircuit = useCallback(() => {
    setCircuit(prev => ({
      ...prev,
      gates: [],
      measurements: []
    }));
    setSelectedQubits([]);
    setSelectedGate(null);
  }, []);

  const addMeasurement = useCallback((qubitIndex: number) => {
    const existingMeasurement = circuit.measurements?.find(m => m.qubit === qubitIndex);
    if (existingMeasurement) return;

    setCircuit(prev => ({
      ...prev,
      measurements: [
        ...(prev.measurements || []),
        { qubit: qubitIndex, classical_bit: qubitIndex }
      ]
    }));
  }, [circuit.measurements]);

  const removeMeasurement = useCallback((qubitIndex: number) => {
    setCircuit(prev => ({
      ...prev,
      measurements: (prev.measurements || []).filter(m => m.qubit !== qubitIndex)
    }));
  }, []);

  const visualizeCircuit = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/circuit/visualize', {
        circuit: {
          name: circuit.name,
          qubits: circuit.qubits,
          gates: circuit.gates.map(g => ({
            type: g.type,
            qubits: g.qubits,
            parameters: g.parameters
          })),
          measurements: circuit.measurements
        }
      }, {
        responseType: 'blob'
      });
      
      // Create image URL from blob
      const imageUrl = URL.createObjectURL(response.data);
      setResult({ type: 'image', url: imageUrl });
    } catch (err: any) {
      setError(err.response?.data?.error || 'Visualization failed');
    } finally {
      setLoading(false);
    }
  };

  const simulateCircuit = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/circuit/simulate', {
        circuit: {
          name: circuit.name,
          qubits: circuit.qubits,
          gates: circuit.gates.map(g => ({
            type: g.type,
            qubits: g.qubits,
            parameters: g.parameters
          })),
          measurements: circuit.measurements
        },
        shots: 1024
      });
      setResult({ type: 'simulation', data: response.data });
    } catch (err: any) {
      setError(err.response?.data?.error || 'Simulation failed');
    } finally {
      setLoading(false);
    }
  };

  const compileCircuit = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/circuit/compile', {
        circuit: {
          name: circuit.name,
          qubits: circuit.qubits,
          gates: circuit.gates.map(g => ({
            type: g.type,
            qubits: g.qubits,
            parameters: g.parameters
          })),
          measurements: circuit.measurements
        }
      });
      setResult({ type: 'compilation', data: response.data });
    } catch (err: any) {
      setError(err.response?.data?.error || 'Compilation failed');
    } finally {
      setLoading(false);
    }
  };

  const saveCircuit = async (name: string) => {
    try {
      await axios.post('/api/cache/circuit', {
        name,
        circuit: {
          name: circuit.name,
          qubits: circuit.qubits,
          gates: circuit.gates.map(g => ({
            type: g.type,
            qubits: g.qubits,
            parameters: g.parameters
          })),
          measurements: circuit.measurements
        }
      });
      setShowSaveDialog(false);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Save failed');
    }
  };

  const exportCircuit = async (format: string) => {
    try {
      const response = await axios.post('/api/circuit/download', {
        circuit: {
          name: circuit.name,
          qubits: circuit.qubits,
          gates: circuit.gates.map(g => ({
            type: g.type,
            qubits: g.qubits,
            parameters: g.parameters
          })),
          measurements: circuit.measurements
        },
        format
      });
      
      if (response.data.content) {
        const blob = new Blob([response.data.content], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${circuit.name}.${format}`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Export failed');
    }
    setExportMenuAnchor(null);
  };

  const getQubitLineStyle = (qubitIndex: number) => {
    const isSelected = selectedQubits.includes(qubitIndex);
    const isHovered = hoveredQubit === qubitIndex;
    const needsSelection = selectedGate && GATE_TYPES.find(g => g.name === selectedGate)?.qubits === 2 && selectedQubits.length === 1;
    
    return {
      height: 3,
      backgroundColor: isSelected ? '#2E86AB' : isHovered ? '#5BA3C7' : '#333',
      flex: 1,
      cursor: selectedGate ? 'pointer' : 'default',
      transition: 'all 0.2s ease',
      border: needsSelection && !isSelected ? '2px dashed #2E86AB' : 'none',
      '&:hover': selectedGate ? { backgroundColor: '#2E86AB' } : {}
    };
  };

  const getGatesInColumn = (column: number) => {
    return circuit.gates.filter(gate => gate.column === column);
  };

  const maxColumns = circuit.gates.length > 0 ? Math.max(...circuit.gates.map(g => g.column)) + 1 : 0;

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
        <CircuitIcon sx={{ mr: 2, color: '#2E86AB' }} />
        Quantum Circuit Editor
      </Typography>

      {/* Circuit Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Circuit Name"
                value={circuit.name}
                onChange={(e) => setCircuit(prev => ({ ...prev, name: e.target.value }))}
                size="small"
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                label="Qubits"
                type="number"
                value={circuit.qubits}
                onChange={(e) => {
                  const newQubits = Math.max(1, parseInt(e.target.value) || 1);
                  setCircuit(prev => ({ ...prev, qubits: newQubits }));
                  setSelectedQubits([]);
                }}
                size="small"
                inputProps={{ min: 1, max: 10 }}
              />
            </Grid>
            <Grid item xs={12} md={7}>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  startIcon={<VisualizeIcon />}
                  onClick={visualizeCircuit}
                  disabled={loading || circuit.gates.length === 0}
                  size="small"
                >
                  Visualize
                </Button>
                <Button
                  variant="contained"
                  startIcon={<SimulateIcon />}
                  onClick={simulateCircuit}
                  disabled={loading || circuit.gates.length === 0}
                  size="small"
                  color="success"
                >
                  Simulate
                </Button>
                <Button
                  variant="contained"
                  startIcon={<CompileIcon />}
                  onClick={compileCircuit}
                  disabled={loading || circuit.gates.length === 0}
                  size="small"
                  color="warning"
                >
                  Compile
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<SaveIcon />}
                  onClick={() => setShowSaveDialog(true)}
                  disabled={circuit.gates.length === 0}
                  size="small"
                >
                  Save
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={(e) => setExportMenuAnchor(e.currentTarget)}
                  disabled={circuit.gates.length === 0}
                  size="small"
                >
                  Export
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<ClearIcon />}
                  onClick={clearCircuit}
                  disabled={circuit.gates.length === 0}
                  size="small"
                  color="error"
                >
                  Clear
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* Gate Palette */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>Gate Palette</Typography>
              
              {selectedGate && GATE_TYPES.find(g => g.name === selectedGate)?.qubits === 2 && (
                <Alert severity="info" sx={{ mb: 2, fontSize: '0.875rem' }}>
                  {selectedQubits.length === 0 ? 'Select control qubit' : 'Select target qubit'}
                </Alert>
              )}
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {GATE_TYPES.map((gate) => (
                  <Box key={gate.name}>
                    <Chip
                      label={`${gate.symbol} - ${gate.label}`}
                      onClick={() => {
                        setSelectedGate(gate.name);
                        setSelectedQubits([]);
                      }}
                      color={selectedGate === gate.name ? 'primary' : 'default'}
                      variant={selectedGate === gate.name ? 'filled' : 'outlined'}
                      sx={{ 
                        width: '100%', 
                        justifyContent: 'flex-start',
                        backgroundColor: selectedGate === gate.name ? gate.color : 'transparent',
                        borderColor: gate.color,
                        color: selectedGate === gate.name ? 'white' : 'inherit',
                        '&:hover': { backgroundColor: `${gate.color}20` }
                      }}
                    />
                    {gate.hasParams && selectedGate === gate.name && (
                      <TextField
                        fullWidth
                        label={`${gate.name} Parameter (radians)`}
                        type="number"
                        value={gateParams[gate.name] || 0}
                        onChange={(e) => setGateParams(prev => ({ ...prev, [gate.name]: parseFloat(e.target.value) || 0 }))}
                        size="small"
                        sx={{ mt: 1 }}
                        inputProps={{ step: 0.1 }}
                      />
                    )}
                  </Box>
                ))}
              </Box>
              
              {selectedGate && (
                <Box sx={{ mt: 2, p: 1, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Selected: {selectedGate}
                    {selectedQubits.length > 0 && ` (Qubits: ${selectedQubits.join(', ')})`}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Circuit Canvas */}
        <Grid item xs={12} md={9}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Circuit Canvas
                <Chip 
                  label={`${circuit.gates.length} gates`} 
                  size="small" 
                  sx={{ ml: 2 }} 
                />
                {selectedQubits.length > 0 && (
                  <Chip 
                    label={`Selected qubits: ${selectedQubits.join(', ')}`} 
                    size="small" 
                    color="primary"
                    sx={{ ml: 1 }} 
                  />
                )}
              </Typography>
              
              <Paper sx={{ p: 3, minHeight: 400, backgroundColor: '#fafafa', overflow: 'auto' }}>
                {/* Column headers */}
                <Box sx={{ display: 'flex', mb: 2, ml: 8 }}>
                  {Array.from({ length: Math.max(maxColumns, 5) }, (_, i) => (
                    <Box key={i} sx={{ width: 80, textAlign: 'center' }}>
                      <Typography variant="caption" color="text.secondary">
                        T{i}
                      </Typography>
                    </Box>
                  ))}
                </Box>
                
                {/* Qubit Lines */}
                {Array.from({ length: circuit.qubits }, (_, i) => (
                  <Box key={i} sx={{ mb: 4, position: 'relative', display: 'flex', alignItems: 'center' }}>
                    <Typography variant="body2" sx={{ mr: 2, minWidth: 60, fontFamily: 'monospace' }}>
                      |q{i}⟩
                    </Typography>
                    
                    {/* Quantum wire */}
                    <Box
                      sx={getQubitLineStyle(i)}
                      onClick={() => selectedGate && addGate(i)}
                      onMouseEnter={() => setHoveredQubit(i)}
                      onMouseLeave={() => setHoveredQubit(null)}
                    />
                    
                    {/* Measurement indicator */}
                    <Box sx={{ ml: 2, minWidth: 100 }}>
                      {circuit.measurements?.find(m => m.qubit === i) ? (
                        <Chip
                          label="📊"
                          size="small"
                          onDelete={() => removeMeasurement(i)}
                          sx={{ backgroundColor: '#4CAF50', color: 'white' }}
                        />
                      ) : (
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => addMeasurement(i)}
                          sx={{ minWidth: 80 }}
                        >
                          Measure
                        </Button>
                      )}
                    </Box>
                    
                    {/* Gates on this qubit */}
                    {Array.from({ length: maxColumns }, (_, col) => {
                      const gatesInColumn = getGatesInColumn(col);
                      const gateOnThisQubit = gatesInColumn.find(gate => gate.qubits.includes(i));
                      
                      if (gateOnThisQubit) {
                        const gateInfo = GATE_TYPES.find(g => g.name === gateOnThisQubit.type);
                        const isControlQubit = gateOnThisQubit.qubits[0] === i;
                        const isTargetQubit = gateOnThisQubit.qubits.length > 1 && gateOnThisQubit.qubits[1] === i;
                        
                        return (
                          <Box
                            key={`${col}-${gateOnThisQubit.id}`}
                            sx={{
                              position: 'absolute',
                              left: 80 + col * 80,
                              top: -12,
                              zIndex: 10
                            }}
                          >
                            <Chip
                              label={isTargetQubit && gateInfo?.qubits === 2 ? '⊕' : gateInfo?.symbol}
                              size="small"
                              onDelete={() => removeGate(gateOnThisQubit.id)}
                              sx={{
                                backgroundColor: gateInfo?.color || '#ccc',
                                color: 'white',
                                fontWeight: 'bold',
                                minWidth: 40
                              }}
                            />
                            
                            {/* Connection line for 2-qubit gates */}
                            {gateOnThisQubit.qubits.length === 2 && isControlQubit && (
                              <Box
                                sx={{
                                  position: 'absolute',
                                  left: '50%',
                                  top: 24,
                                  width: 2,
                                  height: (gateOnThisQubit.qubits[1] - gateOnThisQubit.qubits[0]) * 64 - 24,
                                  backgroundColor: gateInfo?.color || '#ccc',
                                  transform: 'translateX(-50%)'
                                }}
                              />
                            )}
                          </Box>
                        );
                      }
                      return null;
                    })}
                  </Box>
                ))}
                
                {circuit.gates.length === 0 && (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="body2" color="text.secondary">
                      Select a gate from the palette and click on a qubit line to start building your circuit
                    </Typography>
                  </Box>
                )}
              </Paper>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Loading */}
      {loading && <LinearProgress sx={{ mt: 2 }} />}

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Results */}
      {result && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>Results</Typography>
            {result.type === 'image' ? (
              <Box sx={{ textAlign: 'center' }}>
                <img 
                  src={result.url} 
                  alt="Circuit Visualization" 
                  style={{ maxWidth: '100%', height: 'auto' }}
                />
              </Box>
            ) : (
              <pre style={{ backgroundColor: '#f5f5f5', padding: 16, borderRadius: 8, overflow: 'auto' }}>
                {JSON.stringify(result.data, null, 2)}
              </pre>
            )}
          </CardContent>
        </Card>
      )}

      {/* Save Dialog */}
      <Dialog open={showSaveDialog} onClose={() => setShowSaveDialog(false)}>
        <DialogTitle>Save Circuit</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Circuit Name"
            fullWidth
            variant="outlined"
            defaultValue={circuit.name}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                saveCircuit((e.target as HTMLInputElement).value);
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSaveDialog(false)}>Cancel</Button>
          <Button 
            onClick={(e) => {
              const input = e.currentTarget.parentElement?.parentElement?.querySelector('input');
              if (input) saveCircuit(input.value);
            }}
            variant="contained"
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Export Menu */}
      <Menu
        anchorEl={exportMenuAnchor}
        open={Boolean(exportMenuAnchor)}
        onClose={() => setExportMenuAnchor(null)}
      >
        <MenuItem onClick={() => exportCircuit('json')}>Export as JSON</MenuItem>
        <MenuItem onClick={() => exportCircuit('qasm')}>Export as QASM</MenuItem>
        <MenuItem onClick={() => exportCircuit('python')}>Export as Python</MenuItem>
      </Menu>
    </Box>
  );
};

export default CircuitEditor; 