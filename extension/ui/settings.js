/**
 * Settings Page Logic
 */

let config = null;

// Initialize settings page
document.addEventListener('DOMContentLoaded', async () => {
  await loadConfig();
  setupEventListeners();
  updateConfigSections();
});

/**
 * Load configuration
 */
async function loadConfig() {
  const response = await chrome.runtime.sendMessage({ type: 'GET_CONFIG' });
  if (response.ok) {
    config = response.data;
    populateFields();
  }
}

/**
 * Populate form fields with current configuration
 */
function populateFields() {
  // Mode
  document.getElementById('modeSelect').value = config.mode;
  
  // Standalone
  document.getElementById('standaloneApiKey').value = config.standalone.apiKey || '';
  document.getElementById('standaloneModel').value = config.standalone.model || 'gpt-4.1-mini';
  document.getElementById('standaloneBaseUrl').value = config.standalone.baseUrl || 'https://api.openai.com/v1';
  
  // Platform
  document.getElementById('platformType').value = config.platform.type || 'gasable';
  document.getElementById('platformEndpoint').value = config.platform.endpoint || '';
  document.getElementById('platformApiKey').value = config.platform.apiKey || '';
  
  // Orchestrator
  document.getElementById('orchestratorEndpoint').value = config.orchestrator.endpoint || 'http://localhost:8000';
  document.getElementById('orchestratorApiKey').value = config.orchestrator.apiKey || '';
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
  // Mode selector
  document.getElementById('modeSelect').addEventListener('change', updateConfigSections);
  
  // Save button
  document.getElementById('saveBtn').addEventListener('click', saveSettings);
  
  // Test button
  document.getElementById('testBtn').addEventListener('click', testConnection);
}

/**
 * Update visible configuration sections based on mode
 */
function updateConfigSections() {
  const mode = document.getElementById('modeSelect').value;
  
  // Hide all sections
  document.querySelectorAll('.config-section').forEach(section => {
    section.classList.remove('active');
  });
  
  // Show selected section
  const sectionId = mode + 'Config';
  const section = document.getElementById(sectionId);
  if (section) {
    section.classList.add('active');
  }
}

/**
 * Save settings
 */
async function saveSettings() {
  const mode = document.getElementById('modeSelect').value;
  
  const newConfig = {
    mode: mode,
    standalone: {
      apiKey: document.getElementById('standaloneApiKey').value,
      model: document.getElementById('standaloneModel').value,
      baseUrl: document.getElementById('standaloneBaseUrl').value
    },
    platform: {
      type: document.getElementById('platformType').value,
      endpoint: document.getElementById('platformEndpoint').value,
      apiKey: document.getElementById('platformApiKey').value
    },
    orchestrator: {
      endpoint: document.getElementById('orchestratorEndpoint').value,
      apiKey: document.getElementById('orchestratorApiKey').value
    }
  };
  
  try {
    const response = await chrome.runtime.sendMessage({
      type: 'SET_CONFIG',
      config: newConfig
    });
    
    if (response.ok) {
      config = response.data;
      showStatus('Settings saved successfully!', 'success');
    } else {
      showStatus('Failed to save settings: ' + response.error, 'error');
    }
  } catch (error) {
    showStatus('Error saving settings: ' + error.toString(), 'error');
  }
}

/**
 * Test connection
 */
async function testConnection() {
  const testBtn = document.getElementById('testBtn');
  testBtn.disabled = true;
  testBtn.textContent = 'Testing...';
  
  try {
    const response = await chrome.runtime.sendMessage({ type: 'TEST_CONNECTION' });
    
    if (response.ok && response.data.connected) {
      showStatus('Connection successful!', 'success');
    } else {
      showStatus('Connection failed. Please check your settings.', 'error');
    }
  } catch (error) {
    showStatus('Connection error: ' + error.toString(), 'error');
  } finally {
    testBtn.disabled = false;
    testBtn.textContent = 'Test Connection';
  }
}

/**
 * Show status message
 */
function showStatus(message, type) {
  const statusEl = document.getElementById('saveStatus');
  statusEl.textContent = message;
  statusEl.className = 'save-status ' + type;
  
  // Auto-hide after 3 seconds
  setTimeout(() => {
    statusEl.className = 'save-status';
  }, 3000);
}
