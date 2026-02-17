# hrunxtnshn - Orchestrator-Driven Invisible Browsing System

**Autonomous data extraction from LinkedIn with orchestrator control, open-source search, and session management.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Chrome Extension](https://img.shields.io/badge/chrome-extension-green.svg)](https://developer.chrome.com/docs/extensions/)

---

## 🚀 What is hrunxtnshn?

hrunxtnshn is a complete orchestrator-driven system that enables **invisible background browsing** and **automated data extraction** from LinkedIn. The Python orchestrator controls everything, while the Chrome extension executes tasks invisibly in the background.

### Key Features

✅ **Orchestrator-Driven** - Python backend controls all browsing  
✅ **Invisible Browsing** - Extension browses in background (offscreen)  
✅ **SearXNG Integration** - Open-source privacy-focused search  
✅ **Session Management** - Login once, reuse everywhere  
✅ **Multi-Domain Browsing** - Extract from multiple companies in parallel  
✅ **LinkedIn Extraction** - Company employees, profiles, data  
✅ **Fully Local** - Self-hosted, no external dependencies  
✅ **Open Source** - MIT License  

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
│                 "Extract Gasable employees"                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR (Python)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   SearXNG    │  │   Session    │  │  Invisible   │      │
│  │   Client     │  │   Manager    │  │   Browser    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────┬─────────────────────────────────────┘
                        │ WebSocket
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              EXTENSION (Chrome)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Background  │  │  Offscreen   │  │   Content    │      │
│  │   Worker     │  │   Document   │  │   Scripts    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    LINKEDIN.COM                              │
│        (Invisible browsing, data extraction)                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Quick Start

### Prerequisites

- Python 3.11+
- Chrome 109+ or Edge 109+
- OpenAI API key (or compatible LLM)

### 1. Clone Repository

```bash
git clone https://github.com/hrunx/hrunxtnshn.git
cd hrunxtnshn
```

### 2. Setup Orchestrator

```bash
cd orchestrator
pip install -r requirements.txt
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

Start orchestrator:
```bash
python main_v2.py
```

### 3. Load Extension

1. Open Chrome: `chrome://extensions/`
2. Enable **Developer Mode**
3. Click **Load unpacked**
4. Select `hrunxtnshn/extension` folder
5. Extension auto-connects to orchestrator

### 4. Test Extraction

**Extract Gasable employees:**
```bash
curl -X POST "http://localhost:8000/extract/company" \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Gasable", "max_pages": 6}'
```

**Result:**
```json
{
  "status": "completed",
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
        "timeAtCompany": "3 years 2 months"
      },
      // ... 62 more
    ]
  }
}
```

---

## 🎯 Use Cases

### 1. Lead Generation
Extract employees from target companies for sales outreach.

### 2. Competitive Intelligence
Monitor competitor hiring and team structure.

### 3. Talent Sourcing
Find candidates from specific companies or industries.

### 4. Market Research
Analyze company sizes, locations, and growth patterns.

### 5. Network Mapping
Build relationship graphs between companies and people.

---

## 📚 Documentation

- **[ORCHESTRATOR_GUIDE.md](ORCHESTRATOR_GUIDE.md)** - Complete orchestrator setup and API reference
- **[INSTALL_AND_TEST.md](INSTALL_AND_TEST.md)** - Extension installation and testing
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[EXAMPLES.md](EXAMPLES.md)** - Practical usage examples

---

## 🔧 API Endpoints

### Search for Company

```bash
POST /search/company?company_name=Gasable
```

Returns LinkedIn company URL.

### Extract Single Company

```bash
POST /extract/company
{
  "company_name": "Gasable",
  "max_pages": 6
}
```

Extracts all employees from company.

### Extract Multiple Companies

```bash
POST /extract/multiple
{
  "company_names": ["Gasable", "Leadora", "Manus"],
  "max_pages": 3
}
```

Extracts from multiple companies in parallel.

### Check Status

```bash
GET /status
```

Returns orchestrator status, sessions, and active tasks.

---

## 🔐 Session Management

### How It Works

1. **First request:** Orchestrator asks user to log in to LinkedIn
2. **Extension captures session:** Cookies sent to orchestrator
3. **Orchestrator saves session:** Stored locally
4. **Future requests:** Session reused automatically
5. **Expires after 30 days:** User logs in again

### Check Sessions

```bash
GET /sessions
```

### Clear Session

```bash
POST /session/clear?platform=linkedin
```

---

## 🔍 SearXNG Integration

### Why SearXNG?

- ✅ **Open-source** - Self-hostable, no API keys
- ✅ **Privacy-focused** - No tracking
- ✅ **Meta-search** - Aggregates multiple engines
- ✅ **Free** - No rate limits (self-hosted)

### Default: Public Instance

Uses `https://searx.be` by default.

### Self-Hosted (Recommended)

```yaml
# docker-compose.yml
version: '3.7'
services:
  searxng:
    image: searxng/searxng:latest
    ports:
      - "8080:8080"
    restart: unless-stopped
```

```bash
docker-compose up -d
```

Update `.env`:
```env
SEARXNG_URL=http://localhost:8080
```

---

## 🚦 How It Works

### Example: Extract Gasable Employees

**Step 1:** User sends request
```bash
POST /extract/company {"company_name": "Gasable"}
```

**Step 2:** Orchestrator searches via SearXNG
```
Query: "Gasable site:linkedin.com/company"
Result: https://www.linkedin.com/company/gasable/
```

**Step 3:** Orchestrator checks session
```
LinkedIn session exists? Yes → Use saved cookies
```

**Step 4:** Orchestrator sends command to extension
```json
{
  "action": "INVISIBLE_BROWSE",
  "url": "https://www.linkedin.com/company/gasable/people/",
  "extraction_type": "company_employees",
  "cookies": [...]
}
```

**Step 5:** Extension browses invisibly
- Opens offscreen document
- Navigates to LinkedIn
- Loads company people page
- Extracts employee data
- Handles pagination

**Step 6:** Extension returns data
```json
{
  "success": true,
  "data": {
    "employees": [...]
  }
}
```

**Step 7:** Orchestrator returns to user
```json
{
  "status": "completed",
  "result": {...}
}
```

---

## 🎨 Features in Detail

### Orchestrator-Driven Browsing

The orchestrator controls all browsing decisions:
- Which URLs to visit
- What data to extract
- How many pages to scrape
- When to stop

The extension is just an execution engine.

### Invisible Browsing

Uses Chrome's offscreen API:
- No visible browser windows
- Runs in background
- Uses real browser session
- Bypasses bot detection

### Multi-Domain Browsing

Extract from multiple companies simultaneously:
```python
companies = ["Gasable", "Leadora", "Manus", "OpenAI", "Anthropic"]
results = await extract_multiple(companies, max_pages=3)
```

Orchestrator manages concurrency and rate limiting.

### Session Persistence

Login once, use forever:
- Cookies stored securely
- Automatic session refresh
- Works across restarts
- Supports multiple platforms

---

## 📊 Performance

### Extraction Speed

| Task | Time |
|------|------|
| Single company (6 pages) | 30-40s |
| Multiple companies (3x3 pages) | 45-60s |
| Search + extraction | +2-3s |

### Concurrency

- **Max concurrent tasks:** 5 (configurable)
- **Recommended:** 3-5 companies at a time
- **Rate limiting:** Built-in delays

---

## 🛠️ Development

### Project Structure

```
hrunxtnshn/
├── extension/              # Chrome Extension
│   ├── background/         # Service worker
│   ├── content/            # Content scripts
│   ├── offscreen/          # Offscreen document
│   ├── ui/                 # Popup & settings
│   └── manifest.json
│
├── orchestrator/           # Python Backend
│   ├── services/
│   │   ├── searxng_client.py       # Search integration
│   │   ├── session_manager.py      # Session management
│   │   ├── invisible_browser.py    # Browsing control
│   │   └── extension_bridge_v2.py  # WebSocket bridge
│   ├── main_v2.py          # Main application
│   ├── config.py           # Configuration
│   └── requirements.txt
│
└── docs/                   # Documentation
```

### Tech Stack

**Orchestrator:**
- Python 3.11+
- FastAPI (web framework)
- WebSockets (extension communication)
- httpx (HTTP client)
- LangChain/LangGraph (optional AI)

**Extension:**
- JavaScript ES6+
- Chrome Extension API
- Manifest V3
- Offscreen API

**Search:**
- SearXNG (open-source meta-search)

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] More extractors (Instagram, Twitter, etc.)
- [ ] Browser automation (form filling, clicking)
- [ ] Visual workflow builder
- [ ] Chrome Web Store publication
- [ ] Firefox support

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **SearXNG** - Privacy-respecting meta-search engine
- **Chrome Extensions** - Offscreen API for invisible browsing
- **LangChain** - AI orchestration framework
- **FastAPI** - Modern Python web framework

---

## 📞 Support

- **GitHub Issues:** Report bugs or request features
- **Documentation:** Check guides in `/docs`
- **Examples:** See `EXAMPLES.md` for use cases

---

## 🎉 Get Started

```bash
# Clone
git clone https://github.com/hrunx/hrunxtnshn.git

# Setup orchestrator
cd orchestrator
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OpenAI API key
python main_v2.py

# Load extension in Chrome
# chrome://extensions/ → Load unpacked → Select extension folder

# Test
curl -X POST "http://localhost:8000/extract/company" \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Gasable", "max_pages": 6}'
```

**Happy extracting! 🚀**
