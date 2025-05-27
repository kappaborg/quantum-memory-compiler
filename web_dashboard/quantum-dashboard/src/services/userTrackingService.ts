/**
 * Real User Tracking Service
 * Tracks actual users visiting and using the quantum dashboard
 */

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

class UserTrackingService {
  private currentSession: UserSession | null = null;
  private sessionId: string;
  private startTime: Date;
  private lastActivity: Date;
  private pageViews: number = 0;
  private actions: string[] = [];
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private statsUpdateInterval: NodeJS.Timeout | null = null;
  private listeners: ((stats: UserStats) => void)[] = [];

  constructor() {
    this.sessionId = this.generateSessionId();
    this.startTime = new Date();
    this.lastActivity = new Date();
    
    this.initializeSession();
    this.setupEventListeners();
    this.startHeartbeat();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private async getLocationInfo(): Promise<string> {
    try {
      // Try to get location from browser API (requires HTTPS)
      if ('geolocation' in navigator) {
        return new Promise((resolve) => {
          navigator.geolocation.getCurrentPosition(
            (position) => {
              // In a real app, you'd reverse geocode this
              resolve(`${position.coords.latitude.toFixed(1)}, ${position.coords.longitude.toFixed(1)}`);
            },
            () => {
              // Fallback to timezone-based location
              resolve(this.getTimezoneLocation());
            },
            { timeout: 5000 }
          );
        });
      }
    } catch (error) {
      console.log('Geolocation not available');
    }
    
    return this.getTimezoneLocation();
  }

  private getTimezoneLocation(): string {
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const locationMap: { [key: string]: string } = {
      'America/New_York': 'New York, US',
      'America/Los_Angeles': 'Los Angeles, US',
      'America/Chicago': 'Chicago, US',
      'Europe/London': 'London, UK',
      'Europe/Paris': 'Paris, FR',
      'Europe/Berlin': 'Berlin, DE',
      'Europe/Istanbul': 'Istanbul, TR',
      'Asia/Tokyo': 'Tokyo, JP',
      'Asia/Shanghai': 'Shanghai, CN',
      'Asia/Kolkata': 'Mumbai, IN',
      'Australia/Sydney': 'Sydney, AU',
      'America/Sao_Paulo': 'São Paulo, BR',
      'America/Toronto': 'Toronto, CA'
    };
    
    return locationMap[timezone] || timezone.split('/').pop() || 'Unknown';
  }

  private getBrowserInfo(): string {
    const ua = navigator.userAgent;
    if (ua.includes('Chrome')) return 'Chrome';
    if (ua.includes('Firefox')) return 'Firefox';
    if (ua.includes('Safari')) return 'Safari';
    if (ua.includes('Edge')) return 'Edge';
    return 'Other';
  }

  private async initializeSession(): Promise<void> {
    const location = await this.getLocationInfo();
    
    this.currentSession = {
      id: this.sessionId,
      startTime: this.startTime,
      lastActivity: this.lastActivity,
      currentPage: window.location.pathname,
      userAgent: this.getBrowserInfo(),
      location,
      isActive: true,
      actions: []
    };

    // Store session in localStorage for persistence
    this.saveSessionToStorage();
    
    // Track page view
    this.trackPageView(window.location.pathname);
  }

  private saveSessionToStorage(): void {
    if (this.currentSession) {
      localStorage.setItem('quantum_user_session', JSON.stringify({
        ...this.currentSession,
        startTime: this.currentSession.startTime.toISOString(),
        lastActivity: this.currentSession.lastActivity.toISOString()
      }));
    }
  }

  private loadSessionFromStorage(): UserSession | null {
    try {
      const stored = localStorage.getItem('quantum_user_session');
      if (stored) {
        const session = JSON.parse(stored);
        return {
          ...session,
          startTime: new Date(session.startTime),
          lastActivity: new Date(session.lastActivity)
        };
      }
    } catch (error) {
      console.error('Failed to load session from storage:', error);
    }
    return null;
  }

  private setupEventListeners(): void {
    // Track page navigation
    window.addEventListener('popstate', () => {
      this.trackPageView(window.location.pathname);
    });

    // Track user activity
    ['click', 'keydown', 'scroll', 'mousemove'].forEach(event => {
      document.addEventListener(event, () => {
        this.updateActivity();
      }, { passive: true });
    });

    // Track page visibility
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.setInactive();
      } else {
        this.setActive();
      }
    });

    // Track before unload
    window.addEventListener('beforeunload', () => {
      this.endSession();
    });
  }

  private startHeartbeat(): void {
    // Send heartbeat every 30 seconds
    this.heartbeatInterval = setInterval(() => {
      this.sendHeartbeat();
    }, 30000);

    // Update stats every 10 seconds
    this.statsUpdateInterval = setInterval(() => {
      this.updateStats();
    }, 10000);
  }

  private sendHeartbeat(): void {
    if (this.currentSession && this.currentSession.isActive) {
      this.updateActivity();
      
      // In a real implementation, you'd send this to your backend
      console.log('📡 User heartbeat:', {
        sessionId: this.sessionId,
        timestamp: new Date().toISOString(),
        page: window.location.pathname
      });
    }
  }

  private updateActivity(): void {
    this.lastActivity = new Date();
    if (this.currentSession) {
      this.currentSession.lastActivity = this.lastActivity;
      this.currentSession.isActive = true;
      this.saveSessionToStorage();
    }
  }

  private setActive(): void {
    if (this.currentSession) {
      this.currentSession.isActive = true;
      this.updateActivity();
    }
  }

  private setInactive(): void {
    if (this.currentSession) {
      this.currentSession.isActive = false;
      this.saveSessionToStorage();
    }
  }

  public trackPageView(page: string): void {
    this.pageViews++;
    if (this.currentSession) {
      this.currentSession.currentPage = page;
      this.saveSessionToStorage();
    }
    
    console.log('📄 Page view:', page);
  }

  public trackAction(action: string): void {
    this.actions.push(action);
    if (this.currentSession) {
      this.currentSession.actions.push(`${new Date().toISOString()}: ${action}`);
      this.saveSessionToStorage();
    }
    
    console.log('🎯 User action:', action);
  }

  private updateStats(): void {
    const stats = this.calculateStats();
    this.notifyListeners(stats);
  }

  private calculateStats(): UserStats {
    // Get all sessions from localStorage (in a real app, this would come from backend)
    const allSessions = this.getAllStoredSessions();
    const now = new Date();
    const fiveMinutesAgo = new Date(now.getTime() - 5 * 60 * 1000);
    
    // Count active users (activity within last 5 minutes)
    const activeUsers = allSessions.filter(session => 
      session.isActive && new Date(session.lastActivity) > fiveMinutesAgo
    ).length;

    // Calculate session duration
    const sessionDurations = allSessions.map(session => {
      const start = new Date(session.startTime);
      const end = session.isActive ? now : new Date(session.lastActivity);
      return (end.getTime() - start.getTime()) / 1000 / 60; // in minutes
    });

    const avgSessionTime = sessionDurations.length > 0 
      ? sessionDurations.reduce((a, b) => a + b, 0) / sessionDurations.length 
      : 0;

    // Get stored stats
    const storedStats = this.getStoredStats();

    return {
      totalUsers: allSessions.length,
      activeUsers: Math.max(activeUsers, 1), // At least current user
      peakUsers: Math.max(storedStats.peakUsers, activeUsers),
      avgSessionTime,
      totalSessions: storedStats.totalSessions + allSessions.length,
      pageViews: storedStats.pageViews + this.pageViews,
      uniqueVisitors: storedStats.uniqueVisitors + 1
    };
  }

  private getAllStoredSessions(): any[] {
    // In a real implementation, this would fetch from backend
    // For now, we'll simulate with current session
    const currentSession = this.loadSessionFromStorage();
    return currentSession ? [currentSession] : [];
  }

  private getStoredStats(): UserStats {
    try {
      const stored = localStorage.getItem('quantum_user_stats');
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
    
    return {
      totalUsers: 0,
      activeUsers: 0,
      peakUsers: 0,
      avgSessionTime: 0,
      totalSessions: 0,
      pageViews: 0,
      uniqueVisitors: 0
    };
  }

  private saveStats(stats: UserStats): void {
    localStorage.setItem('quantum_user_stats', JSON.stringify(stats));
  }

  public onStatsUpdate(callback: (stats: UserStats) => void): void {
    this.listeners.push(callback);
  }

  public removeStatsListener(callback: (stats: UserStats) => void): void {
    const index = this.listeners.indexOf(callback);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }

  private notifyListeners(stats: UserStats): void {
    this.listeners.forEach(callback => callback(stats));
  }

  public getCurrentSession(): UserSession | null {
    return this.currentSession;
  }

  public getStats(): UserStats {
    return this.calculateStats();
  }

  private endSession(): void {
    if (this.currentSession) {
      this.currentSession.isActive = false;
      this.saveSessionToStorage();
      
      // Save final stats
      const stats = this.calculateStats();
      this.saveStats(stats);
    }

    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }
    
    if (this.statsUpdateInterval) {
      clearInterval(this.statsUpdateInterval);
    }
  }

  public destroy(): void {
    this.endSession();
    this.listeners = [];
  }
}

// Create singleton instance
export const userTrackingService = new UserTrackingService();

export default userTrackingService; 