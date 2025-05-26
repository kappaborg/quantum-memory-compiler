import { Box, CssBaseline } from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import React from 'react';
import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import CircuitEditor from './components/CircuitEditor';
import Compilation from './components/Compilation';
import Dashboard from './components/Dashboard';
import IBMQuantumConnection from './components/IBMQuantumConnection';
import MemoryProfile from './components/MemoryProfile';
import Settings from './components/Settings';
import Sidebar from './components/Sidebar';
import Simulation from './components/Simulation';

// Dark quantum theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2E86AB',
      light: '#5BA3C7',
      dark: '#1B5A7A',
    },
    secondary: {
      main: '#A23B72',
      light: '#C85A8E',
      dark: '#7A2B55',
    },
    background: {
      default: '#0A0E1A',
      paper: '#1A1F2E',
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#B0BEC5',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'linear-gradient(135deg, #1A1F2E 0%, #2A2F3E 100%)',
          border: '1px solid #2E86AB20',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
  },
});

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
          <Sidebar />
          <Box component="main" sx={{ flexGrow: 1, overflow: 'auto' }}>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/circuit-editor" element={<CircuitEditor />} />
              <Route path="/simulation" element={<Simulation />} />
              <Route path="/compilation" element={<Compilation />} />
              <Route path="/memory-profile" element={<MemoryProfile />} />
              <Route path="/ibm-quantum" element={<IBMQuantumConnection />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
};

export default App;
