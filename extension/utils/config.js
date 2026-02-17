/**
 * Configuration Manager
 * Handles extension settings across different integration modes
 */

const DEFAULT_CONFIG = {
  mode: 'standalone', // 'standalone' | 'platform' | 'orchestrator'
  standalone: {
    apiKey: '',
    model: 'gpt-4.1-mini',
    baseUrl: 'https://api.openai.com/v1'
  },
  platform: {
    type: 'gasable', // 'leadora' | 'gasable'
    endpoint: '',
    apiKey: ''
  },
  orchestrator: {
    endpoint: 'http://localhost:8000',
    apiKey: ''
  },
  permissions: {
    offscreenApproved: false
  }
};

class ConfigManager {
  constructor() {
    this.config = null;
  }

  /**
   * Initialize configuration from storage
   */
  async init() {
    const stored = await chrome.storage.sync.get('config');
    this.config = { ...DEFAULT_CONFIG, ...(stored.config || {}) };
    return this.config;
  }

  /**
   * Get current configuration
   */
  async get() {
    if (!this.config) {
      await this.init();
    }
    return this.config;
  }

  /**
   * Update configuration
   */
  async set(updates) {
    if (!this.config) {
      await this.init();
    }
    this.config = { ...this.config, ...updates };
    await chrome.storage.sync.set({ config: this.config });
    return this.config;
  }

  /**
   * Get specific mode configuration
   */
  async getMode() {
    const config = await this.get();
    return config.mode;
  }

  /**
   * Set integration mode
   */
  async setMode(mode) {
    return await this.set({ mode });
  }

  /**
   * Get API configuration for current mode
   */
  async getApiConfig() {
    const config = await this.get();
    const mode = config.mode;
    
    switch (mode) {
      case 'standalone':
        return {
          type: 'openai',
          apiKey: config.standalone.apiKey,
          model: config.standalone.model,
          baseUrl: config.standalone.baseUrl
        };
      
      case 'platform':
        return {
          type: 'platform',
          platform: config.platform.type,
          endpoint: config.platform.endpoint,
          apiKey: config.platform.apiKey
        };
      
      case 'orchestrator':
        return {
          type: 'orchestrator',
          endpoint: config.orchestrator.endpoint,
          apiKey: config.orchestrator.apiKey
        };
      
      default:
        throw new Error(`Unknown mode: ${mode}`);
    }
  }

  /**
   * Validate configuration for current mode
   */
  async validate() {
    const config = await this.get();
    const mode = config.mode;
    
    switch (mode) {
      case 'standalone':
        if (!config.standalone.apiKey) {
          throw new Error('OpenAI API key is required for standalone mode');
        }
        break;
      
      case 'platform':
        if (!config.platform.endpoint || !config.platform.apiKey) {
          throw new Error('Platform endpoint and API key are required');
        }
        break;
      
      case 'orchestrator':
        if (!config.orchestrator.endpoint) {
          throw new Error('Orchestrator endpoint is required');
        }
        break;
    }
    
    return true;
  }

  /**
   * Reset to default configuration
   */
  async reset() {
    this.config = { ...DEFAULT_CONFIG };
    await chrome.storage.sync.set({ config: this.config });
    return this.config;
  }

  /**
   * Check if offscreen permission is approved
   */
  async isOffscreenApproved() {
    const config = await this.get();
    return config.permissions.offscreenApproved;
  }

  /**
   * Set offscreen permission approval
   */
  async setOffscreenApproved(approved) {
    const config = await this.get();
    config.permissions.offscreenApproved = approved;
    await this.set(config);
  }
}

// Export singleton instance
const configManager = new ConfigManager();
