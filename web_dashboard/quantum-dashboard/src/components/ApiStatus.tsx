import {
    Alert,
    Box,
    Button,
    Chip,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    FormControl,
    FormControlLabel,
    InputLabel,
    MenuItem,
    Select,
    Switch,
    TextField,
    Typography
} from '@mui/material';
import React, { useCallback, useEffect, useState } from 'react';
import { ApiService } from '../services/apiService';

interface ApiStatusProps {
  onStatusChange?: (isConnected: boolean) => void;
}

const ApiStatus: React.FC<ApiStatusProps> = ({ onStatusChange }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const [apiInfo, setApiInfo] = useState<any>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState({
    mode: 'demo',
    apiUrl: 'http://localhost:5001',
    isDemo: true
  });

  const checkApiStatus = useCallback(async () => {
    setIsChecking(true);
    try {
      const isHealthy = await ApiService.healthCheck();
      if (isHealthy) {
        const info = await ApiService.getApiInfo();
        setApiInfo(info);
        setIsConnected(true);
        setSettings(prev => ({ ...prev, isDemo: false }));
      } else {
        setIsConnected(false);
        setApiInfo(null);
      }
    } catch (error) {
      console.error('API health check failed:', error);
      setIsConnected(false);
      setApiInfo(null);
    } finally {
      setIsChecking(false);
    }
    
    if (onStatusChange) {
      onStatusChange(isConnected);
    }
  }, [onStatusChange, isConnected]);

  const saveSettings = () => {
    localStorage.setItem('quantum_api_config', JSON.stringify(settings));
    
    if (!settings.isDemo) {
      ApiService.setBaseUrl(settings.apiUrl);
    }
    
    setShowSettings(false);
    checkApiStatus();
  };

  const loadSettings = () => {
    const saved = localStorage.getItem('quantum_api_config');
    if (saved) {
      try {
        const config = JSON.parse(saved);
        setSettings(config);
        
        if (!config.isDemo) {
          ApiService.setBaseUrl(config.apiUrl);
        }
      } catch (e) {
        console.error('Failed to load API settings:', e);
      }
    }
  };

  useEffect(() => {
    loadSettings();
    checkApiStatus();
    
    // Check API status every 30 seconds
    const interval = setInterval(checkApiStatus, 30000);
    return () => clearInterval(interval);
  }, [checkApiStatus]);

  return (
    <Box sx={{ mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
        <Typography variant="h6">API Status:</Typography>
        <Chip
          label={isConnected ? 'Connected' : settings.isDemo ? 'Demo Mode' : 'Disconnected'}
          color={isConnected ? 'success' : settings.isDemo ? 'warning' : 'error'}
          variant={isChecking ? 'outlined' : 'filled'}
        />
        <Button
          size="small"
          variant="outlined"
          onClick={checkApiStatus}
          disabled={isChecking}
        >
          {isChecking ? 'Checking...' : 'Refresh'}
        </Button>
        <Button
          size="small"
          variant="outlined"
          onClick={() => setShowSettings(true)}
        >
          Settings
        </Button>
      </Box>

      {isConnected && apiInfo && (
        <Alert severity="success" sx={{ mb: 1 }}>
          Connected to {apiInfo.name} v{apiInfo.version} - {apiInfo.endpoints?.length || 0} endpoints available
        </Alert>
      )}

      {!isConnected && !settings.isDemo && (
        <Alert severity="error" sx={{ mb: 1 }}>
          Cannot connect to API server at {settings.apiUrl}. Check if the server is running.
        </Alert>
      )}

      {settings.isDemo && (
        <Alert severity="info" sx={{ mb: 1 }}>
          Running in demo mode. Some features may be limited. Connect to a real API server for full functionality.
        </Alert>
      )}

      <Dialog open={showSettings} onClose={() => setShowSettings(false)} maxWidth="sm" fullWidth>
        <DialogTitle>API Settings</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.isDemo}
                  onChange={(e) => setSettings(prev => ({ ...prev, isDemo: e.target.checked }))}
                />
              }
              label="Demo Mode"
              sx={{ mb: 2 }}
            />

            {!settings.isDemo && (
              <TextField
                fullWidth
                label="API URL"
                value={settings.apiUrl}
                onChange={(e) => setSettings(prev => ({ ...prev, apiUrl: e.target.value }))}
                placeholder="http://localhost:5001"
                sx={{ mb: 2 }}
              />
            )}

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Mode</InputLabel>
              <Select
                value={settings.mode}
                onChange={(e) => setSettings(prev => ({ ...prev, mode: e.target.value }))}
              >
                <MenuItem value="demo">Demo</MenuItem>
                <MenuItem value="development">Development</MenuItem>
                <MenuItem value="production">Production</MenuItem>
              </Select>
            </FormControl>

            <Typography variant="body2" color="text.secondary">
              Demo mode uses mock data and doesn't require a running API server.
              Development/Production modes connect to a real Quantum Memory Compiler API server.
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSettings(false)}>Cancel</Button>
          <Button onClick={saveSettings} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ApiStatus; 