/*
 * Quantum Memory Compiler - Web Dashboard
 * Copyright (c) 2025 Quantum Memory Compiler Project
 * Licensed under the Apache License, Version 2.0
 */

import { Settings as SettingsIcon } from '@mui/icons-material';
import { Box, Card, CardContent, Typography } from '@mui/material';
import React from 'react';

const Settings: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
        <SettingsIcon sx={{ mr: 2, color: '#2E86AB' }} />
        Settings
      </Typography>

      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Application Settings
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Settings functionality will be implemented here.
            This will include API configuration, theme settings, and performance preferences.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Settings; 