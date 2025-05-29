/*
 * Quantum Memory Compiler - Web Dashboard
 * Copyright (c) 2025 Quantum Memory Compiler Project
 * Licensed under the Apache License, Version 2.0
 */

import {
    CloudQueue as CloudIcon,
    Computer as LocalIcon,
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
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    FormControl,
    FormControlLabel,
    IconButton,
    Radio,
    RadioGroup,
    TextField,
    Tooltip,
    Typography
} from '@mui/material';
import axios from 'axios';
import React, { useEffect, useState } from 'react';

interface ApiConfigurationProps {
    onConfigChange?: (config: ApiConfig) => void;
}

interface ApiConfig {
    mode: 'demo' | 'local' | 'custom';
    apiUrl: string;
    isDemo: boolean;
}

const ApiConfiguration: React.FC<ApiConfigurationProps> = ({ onConfigChange }) => {
    const [open, setOpen] = useState(false);
    const [config, setConfig] = useState<ApiConfig>({
        mode: 'demo',
        apiUrl: 'https://demo-api.quantum-memory-compiler.com',
        isDemo: true
    });
    const [customUrl, setCustomUrl] = useState('');
    const [testing, setTesting] = useState(false);
    const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

    // Load saved configuration on mount
    useEffect(() => {
        const savedConfig = localStorage.getItem('quantum_api_config');
        if (savedConfig) {
            try {
                const parsed = JSON.parse(savedConfig);
                setConfig(parsed);
                if (parsed.mode === 'custom') {
                    setCustomUrl(parsed.apiUrl);
                }
            } catch (e) {
                console.error('Failed to parse saved config:', e);
            }
        }
    }, []);

    const testApiConnection = async (url: string) => {
        setTesting(true);
        setTestResult(null);
        
        try {
            const response = await axios.get(`${url}/api/info`, { timeout: 5000 });
            if (response.data && response.data.name) {
                setTestResult({
                    success: true,
                    message: `✅ Connected to ${response.data.name} v${response.data.version}`
                });
                return true;
            } else {
                setTestResult({
                    success: false,
                    message: '❌ Invalid API response'
                });
                return false;
            }
        } catch (error: any) {
            setTestResult({
                success: false,
                message: `❌ Connection failed: ${error.message}`
            });
            return false;
        } finally {
            setTesting(false);
        }
    };

    const handleModeChange = (mode: 'demo' | 'local' | 'custom') => {
        let newConfig: ApiConfig;
        
        switch (mode) {
            case 'demo':
                newConfig = {
                    mode: 'demo',
                    apiUrl: 'https://demo-api.quantum-memory-compiler.com',
                    isDemo: true
                };
                break;
            case 'local':
                newConfig = {
                    mode: 'local',
                    apiUrl: 'http://localhost:5001',
                    isDemo: false
                };
                break;
            case 'custom':
                newConfig = {
                    mode: 'custom',
                    apiUrl: customUrl || 'https://your-ngrok-url.ngrok.io',
                    isDemo: false
                };
                break;
        }
        
        setConfig(newConfig);
    };

    const saveConfiguration = async () => {
        let finalConfig = { ...config };
        
        if (config.mode === 'custom') {
            if (!customUrl) {
                setTestResult({
                    success: false,
                    message: '❌ Please enter a custom API URL'
                });
                return;
            }
            finalConfig.apiUrl = customUrl;
        }

        // Test connection for non-demo modes
        if (!finalConfig.isDemo) {
            const connectionSuccess = await testApiConnection(finalConfig.apiUrl);
            if (!connectionSuccess) {
                return; // Don't save if connection fails
            }
        }

        // Save to localStorage
        localStorage.setItem('quantum_api_config', JSON.stringify(finalConfig));
        
        // Update environment variables
        (window as any).REACT_APP_API_URL = finalConfig.apiUrl;
        (window as any).REACT_APP_DEMO_MODE = finalConfig.isDemo.toString();
        
        // Notify parent component
        if (onConfigChange) {
            onConfigChange(finalConfig);
        }
        
        setOpen(false);
        
        // Reload page to apply new configuration
        window.location.reload();
    };

    const getCurrentConfigDisplay = () => {
        const savedConfig = localStorage.getItem('quantum_api_config');
        if (savedConfig) {
            try {
                const parsed = JSON.parse(savedConfig);
                return {
                    mode: parsed.mode,
                    url: parsed.apiUrl,
                    isDemo: parsed.isDemo
                };
            } catch (e) {
                return { mode: 'demo', url: 'Demo Mode', isDemo: true };
            }
        }
        return { mode: 'demo', url: 'Demo Mode', isDemo: true };
    };

    const currentConfig = getCurrentConfigDisplay();

    return (
        <>
            <Card sx={{ mb: 2 }}>
                <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <SettingsIcon sx={{ mr: 2, color: '#2E86AB' }} />
                            <Box>
                                <Typography variant="h6">API Configuration</Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Current: {currentConfig.mode} mode
                                </Typography>
                            </Box>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Chip
                                icon={currentConfig.isDemo ? <CloudIcon /> : <LocalIcon />}
                                label={currentConfig.isDemo ? 'Demo Mode' : 'Live API'}
                                color={currentConfig.isDemo ? 'warning' : 'success'}
                                size="small"
                            />
                            <Button
                                variant="outlined"
                                startIcon={<SettingsIcon />}
                                onClick={() => setOpen(true)}
                                size="small"
                            >
                                Configure
                            </Button>
                        </Box>
                    </Box>
                </CardContent>
            </Card>

            <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
                <DialogTitle>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <SettingsIcon sx={{ mr: 2 }} />
                        API Configuration
                    </Box>
                </DialogTitle>
                <DialogContent>
                    <Alert severity="info" sx={{ mb: 3 }}>
                        <strong>Choose your API mode:</strong>
                        <br />
                        • <strong>Demo Mode:</strong> Works offline with mock data
                        <br />
                        • <strong>Local API:</strong> Connect to your local server (localhost:5001)
                        <br />
                        • <strong>Custom URL:</strong> Connect to your ngrok or custom server
                    </Alert>

                    <FormControl component="fieldset" fullWidth>
                        <RadioGroup
                            value={config.mode}
                            onChange={(e) => handleModeChange(e.target.value as any)}
                        >
                            <FormControlLabel
                                value="demo"
                                control={<Radio />}
                                label={
                                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                        <CloudIcon sx={{ mr: 1 }} />
                                        <Box>
                                            <Typography variant="body1">Demo Mode</Typography>
                                            <Typography variant="caption" color="text.secondary">
                                                Works offline with simulated IBM Quantum features
                                            </Typography>
                                        </Box>
                                    </Box>
                                }
                            />
                            
                            <FormControlLabel
                                value="local"
                                control={<Radio />}
                                label={
                                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                        <LocalIcon sx={{ mr: 1 }} />
                                        <Box>
                                            <Typography variant="body1">Local API Server</Typography>
                                            <Typography variant="caption" color="text.secondary">
                                                Connect to localhost:5001 (requires running: python api.py)
                                            </Typography>
                                        </Box>
                                    </Box>
                                }
                            />
                            
                            <FormControlLabel
                                value="custom"
                                control={<Radio />}
                                label={
                                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                        <SettingsIcon sx={{ mr: 1 }} />
                                        <Box>
                                            <Typography variant="body1">Custom API URL</Typography>
                                            <Typography variant="caption" color="text.secondary">
                                                Use ngrok or your own server URL
                                            </Typography>
                                        </Box>
                                    </Box>
                                }
                            />
                        </RadioGroup>
                    </FormControl>

                    {config.mode === 'custom' && (
                        <Box sx={{ mt: 2 }}>
                            <TextField
                                fullWidth
                                label="Custom API URL"
                                value={customUrl}
                                onChange={(e) => setCustomUrl(e.target.value)}
                                placeholder="https://your-ngrok-url.ngrok.io"
                                helperText="Enter your ngrok URL or custom server URL"
                                InputProps={{
                                    endAdornment: (
                                        <Tooltip title="Test Connection">
                                            <IconButton
                                                onClick={() => testApiConnection(customUrl)}
                                                disabled={!customUrl || testing}
                                            >
                                                <RefreshIcon />
                                            </IconButton>
                                        </Tooltip>
                                    )
                                }}
                            />
                        </Box>
                    )}

                    {config.mode === 'local' && (
                        <Alert severity="warning" sx={{ mt: 2 }}>
                            <strong>Local API Setup:</strong>
                            <br />
                            1. Open terminal in your project directory
                            <br />
                            2. Run: <code>python api.py</code>
                            <br />
                            3. Make sure the server is running on port 5001
                        </Alert>
                    )}

                    {testResult && (
                        <Alert 
                            severity={testResult.success ? 'success' : 'error'} 
                            sx={{ mt: 2 }}
                        >
                            {testResult.message}
                        </Alert>
                    )}

                    <Box sx={{ mt: 3, p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
                        <Typography variant="subtitle2" gutterBottom>
                            🚀 How to use your local API with GitHub Pages:
                        </Typography>
                        <Typography variant="body2" component="div">
                            1. Start your local API: <code>python api.py</code><br />
                            2. Install ngrok: <code>brew install ngrok</code><br />
                            3. Expose your API: <code>ngrok http 5001</code><br />
                            4. Copy the https URL from ngrok<br />
                            5. Paste it in "Custom API URL" above<br />
                            6. Click "Save Configuration"
                        </Typography>
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpen(false)}>Cancel</Button>
                    <Button 
                        onClick={saveConfiguration} 
                        variant="contained"
                        disabled={testing}
                    >
                        Save Configuration
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
};

export default ApiConfiguration; 