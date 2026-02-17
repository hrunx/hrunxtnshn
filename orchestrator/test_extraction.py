#!/usr/bin/env python3
"""
Test script to demonstrate invisible extraction using existing browser cookies.
"""

import asyncio
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from services.headless_browser import HeadlessBrowser
from services.html_navigator import LinkedInHTMLNavigator

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_extraction():
    """Test invisible extraction with Hysabat Solutions."""
    
    print("\n" + "="*70)
    print("🚀 INVISIBLE LINKEDIN EXTRACTION TEST")
    print("="*70)
    print("\n📋 Target: Hysabat Solutions")
    print("🔧 Method: HTML-based navigation with Playwright headless")
    print("👁️  Visibility: COMPLETELY INVISIBLE - No browser window\n")
    
    company_url = "https://www.linkedin.com/company/hysabatsolutions/"
    
    # Create browser instance
    browser = HeadlessBrowser("linkedin_session.json")
    
    try:
        # Start headless browser
        print("[1/5] Starting headless browser...")
        await browser.start(headless=True)
        print("✅ Browser started (invisible)")
        
        # Navigate to company page
        print(f"\n[2/5] Navigating to company page...")
        await browser.navigate(company_url)
        print(f"✅ Navigated to: {company_url}")
        
        # Parse HTML to find People tab
        print("\n[3/5] Parsing HTML to find People tab...")
        html = await browser.get_html()
        navigator = LinkedInHTMLNavigator()
        navigator.parse_page(html)
        
        # Try to navigate to people page directly
        people_url = f"{company_url.rstrip('/')}/people/"
        print(f"✅ Found people URL: {people_url}")
        
        print("\n[4/5] Extracting employees...")
        await browser.navigate(people_url)
        
        # Scroll and extract
        await browser.scroll_to_bottom()
        html = await browser.get_html()
        navigator.parse_page(html)
        
        # Extract company info
        company_info = navigator.extract_company_info()
        print(f"\n📊 Company: {company_info.get('name', 'Unknown')}")
        print(f"👥 Size: {company_info.get('employee_size', 'Unknown')}")
        print(f"📍 Location: {company_info.get('industry', 'Unknown')}")
        
        # Extract employees
        employees = navigator.extract_employee_cards()
        total_count = navigator.get_total_employee_count()
        
        print(f"\n[5/5] Extraction complete!")
        print("="*70)
        print(f"✅ Total employees found: {total_count or len(employees)}")
        print(f"✅ Extracted from page: {len(employees)}")
        print("="*70)
        
        # Display results
        print(f"\n📋 Extracted Employees:\n")
        for i, emp in enumerate(employees[:15], 1):
            print(f"{i:2d}. {emp.get('name', 'Unknown')}")
            if emp.get('headline'):
                print(f"    └─ {emp['headline'][:80]}")
            if emp.get('location'):
                print(f"    └─ 📍 {emp['location']}")
            print()
        
        if len(employees) > 15:
            print(f"... and {len(employees) - 15} more employees\n")
        
        # Save results
        result = {
            'company_name': company_info.get('name', 'Unknown'),
            'company_url': company_url,
            'total_employees': total_count or len(employees),
            'extracted_count': len(employees),
            'employees': employees,
            'company_info': company_info
        }
        
        output_file = "hysabat_extraction_test.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {output_file}\n")
        
        print("="*70)
        print("✅ INVISIBLE EXTRACTION SUCCESSFUL!")
        print("="*70)
        print("\n🎯 Key Points:")
        print("  • No visible browser window appeared")
        print("  • HTML was parsed to identify elements")
        print("  • Navigation happened in the background")
        print("  • All output in terminal only\n")
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}\n")
    
    finally:
        await browser.close()
        print("🔒 Browser closed\n")


if __name__ == '__main__':
    asyncio.run(test_extraction())
