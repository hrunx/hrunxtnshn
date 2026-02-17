# Testing Guide

Complete testing guide for hrunxtnshn extension and orchestrator.

## Quick Start Testing

### 1. Test Extension Installation

```bash
# Open Chrome
chrome://extensions/

# Enable Developer mode
# Click "Load unpacked"
# Select: /path/to/hrunxtnshn/extension

# Verify:
# ✓ Extension icon appears in toolbar
# ✓ No errors in extension console
```

### 2. Test Standalone Mode

**Prerequisites**: OpenAI API key

**Steps**:

1. Click extension icon
2. Click "Settings"
3. Select "Standalone (OpenAI API)" mode
4. Enter your OpenAI API key: `sk-...`
5. Select model: `gpt-4.1-mini`
6. Click "Save Settings"
7. Click "Test Connection"
8. Verify: Green "Connected" status

**Test Task**:

1. Return to popup
2. Enter task:
   ```
   What is 2+2? Just respond with the number.
   ```
3. Click "Execute Task"
4. Verify: Result shows "4" or similar response

### 3. Test Orchestrator Mode

**Prerequisites**: Python 3.11+, OpenAI API key

**Steps**:

1. **Start orchestrator**:
   ```bash
   cd orchestrator
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env: Add OPENAI_API_KEY=sk-...
   python main.py
   ```

2. **Verify orchestrator**:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy","version":"1.0.0","agent_ready":false}
   ```

3. **Configure extension**:
   - Open extension settings
   - Select "Custom Orchestrator" mode
   - Enter endpoint: `http://localhost:8000`
   - Save settings
   - Test connection

4. **Test task**:
   - Enter simple task in popup
   - Execute and verify response

## Detailed Testing

### Extension Components

#### 1. Configuration Manager

Test configuration storage and retrieval:

```javascript
// Open extension popup
// Open browser console (F12)
// Test config operations:

chrome.runtime.sendMessage({type: 'GET_CONFIG'}, (response) => {
  console.log('Config:', response.data);
});

chrome.runtime.sendMessage({
  type: 'SET_CONFIG',
  config: {mode: 'standalone'}
}, (response) => {
  console.log('Updated:', response.data);
});
```

#### 2. API Client

Test API connectivity:

```javascript
// Test OpenAI connection
chrome.runtime.sendMessage({type: 'TEST_CONNECTION'}, (response) => {
  console.log('Connected:', response.data.connected);
});
```

#### 3. Offscreen Controller

Test invisible browsing:

```javascript
chrome.runtime.sendMessage({
  type: 'LOAD_PAGE',
  url: 'https://example.com'
}, (response) => {
  console.log('HTML:', response.data);
});
```

#### 4. Fetch Engine

Test authenticated requests:

```javascript
chrome.runtime.sendMessage({
  type: 'FETCH',
  url: 'https://example.com'
}, (response) => {
  console.log('Response:', response.data);
});
```

### Data Extraction Testing

#### LinkedIn Extraction

**Prerequisites**: Logged into LinkedIn

**Test**:

```javascript
chrome.runtime.sendMessage({
  type: 'EXTRACT_LINKEDIN',
  url: 'https://www.linkedin.com/in/example'
}, (response) => {
  console.log('Profile:', response.data);
});
```

**Expected Output**:
```json
{
  "name": "John Doe",
  "headline": "Software Engineer at Company",
  "location": "San Francisco, CA",
  "experience": [...],
  "education": [...]
}
```

#### Instagram Extraction

**Prerequisites**: Logged into Instagram

**Test**:

```javascript
chrome.runtime.sendMessage({
  type: 'EXTRACT_INSTAGRAM',
  url: 'https://www.instagram.com/username'
}, (response) => {
  console.log('Profile:', response.data);
});
```

#### Google Maps Extraction

**Test**:

```javascript
chrome.runtime.sendMessage({
  type: 'EXTRACT_MAPS',
  url: 'https://www.google.com/maps/place/...'
}, (response) => {
  console.log('Place:', response.data);
});
```

### Orchestrator Testing

#### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "agent_ready": false
}
```

#### 2. Task Execution

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the capital of France?",
    "needsPlanning": true
  }'
```

Expected:
```json
{
  "task_id": "uuid",
  "status": "completed",
  "result": {
    "result": {...},
    "plan": [...]
  }
}
```

#### 3. Task Status

```bash
curl http://localhost:8000/api/tasks/{task_id}
```

#### 4. Streaming

```bash
curl -X POST http://localhost:8000/api/tasks/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test task"}' \
  --no-buffer
```

### Integration Testing

#### End-to-End Test: LinkedIn Profile Extraction

**Scenario**: Extract LinkedIn profile data

**Steps**:

1. Ensure logged into LinkedIn
2. Configure extension (standalone or orchestrator mode)
3. Enter task:
   ```
   Extract data from LinkedIn profile https://www.linkedin.com/in/example
   ```
4. Execute task
5. Verify extracted data includes:
   - Name
   - Headline
   - Location
   - Experience
   - Education

**Expected Result**:
```json
{
  "result": {
    "name": "John Doe",
    "headline": "Software Engineer",
    "location": "San Francisco, CA",
    "experience": [
      {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "duration": "2020 - Present"
      }
    ],
    "education": [...]
  }
}
```

#### End-to-End Test: Multi-Step Task

**Scenario**: Complex task requiring planning

**Task**:
```
Find information about the Eiffel Tower on Wikipedia and tell me:
1. When it was built
2. How tall it is
3. Who designed it
```

**Expected**: Agent plans multiple steps, executes them, and synthesizes results.

