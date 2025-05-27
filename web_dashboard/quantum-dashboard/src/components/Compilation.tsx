import {
  Build as CompileIcon,
  ExpandMore as ExpandMoreIcon,
  Timeline as MetricsIcon,
  Speed as OptimizeIcon,
  Upload as UploadIcon
} from '@mui/icons-material';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  FormControl,
  FormControlLabel,
  Grid,
  InputLabel,
  LinearProgress,
  MenuItem,
  Paper,
  Select,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography
} from '@mui/material';
import React, { useCallback, useState } from 'react';
import { ApiService } from '../services/apiService';
import { MockApiService } from '../services/mockApiService';

// Function to get API configuration from localStorage
const getApiConfig = () => {
  const savedConfig = localStorage.getItem('quantum_api_config');
  if (savedConfig) {
    try {
      return JSON.parse(savedConfig);
    } catch (e) {
      console.error('Failed to parse API config:', e);
    }
  }
  return {
    mode: 'demo',
    apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:5001',
    isDemo: process.env.REACT_APP_DEMO_MODE === 'true' || process.env.REACT_APP_API_URL?.includes('demo') || false
  };
};

const config = getApiConfig();
const API_BASE_URL = config.apiUrl;
const IS_DEMO_MODE = config.isDemo;

// Set API base URL if not in demo mode
if (!IS_DEMO_MODE) {
  ApiService.setBaseUrl(API_BASE_URL);
}

interface CompilationResult {
  success: boolean;
  compiled_circuit: any;
  metrics: {
    original_qubits: number;
    compiled_qubits: number;
    original_gates: number;
    compiled_gates: number;
    original_depth: number;
    compiled_depth: number;
    strategy: string;
    meta_compiler_used: boolean;
  };
  execution_time?: number;
  error?: string;
}

