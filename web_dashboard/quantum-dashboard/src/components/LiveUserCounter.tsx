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
    List,
    ListItem,
    ListItemAvatar,
    ListItemText,
    Tooltip,
    Typography
} from '@mui/material';
import React, { useEffect, useState } from 'react';

interface UserSession {
  id: string;
  location: string;
  browser: string;
  startTime: Date;
  lastActivity: Date;
  isActive: boolean;
  currentPage: string;
}

interface SystemStats {
  totalUsers: number;
  activeUsers: number;
  peakUsers: number;
  avgSessionTime: number;
  totalSessions: number;
  systemLoad: number;
  memoryUsage: number;
}

const LiveUserCounter: React.FC = () => {
  const [users, setUsers] = useState<UserSession[]>([]);
  const [stats, setStats] = useState<SystemStats>({
    totalUsers: 0,
    activeUsers: 0,
    peakUsers: 0,
    avgSessionTime: 0,
    totalSessions: 0,
    systemLoad: 0,
    memoryUsage: 0
  });
  const [isConnected, setIsConnected] = useState(false);

  // Simulated user data generator
  const generateRandomUser = (): UserSession => {
    const locations = ['New York', 'London', 'Tokyo', 'Berlin', 'Sydney', 'São Paulo', 'Mumbai', 'Toronto'];
    const browsers = ['Chrome', 'Firefox', 'Safari', 'Edge'];
    const pages = ['/dashboard', '/circuit-editor', '/simulation', '/compilation', '/examples'];
    
    return {
      id: Math.random().toString(36).substr(2, 9),
      location: locations[Math.floor(Math.random() * locations.length)],
      browser: browsers[Math.floor(Math.random() * browsers.length)],
      startTime: new Date(Date.now() - Math.random() * 3600000), // Random start time within last hour
      lastActivity: new Date(Date.now() - Math.random() * 300000), // Random activity within last 5 minutes
      isActive: Math.random() > 0.3, // 70% chance of being active
      currentPage: pages[Math.floor(Math.random() * pages.length)]
    };
  };

  // Initialize with some users
  useEffect(() => {
    const initialUsers = Array.from({ length: Math.floor(Math.random() * 8) + 2 }, generateRandomUser);
    setUsers(initialUsers);
    setIsConnected(true);

    // Simulate real-time updates
    const interval = setInterval(() => {
      setUsers(prevUsers => {
        let newUsers = [...prevUsers];
        
        // Randomly add new users (20% chance)
        if (Math.random() < 0.2 && newUsers.length < 15) {
          newUsers.push(generateRandomUser());
        }
        
        // Randomly remove users (15% chance)
        if (Math.random() < 0.15 && newUsers.length > 1) {
          const randomIndex = Math.floor(Math.random() * newUsers.length);
          newUsers.splice(randomIndex, 1);
        }
        
        // Update user activity
        newUsers = newUsers.map(user => ({
          ...user,
          isActive: Math.random() > 0.25, // 75% chance of being active
          lastActivity: Math.random() < 0.3 ? new Date() : user.lastActivity
        }));
        
        return newUsers;
      });
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  // Update stats when users change
  useEffect(() => {
    const activeUsers = users.filter(user => user.isActive).length;
    const totalSessions = users.length + Math.floor(Math.random() * 50) + 100; // Simulate total sessions
    const avgSessionTime = users.reduce((acc, user) => {
      const sessionTime = (Date.now() - user.startTime.getTime()) / 1000 / 60; // in minutes
      return acc + sessionTime;
    }, 0) / users.length || 0;

    setStats(prevStats => ({
      totalUsers: users.length,
      activeUsers,
      peakUsers: Math.max(users.length, prevStats.peakUsers),
      avgSessionTime,
      totalSessions,
      systemLoad: Math.random() * 100,
      memoryUsage: Math.random() * 100
    }));
  }, [users]);

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
      'New York': '🇺🇸',
      'London': '🇬🇧',
      'Tokyo': '🇯🇵',
      'Berlin': '🇩🇪',
      'Sydney': '🇦🇺',
      'São Paulo': '🇧🇷',
      'Mumbai': '🇮🇳',
      'Toronto': '🇨🇦'
    };
    return flags[location] || '🌍';
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
              {stats.totalUsers}
            </Typography>
            <Typography variant="caption" color="secondary.contrastText">
              Total Online
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

        {/* Active Users List */}
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          Active Users ({stats.activeUsers})
        </Typography>
        
        <List dense sx={{ maxHeight: 300, overflow: 'auto' }}>
          {users
            .filter(user => user.isActive)
            .slice(0, 8) // Show max 8 users
            .map((user) => (
              <ListItem key={user.id} sx={{ px: 0 }}>
                <ListItemAvatar>
                  <Avatar sx={{ width: 32, height: 32, fontSize: '0.8rem' }}>
                    <Person fontSize="small" />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Typography variant="body2" noWrap>
                        {getLocationFlag(user.location)} {user.location}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {getBrowserIcon(user.browser)}
                      </Typography>
                    </Box>
                  }
                  secondary={
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="caption" color="text.secondary">
                        {user.currentPage}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {getSessionDuration(user.startTime)}
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            ))}
        </List>

        {/* System Stats */}
        <Divider sx={{ my: 1 }} />
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          System Status
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Computer fontSize="small" color="action" sx={{ mr: 0.5 }} />
            <Typography variant="caption">
              Load: {stats.systemLoad.toFixed(1)}%
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Memory fontSize="small" color="action" sx={{ mr: 0.5 }} />
            <Typography variant="caption">
              Memory: {stats.memoryUsage.toFixed(1)}%
            </Typography>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Public fontSize="small" color="action" sx={{ mr: 0.5 }} />
          <Typography variant="caption">
            Total Sessions Today: {stats.totalSessions}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default LiveUserCounter; 