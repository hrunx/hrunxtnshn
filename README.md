# 🕵️ hrunxtnshn - Invisible LinkedIn Extraction

**Completely invisible, background-only LinkedIn employee extraction system.**

No visible browser. No tabs. No windows. Just results.

---

## 🎯 What This Does

Extract employee data from any LinkedIn company page **completely invisibly**:

- ✅ **No visible browser** - Runs in headless mode
- ✅ **No tabs or windows** - Everything in background
- ✅ **Session-based** - Login once, reuse forever
- ✅ **Terminal-only** - All output in command line
- ✅ **HTML parsing** - Intelligent DOM navigation
- ✅ **Fully automated** - Search → Extract → Save

---

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies

```bash
cd orchestrator
pip install -r requirements.txt
playwright install chromium
```

### 2. Login Once (One-Time Setup)

```bash
python cli_extractor.py login
```

**What happens:**
- Opens a visible browser window (one time only)
- You log in to LinkedIn manually
- Session saved to `linkedin_session.json`
- Browser closes

**You never need to do this again!**

### 3. Extract Employees (Invisible)

```bash
python cli_extractor.py extract "Hysabat Solutions"
```

**What happens:**
- Loads your saved session (no login)
- Starts invisible browser (headless)
- Searches for company
- Navigates to LinkedIn page
- Extracts all employees
- Saves to JSON
- **NO VISIBLE BROWSER AT ANY POINT**

---

## 📊 Example Usage

### Extract by Company Name

```bash
python cli_extractor.py extract "Gasable"
```

**Output:**
```
🔍 Extracting employees from: Gasable
============================================================

[1/4] Searching for company LinkedIn URL...
✅ Found: https://www.linkedin.com/company/gasable/

[2/4] Checking LinkedIn session...
✅ Logged in with saved session

[3/4] Extracting employees (max 10 pages)...
⏳ This happens completely in the background...

[4/4] Extraction complete!
============================================================
Company: Gasable | غازابل
Total Employees: 63
Extracted: 63
Pages Scraped: 6
============================================================

📋 First 10 employees:

1. Dana Al-Yemni
   Position: Deputy Manager Of Information Technology
   Location: Riyadh, Saudi Arabia

2. Ahmed Alsoboh, CPIM
   Position: Supply Chain Manager
   Location: Riyadh, Saudi Arabia

... and 61 more employees

💾 Full results saved to: gasable_employees.json
```

### Extract by Direct URL

```bash
python cli_extractor.py url "https://www.linkedin.com/company/hysabatsolutions/"
```

### Extract with Page Limit

```bash
python cli_extractor.py extract "Company Name" --max-pages 5
```

---

## 🏗️ How It Works

```
User Command
    ↓
Search Company (SearXNG)
    ↓
Find LinkedIn URL
    ↓
Load Saved Session (linkedin_session.json)
    ↓
Start Headless Browser (Playwright)
    ↓
Navigate Invisibly
    ↓
Parse HTML (BeautifulSoup)
    ↓
Extract Employee Data
    ↓
Handle Pagination
    ↓
Save to JSON
    ↓
Close Browser
```

**Everything happens in the background. No visible windows.**

---

## 🔐 Session Management

### How Sessions Work

1. **First time:** You log in manually (visible browser)
2. **Session saved:** Cookies stored in `linkedin_session.json`
3. **Future extractions:** Session loaded automatically (invisible)
4. **Session duration:** 30-90 days typically
5. **Re-login:** Just run `python cli_extractor.py login` again

### Session File

```json
{
  "cookies": [
    {
      "name": "li_at",
      "value": "AQEDARxxxxxxxx...",
      "domain": ".linkedin.com"
    }
  ],
  "origins": [...]
}
```

**Keep this file secure!** It contains your LinkedIn session.

---

## 📁 Project Structure

```
hrunxtnshn/
├── orchestrator/
│   ├── cli_extractor.py          # Main CLI tool
│   ├── test_extraction.py        # Test script
│   ├── config.py                 # Configuration
│   ├── requirements.txt          # Dependencies
│   ├── services/
│   │   ├── headless_browser.py   # Playwright headless browser
│   │   ├── html_navigator.py    # HTML parsing & navigation
│   │   ├── searxng_client.py    # Search integration
│   │   └── session_manager.py   # Session management
│   └── linkedin_session.json    # Saved session (created after login)
└── INVISIBLE_EXTRACTION_GUIDE.md # Complete documentation
```

---

## 🎨 Key Components

### 1. Headless Browser (`headless_browser.py`)

```python
browser = HeadlessBrowser()
await browser.start(headless=True)  # Invisible!
await browser.navigate(url)
employees = await browser.extract_company_employees(url)
```

**Features:**
- Playwright-based
- Completely invisible
- Session persistence
- Automatic scrolling
- Pagination handling

### 2. HTML Navigator (`html_navigator.py`)

