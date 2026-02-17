# 🕵️ Invisible LinkedIn Extraction Guide

Complete guide for HTML-based invisible browsing with the hrunxtnshn orchestrator.

---

## 🎯 What is Invisible Extraction?

**Invisible extraction** means:
- ✅ **No visible browser window** - Everything runs in the background
- ✅ **HTML-based navigation** - Orchestrator parses DOM and knows where to click
- ✅ **Terminal-only output** - All results displayed in command line
- ✅ **Session persistence** - Login once, reuse forever
- ✅ **Completely automated** - No manual intervention needed

---

## 🏗️ Architecture

```
User Request
    ↓
Orchestrator (Python)
    ↓
SearXNG Search → Find LinkedIn URL
    ↓
Playwright Headless Browser
    ↓
HTML Navigator (BeautifulSoup)
    ├─ Parse DOM structure
    ├─ Find clickable elements
    ├─ Extract employee data
    └─ Handle pagination
    ↓
JSON Results → Terminal Output
```

---

## 📦 Components

### 1. **HTML Navigator** (`services/html_navigator.py`)
- Parses LinkedIn's HTML structure
- Identifies tabs, buttons, and employee cards
- Extracts data from DOM elements
- Handles pagination logic

**Key Methods:**
```python
navigator.find_people_tab()          # Find "People" tab
navigator.extract_employee_cards()   # Extract all employees
navigator.find_next_page_button()    # Find pagination
navigator.get_total_employee_count() # Get total count
```

### 2. **Headless Browser** (`services/headless_browser.py`)
- Playwright-based invisible browsing
- Session management (cookies/storage)
- Automated navigation and clicking
- Scroll handling for dynamic content

**Key Methods:**
```python
browser.start(headless=True)                    # Start invisible
browser.navigate(url)                           # Go to URL
browser.extract_company_employees(url)          # Full extraction
```

### 3. **CLI Tool** (`cli_extractor.py`)
- Command-line interface for extraction
- Login flow management
- Progress display in terminal
- JSON output

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd orchestrator
pip install -r requirements.txt
playwright install chromium
```

### Step 2: Login to LinkedIn (One-Time)

```bash
python cli_extractor.py login
```

This will:
1. Open a visible browser window
2. Let you log in manually
3. Save session to `linkedin_session.json`
4. Close the browser

**You only need to do this once!**

### Step 3: Extract Employees (Invisible)

**By company name:**
```bash
python cli_extractor.py extract "Hysabat Solutions"
```

**By LinkedIn URL:**
```bash
python cli_extractor.py url "https://www.linkedin.com/company/hysabatsolutions/"
```

**With custom page limit:**
```bash
python cli_extractor.py extract "Gasable" --max-pages 5
```

---

## 📊 Example Output

```
🔍 Extracting employees from: Hysabat Solutions
============================================================

[1/4] Searching for company LinkedIn URL...
✅ Found: https://www.linkedin.com/company/hysabatsolutions/

[2/4] Checking LinkedIn session...
✅ Logged in with saved session

[3/4] Extracting employees (max 10 pages)...
⏳ This happens completely in the background...

[4/4] Extraction complete!
============================================================
Company: Hysabat Solutions حلول حسابات
Total Employees: 18
Extracted: 18
Pages Scraped: 2
============================================================

📋 First 10 employees:

1. Jameel Khan
   Position: Founder & CEO @ JMM/Hysabat | Planning & Growth | Entrepreneur
   Location: Riyadh, Saudi Arabia
   Connection: 1st

2. Mohammad Shah
   Position: Co-Founder @ Hysabat | Building Partnerships that Drive Success
   Location: Riyadh, Saudi Arabia
   Connection: 1st

3. Wafiullah Salarzai
   Position: Co-Founder | CTO at Hysabat Solutions & JMM Technologies
   Location: Riyadh, Saudi Arabia
   Connection: 1st

... and 15 more employees

