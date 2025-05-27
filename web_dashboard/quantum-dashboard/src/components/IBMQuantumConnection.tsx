import {
    CheckCircle as CheckIcon,
    CloudQueue as CloudIcon,
    Computer as ComputerIcon,
    Error as ErrorIcon,
    Memory as MemoryIcon,
    PlayArrow as PlayIcon,
    Refresh as RefreshIcon,
    Settings as SettingsIcon
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    CircularProgress,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Grid,
    IconButton,
    LinearProgress,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Tooltip,
    Typography
} from '@mui/material';
import React, { useCallback, useEffect, useState } from 'react';
import {
    Bar,
    BarChart,
    CartesianGrid,
    Tooltip as RechartsTooltip,
    ResponsiveContainer,
    XAxis,
    YAxis
} from 'recharts';

import ibmQuantumService, { IBMBackend, IBMExecutionResult, IBMStatus } from '../services/ibmQuantumService';

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
const IS_DEMO_MODE = config.isDemo;

// Debug logging
console.log('🔧 IBMQuantumConnection Config:', {
  mode: config.mode,
  apiUrl: config.apiUrl,
  IS_DEMO_MODE,
  REACT_APP_API_URL: process.env.REACT_APP_API_URL,
  REACT_APP_DEMO_MODE: process.env.REACT_APP_DEMO_MODE
});