```python
navigator = LinkedInHTMLNavigator()
navigator.parse_page(html)
employees = navigator.extract_employee_cards()
```

**Features:**
- BeautifulSoup parsing
- Element detection
- Data extraction
- Pagination logic

### 3. CLI Tool (`cli_extractor.py`)

```bash
python cli_extractor.py login              # One-time login
python cli_extractor.py extract "Company"  # Extract by name
python cli_extractor.py url "https://..."  # Extract by URL
```

---

## 🔧 Advanced Usage

### Programmatic Usage

```python
from services.headless_browser import HeadlessBrowser

async def extract_company(url):
    browser = HeadlessBrowser("linkedin_session.json")
    await browser.start(headless=True)
    
    result = await browser.extract_company_employees(url, max_pages=10)
    
    await browser.close()
    return result

# Run
result = asyncio.run(extract_company("https://linkedin.com/company/xyz/"))
print(f"Extracted {result['extracted_count']} employees")
```

### Batch Processing

```python
companies = [
    "https://linkedin.com/company/company1/",
    "https://linkedin.com/company/company2/",
    "https://linkedin.com/company/company3/",
]

for url in companies:
    result = await browser.extract_company_employees(url)
    save_to_database(result)
    await asyncio.sleep(10)  # Rate limiting
```

### API Integration

```python
from fastapi import FastAPI
from services.headless_browser import HeadlessBrowser

app = FastAPI()

@app.post("/extract")
async def extract(company_url: str):
    browser = HeadlessBrowser()
    await browser.start(headless=True)
    result = await browser.extract_company_employees(company_url)
    await browser.close()
    return result
```

---

## 🐛 Troubleshooting

### "Not logged in" Error

**Solution:**
```bash
python cli_extractor.py login
```

### "No employee cards found"

**Possible causes:**
- Session expired
- LinkedIn changed HTML structure
- Page didn't load

**Solutions:**
1. Re-login: `python cli_extractor.py login`
2. Increase wait time in `headless_browser.py`
3. Update selectors in `html_navigator.py`

### Session Expired

LinkedIn sessions last 30-90 days. If expired:
```bash
python cli_extractor.py login  # Re-login
```

---

## ⚡ Performance

- **Single page:** ~5-10 seconds
- **10 pages:** ~1-2 minutes  
- **100 employees:** ~2-3 minutes

### Optimization

```python
# Reduce wait times (if stable)
await asyncio.sleep(1)  # Instead of 2-3

# Parallel extraction
tasks = [extract_company(url) for url in urls]
results = await asyncio.gather(*tasks)
```

---

## 🔒 Privacy & Ethics

### Best Practices

✅ **DO:**
- Use for legitimate purposes
- Respect LinkedIn's ToS
- Rate limit requests
- Extract public data only

❌ **DON'T:**
- Scrape at high frequency
- Extract private data
- Violate privacy laws

### Rate Limiting

```python
await asyncio.sleep(random.uniform(5, 10))  # Random delay
```

---

## 📚 Full Documentation

See `INVISIBLE_EXTRACTION_GUIDE.md` for:
- Complete architecture
- HTML parsing examples
- Customization guide
- API reference
- Advanced techniques

---

## 🎯 Use Cases

1. **Recruitment:** Find candidates at specific companies
2. **Market Research:** Analyze competitor team sizes
3. **Lead Generation:** Identify decision makers
4. **Network Analysis:** Map company connections

---

## ✨ Why This System?

### Traditional Scraping
- ❌ Visible browser windows
- ❌ Manual clicking
- ❌ Browser automation visible to user
- ❌ Requires constant attention

### hrunxtnshn
- ✅ Completely invisible
- ✅ Fully automated
- ✅ Background processing
- ✅ Terminal-only output
- ✅ Session persistence
- ✅ HTML-based navigation

---

## 🚀 Getting Started

```bash
# 1. Clone repo
git clone https://github.com/hrunx/hrunxtnshn.git
cd hrunxtnshn/orchestrator

# 2. Install
pip install -r requirements.txt
playwright install chromium

# 3. Login (one time)
python cli_extractor.py login

# 4. Extract (invisible)
python cli_extractor.py extract "Your Company Name"
```

**That's it! No visible browser. No tabs. Just results.**

---

## 📞 Support

- **Documentation:** `INVISIBLE_EXTRACTION_GUIDE.md`
- **GitHub:** https://github.com/hrunx/hrunxtnshn
- **Issues:** Check troubleshooting section

---

## 🎉 Summary

**hrunxtnshn** is a completely invisible LinkedIn extraction system that:

- Runs in the background (no visible browser)
- Uses saved sessions (login once)
- Parses HTML intelligently
- Extracts employee data automatically
- Outputs to terminal and JSON

**Perfect for automated, invisible LinkedIn data extraction.**

---

**Happy invisible browsing! 🕵️**