💾 Full results saved to: hysabat_solutions_employees.json
```

---

## 🔍 How HTML Navigation Works

### 1. **Finding the People Tab**

The HTML navigator looks for:
```html
<!-- Method 1: Link with "People" text -->
<a href="/company/hysabatsolutions/people/">People</a>

<!-- Method 2: Navigation item with ID -->
<a id="org-menu-PEOPLE">People</a>

<!-- Method 3: Link with /people in href -->
<a href="https://linkedin.com/company/xyz/people/">...</a>
```

**Code:**
```python
people_tab = navigator.find_people_tab()
# Returns: {'selector': 'a[href*="/people"]', 'href': '...'}

await browser.click_element(people_tab['selector'])
```

### 2. **Extracting Employee Cards**

LinkedIn uses specific HTML structure:
```html
<li class="org-people-profile-card">
  <a class="org-people-profile-card__profile-title" href="/in/john-doe">
    John Doe
  </a>
  <div class="org-people-profile-card__headline">
    Software Engineer at Company
  </div>
  <div class="org-people-profile-card__location">
    San Francisco, CA
  </div>
</li>
```

**Code:**
```python
html = await browser.get_html()
navigator.parse_page(html)
employees = navigator.extract_employee_cards()
# Returns: [{'name': 'John Doe', 'headline': '...', ...}]
```

### 3. **Handling Pagination**

The navigator finds next page buttons:
```html
<!-- Method 1: Button with aria-label -->
<button aria-label="Next">Next</button>

<!-- Method 2: Page number buttons -->
<button aria-label="Page 2">2</button>
<button aria-label="Page 3">3</button>
```

**Code:**
```python
next_button = navigator.find_next_page_button()
if next_button and not next_button['disabled']:
    await browser.click_element(next_button['selector'])
```

---

## 🔐 Session Management

### How It Works

1. **First Login** (manual, visible browser):
   ```bash
   python cli_extractor.py login
   ```
   - Opens visible browser
   - You log in manually
   - Saves cookies/storage to `linkedin_session.json`

2. **Subsequent Extractions** (invisible):
   ```bash
   python cli_extractor.py extract "Company Name"
   ```
   - Loads saved session
   - No login required
   - Completely invisible

### Session File Structure

```json
{
  "cookies": [
    {
      "name": "li_at",
      "value": "...",
      "domain": ".linkedin.com",
      ...
    }
  ],
  "origins": [...]
}
```

### Session Expiration

LinkedIn sessions typically last **30-90 days**. If expired:
```bash
python cli_extractor.py login  # Re-login
```

---

## 🎨 Customization

### Extract Different Data

Edit `services/html_navigator.py`:

```python
def _parse_employee_card(self, card):
    employee = {}
    
    # Add custom field extraction
    skills_elem = card.select_one('.skills')
    if skills_elem:
        employee['skills'] = skills_elem.get_text(strip=True)
    
    # Add years of experience
    exp_pattern = re.compile(r'(\d+)\s*years?')
    exp_elem = card.find(string=exp_pattern)
    if exp_elem:
        employee['years_experience'] = exp_elem
    
    return employee
```

### Change Pagination Logic

```python
def find_next_page_button(self):
    # Custom logic for different pagination styles
    buttons = self.soup.find_all('button', class_='custom-next-btn')
    ...
```

### Add New Platforms

Create new navigator classes:
```python
class InstagramHTMLNavigator:
    def find_followers_tab(self): ...
    def extract_follower_cards(self): ...
