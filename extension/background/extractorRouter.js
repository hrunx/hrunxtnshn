/**
 * Extractor Router
 * Routes extraction requests to appropriate extractors
 */

importScripts('../utils/schemaMaps.js', '../utils/schemaLinkedIn.js', '../utils/schemaInstagram.js');

const extractorRouter = {
  /**
   * Extract Google Maps data
   */
  async maps(url) {
    console.log('Extracting Maps data from:', url);
    
    // Load page in offscreen
    const html = await offscreenController.load(url);
    
    // Parse HTML
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    
    // Extract data using schema
    return parseMaps(doc);
  },

  /**
   * Extract LinkedIn profile data
   */
  async linkedin(url) {
    console.log('Extracting LinkedIn data from:', url);
    
    // Check if logged in
    const loggedIn = await fetchEngine.isLoggedIn('linkedin.com');
    if (!loggedIn) {
      throw new Error('Not logged in to LinkedIn');
    }
    
    // Load page in offscreen
    const html = await offscreenController.load(url);
    
    // Parse HTML
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    
    // Extract data using schema
    return parseLinkedIn(doc);
  },

  /**
   * Extract Instagram profile data
   */
  async instagram(url) {
    console.log('Extracting Instagram data from:', url);
    
    // Check if logged in
    const loggedIn = await fetchEngine.isLoggedIn('instagram.com');
    if (!loggedIn) {
      throw new Error('Not logged in to Instagram');
    }
    
    // Load page in offscreen
    const html = await offscreenController.load(url);
    
    // Parse HTML
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    
    // Extract data using schema
    return parseInstagram(doc);
  }
};
