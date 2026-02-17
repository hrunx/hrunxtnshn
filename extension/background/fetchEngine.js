/**
 * Fetch Engine
 * Handles authenticated HTTP requests using user cookies
 */

const fetchEngine = {
  /**
   * Fetch URL with user session cookies
   */
  async fetchWithSession(url) {
    try {
      const response = await fetch(url, {
        credentials: 'include',
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.5'
        }
      });
      
      const text = await response.text();
      
      return {
        ok: response.ok,
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
        body: text,
        url: response.url
      };
    } catch (error) {
      console.error('Fetch error:', error);
      throw error;
    }
  },

  /**
   * Get cookies for a URL
   */
  async getCookies(url) {
    const urlObj = new URL(url);
    const cookies = await chrome.cookies.getAll({
      domain: urlObj.hostname
    });
    return cookies;
  },

  /**
   * Check if user is logged in to a domain
   */
  async isLoggedIn(domain) {
    const cookies = await chrome.cookies.getAll({ domain });
    
    // Check for common session cookies
    const sessionCookies = cookies.filter(cookie => {
      const name = cookie.name.toLowerCase();
      return name.includes('session') || 
             name.includes('auth') || 
             name.includes('token') ||
             name.includes('login');
    });
    
    return sessionCookies.length > 0;
  }
};