### Error Handling Testing

#### 1. Invalid API Key

- Enter invalid API key in settings
- Attempt task execution
- Verify: Clear error message

#### 2. Network Error

- Disconnect internet
- Attempt task execution
- Verify: Timeout or network error message

#### 3. Invalid URL

- Enter invalid URL for extraction
- Verify: Error message

#### 4. Not Logged In

- Attempt LinkedIn extraction without login
- Verify: "Not logged in" error

### Performance Testing

#### 1. Response Time

Test task execution time:

```javascript
const start = Date.now();
chrome.runtime.sendMessage({
  type: 'EXECUTE_TASK',
  task: {prompt: 'Simple task'}
}, (response) => {
  const duration = Date.now() - start;
  console.log(`Duration: ${duration}ms`);
});
```

**Target**: < 5 seconds for simple tasks

#### 2. Concurrent Tasks

Test multiple simultaneous tasks:

```bash
# Start orchestrator
# Run multiple curl commands simultaneously
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/tasks \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"Task $i\"}" &
done
wait
```

#### 3. Memory Usage

Monitor extension memory:

```
chrome://extensions/
→ Click "Details" on hrunxtnshn
→ Check "Memory" usage
```

**Target**: < 50MB idle, < 200MB during execution

### Security Testing

#### 1. API Key Storage

Verify API keys are encrypted:

```javascript
// Should NOT be able to read API key directly from storage
chrome.storage.sync.get('config', (data) => {
  console.log('Config:', data);
  // API key should be present but encrypted by Chrome
});
```

#### 2. CORS

Test cross-origin requests are blocked:

```javascript
fetch('http://localhost:8000/api/tasks', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({prompt: 'Test'})
}).catch(err => console.log('CORS blocked:', err));
```

#### 3. Input Validation

Test with malicious inputs:

```javascript
// SQL injection attempt
chrome.runtime.sendMessage({
  type: 'EXECUTE_TASK',
  task: {prompt: "'; DROP TABLE users; --"}
}, (response) => {
  console.log('Response:', response);
  // Should handle safely
});
```

### Compatibility Testing

Test on different browsers:

- ✓ Chrome 109+
- ✓ Edge 109+
- ✓ Brave (Chromium-based)
- ✗ Firefox (Manifest V3 support limited)
- ✗ Safari (Different extension API)

### Automated Testing

#### Extension Tests

Create `extension/tests/test.js`:

```javascript
// Basic test suite
const tests = {
  async testConfigManager() {
    const response = await chrome.runtime.sendMessage({type: 'GET_CONFIG'});
    console.assert(response.ok, 'Config should load');
    console.assert(response.data.mode, 'Config should have mode');
  },
  
  async testApiClient() {
    // Mock API key for testing
    await chrome.runtime.sendMessage({
      type: 'SET_CONFIG',
      config: {
        mode: 'standalone',
        standalone: {apiKey: 'test-key'}
      }
    });
    
    const response = await chrome.runtime.sendMessage({type: 'TEST_CONNECTION'});
    console.assert(response.ok !== undefined, 'Connection test should return result');
  }
};

// Run tests
Object.entries(tests).forEach(async ([name, test]) => {
  try {
    await test();
    console.log(`✓ ${name}`);
  } catch (error) {
    console.error(`✗ ${name}:`, error);
  }
});
```

#### Orchestrator Tests

Create `orchestrator/tests/test_api.py`:

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_task():
    response = client.post("/api/tasks", json={
        "prompt": "Test task"
    })
    assert response.status_code == 200
    assert "task_id" in response.json()

def test_get_task():
    # Create task
    create_response = client.post("/api/tasks", json={
        "prompt": "Test"
    })
    task_id = create_response.json()["task_id"]
    
    # Get task
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 200
```

Run tests:
```bash
cd orchestrator
pytest tests/
```

## Test Checklist

### Pre-Release Testing

- [ ] Extension loads without errors
- [ ] All three integration modes work
- [ ] Configuration saves and loads correctly
- [ ] API connections test successfully
- [ ] Offscreen browsing works
- [ ] LinkedIn extraction works (when logged in)
- [ ] Instagram extraction works (when logged in)
- [ ] Google Maps extraction works
- [ ] Error messages are clear and helpful
- [ ] UI is responsive and intuitive
- [ ] Orchestrator starts without errors
- [ ] Orchestrator API endpoints respond correctly
- [ ] Task queue processes tasks
- [ ] Streaming API works
- [ ] Documentation is accurate
- [ ] Examples work as documented

### Regression Testing

After each update, test:

- [ ] Existing configurations still work
- [ ] Previously working tasks still work
- [ ] No new console errors
- [ ] Performance hasn't degraded
- [ ] Security measures still in place

## Troubleshooting Tests

### Extension Not Loading

1. Check manifest.json syntax
2. Check for JavaScript errors in background console
3. Verify all files are present

### Tasks Failing

1. Check API key is valid
2. Check network connectivity
3. Check orchestrator is running (if using orchestrator mode)
4. Check browser console for errors
5. Check extension background console

### Extraction Failing

1. Verify logged into target website
2. Check website hasn't changed structure
3. Test with different profile/page
4. Check extraction schema selectors

## Reporting Issues

When reporting issues, include:

1. Extension version
2. Browser version
3. Integration mode used
4. Steps to reproduce
5. Expected vs actual behavior
6. Console errors (if any)
7. Screenshots (if applicable)

## Support

For testing issues:
- GitHub Issues: https://github.com/hrunx/hrunxtnshn/issues
- Include test results and logs
