/**
 * Background Service Worker
 * Main entry point for extension background tasks
 */

importScripts('taskRouter.js', 'fetchEngine.js', 'offscreenController.js', 'extractorRouter.js', 'apiClient.js');

console.log('hrunxtnshn background service worker loaded');

/**
 * Handle extension installation
 */
chrome.runtime.onInstalled.addListener(async (details) => {
  console.log('Extension installed:', details.reason);
  
  if (details.reason === 'install') {
    // Initialize default configuration
    await configManager.init();
    
    // Open welcome page
    chrome.tabs.create({
      url: chrome.runtime.getURL('ui/popup.html')
    });
  }
});

/**
 * Handle messages from popup, content scripts, and offscreen documents
 */
chrome.runtime.onMessage.addListener((msg, sender, respond) => {
  console.log('Background received message:', msg.type, msg);
  
  // Handle async messages
  (async () => {
    try {
      switch (msg.type) {
        case 'EXECUTE_TASK':
          const result = await taskRouter.execute(msg.task);
          respond({ ok: true, data: result });
          break;
        
        case 'LOAD_PAGE':
          const html = await offscreenController.load(msg.url);
          respond({ ok: true, data: html });
          break;
        
        case 'FETCH':
          const fetchResult = await fetchEngine.fetchWithSession(msg.url);
          respond({ ok: true, data: fetchResult });
          break;
        
        case 'EXTRACT_MAPS':
          const mapsData = await extractorRouter.maps(msg.url);
          respond({ ok: true, data: mapsData });
          break;
        
        case 'EXTRACT_LINKEDIN':
          const linkedinData = await extractorRouter.linkedin(msg.url);
          respond({ ok: true, data: linkedinData });
          break;
        
        case 'EXTRACT_INSTAGRAM':
          const instagramData = await extractorRouter.instagram(msg.url);
          respond({ ok: true, data: instagramData });
          break;
        
        case 'OFFSCREEN_LOAD':
          // Message from offscreen document
          respond({ ok: true, data: msg.html });
          break;
        
        case 'LOGIN_REQUIRED':
          // Login detected by content script
          console.log('Login required for:', msg.url);
          respond({ ok: true });
          break;
        
        case 'REQUEST_PERMISSION_POPUP':
          // Open permission prompt
          chrome.windows.create({
            url: chrome.runtime.getURL('ui/permissionPrompt.html'),
            type: 'popup',
            width: 400,
            height: 500
          });
          respond({ ok: true });
          break;
        
        case 'PERMISSION_APPROVED':
          await configManager.setOffscreenApproved(true);
          respond({ ok: true });
          break;
        
        case 'PERMISSION_DENIED':
          await configManager.setOffscreenApproved(false);
          respond({ ok: true });
          break;
        
        case 'GET_CONFIG':
          const config = await configManager.get();
          respond({ ok: true, data: config });
          break;
        
        case 'SET_CONFIG':
          const updated = await configManager.set(msg.config);
          respond({ ok: true, data: updated });
          break;
        
        case 'TEST_CONNECTION':
          const connected = await apiClient.testConnection();
          respond({ ok: true, data: { connected } });
          break;
        
        default:
          respond({ ok: false, error: 'Unknown message type: ' + msg.type });
      }
    } catch (error) {
      console.error('Error handling message:', error);
      respond({ ok: false, error: error.toString() });
    }
  })();
  
  // Return true to indicate async response
  return true;
});

/**
 * Handle external messages (from websites or other extensions)
 */
chrome.runtime.onMessageExternal.addListener((msg, sender, respond) => {
  console.log('External message received:', msg);
  
  // Forward to task router
  (async () => {
    try {
      const result = await taskRouter.execute(msg);
      respond({ ok: true, data: result });
    } catch (error) {
      respond({ ok: false, error: error.toString() });
    }
  })();
  
  return true;
});

/**
 * Keep service worker alive
 */
setInterval(() => {
  console.log('Service worker heartbeat');
}, 20000);
