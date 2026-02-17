/**
 * API Client
 * Unified client for all integration modes (standalone, platform, orchestrator)
 */

importScripts('../utils/config.js');

class ApiClient {
  constructor() {
    this.config = null;
  }

  /**
   * Initialize API client with configuration
   */
  async init() {
    this.config = await configManager.getApiConfig();
  }

  /**
   * Execute a task through the appropriate API
   */
  async executeTask(task) {
    if (!this.config) {
      await this.init();
    }

    switch (this.config.type) {
      case 'openai':
        return await this.executeWithOpenAI(task);
      
      case 'platform':
        return await this.executeWithPlatform(task);
      
      case 'orchestrator':
        return await this.executeWithOrchestrator(task);
      
      default:
        throw new Error(`Unknown API type: ${this.config.type}`);
    }
  }

  /**
   * Execute task with OpenAI API (standalone mode)
   */
  async executeWithOpenAI(task) {
    const messages = [
      {
        role: 'system',
        content: `You are an autonomous browsing agent. You can:
- Load web pages invisibly using offscreen rendering
- Extract data from LinkedIn, Instagram, and Google Maps
- Fetch authenticated content using user cookies
- Plan and execute multi-step research tasks

Available actions:
- LOAD_PAGE: Load a URL in offscreen browser
- FETCH: Fetch URL with user session
- EXTRACT_LINKEDIN: Extract LinkedIn profile data
- EXTRACT_INSTAGRAM: Extract Instagram profile data
- EXTRACT_MAPS: Extract Google Maps place data

Respond with a JSON array of actions to execute. Example:
[
  {"action": "LOAD_PAGE", "url": "https://linkedin.com/in/example"},
  {"action": "EXTRACT_LINKEDIN"}
]`
      },
      {
        role: 'user',
        content: task.prompt || task.description || JSON.stringify(task)
      }
    ];

    const response = await fetch(`${this.config.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.config.apiKey}`
      },
      body: JSON.stringify({
        model: this.config.model,
        messages: messages,
        temperature: 0.7,
        max_tokens: 2000
      })
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`OpenAI API error: ${error}`);
    }

    const data = await response.json();
    const content = data.choices[0].message.content;
    
    // Try to parse JSON response
    try {
      const actions = JSON.parse(content);
      return { actions, raw: content };
    } catch (e) {
      // If not JSON, return as text
      return { text: content, raw: content };
    }
  }

  /**
   * Execute task with platform API (Leadora/Gasable Hub)
   */
  async executeWithPlatform(task) {
    const endpoint = this.config.endpoint;
    const platform = this.config.platform;

    // Platform-specific API format
    const payload = {
      task: task,
      extensionId: chrome.runtime.id,
      capabilities: [
        'offscreen_browsing',
        'linkedin_extraction',
        'instagram_extraction',
        'maps_extraction',
        'authenticated_fetch'
      ]
    };

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.config.apiKey}`,
        'X-Platform': platform
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Platform API error: ${error}`);
    }

    return await response.json();
  }

  /**
   * Execute task with custom orchestrator
   */
  async executeWithOrchestrator(task) {
    const endpoint = `${this.config.endpoint}/api/tasks`;
    
    const headers = {
      'Content-Type': 'application/json'
    };

    if (this.config.apiKey) {
      headers['Authorization'] = `Bearer ${this.config.apiKey}`;
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(task)
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Orchestrator API error: ${error}`);
    }

    return await response.json();
  }

  /**
   * Stream task execution (for real-time updates)
   */
  async *streamTask(task) {
    if (!this.config) {
      await this.init();
    }

    // Only orchestrator supports streaming for now
    if (this.config.type === 'orchestrator') {
      const endpoint = `${this.config.endpoint}/api/tasks/stream`;
      
      const headers = {
        'Content-Type': 'application/json'
      };

      if (this.config.apiKey) {
        headers['Authorization'] = `Bearer ${this.config.apiKey}`;
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(task)
      });

      if (!response.ok) {
        throw new Error(`Orchestrator API error: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.trim());
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            yield data;
          }
        }
      }
    } else {
      // For non-streaming modes, just return the result
      const result = await this.executeTask(task);
      yield result;
    }
  }

  /**
   * Test API connection
   */
  async testConnection() {
    if (!this.config) {
      await this.init();
    }

    try {
      switch (this.config.type) {
        case 'openai':
          const response = await fetch(`${this.config.baseUrl}/models`, {
            headers: {
              'Authorization': `Bearer ${this.config.apiKey}`
            }
          });
          return response.ok;
        
        case 'platform':
        case 'orchestrator':
          const healthEndpoint = this.config.type === 'orchestrator'
            ? `${this.config.endpoint}/health`
            : this.config.endpoint;
          
          const healthResponse = await fetch(healthEndpoint);
          return healthResponse.ok;
        
        default:
          return false;
      }
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    }
  }
}

// Export singleton instance
const apiClient = new ApiClient();