const IBMQuantumConnection: React.FC = () => {
  const [token, setToken] = useState<string>('');
  const [status, setStatus] = useState<IBMStatus | null>(null);
  const [backends, setBackends] = useState<IBMBackend[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedBackend, setSelectedBackend] = useState<IBMBackend | null>(null);
  const [executionResult, setExecutionResult] = useState<IBMExecutionResult | null>(null);
  const [executing, setExecuting] = useState(false);
  const [showTokenDialog, setShowTokenDialog] = useState(false);
  const [showExecutionDialog, setShowExecutionDialog] = useState(false);

  const checkStatus = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const statusData = await ibmQuantumService.getStatus();
      setStatus(statusData);
      
      if (statusData.integration_ready) {
        await loadBackends();
      }
    } catch (err) {
      setError('IBM Quantum durumu kontrol edilemedi');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Load saved token on component mount
    const savedToken = ibmQuantumService.getToken();
    if (savedToken) {
      setToken(savedToken);
      checkStatus();
    }
  }, [checkStatus]);

  const loadBackends = async () => {
    try {
      const backendsData = await ibmQuantumService.getBackends();
      setBackends(backendsData.backends);
    } catch (err) {
      setError('Backend\'ler yüklenemedi');
      console.error(err);
    }
  };

  const handleTokenSave = () => {
    if (token.trim()) {
      ibmQuantumService.setToken(token.trim());
      setShowTokenDialog(false);
      checkStatus();
    }
  };

  const handleTokenClear = () => {
    ibmQuantumService.clearToken();
    setToken('');
    setStatus(null);
    setBackends([]);
  };

  const executeTestCircuit = async (backend: IBMBackend) => {
    setExecuting(true);
    setError(null);
    
    try {
      const testCircuit = ibmQuantumService.createTestCircuit();
      const result = await ibmQuantumService.executeCircuit(
        testCircuit,
        backend.name,
        1024,
        1,
        true
      );
      
      setExecutionResult(result);
      setSelectedBackend(backend);
      setShowExecutionDialog(true);
    } catch (err) {
      setError(`Devre çalıştırılamadı: ${err}`);
      console.error(err);
    } finally {
      setExecuting(false);
    }
  };

  const getStatusColor = (status: IBMStatus | null) => {
    if (!status) return 'default';
    if (status.integration_ready) return 'success';
    if (status.qiskit_available) return 'warning';
    return 'error';
  };

  const getStatusText = (status: IBMStatus | null) => {
    if (!status) return 'Durum bilinmiyor';
    if (status.integration_ready) return 'Hazır';
    if (status.qiskit_available && !status.token_provided) return 'Token gerekli';
    if (!status.qiskit_available) return 'Qiskit yüklü değil';
    return 'Bağlantı hatası';
  };

  const formatResultsForChart = (results: Record<string, number>) => {
    return Object.entries(results)
      .map(([state, count]) => ({
        state,
        count,
        probability: count / Object.values(results).reduce((sum, c) => sum + c, 0)
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 8); // Show top 8 results
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
        <CloudIcon sx={{ mr: 2, color: '#2E86AB' }} />
        IBM Quantum Bağlantısı
      </Typography>

      {IS_DEMO_MODE && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <strong>🚀 Demo Mode</strong> - IBM Quantum integration is in demo mode. 
          To connect with your real IBM Quantum token, please run the API server locally.
          <br />
          <strong>Demo Features:</strong> Mock backends, simulated status, educational interface.
        </Alert>
      )}

      {/* Status Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Bağlantı Durumu</Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                startIcon={<SettingsIcon />}
                onClick={() => setShowTokenDialog(true)}
                size="small"
              >
                Token Ayarla
              </Button>
              <IconButton onClick={checkStatus} disabled={loading}>
                <RefreshIcon />
              </IconButton>
            </Box>
          </Box>

          {loading && <LinearProgress sx={{ mb: 2 }} />}

          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Chip
                  label={getStatusText(status)}
                  color={getStatusColor(status)}
                  icon={status?.integration_ready ? <CheckIcon /> : <ErrorIcon />}
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  Genel Durum
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Chip
                  label={status?.qiskit_available ? `v${status.qiskit_version}` : 'Yok'}
                  color={status?.qiskit_available ? 'success' : 'error'}
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  Qiskit
                </Typography>
              </Box>
            </Grid>

            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Chip
                  label={status?.token_provided ? 'Mevcut' : 'Yok'}
                  color={status?.token_provided ? 'success' : 'warning'}
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  API Token
                </Typography>
              </Box>
            </Grid>

            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Chip
                  label={status?.connected ? 'Bağlı' : 'Bağlı Değil'}
                  color={status?.connected ? 'success' : 'error'}
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  IBM Quantum
                </Typography>
              </Box>
            </Grid>
          </Grid>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Backends Table */}
      {backends.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Mevcut Backend'ler ({backends.length})
            </Typography>
            
            <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
              <Table stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell>İsim</TableCell>
                    <TableCell>Tip</TableCell>
                    <TableCell align="center">Qubit</TableCell>
                    <TableCell align="center">Durum</TableCell>
                    <TableCell align="center">Bekleyen İş</TableCell>
                    <TableCell align="center">İşlemler</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {backends.map((backend) => (
                    <TableRow key={backend.name} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {backend.simulator ? <ComputerIcon sx={{ mr: 1, color: '#2E86AB' }} /> : <MemoryIcon sx={{ mr: 1, color: '#A23B72' }} />}
                          <Typography variant="body2" fontWeight={backend.least_busy ? 600 : 400}>
                            {backend.name}
                            {backend.least_busy && (
                              <Chip label="En Az Meşgul" size="small" color="success" sx={{ ml: 1 }} />
                            )}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={backend.simulator ? 'Simülatör' : 'Donanım'}
                          color={backend.simulator ? 'info' : 'secondary'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Typography variant="body2">{backend.num_qubits}</Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={backend.operational ? 'Aktif' : 'Bakımda'}
                          color={backend.operational ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Typography variant="body2">{backend.pending_jobs}</Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title="Test Devresi Çalıştır">
                          <IconButton
                            onClick={() => executeTestCircuit(backend)}
                            disabled={executing || !backend.operational}
                            color="primary"
                          >
                            {executing ? <CircularProgress size={20} /> : <PlayIcon />}
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Token Dialog */}
      <Dialog open={showTokenDialog} onClose={() => setShowTokenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>IBM Quantum API Token</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            IBM Quantum Network hesabınızdan API token'ınızı alabilirsiniz.
          </Alert>
          <TextField
            fullWidth
            label="API Token"
            type="password"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            placeholder="IBM Quantum API token'ınızı girin"
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowTokenDialog(false)}>İptal</Button>
          <Button onClick={handleTokenClear} color="error">Temizle</Button>
          <Button onClick={handleTokenSave} variant="contained">Kaydet</Button>
        </DialogActions>
      </Dialog>

      {/* Execution Results Dialog */}
      <Dialog 
        open={showExecutionDialog} 
        onClose={() => setShowExecutionDialog(false)} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          Çalıştırma Sonuçları - {selectedBackend?.name}
        </DialogTitle>
        <DialogContent>
          {executionResult && (
            <Box>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h6" color="primary">
                      {executionResult.shots}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Shots
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h6" color="primary">
                      {executionResult.execution_time.toFixed(2)}s
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Çalışma Süresi
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h6" color="primary">
                      {executionResult.queue_time.toFixed(2)}s
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Kuyruk Süresi
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Chip
                      label={executionResult.status}
                      color={executionResult.success ? 'success' : 'error'}
                    />
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      Durum
                    </Typography>
                  </Box>
                </Grid>
              </Grid>

              {executionResult.success && Object.keys(executionResult.results).length > 0 && (
                <Box>
                  <Typography variant="h6" sx={{ mb: 2 }}>Ölçüm Sonuçları</Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={formatResultsForChart(executionResult.results)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="state" />
                      <YAxis />
                      <RechartsTooltip 
                        formatter={(value: any, name: string) => [
                          name === 'count' ? `${value} ölçüm` : `${(value * 100).toFixed(1)}%`,
                          name === 'count' ? 'Sayı' : 'Olasılık'
                        ]}
                      />
                      <Bar dataKey="count" fill="#2E86AB" />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              )}

              {executionResult.error_message && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {executionResult.error_message}
                </Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowExecutionDialog(false)}>Kapat</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default IBMQuantumConnection; 