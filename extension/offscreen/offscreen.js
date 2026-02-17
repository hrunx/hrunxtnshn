/**
 * Offscreen Document
 * Invisible DOM loader for rendering web pages
 */

console.log('Offscreen document loaded');

/**
 * Listen for load requests from background
 */
chrome.runtime.onMessage.addListener(async (msg, sender, respond) => {
  if (msg.type === 'OFFSCREEN_LOAD') {
    console.log('Loading URL in offscreen:', msg.url);
    
    try {
      // Create invisible iframe
      const iframe = document.createElement('iframe');
      iframe.style.display = 'none';
      iframe.src = msg.url;
      
      // Wait for iframe to load
      await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('Iframe load timeout'));
        }, 25000);
        
        iframe.onload = () => {
          clearTimeout(timeout);
          resolve();
        };
        
        iframe.onerror = () => {
          clearTimeout(timeout);
          reject(new Error('Iframe load error'));
        };
        
        document.body.appendChild(iframe);
      });
      
      // Get HTML content
      const html = iframe.contentDocument.documentElement.outerHTML;
      
      // Send HTML back to background
      chrome.runtime.sendMessage({
        type: 'OFFSCREEN_LOAD',
        url: msg.url,
        html: html
      });
      
      // Clean up
      document.body.removeChild(iframe);
      
      respond({ ok: true });
    } catch (error) {
      console.error('Offscreen load error:', error);
      respond({ ok: false, error: error.toString() });
    }
  }
  
  return true;
});
