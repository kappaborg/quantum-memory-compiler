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
import envService from '../services/envService';

interface IBMQuantumConfigProps {
  onConfigChange?: (isConfigured: boolean) => void;
}

const IBMQuantumConfig: React.FC<IBMQuantumConfigProps> = ({ onConfigChange }) => {
  const [isConfigured, setIsConfigured] = useState(false);
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
  }, [onConfigChange]);

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
                  {isConfigured ? 'Connected and ready' : 'Not configured'}
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                icon={isConfigured ? <CheckIcon /> : <ErrorIcon />}
                label={isConfigured ? 'Configured' : 'Not Configured'}
                color={isConfigured ? 'success' : 'error'}
                variant="outlined"
              />
              
              <Tooltip title="Configure IBM Quantum">
                <IconButton onClick={() => setShowDialog(true)}>
                  <SettingsIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>

          {config.isGitHubPages && (
            <Alert severity="info" sx={{ mt: 2 }}>
              <strong>GitHub Pages Mode:</strong> IBM Quantum token is configured via environment variables.
            </Alert>
          )}

          {!isConfigured && !config.isGitHubPages && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              Configure your IBM Quantum token to access real quantum hardware and simulators.
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
              label="Remember token (save in browser)"
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
                <strong>Security Note:</strong> Your token will be stored locally in your browser. 
                Never share your token or commit it to version control.
              </Typography>
            </Alert>

            {isConfigured && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Current Configuration:
                </Typography>
                <Chip label="Token Configured" color="success" size="small" />
                <Button
                  variant="outlined"
                  color="error"
                  size="small"
                  onClick={handleTokenClear}
                  sx={{ ml: 1 }}
                >
                  Clear Token
                </Button>
              </Box>
            )}
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleDialogClose}>Cancel</Button>
          <Button 
            onClick={handleTokenSubmit}
            variant="contained"
            disabled={!token.trim() || isValidating}
          >
            {isValidating ? 'Validating...' : 'Save Token'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default IBMQuantumConfig; 