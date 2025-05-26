import { CloudQueue, Computer, Memory, Speed } from '@mui/icons-material';
import { Box, Card, CardContent, Chip, Grid, Typography } from '@mui/material';
import React from 'react';

const Dashboard: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
        <Computer sx={{ mr: 2, color: '#2E86AB' }} />
        Quantum Memory Compiler Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Memory sx={{ mr: 1, color: '#A23B72' }} />
                <Typography variant="h6">Memory</Typography>
              </Box>
              <Typography variant="h4" color="primary">4.0 GB</Typography>
              <Typography variant="body2" color="text.secondary">
                GPU Memory Available
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Speed sx={{ mr: 1, color: '#F18F01' }} />
                <Typography variant="h6">Performance</Typography>
              </Box>
              <Typography variant="h4" color="primary">8x</Typography>
              <Typography variant="body2" color="text.secondary">
                Parallel Workers
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CloudQueue sx={{ mr: 1, color: '#2E86AB' }} />
                <Typography variant="h6">IBM Quantum</Typography>
              </Box>
              <Chip label="Ready" color="success" />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Integration Status
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Computer sx={{ mr: 1, color: '#C73E1D' }} />
                <Typography variant="h6">Acceleration</Typography>
              </Box>
              <Chip label="GPU + JIT" color="success" />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Full Acceleration
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Welcome to Quantum Memory Compiler
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Advanced quantum circuit compilation with GPU acceleration and IBM Quantum integration.
            Navigate through the menu to access different features:
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Chip label="Circuit Editor" sx={{ mr: 1, mb: 1 }} />
            <Chip label="Simulation" sx={{ mr: 1, mb: 1 }} />
            <Chip label="Compilation" sx={{ mr: 1, mb: 1 }} />
            <Chip label="Memory Profile" sx={{ mr: 1, mb: 1 }} />
            <Chip label="IBM Quantum" sx={{ mr: 1, mb: 1 }} />
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Dashboard; 