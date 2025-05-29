/*
 * Quantum Memory Compiler - Web Dashboard
 * Copyright (c) 2025 Quantum Memory Compiler Project
 * Licensed under the Apache License, Version 2.0
 */

import {
    CloudQueue as CloudIcon,
    Build as CompileIcon,
    Dashboard as DashboardIcon,
    Memory as MemoryIcon,
    PlayArrow as PlayIcon,
    Science as ScienceIcon,
    Settings as SettingsIcon
} from '@mui/icons-material';
import {
    Box,
    Card,
    CardContent,
    Chip,
    Drawer,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Typography
} from '@mui/material';
import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const drawerWidth = 280;

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Circuit Editor', icon: <ScienceIcon />, path: '/circuit-editor' },
    { text: 'Simulation', icon: <PlayIcon />, path: '/simulation' },
    { text: 'Compilation', icon: <CompileIcon />, path: '/compilation' },
    { text: 'Memory Profile', icon: <MemoryIcon />, path: '/memory-profile' },
    { text: 'IBM Quantum', icon: <CloudIcon />, path: '/ibm-quantum' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          background: 'linear-gradient(180deg, #1A1F2E 0%, #0F1419 100%)',
          borderRight: '1px solid #2E86AB30',
        },
      }}
    >
      <Box sx={{ p: 3, borderBottom: '1px solid #2E86AB30' }}>
        <Typography variant="h6" sx={{ color: '#2E86AB', fontWeight: 700 }}>
          🚀 Quantum Lab
        </Typography>
        <Typography variant="body2" sx={{ color: '#B0BEC5', mt: 0.5 }}>
          Developer: kappasutra
        </Typography>
      </Box>
      
      <List sx={{ pt: 2 }}>
        {menuItems.map((item) => (
          <ListItem
            key={item.text}
            onClick={() => navigate(item.path)}
            sx={{
              mx: 1,
              mb: 0.5,
              borderRadius: 2,
              cursor: 'pointer',
              backgroundColor: location.pathname === item.path ? '#2E86AB20' : 'transparent',
              '&:hover': {
                backgroundColor: '#2E86AB15',
              },
            }}
          >
            <ListItemIcon sx={{ color: location.pathname === item.path ? '#2E86AB' : '#B0BEC5' }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText 
              primary={item.text}
              sx={{ 
                '& .MuiListItemText-primary': { 
                  color: location.pathname === item.path ? '#2E86AB' : '#FFFFFF',
                  fontWeight: location.pathname === item.path ? 600 : 400,
                }
              }}
            />
          </ListItem>
        ))}
      </List>

      <Box sx={{ mt: 'auto', p: 2 }}>
        <Card sx={{ background: 'linear-gradient(135deg, #2E86AB20 0%, #A23B7220 100%)' }}>
          <CardContent sx={{ p: 2 }}>
            <Typography variant="body2" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
              Quantum Status
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
              <Chip 
                label="Online" 
                size="small" 
                sx={{ 
                  backgroundColor: '#4CAF50', 
                  color: 'white',
                  fontSize: '0.75rem'
                }} 
              />
            </Box>
            <Typography variant="caption" sx={{ color: '#B0BEC5', mt: 1, display: 'block' }}>
              API Server: Active
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Drawer>
  );
};

export default Sidebar; 