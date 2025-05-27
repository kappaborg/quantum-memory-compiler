/**
 * Environment Configuration Service
 * Manages environment variables and configuration for the Quantum Dashboard
 */

export interface EnvironmentConfig {
  apiUrl: string;
  isDemoMode: boolean;
  isGitHubPages: boolean;
  ibmQuantum: {
    token?: string;
    instance: string;
    channel: string;
    enabled: boolean;
  };
  development: {
    isDevMode: boolean;
    environment: string;
  };
}

class EnvironmentService {
  private config: EnvironmentConfig;

  constructor() {
    this.config = this.loadConfiguration();
  }

  private loadConfiguration(): EnvironmentConfig {
    // Check if we're in GitHub Pages environment
    const isGitHubPages = process.env.REACT_APP_GITHUB_PAGES === 'true' || 
                         window.location.hostname.includes('github.io') ||
                         window.location.hostname.includes('github.com');

    // Load IBM Quantum token from environment or localStorage
    const ibmToken = this.getIBMQuantumToken();

    // Determine API URL based on environment
    const apiUrl = this.determineApiUrl(isGitHubPages);

    // Demo mode logic
    const isDemoMode = this.determineDemoMode(isGitHubPages, ibmToken, apiUrl);

    return {
      apiUrl,
      isDemoMode,
      isGitHubPages,
      ibmQuantum: {
        token: ibmToken,
        instance: process.env.REACT_APP_IBM_QUANTUM_INSTANCE || 'ibm_quantum',
        channel: process.env.REACT_APP_IBM_QUANTUM_CHANNEL || 'ibm_quantum',
        enabled: !!ibmToken
      },
      development: {
        isDevMode: process.env.NODE_ENV === 'development',
        environment: process.env.REACT_APP_ENV || 'development'
      }
    };
  }

  private determineApiUrl(isGitHubPages: boolean): string {
    // Priority order for API URL:
    // 1. Environment variable
    // 2. localStorage setting
    // 3. Default based on environment

    const envApiUrl = process.env.REACT_APP_API_URL;
    if (envApiUrl && envApiUrl !== 'http://localhost:5001') {
      return envApiUrl;
    }

    const savedApiUrl = localStorage.getItem('quantum_api_url');
    if (savedApiUrl) {
      return savedApiUrl;
    }

    if (isGitHubPages) {
      // For GitHub Pages, use demo mode by default
      return 'demo://api.quantum-memory-compiler.local';
    }

    return 'http://localhost:5001';
  }

  private determineDemoMode(isGitHubPages: boolean, ibmToken?: string, apiUrl?: string): boolean {
    // Force demo mode if:
    // 1. Explicitly set in environment
    // 2. On GitHub Pages without real API
    // 3. API URL is demo URL
    // 4. No IBM token available

    if (process.env.REACT_APP_DEMO_MODE === 'true') {
      return true;
    }

    if (apiUrl?.startsWith('demo://')) {
      return true;
    }

    if (isGitHubPages && (!apiUrl || apiUrl.includes('localhost'))) {
      return true;
    }

    return false;
  }

  private getIBMQuantumToken(): string | undefined {
    // Priority order:
    // 1. Environment variable (for GitHub Pages)
    // 2. localStorage (for user input)
    // 3. sessionStorage (temporary)

    const envToken = process.env.REACT_APP_IBM_QUANTUM_TOKEN;
    if (envToken && envToken !== 'your_ibm_quantum_token_here') {
      return envToken;
    }

    const localToken = localStorage.getItem('ibm_quantum_token');
    if (localToken) {
      return localToken;
    }

    const sessionToken = sessionStorage.getItem('ibm_quantum_token');
    if (sessionToken) {
      return sessionToken;
    }

    return undefined;
  }

  /**
   * Get current configuration
   */
  getConfig(): EnvironmentConfig {
    return { ...this.config };
  }

  /**
   * Update IBM Quantum token
   */
  setIBMQuantumToken(token: string, persistent: boolean = true): void {
    this.config.ibmQuantum.token = token;
    this.config.ibmQuantum.enabled = !!token;
    this.config.isDemoMode = !token;

    if (persistent) {
      localStorage.setItem('ibm_quantum_token', token);
    } else {
      sessionStorage.setItem('ibm_quantum_token', token);
    }
  }

  /**
   * Clear IBM Quantum token
   */
  clearIBMQuantumToken(): void {
    this.config.ibmQuantum.token = undefined;
    this.config.ibmQuantum.enabled = false;
    this.config.isDemoMode = true;

    localStorage.removeItem('ibm_quantum_token');
    sessionStorage.removeItem('ibm_quantum_token');
  }

  /**
   * Check if IBM Quantum is available
   */
  isIBMQuantumAvailable(): boolean {
    return this.config.ibmQuantum.enabled && !!this.config.ibmQuantum.token;
  }

  /**
   * Get API base URL
   */
  getApiUrl(): string {
    return this.config.apiUrl;
  }

  /**
   * Check if in demo mode
   */
  isDemoMode(): boolean {
    return this.config.isDemoMode;
  }

  /**
   * Check if in GitHub Pages environment
   */
  isGitHubPages(): boolean {
    return this.config.isGitHubPages;
  }

  /**
   * Check if API is available (not demo mode)
   */
  isApiAvailable(): boolean {
    return !this.config.isDemoMode && 
           !this.config.apiUrl.startsWith('demo://') &&
           (this.config.apiUrl !== 'http://localhost:5001' || 
           !this.config.isGitHubPages);
  }

  /**
   * Get IBM Quantum configuration
   */
  getIBMQuantumConfig() {
    return {
      token: this.config.ibmQuantum.token,
      instance: this.config.ibmQuantum.instance,
      channel: this.config.ibmQuantum.channel
    };
  }

  /**
   * Update API URL (for development)
   */
  setApiUrl(url: string): void {
    this.config.apiUrl = url;
    this.config.isDemoMode = url.startsWith('demo://');
    localStorage.setItem('quantum_api_url', url);
  }

  /**
   * Reset to default configuration
   */
  resetToDefaults(): void {
    localStorage.removeItem('ibm_quantum_token');
    localStorage.removeItem('quantum_api_url');
    sessionStorage.clear();
    this.config = this.loadConfiguration();
  }

  /**
   * Export configuration for debugging
   */
  exportConfig(): string {
    const safeConfig = {
      ...this.config,
      ibmQuantum: {
        ...this.config.ibmQuantum,
        token: this.config.ibmQuantum.token ? '***HIDDEN***' : undefined
      }
    };
    return JSON.stringify(safeConfig, null, 2);
  }
}

// Create singleton instance
export const envService = new EnvironmentService();

// Export for React components
export default envService; 