/*
 * Quantum Memory Compiler - Web Dashboard
 * Copyright (c) 2025 Quantum Memory Compiler Project
 * Licensed under the Apache License, Version 2.0
 */

import {
    CheckCircle as CheckIcon,
    Error as ErrorIcon,
    CloudQueue as IBMIcon,
    Settings as SettingsIcon,
    Visibility,
    VisibilityOff
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
    FormControlLabel,
    IconButton,
    InputAdornment,
    Link,
    Switch,
    TextField,
    Tooltip,
    Typography
} from '@mui/material';
import React, { useEffect, useState } from 'react';
import ApiService from '../services/apiService';
import envService from '../services/envService';

interface IBMQuantumConfigProps {
  onConfigChange?: (isConfigured: boolean) => void;
}

const IBMQuantumConfig: React.FC<IBMQuantumConfigProps> = ({ onConfigChange }) => {
  const [isConfigured, setIsConfigured] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'unknown' | 'connected' | 'error'>('unknown');
  const [showDialog, setShowDialog] = useState(false);
  const [token, setToken] = useState('');
  const [showToken, setShowToken] = useState(false);
  const [persistent, setPersistent] = useState(true);
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<{
    isValid: boolean;
    message: string;
  } | null>(null);

  useEffect(() => {
    const config = envService.getConfig();
    setIsConfigured(config.ibmQuantum.enabled);
    if (onConfigChange) {
      onConfigChange(config.ibmQuantum.enabled);
    }
    
    // Check IBM Quantum status
    checkIBMQuantumStatus();
  }, [onConfigChange]);

  const checkIBMQuantumStatus = async () => {
    try {
      const status = await ApiService.getIBMQuantumStatus();
      if (status.success) {
        setConnectionStatus('connected');
      } else {
        setConnectionStatus('error');
      }
    } catch (error) {
      console.log('IBM Quantum status check failed (expected in demo mode):', error);
      // In demo mode, this is expected - don't show as error
      const config = envService.getConfig();
      if (config.isDemoMode) {
        setConnectionStatus('connected'); // Show as connected in demo mode
      } else {
        setConnectionStatus('error');
      }
    }
  };

  const handleTokenSubmit = async () => {
    if (!token.trim()) {
      setValidationResult({
        isValid: false,
        message: 'Please enter a valid IBM Quantum token'
      });
      return;
    }

    setIsValidating(true);
    setValidationResult(null);

    try {
      // Basic token format validation
      if (token.length < 20) {
        throw new Error('Token appears to be too short');
      }

      // Save token
      envService.setIBMQuantumToken(token, persistent);
      
      // Test the connection
      await checkIBMQuantumStatus();
      
      setValidationResult({
        isValid: true,
        message: 'IBM Quantum token configured successfully!'
      });

      setIsConfigured(true);
      if (onConfigChange) {
        onConfigChange(true);
      }

      // Close dialog after success
      setTimeout(() => {
        setShowDialog(false);
        setToken('');
        setValidationResult(null);
      }, 2000);

    } catch (error: any) {
      setValidationResult({
        isValid: false,
        message: error.message || 'Failed to validate token'
      });
    } finally {
      setIsValidating(false);
    }
  };

  const handleTokenClear = () => {
    envService.clearIBMQuantumToken();
    setIsConfigured(false);
    setConnectionStatus('unknown');
    setToken('');
    setValidationResult(null);
    if (onConfigChange) {
      onConfigChange(false);
    }
  };

  const handleDialogClose = () => {
    setShowDialog(false);
    setToken('');
    setValidationResult(null);
    setShowToken(false);
  };

  const config = envService.getConfig();

  const getStatusChip = () => {
    if (config.isDemoMode) {
      return (
        <Chip
          icon={<CheckIcon />}
          label="Demo Mode"
          color="warning"
          variant="outlined"
        />
      );
    }

    if (!isConfigured) {
      return (
        <Chip
          icon={<ErrorIcon />}
          label="Not Configured"
          color="error"
          variant="outlined"
        />
      );
    }

    switch (connectionStatus) {
      case 'connected':
        return (
          <Chip
            icon={<CheckIcon />}
            label="Connected"
            color="success"
            variant="outlined"
          />
        );
      case 'error':
        return (
          <Chip
            icon={<ErrorIcon />}
            label="Connection Error"
            color="error"
            variant="outlined"
          />
        );
      default:
        return (
          <Chip
            icon={<ErrorIcon />}
            label="Checking..."
            color="default"
            variant="outlined"
          />
        );
    }
  };

  const getStatusMessage = () => {
    if (config.isDemoMode) {
      return 'Running in demo mode with simulated IBM Quantum integration';
    }

    if (!isConfigured) {
      return 'Not configured - Add your IBM Quantum token to get started';
    }

    switch (connectionStatus) {
      case 'connected':
        return 'Connected and ready to use IBM Quantum services';
      case 'error':
        return 'Token configured but connection failed - Check your token';
      default:
        return 'Checking connection status...';
    }
  };

  return (
    <Box sx={{ mb: 2 }}>
      <Card variant="outlined">
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <IBMIcon sx={{ color: '#1976d2' }} />
              <Box>
                <Typography variant="h6">IBM Quantum</Typography>
                <Typography variant="body2" color="text.secondary">
                  {getStatusMessage()}
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {getStatusChip()}
              
              {!config.isDemoMode && (
                <Tooltip title="Configure IBM Quantum">
                  <IconButton onClick={() => setShowDialog(true)}>
                    <SettingsIcon />
                  </IconButton>
                </Tooltip>
              )}
            </Box>
          </Box>

          {config.isDemoMode && (
            <Alert severity="info" sx={{ mt: 2 }}>
              <strong>Demo Mode:</strong> IBM Quantum integration is simulated. 
              All quantum operations use demo data for testing purposes.
            </Alert>
          )}

          {config.isGitHubPages && !config.isDemoMode && (
            <Alert severity="info" sx={{ mt: 2 }}>
              <strong>GitHub Pages Mode:</strong> IBM Quantum token is configured via environment variables.
            </Alert>
          )}

          {!isConfigured && !config.isGitHubPages && !config.isDemoMode && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              Configure your IBM Quantum token to access real quantum hardware and simulators.
            </Alert>
          )}

          {connectionStatus === 'error' && isConfigured && !config.isDemoMode && (
            <Alert severity="error" sx={{ mt: 2 }}>
              <strong>Connection Failed:</strong> Unable to connect to IBM Quantum services. 
              Please check your token and network connection.
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Configuration Dialog */}
      <Dialog open={showDialog} onClose={handleDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IBMIcon sx={{ color: '#1976d2' }} />
            IBM Quantum Configuration
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="body2">
                Get your IBM Quantum token from{' '}
                <Link 
                  href="https://quantum-computing.ibm.com/account" 
                  target="_blank" 
                  rel="noopener noreferrer"
                >
                  IBM Quantum Network
                </Link>
              </Typography>
            </Alert>

            <TextField
              fullWidth
              label="IBM Quantum Token"
              type={showToken ? 'text' : 'password'}
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Enter your IBM Quantum token"
              sx={{ mb: 2 }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowToken(!showToken)}
                      edge="end"
                    >
                      {showToken ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <FormControlLabel
              control={
                <Switch
                  checked={persistent}
                  onChange={(e) => setPersistent(e.target.checked)}
                />
              }
              label="Remember token (store in localStorage)"
              sx={{ mb: 2 }}
            />

            {validationResult && (
              <Alert 
                severity={validationResult.isValid ? 'success' : 'error'} 
                sx={{ mb: 2 }}
              >
                {validationResult.message}
              </Alert>
            )}

            <Alert severity="warning" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Security Note:</strong> Your token will be stored securely and used only 
                for IBM Quantum API calls. Never share your token with others.
              </Typography>
            </Alert>
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleDialogClose}>
            Cancel
          </Button>
          {isConfigured && (
            <Button onClick={handleTokenClear} color="error">
              Clear Token
            </Button>
          )}
          <Button 
            onClick={handleTokenSubmit} 
            variant="contained"
            disabled={isValidating || !token.trim()}
          >
            {isValidating ? 'Validating...' : 'Save Token'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default IBMQuantumConfig; 