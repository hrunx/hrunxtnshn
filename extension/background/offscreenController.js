/**
 * Offscreen Controller
 * Manages invisible offscreen document for DOM rendering
 */

const offscreenController = {
  /**
   * Ensure offscreen document exists
   */
  async ensure() {
    // Check if offscreen document already exists
    if (await chrome.offscreen.hasDocument()) {
      return;
    }

    // Check if user approved offscreen permission
    const approved = await configManager.isOffscreenApproved();
    if (!approved) {
      // Request permission from user
      await chrome.runtime.sendMessage({ type: 'REQUEST_PERMISSION_POPUP' });
      throw new Error('Offscreen permission not approved');
    }

    // Create offscreen document
    await chrome.offscreen.createDocument({
      url: chrome.runtime.getURL('offscreen/offscreen.html'),
      reasons: ['DOM_PARSER'],
      justification: 'Invisible browsing for hrunxtnshn'
    });
    
    console.log('Offscreen document created');
  },

  /**
   * Load URL in offscreen document and return HTML
   */
  async load(url) {
    await this.ensure();
    
    return new Promise((resolve, reject) => {
      // Set timeout for loading
      const timeout = setTimeout(() => {
        reject(new Error('Offscreen load timeout'));
      }, 30000);

      // Listen for response from offscreen document
      const listener = (msg, sender, respond) => {
        if (msg.type === 'OFFSCREEN_LOAD' && msg.url === url) {
          clearTimeout(timeout);
          chrome.runtime.onMessage.removeListener(listener);
          resolve(msg.html);
        }
      };
      
      chrome.runtime.onMessage.addListener(listener);
      
      // Send load request to offscreen document
      chrome.runtime.sendMessage({
        type: 'OFFSCREEN_LOAD',
        url: url
      }).catch(reject);
    });
  },

  /**
   * Close offscreen document
   */
  async close() {
    if (await chrome.offscreen.hasDocument()) {
      await chrome.offscreen.closeDocument();
      console.log('Offscreen document closed');
    }
  }
};