const Compilation: React.FC = () => {
  const [circuit, setCircuit] = useState<any>(null);
  const [compilationParams, setCompilationParams] = useState({
    strategy: 'balanced',
    use_meta_compiler: false,
    optimization_level: 1,
    target_backend: 'generic'
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CompilationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadedFile(file);
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        if (file.name.endsWith('.json')) {
          const circuitData = JSON.parse(content);
          setCircuit(circuitData);
        } else if (file.name.endsWith('.qasm')) {
          setCircuit({ qasm: content, type: 'qasm' });
        }
        setError(null);
      } catch (err) {
        setError('Failed to parse circuit file');
      }
    };
    reader.readAsText(file);
  }, []);

  const runCompilation = async () => {
    if (!circuit) {
      setError('Please upload a circuit first');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      if (IS_DEMO_MODE) {
        const mockResult = await MockApiService.compileCircuit(circuit, compilationParams);
        setResult(mockResult);
      } else {
        const result = await ApiService.compileCircuit(circuit, {
          strategy: compilationParams.strategy,
          use_meta_compiler: compilationParams.use_meta_compiler
        });
        setResult(result);
      }
    } catch (err: any) {
      console.error('Compilation error:', err);
      setError(err.message || 'Compilation failed');
    } finally {
      setLoading(false);
    }
  };

  const createTestCircuit = (type: string) => {
    const circuits = {
      simple: {
        name: 'Simple Circuit',
        qubits: 2,
        gates: [
          { type: 'H', qubits: [0] },
          { type: 'CNOT', qubits: [0, 1] }
        ]
      },
      complex: {
        name: 'Complex Circuit',
        qubits: 4,
        gates: [
          { type: 'H', qubits: [0] },
          { type: 'H', qubits: [1] },
          { type: 'CNOT', qubits: [0, 2] },
          { type: 'CNOT', qubits: [1, 3] },
          { type: 'RZ', qubits: [2], parameters: [1.57] },
          { type: 'RZ', qubits: [3], parameters: [1.57] },
          { type: 'CNOT', qubits: [2, 3] }
        ]
      },
      optimization: {
        name: 'Optimization Test',
        qubits: 3,
        gates: [
          { type: 'X', qubits: [0] },
          { type: 'X', qubits: [0] }, // Should be optimized out
          { type: 'H', qubits: [1] },
          { type: 'Z', qubits: [1] },
          { type: 'H', qubits: [1] }, // Should create X gate
          { type: 'CNOT', qubits: [0, 2] }
        ]
      }
    };
    setCircuit(circuits[type as keyof typeof circuits]);
  };

  const getOptimizationRatio = (metrics: any) => {
    if (!metrics) return 0;
    const gateReduction = ((metrics.original_gates - metrics.compiled_gates) / metrics.original_gates) * 100;
    const depthReduction = ((metrics.original_depth - metrics.compiled_depth) / metrics.original_depth) * 100;
    return Math.max(gateReduction, depthReduction);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
        <CompileIcon sx={{ mr: 2, color: '#2E86AB' }} />
        Quantum Circuit Compilation
      </Typography>

      <Grid container spacing={3}>
        {/* Circuit Upload & Test Circuits */}
        <Grid item xs={12} md={4}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>Circuit Input</Typography>
              
              <Button
                variant="outlined"
                component="label"
                startIcon={<UploadIcon />}
                fullWidth
                sx={{ mb: 2 }}
              >
                Upload Circuit File
                <input
                  type="file"
                  hidden
                  accept=".json,.qasm"
                  onChange={handleFileUpload}
                />
              </Button>

              {uploadedFile && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  Loaded: {uploadedFile.name}
                </Alert>
              )}

              <Typography variant="subtitle2" sx={{ mb: 1 }}>Or use test circuits:</Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => createTestCircuit('simple')}
                >
                  Simple Circuit
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => createTestCircuit('complex')}
                >
                  Complex Circuit
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => createTestCircuit('optimization')}
                >
                  Optimization Test
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Compilation Parameters */}
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                <OptimizeIcon sx={{ mr: 1 }} />
                Compilation Settings
              </Typography>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Strategy</InputLabel>
                <Select
                  value={compilationParams.strategy}
                  onChange={(e) => setCompilationParams(prev => ({ ...prev, strategy: e.target.value }))}
                >
                  <MenuItem value="balanced">Balanced</MenuItem>
                  <MenuItem value="speed">Speed Optimized</MenuItem>
                  <MenuItem value="memory">Memory Optimized</MenuItem>
                  <MenuItem value="depth">Depth Optimized</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Target Backend</InputLabel>
                <Select
                  value={compilationParams.target_backend}
                  onChange={(e) => setCompilationParams(prev => ({ ...prev, target_backend: e.target.value }))}
                >
                  <MenuItem value="generic">Generic</MenuItem>
                  <MenuItem value="ibm_quantum">IBM Quantum</MenuItem>
                  <MenuItem value="google_quantum">Google Quantum</MenuItem>
                  <MenuItem value="rigetti">Rigetti</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Optimization Level</InputLabel>
                <Select
                  value={compilationParams.optimization_level}
                  onChange={(e) => setCompilationParams(prev => ({ ...prev, optimization_level: e.target.value as number }))}
                >
                  <MenuItem value={0}>Level 0 - No optimization</MenuItem>
                  <MenuItem value={1}>Level 1 - Basic optimization</MenuItem>
                  <MenuItem value={2}>Level 2 - Advanced optimization</MenuItem>
                  <MenuItem value={3}>Level 3 - Maximum optimization</MenuItem>
                </Select>
              </FormControl>

              <FormControlLabel
                control={
                  <Switch
                    checked={compilationParams.use_meta_compiler}
                    onChange={(e) => setCompilationParams(prev => ({ ...prev, use_meta_compiler: e.target.checked }))}
                  />
                }
                label="Use Meta-Compiler"
                sx={{ mb: 1 }}
              />

              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                Meta-compiler uses advanced AI techniques for optimization
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Circuit Display & Results */}
        <Grid item xs={12} md={8}>
          {/* Circuit Info */}
          {circuit && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Current Circuit</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Chip label={`Name: ${circuit.name || 'Unnamed'}`} />
                  </Grid>
                  <Grid item xs={6}>
                    <Chip label={`Qubits: ${circuit.qubits || 'Unknown'}`} />
                  </Grid>
                  <Grid item xs={6}>
                    <Chip label={`Gates: ${circuit.gates?.length || 0}`} />
                  </Grid>
                  <Grid item xs={6}>
                    <Chip label={`Strategy: ${compilationParams.strategy}`} />
                  </Grid>
                </Grid>
                
                <Button
                  variant="contained"
                  startIcon={<CompileIcon />}
                  onClick={runCompilation}
                  disabled={loading}
                  sx={{ mt: 2 }}
                  size="large"
                >
                  Compile Circuit
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Loading */}
          {loading && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Compiling Circuit...</Typography>
                <LinearProgress />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Applying {compilationParams.strategy} optimization strategy...
                </Typography>
              </CardContent>
            </Card>
          )}

          {/* Error Display */}
          {error && (
            <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Results */}
          {result && (
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                  <MetricsIcon sx={{ mr: 1 }} />
                  Compilation Results
                </Typography>

                {/* Summary Metrics */}
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h6" color="primary">
                        {result.metrics?.original_gates || 0} → {result.metrics?.compiled_gates || 0}
                      </Typography>
                      <Typography variant="body2">Gates</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h6" color="primary">
                        {result.metrics?.original_depth || 0} → {result.metrics?.compiled_depth || 0}
                      </Typography>
                      <Typography variant="body2">Depth</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h6" color="primary">
                        {result.metrics?.original_qubits || 0} → {result.metrics?.compiled_qubits || 0}
                      </Typography>
                      <Typography variant="body2">Qubits</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h6" color={getOptimizationRatio(result.metrics) > 0 ? 'success.main' : 'warning.main'}>
                        {getOptimizationRatio(result.metrics).toFixed(1)}%
                      </Typography>
                      <Typography variant="body2">Optimization</Typography>
                    </Paper>
                  </Grid>
                </Grid>

                {/* Detailed Metrics */}
                <Accordion defaultExpanded>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="h6">Compilation Metrics</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <TableContainer component={Paper}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Metric</TableCell>
                            <TableCell align="right">Original</TableCell>
                            <TableCell align="right">Compiled</TableCell>
                            <TableCell align="right">Improvement</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          <TableRow>
                            <TableCell>Gate Count</TableCell>
                            <TableCell align="right">{result.metrics?.original_gates || 0}</TableCell>
                            <TableCell align="right">{result.metrics?.compiled_gates || 0}</TableCell>
                            <TableCell align="right">
                              {result.metrics ? 
                                `${(((result.metrics.original_gates - result.metrics.compiled_gates) / result.metrics.original_gates) * 100).toFixed(1)}%`
                                : '0%'
                              }
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Circuit Depth</TableCell>
                            <TableCell align="right">{result.metrics?.original_depth || 0}</TableCell>
                            <TableCell align="right">{result.metrics?.compiled_depth || 0}</TableCell>
                            <TableCell align="right">
                              {result.metrics ? 
                                `${(((result.metrics.original_depth - result.metrics.compiled_depth) / result.metrics.original_depth) * 100).toFixed(1)}%`
                                : '0%'
                              }
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Qubit Usage</TableCell>
                            <TableCell align="right">{result.metrics?.original_qubits || 0}</TableCell>
                            <TableCell align="right">{result.metrics?.compiled_qubits || 0}</TableCell>
                            <TableCell align="right">
                              {result.metrics ? 
                                `${(((result.metrics.original_qubits - result.metrics.compiled_qubits) / result.metrics.original_qubits) * 100).toFixed(1)}%`
                                : '0%'
                              }
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </TableContainer>
                    
                    <Divider sx={{ my: 2 }} />
                    
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="subtitle2" gutterBottom>
                          Compilation Strategy
                        </Typography>
                        <Chip label={result.metrics?.strategy || 'Unknown'} color="primary" />
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="subtitle2" gutterBottom>
                          Meta-Compiler Used
                        </Typography>
                        <Chip 
                          label={result.metrics?.meta_compiler_used ? 'Yes' : 'No'} 
                          color={result.metrics?.meta_compiler_used ? 'success' : 'default'} 
                        />
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>

                {/* Compiled Circuit */}
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="h6">Compiled Circuit</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <pre style={{ 
                      backgroundColor: '#f5f5f5', 
                      padding: 16, 
                      borderRadius: 8, 
                      overflow: 'auto',
                      fontSize: '0.875rem'
                    }}>
                      {JSON.stringify(result.compiled_circuit, null, 2)}
                    </pre>
                  </AccordionDetails>
                </Accordion>

                {/* Raw Data */}
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="h6">Raw Results</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <pre style={{ 
                      backgroundColor: '#f5f5f5', 
                      padding: 16, 
                      borderRadius: 8, 
                      overflow: 'auto',
                      fontSize: '0.875rem'
                    }}>
                      {JSON.stringify(result, null, 2)}
                    </pre>
                  </AccordionDetails>
                </Accordion>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default Compilation; 