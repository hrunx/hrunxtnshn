/**
 * Popup UI Logic
 */

let config = null;

// Initialize popup
document.addEventListener('DOMContentLoaded', async () => {
  await loadConfig();
  await checkConnection();
  setupEventListeners();
});

/**
 * Load configuration
 */
async function loadConfig() {
  const response = await chrome.runtime.sendMessage({ type: 'GET_CONFIG' });
  if (response.ok) {
    config = response.data;
    document.getElementById('modeSelect').value = config.mode;
  }
}

/**
 * Check API connection
 */
async function checkConnection() {
  const statusDot = document.getElementById('statusDot');
  const statusText = document.getElementById('statusText');
  
  statusDot.className = 'status-dot status-checking';
  statusText.textContent = 'Checking connection...';
  
  try {
    const response = await chrome.runtime.sendMessage({ type: 'TEST_CONNECTION' });
    
    if (response.ok && response.data.connected) {
      statusDot.className = 'status-dot status-connected';
      statusText.textContent = 'Connected';
    } else {
      statusDot.className = 'status-dot status-disconnected';
      statusText.textContent = 'Not configured';
    }
  } catch (error) {
    statusDot.className = 'status-dot status-error';
    statusText.textContent = 'Connection error';
  }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
  // Mode selector
  document.getElementById('modeSelect').addEventListener('change', async (e) => {
    const mode = e.target.value;
    await chrome.runtime.sendMessage({
      type: 'SET_CONFIG',
      config: { mode }
    });
    await checkConnection();
  });

  // Execute button
  document.getElementById('executeBtn').addEventListener('click', executeTask);

  // Settings button
  document.getElementById('settingsBtn').addEventListener('click', () => {
    chrome.runtime.openOptionsPage();
  });
}

/**
 * Execute task
 */
async function executeTask() {
  const taskInput = document.getElementById('taskInput').value.trim();
  const executeBtn = document.getElementById('executeBtn');
  const resultSection = document.getElementById('resultSection');
  const resultOutput = document.getElementById('resultOutput');
  const errorSection = document.getElementById('errorSection');
  const errorText = document.getElementById('errorText');
  
  // Hide previous results
  resultSection.style.display = 'none';
  errorSection.style.display = 'none';
  
  if (!taskInput) {
    showError('Please enter a task description');
    return;
  }
  
  // Disable button
  executeBtn.disabled = true;
  executeBtn.textContent = 'Executing...';
  
  try {
    const response = await chrome.runtime.sendMessage({
      type: 'EXECUTE_TASK',
      task: {
        prompt: taskInput,
        needsPlanning: true
      }
    });
    
    if (response.ok) {
      resultSection.style.display = 'block';
      resultOutput.textContent = JSON.stringify(response.data, null, 2);
    } else {
      showError(response.error || 'Task execution failed');
    }
  } catch (error) {
    showError(error.toString());
  } finally {
    executeBtn.disabled = false;
    executeBtn.textContent = 'Execute Task';
  }
}

/**
 * Show error message
 */
function showError(message) {
  const errorSection = document.getElementById('errorSection');
  const errorText = document.getElementById('errorText');
  
  errorSection.style.display = 'block';
  errorText.textContent = message;
}
