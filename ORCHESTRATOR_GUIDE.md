## hrunxtnshn Orchestrator V2 - Complete Guide

**Orchestrator-Driven Invisible Browsing System**

---

## Overview

The orchestrator is the brain of hrunxtnshn. It:

✅ **Controls invisible browsing** - Extension browses in background  
✅ **Integrates SearXNG** - Open-source privacy-focused search  
✅ **Manages sessions** - Login once, reuse everywhere  
✅ **Coordinates multi-browsing** - Multiple tasks in parallel  
✅ **Extracts data** - LinkedIn employees, profiles, companies  

---

## Architecture

```
User Request
    ↓
Orchestrator (Python)
    ↓
SearXNG Search → Find LinkedIn URLs
    ↓
Session Manager → Check/Request Login
    ↓
Invisible Browser → Send Commands via WebSocket
    ↓
Extension (Chrome) → Browse Invisibly + Extract Data
    ↓
Return Results to Orchestrator
    ↓
User Gets Data
```

---

## Quick Start

### 1. Install Dependencies

```bash
cd orchestrator
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4.1-mini
HOST=0.0.0.0
PORT=8000
SEARXNG_URL=https://searx.be
```

### 3. Start Orchestrator

```bash
python main_v2.py
```

You should see:
```
============================================================
Starting hrunxtnshn Orchestrator V2
============================================================
SearXNG: https://searx.be
Invisible browser initialized
No active sessions
============================================================
Server: 0.0.0.0:8000
WebSocket: ws://0.0.0.0:8000/ws
Orchestrator ready!
============================================================
```

### 4. Load Extension

1. Open Chrome: `chrome://extensions/`
2. Enable Developer Mode
3. Load unpacked: Select `extension` folder
4. Extension will auto-connect to orchestrator

### 5. Test Connection

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "extension_connected": true,
  "connections": 1,
  "sessions": []
}
```

---

## Usage Examples

### Example 1: Extract Gasable Employees

**API Request:**
```bash
curl -X POST "http://localhost:8000/extract/company" \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Gasable", "max_pages": 6}'
```

**What Happens:**
1. Orchestrator searches "Gasable site:linkedin.com/company" via SearXNG
2. Finds: `https://www.linkedin.com/company/gasable/`
3. Checks if LinkedIn session exists
4. If no session: Requests user to log in
5. If session exists: Sends invisible browse command to extension
6. Extension navigates to `/people/` page invisibly
7. Extension extracts all employees (with pagination)
8. Returns data to orchestrator

**Response:**
```json
{
  "task_id": "abc-123",
  "status": "completed",
  "url": "https://www.linkedin.com/company/gasable/people/",
  "result": {
    "companyName": "Gasable | غازابل",
    "totalEmployees": 63,
    "extractedCount": 63,
    "employees": [
      {
        "name": "Dana Al-Yemni",
        "profileUrl": "https://www.linkedin.com/in/...",
        "headline": "Deputy Manager Of Information Technology",
        "location": "Riyadh, Saudi Arabia",
        "connectionDegree": "2nd",
        "timeAtCompany": "3 years 2 months"
      },
      // ... 62 more employees
    ],
    "pagesScraped": 6
  }
}
```

### Example 2: Extract Multiple Companies

**API Request:**
```bash
curl -X POST "http://localhost:8000/extract/multiple" \
  -H "Content-Type": application/json" \
  -d '{
    "company_names": ["Gasable", "Leadora", "Manus"],
    "max_pages": 3
  }'
```

**What Happens:**
1. Orchestrator searches for all 3 companies in parallel
2. Finds LinkedIn URLs for each
3. Extracts employees from all 3 companies concurrently
4. Returns combined results

**Response:**
```json
{
  "total_companies": 3,
  "extracted_companies": 3,
  "results": {
    "Gasable": {
      "companyName": "Gasable | غازابل",
      "extractedCount": 63,
      "employees": [...]
    },
    "Leadora": {
      "companyName": "Leadora",
      "extractedCount": 45,
      "employees": [...]
    },
    "Manus": {
      "companyName": "Manus",
      "extractedCount": 120,
      "employees": [...]
    }
  }
}
```

### Example 3: Search for Company URL Only

**API Request:**
```bash
curl -X POST "http://localhost:8000/search/company?company_name=Gasable"
```

**Response:**
```json
{
  "company_name": "Gasable",
  "linkedin_url": "https://www.linkedin.com/company/gasable/"
}
```

---

## Session Management

### How It Works

1. **First Request:** User is asked to log in to LinkedIn
2. **Extension Captures Session:** Cookies are sent to orchestrator
3. **Orchestrator Saves Session:** Stored in `data/sessions/sessions.json`
4. **Future Requests:** Session is reused automatically
5. **Session Expires:** After 30 days, user logs in again

### Check Session Status

```bash
curl http://localhost:8000/sessions
```

Response:
```json
{
  "linkedin": {
    "valid": true,
    "stored_at": "2026-02-17T10:00:00",
    "expires_at": "2026-03-19T10:00:00",
    "user_id": "default"
  }
}
```

### Clear Session

```bash
curl -X POST "http://localhost:8000/session/clear?platform=linkedin"
```

---

## SearXNG Integration

### Why SearXNG?

- ✅ **Open-source** - Self-hostable, no API keys needed
- ✅ **Privacy-focused** - No tracking, no logs
- ✅ **Meta-search** - Aggregates results from multiple engines
- ✅ **Fast** - Concurrent searches across engines
- ✅ **Free** - No rate limits on self-hosted instance

