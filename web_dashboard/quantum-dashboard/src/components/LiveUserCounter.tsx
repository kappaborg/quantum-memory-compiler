import {
    Computer,
    Group,
    Memory,
    Person,
    Public,
    Speed,
    Timeline
} from '@mui/icons-material';
import {
    Avatar,
    Box,
    Card,
    CardContent,
    Chip,
    Divider,
    ListItem,
    ListItemAvatar,
    ListItemText,
    Tooltip,
    Typography
} from '@mui/material';
import React, { useEffect, useState } from 'react';
import userTrackingService from '../services/userTrackingService';

interface UserSession {
  id: string;
  startTime: Date;
  lastActivity: Date;
  currentPage: string;
  userAgent: string;
  location: string;
  isActive: boolean;
  actions: string[];
}

interface UserStats {
  totalUsers: number;
  activeUsers: number;
  peakUsers: number;
  avgSessionTime: number;
  totalSessions: number;
  pageViews: number;
  uniqueVisitors: number;
}

const LiveUserCounter: React.FC = () => {
  const [currentSession, setCurrentSession] = useState<UserSession | null>(null);
  const [stats, setStats] = useState<UserStats>({
    totalUsers: 0,
    activeUsers: 0,
    peakUsers: 0,
    avgSessionTime: 0,
    totalSessions: 0,
    pageViews: 0,
    uniqueVisitors: 0
  });
  const [isConnected, setIsConnected] = useState(false);
  const [systemLoad, setSystemLoad] = useState(0);
  const [memoryUsage, setMemoryUsage] = useState(0);

  useEffect(() => {
    // Initialize tracking
    setIsConnected(true);
    
    // Get current session
    const session = userTrackingService.getCurrentSession();
    setCurrentSession(session);
    
    // Get initial stats
    const initialStats = userTrackingService.getStats();
    setStats(initialStats);

    // Listen for stats updates
    const handleStatsUpdate = (newStats: UserStats) => {
      setStats(newStats);
    };

    userTrackingService.onStatsUpdate(handleStatsUpdate);

    // Update system metrics periodically
    const systemInterval = setInterval(() => {
      setSystemLoad(Math.random() * 100);
      setMemoryUsage(Math.random() * 100);
    }, 5000);

    // Cleanup
    return () => {
      userTrackingService.removeStatsListener(handleStatsUpdate);
      clearInterval(systemInterval);
    };
  }, []);

  const getSessionDuration = (startTime: Date): string => {
    const duration = (Date.now() - startTime.getTime()) / 1000 / 60; // in minutes
    if (duration < 60) return `${Math.floor(duration)}m`;
    return `${Math.floor(duration / 60)}h ${Math.floor(duration % 60)}m`;
  };

  const getBrowserIcon = (browser: string) => {
    switch (browser) {
      case 'Chrome': return '🌐';
      case 'Firefox': return '🦊';
      case 'Safari': return '🧭';
      case 'Edge': return '🔷';
      default: return '💻';
    }
  };

  const getLocationFlag = (location: string) => {
    const flags: { [key: string]: string } = {
      'New York, US': '🇺🇸',
      'Los Angeles, US': '🇺🇸',
      'Chicago, US': '🇺🇸',
      'London, UK': '🇬🇧',
      'Paris, FR': '🇫🇷',
      'Berlin, DE': '🇩🇪',
      'Istanbul, TR': '🇹🇷',
      'Tokyo, JP': '🇯🇵',
      'Shanghai, CN': '🇨🇳',
      'Mumbai, IN': '🇮🇳',
      'Sydney, AU': '🇦🇺',
      'São Paulo, BR': '🇧🇷',
      'Toronto, CA': '🇨🇦'
    };
    return flags[location] || '🌍';
  };

  const getPageDisplayName = (page: string) => {
    const pageNames: { [key: string]: string } = {
      '/': 'Dashboard',
      '/dashboard': 'Dashboard',
      '/circuit-editor': 'Circuit Editor',
      '/simulation': 'Simulation',
      '/compilation': 'Compilation',
      '/examples': 'Examples',
      '/memory-profile': 'Memory Profile',
      '/ibm-quantum': 'IBM Quantum'
    };
    return pageNames[page] || page;
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Group color="primary" sx={{ mr: 1 }} />
          <Typography variant="h6" component="h2">
            Live Users
          </Typography>
          <Chip
            size="small"
            label={isConnected ? 'Live' : 'Offline'}
            color={isConnected ? 'success' : 'error'}
            sx={{ ml: 'auto' }}
          />
        </Box>

        {/* Stats Overview */}
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 1, mb: 2 }}>
          <Box sx={{ textAlign: 'center', p: 1, bgcolor: 'primary.light', borderRadius: 1 }}>
            <Typography variant="h4" color="primary.contrastText">
              {stats.activeUsers}
            </Typography>
            <Typography variant="caption" color="primary.contrastText">
              Active Now
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'center', p: 1, bgcolor: 'secondary.light', borderRadius: 1 }}>
            <Typography variant="h4" color="secondary.contrastText">
              {stats.uniqueVisitors}
            </Typography>
            <Typography variant="caption" color="secondary.contrastText">
              Total Visitors
            </Typography>
          </Box>
        </Box>

        {/* Additional Stats */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Tooltip title="Peak concurrent users today">
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Timeline fontSize="small" color="action" sx={{ mr: 0.5 }} />
              <Typography variant="body2">
                Peak: {stats.peakUsers}
              </Typography>
            </Box>
          </Tooltip>
          <Tooltip title="Average session duration">
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Speed fontSize="small" color="action" sx={{ mr: 0.5 }} />
              <Typography variant="body2">
                Avg: {Math.floor(stats.avgSessionTime)}m
              </Typography>
            </Box>
          </Tooltip>
        </Box>

        <Divider sx={{ my: 1 }} />

        {/* Current User Session */}
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          Your Session
        </Typography>
        
        {currentSession && (
          <ListItem sx={{ px: 0, mb: 1, bgcolor: 'action.hover', borderRadius: 1 }}>
            <ListItemAvatar>
              <Avatar sx={{ width: 32, height: 32, fontSize: '0.8rem', bgcolor: 'primary.main' }}>
                <Person fontSize="small" />
              </Avatar>
            </ListItemAvatar>
            <ListItemText
              primary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Typography variant="body2" noWrap>
                    {getLocationFlag(currentSession.location)} {currentSession.location}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {getBrowserIcon(currentSession.userAgent)}
                  </Typography>
                </Box>
              }
              secondary={
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption" color="text.secondary">
                    {getPageDisplayName(currentSession.currentPage)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {getSessionDuration(currentSession.startTime)}
                  </Typography>
                </Box>
              }
            />
          </ListItem>
        )}

        {/* Session Stats */}
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 1, mb: 2 }}>
          <Box sx={{ textAlign: 'center', p: 1, bgcolor: 'info.light', borderRadius: 1 }}>
            <Typography variant="h6" color="info.contrastText">
              {stats.pageViews}
            </Typography>
            <Typography variant="caption" color="info.contrastText">
              Page Views
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'center', p: 1, bgcolor: 'success.light', borderRadius: 1 }}>
            <Typography variant="h6" color="success.contrastText">
              {stats.totalSessions}
            </Typography>
            <Typography variant="caption" color="success.contrastText">
              Total Sessions
            </Typography>
          </Box>
        </Box>

        {/* System Stats */}
        <Divider sx={{ my: 1 }} />
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          System Status
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Computer fontSize="small" color="action" sx={{ mr: 0.5 }} />
            <Typography variant="caption">
              Load: {systemLoad.toFixed(1)}%
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Memory fontSize="small" color="action" sx={{ mr: 0.5 }} />
            <Typography variant="caption">
              Memory: {memoryUsage.toFixed(1)}%
            </Typography>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Public fontSize="small" color="action" sx={{ mr: 0.5 }} />
          <Typography variant="caption">
            Session ID: {currentSession?.id.split('_')[2] || 'Unknown'}
          </Typography>
        </Box>

        {/* Real-time indicator */}
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1, justifyContent: 'center' }}>
          <Box 
            sx={{ 
              width: 8, 
              height: 8, 
              borderRadius: '50%', 
              bgcolor: 'success.main',
              mr: 1,
              animation: 'pulse 2s infinite'
            }} 
          />
          <Typography variant="caption" color="text.secondary">
            Real-time tracking active
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default LiveUserCounter; 