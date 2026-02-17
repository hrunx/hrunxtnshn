"""
HTML-based navigation system for LinkedIn pages.
Parses DOM structure and intelligently identifies elements to interact with.
"""

from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class LinkedInHTMLNavigator:
    """
    Intelligent HTML parser and navigator for LinkedIn pages.
    Understands LinkedIn's DOM structure and can identify clickable elements.
    """
    
    def __init__(self):
        self.current_html = None
        self.soup = None
        
    def parse_page(self, html: str) -> None:
        """Parse HTML content and prepare for navigation."""
        self.current_html = html
        self.soup = BeautifulSoup(html, 'html.parser')
        logger.info("HTML parsed successfully")
    
    def find_people_tab(self) -> Optional[Dict[str, str]]:
        """
        Find the 'People' tab link on a company page.
        Returns selector information for clicking.
        """
        # Method 1: Look for exact text "People"
        people_links = self.soup.find_all('a', string=re.compile(r'People', re.IGNORECASE))
        for link in people_links:
            href = link.get('href', '')
            if '/people' in href:
                return {
                    'type': 'link',
                    'selector': f"a[href*='/people']",
                    'text': link.get_text(strip=True),
                    'href': href
                }
        
        # Method 2: Look for navigation with 'people' in ID or class
        nav_items = self.soup.find_all(['a', 'button'], id=re.compile(r'people', re.IGNORECASE))
        if nav_items:
            item = nav_items[0]
            return {
                'type': 'link',
                'selector': f"#{item.get('id')}",
                'text': item.get_text(strip=True),
                'href': item.get('href', '')
            }
        
        logger.warning("Could not find People tab")
        return None
    
    def extract_employee_cards(self) -> List[Dict[str, str]]:
        """
        Extract employee information from company people page.
        Parses employee cards from LinkedIn's HTML structure.
        """
        employees = []
        
        # LinkedIn uses specific classes for employee cards
        # Pattern: org-people-profile-card or similar
        card_selectors = [
            'li.org-people-profile-card',
            'div.org-people-profile-card',
            'li[class*="people-profile"]',
            'div[class*="people-profile"]'
        ]
        
        cards = []
        for selector in card_selectors:
            found = self.soup.select(selector)
            if found:
                cards = found
                logger.info(f"Found {len(cards)} employee cards using selector: {selector}")
                break
        
        if not cards:
            logger.warning("No employee cards found")
            return employees
        
        for card in cards:
            employee = self._parse_employee_card(card)
            if employee:
                employees.append(employee)
        
        logger.info(f"Extracted {len(employees)} employees")
        return employees
    
    def _parse_employee_card(self, card) -> Optional[Dict[str, str]]:
        """Parse individual employee card to extract data."""
        try:
            employee = {}
            
            # Extract name
            name_selectors = [
                'a.org-people-profile-card__profile-title',
                'div.org-people-profile-card__profile-title',
                'a[href*="/in/"]',
                'span.org-people-profile-card__profile-title'
            ]
            
            for selector in name_selectors:
                name_elem = card.select_one(selector)
                if name_elem:
                    employee['name'] = name_elem.get_text(strip=True)
                    employee['profile_url'] = name_elem.get('href', '')
                    break
            
            if not employee.get('name'):
                return None
            
            # Extract position/headline
            headline_selectors = [
                'div.artdeco-entity-lockup__subtitle',
                'div.org-people-profile-card__headline',
                'span.org-people-profile-card__headline',
                'div[class*="headline"]'
            ]
            
            for selector in headline_selectors:
                headline_elem = card.select_one(selector)
                if headline_elem:
                    employee['headline'] = headline_elem.get_text(strip=True)
                    break
            
            # Extract location
            location_selectors = [
                'div.artdeco-entity-lockup__caption',
                'div.org-people-profile-card__location',
                'span[class*="location"]'
            ]
            
            for selector in location_selectors:
                location_elem = card.select_one(selector)
                if location_elem:
                    employee['location'] = location_elem.get_text(strip=True)
                    break
            
            # Extract connection degree
            connection_elem = card.find(string=re.compile(r'\d+(st|nd|rd|th)'))
            if connection_elem:
                employee['connection_degree'] = connection_elem.strip()
            
            # Extract time at company (if visible)
            time_pattern = re.compile(r'\d+\s*(year|month|yr|mo)', re.IGNORECASE)
            time_elem = card.find(string=time_pattern)
            if time_elem:
                employee['time_at_company'] = time_elem.strip()
            
            return employee
            
        except Exception as e:
            logger.error(f"Error parsing employee card: {e}")
            return None
    
    def find_next_page_button(self) -> Optional[Dict[str, str]]:
        """
        Find the 'Next' button for pagination.
        Returns selector information for clicking.
        """
        # Method 1: Button with aria-label="Next"
        next_buttons = self.soup.find_all('button', attrs={'aria-label': re.compile(r'Next', re.IGNORECASE)})
        if next_buttons:
            button = next_buttons[0]
            return {
                'type': 'button',
                'selector': f"button[aria-label*='Next']",
                'text': button.get_text(strip=True),
                'disabled': button.get('disabled') is not None
            }
        
        # Method 2: Link with "Next" text
        next_links = self.soup.find_all('a', string=re.compile(r'Next', re.IGNORECASE))
        if next_links:
            link = next_links[0]
            return {
                'type': 'link',
                'selector': "a:contains('Next')",
                'text': link.get_text(strip=True),
                'href': link.get('href', '')
            }
        
        # Method 3: Pagination with page numbers
        page_buttons = self.soup.find_all('button', attrs={'aria-label': re.compile(r'Page \d+', re.IGNORECASE)})
        if page_buttons:
            # Find the highest page number
            current_page = 1
            for btn in page_buttons:
                label = btn.get('aria-label', '')
                match = re.search(r'Page (\d+)', label)
                if match:
                    page_num = int(match.group(1))
                    if page_num > current_page:
                        return {
                            'type': 'button',
                            'selector': f"button[aria-label='Page {page_num}']",
                            'text': str(page_num),
                            'disabled': False
                        }
        
        logger.info("No next page button found - likely on last page")
        return None
    
    def find_show_more_button(self) -> Optional[Dict[str, str]]:
        """
        Find 'Show more' or 'Load more' button for infinite scroll pages.
        """
        show_more_patterns = [
            'Show more',
            'Load more',
            'See more',
            'Show all'
        ]
        
        for pattern in show_more_patterns:
            buttons = self.soup.find_all('button', string=re.compile(pattern, re.IGNORECASE))
            if buttons:
                button = buttons[0]
                return {
                    'type': 'button',
                    'selector': f"button:contains('{pattern}')",
                    'text': button.get_text(strip=True),
                    'disabled': button.get('disabled') is not None
                }
        
        return None
    
    def get_total_employee_count(self) -> Optional[int]:
        """
        Extract total employee count from page.
        Usually displayed as "X associated members" or similar.
        """
        # Pattern: "18 associated members", "63 employees", etc.
        count_patterns = [
            r'(\d+)\s*associated members',
            r'(\d+)\s*employees',
            r'(\d+)\s*people',
            r'(\d+)\s*results'
        ]
        
        for pattern in count_patterns:
            text_elem = self.soup.find(string=re.compile(pattern, re.IGNORECASE))
            if text_elem:
                match = re.search(pattern, text_elem, re.IGNORECASE)
                if match:
                    count = int(match.group(1))
                    logger.info(f"Found total employee count: {count}")
                    return count
        
        return None
    
    def extract_company_info(self) -> Dict[str, str]:
        """
        Extract company information from company page.
        """
        company_info = {}
        
        # Company name
        name_selectors = [
            'h1.org-top-card-summary__title',
            'h1[class*="top-card"]',
            'h1.t-24'
        ]
        
        for selector in name_selectors:
            name_elem = self.soup.select_one(selector)
            if name_elem:
                company_info['name'] = name_elem.get_text(strip=True)
                break
        
        # Follower count
        follower_elem = self.soup.find(string=re.compile(r'(\d+[\d,]*)\s*followers?', re.IGNORECASE))
        if follower_elem:
            match = re.search(r'(\d+[\d,]*)\s*followers?', follower_elem, re.IGNORECASE)
            if match:
                company_info['followers'] = match.group(1).replace(',', '')
        
        # Employee size
        size_elem = self.soup.find(string=re.compile(r'(\d+-\d+|\d+)\s*employees?', re.IGNORECASE))
        if size_elem:
            match = re.search(r'(\d+-\d+|\d+)\s*employees?', size_elem, re.IGNORECASE)
            if match:
                company_info['employee_size'] = match.group(1)
        
        # Industry
        industry_selectors = [
            'div.org-top-card-summary__info-item',
            'div[class*="industry"]'
        ]
        
        for selector in industry_selectors:
            elems = self.soup.select(selector)
            for elem in elems:
                text = elem.get_text(strip=True)
                if len(text) > 10 and len(text) < 100:  # Reasonable industry length
                    company_info['industry'] = text
                    break
        
        return company_info