### Using Public Instance (Default)

The orchestrator uses `https://searx.be` by default. No setup needed.

### Self-Hosting SearXNG (Recommended)

**Benefits:**
- No rate limits
- Full control
- Better performance
- Custom configuration

**Setup (Docker):**

1. Create `docker-compose.yml`:
```yaml
version: '3.7'

services:
  searxng:
    image: searxng/searxng:latest
    container_name: searxng
    ports:
      - "8080:8080"
    volumes:
      - ./searxng:/etc/searxng
    environment:
      - SEARXNG_BASE_URL=http://localhost:8080
    restart: unless-stopped
```

2. Start SearXNG:
```bash
docker-compose up -d
```

3. Update `.env`:
```env
SEARXNG_URL=http://localhost:8080
```

4. Restart orchestrator

---

## API Reference

### Health Check

**GET** `/health`

Returns orchestrator health status.

### Get Status

**GET** `/status`

Returns detailed status including:
- Extension connection
- Active sessions
- Running tasks
- SearXNG URL

### Search Company

**POST** `/search/company?company_name={name}`

Search for LinkedIn company URL.

**Parameters:**
- `company_name` (string): Company name to search

**Returns:**
- `company_name`: Input company name
- `linkedin_url`: Found LinkedIn URL or null

### Extract Company Employees

**POST** `/extract/company`

Extract employees from LinkedIn company.

**Body:**
```json
{
  "company_name": "Gasable",  // Optional if company_url provided
  "company_url": "https://...",  // Optional if company_name provided
  "max_pages": 6  // Optional, default 6
}
```

**Returns:**
- `task_id`: Unique task identifier
- `status`: Task status (completed, failed, etc.)
- `result`: Extraction data with employees array

### Extract Multiple Companies

**POST** `/extract/multiple`

Extract employees from multiple companies in parallel.

**Body:**
```json
{
  "company_names": ["Gasable", "Leadora", "Manus"],
  "max_pages": 3
}
```

**Returns:**
- `total_companies`: Number of companies requested
- `extracted_companies`: Number successfully extracted
- `results`: Dictionary mapping company names to extraction results

### Get Tasks

**GET** `/tasks`

Get all browsing tasks (active and completed).

### Get Task Status

**GET** `/tasks/{task_id}`

Get status of specific task.

### Get Sessions

**GET** `/sessions`

Get all saved session statuses.

### Clear Session

**POST** `/session/clear?platform=linkedin`

Clear saved session for a platform.

---

## WebSocket Protocol

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### Command Format

**From Orchestrator to Extension:**
```json
{
  "command_id": "uuid",
  "action": "INVISIBLE_BROWSE",
  "url": "https://linkedin.com/company/gasable/people/",
  "extraction_type": "company_employees",
  "params": {
    "max_pages": 6
  },
  "cookies": [...]  // Optional session cookies
}
```

**From Extension to Orchestrator:**
```json
{
  "type": "response",
  "command_id": "uuid",
  "success": true,
  "data": {
    "companyName": "Gasable",
    "employees": [...]
  }
}
```

### Events

**Session Captured:**
```json
{
  "type": "event",
  "event": "session_captured",
  "data": {
    "platform": "linkedin",
    "cookies": [...],
    "user_id": "default"
  }
}
```

---

## Troubleshooting

### Extension Not Connecting

**Problem:** `extension_connected: false` in `/health`

**Solutions:**
1. Make sure extension is loaded in Chrome
2. Check extension console for WebSocket errors
3. Verify orchestrator is running on correct port
4. Check firewall settings

### No Session Available

**Problem:** "Please log in to LinkedIn" message

**Solutions:**
1. Open LinkedIn in Chrome and log in manually
2. Extension will capture session automatically
3. Check `/sessions` endpoint to verify
4. If not captured, reload extension

### SearXNG Not Working

**Problem:** Company search fails

**Solutions:**
1. Check SearXNG URL in `.env`
2. Test SearXNG directly: `curl https://searx.be/search?q=test&format=json`
3. Try different public instance
4. Self-host SearXNG for reliability

### Extraction Timeout

**Problem:** Task times out

**Solutions:**
1. Reduce `max_pages` parameter
2. Check LinkedIn is not rate limiting
3. Verify session is still valid
4. Try again after a few minutes

---

## Performance

### Extraction Speed

- **Single company (6 pages):** ~30-40 seconds
- **Multiple companies (3 companies, 3 pages each):** ~45-60 seconds
- **Search + extraction:** Add ~2-3 seconds for search

### Concurrency

- **Max concurrent tasks:** 5 (configurable in `config.py`)
- **Recommended:** 3-5 companies at a time
- **Rate limiting:** Built-in delays to avoid LinkedIn blocks

---

## Next Steps

1. ✅ **Test with Gasable** - Extract employees
2. ✅ **Try multiple companies** - Test parallel extraction
3. ✅ **Self-host SearXNG** - Better performance
4. ✅ **Integrate with your app** - Use API endpoints
5. ✅ **Customize extraction** - Add more data fields

---

## Support

- **Logs:** Check orchestrator console for detailed logs
- **Extension logs:** Open extension popup → Console
- **API errors:** Check response body for error details
- **WebSocket:** Monitor WebSocket tab in browser DevTools

---

**Congratulations!** You now have a fully functional orchestrator-driven invisible browsing system. The orchestrator controls everything, searches via SearXNG, manages sessions, and coordinates multi-domain browsing through the extension.