```

---

## 🐛 Troubleshooting

### Issue: "Not logged in"

**Solution:**
```bash
python cli_extractor.py login
```

### Issue: "No employee cards found"

**Causes:**
- LinkedIn changed HTML structure
- Page didn't load completely
- Auth wall appeared

**Solution:**
1. Check if session is valid
2. Increase wait time in `headless_browser.py`:
   ```python
   await asyncio.sleep(5)  # Increase from 2 to 5
   ```
3. Update selectors in `html_navigator.py`

### Issue: "Click failed"

**Solution:**
- Element might be hidden or disabled
- Try alternative selector
- Add scroll before click:
  ```python
  await browser.scroll_to_element(selector)
  await browser.click_element(selector)
  ```

---

## 📈 Performance

### Extraction Speed

- **Single page**: ~5-10 seconds
- **10 pages**: ~1-2 minutes
- **100 employees**: ~2-3 minutes

### Optimization Tips

1. **Reduce wait times** (if stable):
   ```python
   await asyncio.sleep(1)  # Instead of 2-3
   ```

2. **Parallel extraction** (multiple companies):
   ```python
   tasks = [extract_company(url) for url in urls]
   results = await asyncio.gather(*tasks)
   ```

3. **Cache company URLs**:
   ```python
   # Store search results to avoid re-searching
   ```

---

## 🔒 Privacy & Ethics

### Best Practices

✅ **DO:**
- Use for legitimate business purposes
- Respect LinkedIn's terms of service
- Rate limit your requests
- Only extract public data

❌ **DON'T:**
- Scrape at high frequency
- Extract private/restricted data
- Sell scraped data
- Violate GDPR/privacy laws

### Rate Limiting

Add delays between requests:
```python
await asyncio.sleep(random.uniform(2, 5))  # Random delay
```

---

## 🎯 Use Cases

### 1. **Recruitment**
```bash
# Find all engineers at a company
python cli_extractor.py extract "Google" --max-pages 20
```

### 2. **Market Research**
```bash
# Analyze competitor team size
python cli_extractor.py extract "Competitor Inc"
```

### 3. **Lead Generation**
```bash
# Find decision makers
python cli_extractor.py url "https://linkedin.com/company/target/"
```

### 4. **Network Analysis**
```bash
# Map connections between companies
for company in companies:
    extract_company(company)
```

---

## 🚀 Advanced Usage

### Integrate with Orchestrator API

```python
from services.headless_browser import HeadlessBrowser

async def api_extract(company_url):
    browser = HeadlessBrowser()
    await browser.start(headless=True)
    result = await browser.extract_company_employees(company_url)
    await browser.close()
    return result
```

### Use with FastAPI

```python
@app.post("/extract/company")
async def extract_company(request: CompanyRequest):
    result = await api_extract(request.company_url)
    return result
```

### Batch Processing

```python
companies = [
    "https://linkedin.com/company/company1/",
    "https://linkedin.com/company/company2/",
    ...
]

for company_url in companies:
    result = await browser.extract_company_employees(company_url)
    save_to_database(result)
    await asyncio.sleep(10)  # Rate limiting
```

---

## 📚 API Reference

### HeadlessBrowser

```python
class HeadlessBrowser:
    async def start(headless: bool = True)
    async def navigate(url: str)
    async def get_html() -> str
    async def click_element(selector: str)
    async def scroll_to_bottom()
    async def extract_company_employees(url: str, max_pages: int) -> Dict
    async def save_session()
    async def is_logged_in() -> bool
    async def close()
```

### LinkedInHTMLNavigator

```python
class LinkedInHTMLNavigator:
    def parse_page(html: str)
    def find_people_tab() -> Optional[Dict]
    def extract_employee_cards() -> List[Dict]
    def find_next_page_button() -> Optional[Dict]
    def get_total_employee_count() -> Optional[int]
    def extract_company_info() -> Dict
```

---

## 🎉 Summary

You now have a **complete invisible extraction system** that:

✅ Parses HTML to understand page structure  
✅ Navigates by identifying clickable elements  
✅ Extracts data from DOM  
✅ Runs completely in the background  
✅ Outputs everything to terminal  
✅ Saves sessions for reuse  

**No visible browser. No manual clicking. Just results.**

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review HTML structure with browser DevTools
3. Update selectors in `html_navigator.py`
4. Test with `test_extraction.py`

**Happy invisible browsing! 🕵️**
