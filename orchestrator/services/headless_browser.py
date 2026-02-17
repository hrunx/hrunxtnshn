"""
Headless browser using Playwright for invisible browsing.
Manages LinkedIn sessions and performs HTML-based navigation.
"""

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional, Dict, List
import asyncio
import json
import logging
from pathlib import Path

from .html_navigator import LinkedInHTMLNavigator

logger = logging.getLogger(__name__)


class HeadlessBrowser:
    """
    Invisible browser controller using Playwright.
    All navigation happens in the background with no visible windows.
    """
    
    def __init__(self, session_file: str = "linkedin_session.json"):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.session_file = Path(session_file)
        self.navigator = LinkedInHTMLNavigator()
        
    async def start(self, headless: bool = True):
        """Start the headless browser."""
        logger.info("Starting headless browser...")
        self.playwright = await async_playwright().start()
        
        # Launch browser in headless mode (invisible)
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        # Create context with session if available
        context_options = {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Load saved session if exists
        if self.session_file.exists():
            logger.info(f"Loading session from {self.session_file}")
            with open(self.session_file, 'r') as f:
                storage_state = json.load(f)
            context_options['storage_state'] = storage_state
        
        self.context = await self.browser.new_context(**context_options)
        self.page = await self.context.new_page()
        
        logger.info("Headless browser started successfully")
    
    async def save_session(self):
        """Save current browser session for reuse."""
        if self.context:
            storage_state = await self.context.storage_state()
            with open(self.session_file, 'w') as f:
                json.dump(storage_state, f, indent=2)
            logger.info(f"Session saved to {self.session_file}")
    
    async def is_logged_in(self) -> bool:
        """Check if user is logged into LinkedIn."""
        try:
            await self.page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=10000)
            await asyncio.sleep(2)
            
            # Check if we're on the feed page (logged in) or login page
            current_url = self.page.url
            if '/login' in current_url or '/uas/login' in current_url:
                logger.info("Not logged in - on login page")
                return False
            
            # Check for feed elements
            html = await self.page.content()
            if 'feed' in html.lower() and 'home' in html.lower():
                logger.info("Logged in successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False
    
    async def navigate(self, url: str, wait_for: str = 'domcontentloaded'):
        """Navigate to a URL invisibly."""
        logger.info(f"Navigating to: {url}")
        await self.page.goto(url, wait_until=wait_for, timeout=30000)
        await asyncio.sleep(2)  # Wait for dynamic content
        logger.info(f"Navigation complete: {self.page.url}")
    
    async def get_html(self) -> str:
        """Get current page HTML."""
        return await self.page.content()
    
    async def click_element(self, selector: str):
        """Click an element by selector."""
        logger.info(f"Clicking element: {selector}")
        try:
            await self.page.click(selector, timeout=5000)
            await asyncio.sleep(1)
            logger.info("Click successful")
        except Exception as e:
            logger.error(f"Click failed: {e}")
            raise
    
    async def scroll_to_bottom(self):
        """Scroll to bottom of page to load dynamic content."""
        logger.info("Scrolling to bottom...")
        await self.page.evaluate("""
            window.scrollTo(0, document.body.scrollHeight);
        """)
        await asyncio.sleep(2)
    
    async def extract_company_employees(self, company_url: str, max_pages: int = 10) -> Dict:
        """
        Extract all employees from a LinkedIn company page.
        Uses HTML-based navigation - completely invisible.
        """
        logger.info(f"Starting employee extraction for: {company_url}")
        
        # Navigate to company page
        await self.navigate(company_url)
        
        # Parse HTML to find People tab
        html = await self.get_html()
        self.navigator.parse_page(html)
        
        # Extract company info
        company_info = self.navigator.extract_company_info()
        logger.info(f"Company info: {company_info}")
        
        # Find and click People tab
        people_tab = self.navigator.find_people_tab()
        if not people_tab:
            # Try direct URL
            people_url = f"{company_url.rstrip('/')}/people/"
            logger.info(f"People tab not found, trying direct URL: {people_url}")
            await self.navigate(people_url)
        else:
            logger.info(f"Found People tab: {people_tab}")
            await self.click_element(people_tab['selector'])
            await asyncio.sleep(2)
        
        # Extract employees with pagination
        all_employees = []
        current_page = 1
        
        while current_page <= max_pages:
            logger.info(f"Extracting page {current_page}...")
            
            # Scroll to load all content
            await self.scroll_to_bottom()
            
            # Get HTML and parse
            html = await self.get_html()
            self.navigator.parse_page(html)
            
            # Extract employees from current page
            employees = self.navigator.extract_employee_cards()
            logger.info(f"Found {len(employees)} employees on page {current_page}")
            
            # Add to results (avoid duplicates)
            for emp in employees:
                if emp not in all_employees:
                    all_employees.append(emp)
            
            # Check for next page
            next_button = self.navigator.find_next_page_button()
            if not next_button or next_button.get('disabled'):
                logger.info("No more pages - extraction complete")
                break
            
            # Click next page
            try:
                await self.click_element(next_button['selector'])
                await asyncio.sleep(3)  # Wait for page load
                current_page += 1
            except Exception as e:
                logger.error(f"Failed to click next page: {e}")
                break
        
        # Get total count
        total_count = self.navigator.get_total_employee_count()
        
        result = {
            'company_name': company_info.get('name', 'Unknown'),
            'company_url': company_url,
            'total_employees': total_count or len(all_employees),
            'extracted_count': len(all_employees),
            'pages_scraped': current_page,
            'employees': all_employees,
            'company_info': company_info
        }
        
        logger.info(f"Extraction complete: {len(all_employees)} employees from {current_page} pages")
        return result
    
    async def close(self):
        """Close the browser."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser closed")


class LinkedInSessionManager:
    """
    Manages LinkedIn authentication sessions.
    User logs in once, session is saved and reused.
    """
    
    def __init__(self, session_file: str = "linkedin_session.json"):
        self.session_file = Path(session_file)
        self.browser = HeadlessBrowser(session_file)
    
    async def ensure_logged_in(self) -> bool:
        """
        Ensure user is logged into LinkedIn.
        Returns True if logged in, False if manual login required.
        """
        await self.browser.start(headless=True)
        
        if await self.browser.is_logged_in():
            logger.info("Already logged in with saved session")
            return True
        
        logger.warning("Not logged in - manual login required")
        logger.info("Please run the login flow separately")
        return False
    
    async def manual_login_flow(self):
        """
        Start browser in visible mode for user to log in manually.
        Session will be saved for future use.
        """
        logger.info("Starting manual login flow...")
        await self.browser.start(headless=False)  # Visible browser
        
        await self.browser.navigate('https://www.linkedin.com/login')
        
        print("\n" + "="*60)
        print("MANUAL LOGIN REQUIRED")
        print("="*60)
        print("1. A browser window has opened")
        print("2. Please log in to LinkedIn")
        print("3. Once logged in, press ENTER here to continue...")
        print("="*60 + "\n")
        
        input("Press ENTER after logging in...")
        
        # Verify login
        if await self.browser.is_logged_in():
            await self.browser.save_session()
            print("\n✅ Login successful! Session saved for future use.\n")
            await self.browser.close()
            return True
        else:
            print("\n❌ Login failed. Please try again.\n")
            await self.browser.close()
            return False
