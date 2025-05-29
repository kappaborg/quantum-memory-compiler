/*
 * Quantum Memory Compiler - Web Dashboard
 * Copyright (c) 2025 Quantum Memory Compiler Project
 * Licensed under the Apache License, Version 2.0
 */

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
import envService from '../services/envService';

interface ApiStatusProps {
  onStatusChange?: (isConnected: boolean) => void;
}

const ApiStatus: React.FC<ApiStatusProps> = ({ onStatusChange }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const [apiInfo, setApiInfo] = useState<any>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [config, setConfig] = useState(envService.getConfig());

  const checkApiStatus = useCallback(async () => {
    setIsChecking(true);
    try {
      const isHealthy = await ApiService.healthCheck();
      if (isHealthy) {
        const info = await ApiService.getApiInfo();
        setApiInfo(info);
        setIsConnected(true);
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

  const updateApiUrl = (url: string) => {
    envService.setApiUrl(url);
    ApiService.setBaseUrl(url);
    setConfig(envService.getConfig());
    checkApiStatus();
  };

  const toggleDemoMode = () => {
    const newConfig = envService.getConfig();
    if (newConfig.isDemoMode) {
      // Switch to real API mode
      updateApiUrl('http://localhost:5001');
    } else {
      // Switch to demo mode
      updateApiUrl('demo://api.quantum-memory-compiler.local');
    }
    setShowSettings(false);
  };

  useEffect(() => {
    setConfig(envService.getConfig());
    checkApiStatus();
    
    // Check API status every 30 seconds
    const interval = setInterval(checkApiStatus, 30000);
    return () => clearInterval(interval);
  }, [checkApiStatus]);

  const getStatusColor = () => {
    if (config.isDemoMode) return 'warning';
    return isConnected ? 'success' : 'error';
  };

  const getStatusLabel = () => {
    if (config.isDemoMode) return 'Demo Mode';
    return isConnected ? 'Connected' : 'Disconnected';
  };

  const getStatusMessage = () => {
    if (config.isDemoMode) {
      return 'Running in demo mode with simulated data. All features are available for testing.';
    }
    if (isConnected && apiInfo) {
      return `Connected to ${apiInfo.name} v${apiInfo.version} - ${apiInfo.endpoints?.length || 0} endpoints available`;
    }
    if (!isConnected) {
      return `Cannot connect to API server at ${config.apiUrl}. Check if the server is running.`;
    }
    return 'Checking connection...';
  };

  return (
    <Box sx={{ mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
        <Typography variant="h6">API Status:</Typography>
        <Chip
          label={getStatusLabel()}
          color={getStatusColor()}
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

      <Alert severity={getStatusColor()} sx={{ mb: 1 }}>
        {getStatusMessage()}
        {config.isGitHubPages && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="caption" display="block">
              🌐 Running on GitHub Pages - Demo mode is automatically enabled for the best experience.
            </Typography>
          </Box>
        )}
      </Alert>

      <Dialog open={showSettings} onClose={() => setShowSettings(false)} maxWidth="sm" fullWidth>
        <DialogTitle>API Configuration</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <Alert severity="info" sx={{ mb: 2 }}>
              {config.isGitHubPages 
                ? 'GitHub Pages detected. Demo mode provides full functionality without requiring a backend server.'
                : 'Configure your API connection settings below.'
              }
            </Alert>

            <FormControlLabel
              control={
                <Switch
                  checked={config.isDemoMode}
                  onChange={toggleDemoMode}
                />
              }
              label="Demo Mode"
              sx={{ mb: 2 }}
            />

            {!config.isDemoMode && (
              <TextField
                fullWidth
                label="API URL"
                value={config.apiUrl}
                onChange={(e) => updateApiUrl(e.target.value)}
                placeholder="http://localhost:5001"
                sx={{ mb: 2 }}
                helperText="Enter the URL of your Quantum Memory Compiler API server"
              />
            )}

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Environment</InputLabel>
              <Select
                value={config.development.environment}
                disabled
              >
                <MenuItem value="development">Development</MenuItem>
                <MenuItem value="production">Production</MenuItem>
                <MenuItem value="demo">Demo</MenuItem>
              </Select>
            </FormControl>

            <Typography variant="body2" color="text.secondary">
              <strong>Demo Mode:</strong> Uses simulated data and doesn't require a running API server. 
              Perfect for testing and demonstrations.
              <br /><br />
              <strong>API Mode:</strong> Connects to a real Quantum Memory Compiler API server for 
              full quantum circuit simulation and compilation capabilities.
            </Typography>

            {config.isGitHubPages && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                <Typography variant="caption">
                  <strong>GitHub Pages Note:</strong> Real API connections may be blocked due to CORS policies. 
                  Demo mode is recommended for GitHub Pages deployment.
                </Typography>
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSettings(false)}>Close</Button>
          <Button onClick={checkApiStatus} variant="contained">Test Connection</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ApiStatus; 