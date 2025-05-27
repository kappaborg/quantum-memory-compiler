import {
    BarChart as BarChartIcon,
    ExpandMore as ExpandMoreIcon,
    Settings as SettingsIcon,
    PlayArrow as SimulateIcon,
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
    FormControl,
    FormControlLabel,
    Grid,
    InputLabel,
    LinearProgress,
    MenuItem,
    Paper,
    Select,
    Slider,
    Switch,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
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

// Recharts import with error handling
let BarChart: any, Bar: any, XAxis: any, YAxis: any, CartesianGrid: any, Tooltip: any, ResponsiveContainer: any;
try {
  const recharts = require('recharts');
  BarChart = recharts.BarChart;
  Bar = recharts.Bar;
  XAxis = recharts.XAxis;
  YAxis = recharts.YAxis;
  CartesianGrid = recharts.CartesianGrid;
  Tooltip = recharts.Tooltip;
  ResponsiveContainer = recharts.ResponsiveContainer;
} catch (error) {
  console.warn('Recharts not available, using fallback visualization');
}

interface SimulationResult {
  success: boolean;
  results: Record<string, number>;
  execution_time: number;
  shots: number;
  backend: string;
  statevector?: number[][];
  probabilities?: Record<string, number>;
  fidelity?: number;
  error?: string;
}

const Simulation: React.FC = () => {
  const [circuit, setCircuit] = useState<any>(null);
  const [simulationParams, setSimulationParams] = useState({
    shots: 1024,
    backend: 'qasm_simulator',
    noise_model: false,
    optimization_level: 1,
    seed: null as number | null,
    memory: false
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SimulationResult | null>(null);
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
          // Handle QASM files
          setCircuit({ qasm: content, type: 'qasm' });
        }
        setError(null);
      } catch (err) {
        setError('Failed to parse circuit file');
      }
    };
    reader.readAsText(file);
  }, []);

  const runSimulation = async () => {
    if (!circuit) {
      setError('Please upload a circuit first');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      if (IS_DEMO_MODE) {
        const mockResult = await MockApiService.simulateCircuit(circuit, simulationParams);
        setResult(mockResult);
      } else {
        const result = await ApiService.simulateCircuit(circuit, {
          shots: simulationParams.shots,
          noise: simulationParams.noise_model,
          mitigation: false,
          backend: simulationParams.backend
        });
        setResult(result);
      }
    } catch (err: any) {
      console.error('Simulation error:', err);
      setError(err.message || 'Simulation failed');
    } finally {
      setLoading(false);
    }
  };

  const formatResultsForChart = (results: Record<string, number>) => {
    return Object.entries(results)
      .map(([state, count]) => ({
        state,
        count,
        probability: count / Object.values(results).reduce((sum, c) => sum + c, 0)
      }))
      .sort((a, b) => b.count - a.count);
  };

  const createTestCircuit = (type: string) => {
    const circuits = {
      bell: {
        name: 'Bell State',
        qubits: 2,
        gates: [
          { type: 'H', qubits: [0] },
          { type: 'CNOT', qubits: [0, 1] }
        ],
        measurements: [
          { qubit: 0, classical_bit: 0 },
          { qubit: 1, classical_bit: 1 }
        ]
      },
      ghz: {
        name: 'GHZ State',
        qubits: 3,
        gates: [
          { type: 'H', qubits: [0] },
          { type: 'CNOT', qubits: [0, 1] },
          { type: 'CNOT', qubits: [1, 2] }
        ],
        measurements: [
          { qubit: 0, classical_bit: 0 },
          { qubit: 1, classical_bit: 1 },
          { qubit: 2, classical_bit: 2 }
        ]
      },
      superposition: {
        name: 'Superposition',
        qubits: 1,
        gates: [
          { type: 'H', qubits: [0] }
        ],
        measurements: [
          { qubit: 0, classical_bit: 0 }
        ]
      }
    };
    setCircuit(circuits[type as keyof typeof circuits]);
  };

  // Fallback chart component when Recharts is not available
  const FallbackChart = ({ data }: { data: any[] }) => (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>Measurement Results</Typography>
      {data.map((item, index) => (
        <Box key={index} sx={{ mb: 1, display: 'flex', alignItems: 'center' }}>
          <Typography variant="body2" sx={{ minWidth: 80 }}>
            |{item.state}⟩
          </Typography>
          <Box
            sx={{
              width: `${(item.probability * 100)}%`,
              height: 20,
              backgroundColor: '#2E86AB',
              mr: 1,
              borderRadius: 1
            }}
          />
          <Typography variant="body2">
            {item.count} ({(item.probability * 100).toFixed(1)}%)
          </Typography>
        </Box>
      ))}
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
        <SimulateIcon sx={{ mr: 2, color: '#2E86AB' }} />
        Quantum Circuit Simulation
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
                  onClick={() => createTestCircuit('bell')}
                >
                  Bell State
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => createTestCircuit('ghz')}
                >
                  GHZ State
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => createTestCircuit('superposition')}
                >
                  Superposition
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Simulation Parameters */}
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                <SettingsIcon sx={{ mr: 1 }} />
                Simulation Parameters
              </Typography>

              <Box sx={{ mb: 2 }}>
                <Typography gutterBottom>Shots: {simulationParams.shots}</Typography>
                <Slider
                  value={simulationParams.shots}
                  onChange={(_, value) => setSimulationParams(prev => ({ ...prev, shots: value as number }))}
                  min={100}
                  max={8192}
                  step={100}
                  marks={[
                    { value: 100, label: '100' },
                    { value: 1024, label: '1K' },
                    { value: 4096, label: '4K' },
                    { value: 8192, label: '8K' }
                  ]}
                />
              </Box>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Backend</InputLabel>
                <Select
                  value={simulationParams.backend}
                  onChange={(e) => setSimulationParams(prev => ({ ...prev, backend: e.target.value }))}
                >
                  <MenuItem value="qasm_simulator">QASM Simulator</MenuItem>
                  <MenuItem value="statevector_simulator">Statevector Simulator</MenuItem>
                  <MenuItem value="unitary_simulator">Unitary Simulator</MenuItem>
                </Select>
              </FormControl>

              <Box sx={{ mb: 2 }}>
                <Typography gutterBottom>Optimization Level: {simulationParams.optimization_level}</Typography>
                <Slider
                  value={simulationParams.optimization_level}
                  onChange={(_, value) => setSimulationParams(prev => ({ ...prev, optimization_level: value as number }))}
                  min={0}
                  max={3}
                  step={1}
                  marks={[
                    { value: 0, label: '0' },
                    { value: 1, label: '1' },
                    { value: 2, label: '2' },
                    { value: 3, label: '3' }
                  ]}
                />
              </Box>

              <TextField
                fullWidth
                label="Random Seed (optional)"
                type="number"
                value={simulationParams.seed || ''}
                onChange={(e) => setSimulationParams(prev => ({ 
                  ...prev, 
                  seed: e.target.value ? parseInt(e.target.value) : null 
                }))}
                sx={{ mb: 2 }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={simulationParams.noise_model}
                    onChange={(e) => setSimulationParams(prev => ({ ...prev, noise_model: e.target.checked }))}
                  />
                }
                label="Enable Noise Model"
                sx={{ mb: 1 }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={simulationParams.memory}
                    onChange={(e) => setSimulationParams(prev => ({ ...prev, memory: e.target.checked }))}
                  />
                }
                label="Return Memory"
              />
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
                    <Chip label={`Measurements: ${circuit.measurements?.length || 0}`} />
                  </Grid>
                </Grid>
                
                <Button
                  variant="contained"
                  startIcon={<SimulateIcon />}
                  onClick={runSimulation}
                  disabled={loading}
                  sx={{ mt: 2 }}
                  size="large"
                >
                  Run Simulation
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Loading */}
          {loading && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Running Simulation...</Typography>
                <LinearProgress />
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
                  <BarChartIcon sx={{ mr: 1 }} />
                  Simulation Results
                </Typography>

                {/* Summary */}
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h6" color="primary">
                        {result.shots}
                      </Typography>
                      <Typography variant="body2">Shots</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h6" color="primary">
                        {result.execution_time?.toFixed(3) || '0.000'}s
                      </Typography>
                      <Typography variant="body2">Execution Time</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h6" color="primary">
                        {result.backend}
                      </Typography>
                      <Typography variant="body2">Backend</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h6" color={result.success ? 'success.main' : 'error.main'}>
                        {result.success ? 'Success' : 'Failed'}
                      </Typography>
                      <Typography variant="body2">Status</Typography>
                    </Paper>
                  </Grid>
                </Grid>

                {/* Results Chart */}
                {result.success && result.results && (
                  <Accordion defaultExpanded>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="h6">Measurement Results</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      {ResponsiveContainer ? (
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart data={formatResultsForChart(result.results)}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="state" />
                            <YAxis />
                            <Tooltip 
                              formatter={(value: any, name: string) => [
                                name === 'count' ? `${value} measurements` : `${(value * 100).toFixed(1)}%`,
                                name === 'count' ? 'Count' : 'Probability'
                              ]}
                            />
                            <Bar dataKey="count" fill="#2E86AB" />
                          </BarChart>
                        </ResponsiveContainer>
                      ) : (
                        <FallbackChart data={formatResultsForChart(result.results)} />
                      )}
                    </AccordionDetails>
                  </Accordion>
                )}

                {/* Detailed Results Table */}
                {result.success && result.results && (
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="h6">Detailed Results</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <TableContainer component={Paper}>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>State</TableCell>
                              <TableCell align="right">Count</TableCell>
                              <TableCell align="right">Probability</TableCell>
                              <TableCell align="right">Percentage</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {formatResultsForChart(result.results).map((row) => (
                              <TableRow key={row.state}>
                                <TableCell component="th" scope="row">
                                  |{row.state}⟩
                                </TableCell>
                                <TableCell align="right">{row.count}</TableCell>
                                <TableCell align="right">{row.probability.toFixed(4)}</TableCell>
                                <TableCell align="right">{(row.probability * 100).toFixed(2)}%</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </AccordionDetails>
                  </Accordion>
                )}

                {/* Raw Data */}
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="h6">Raw Data</Typography>
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

export default Simulation; 