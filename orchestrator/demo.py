#!/usr/bin/env python3
"""
Demo script showing invisible LinkedIn extraction.
Run this to see the system in action.
"""

import asyncio
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from services.headless_browser import HeadlessBrowser, LinkedInSessionManager
from services.html_navigator import LinkedInHTMLNavigator

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def print_step(step, text):
    """Print a step."""
    print(f"[{step}] {text}")


async def demo_extraction():
    """
    Demonstrate invisible LinkedIn extraction.
    """
    
    print_header("🕵️  INVISIBLE LINKEDIN EXTRACTION DEMO")
    
    print("📋 This demo shows how the system works:")
    print("   • No visible browser windows")
    print("   • All navigation in background")
    print("   • HTML-based element detection")
    print("   • Terminal-only output")
    print()
    
    # Configuration
    company_url = "https://www.linkedin.com/company/hysabatsolutions/"
    company_name = "Hysabat Solutions"
    
    print(f"🎯 Target: {company_name}")
    print(f"🔗 URL: {company_url}")
    print()
    
    # Check if session exists
    session_file = Path("linkedin_session.json")
    if not session_file.exists():
        print_header("⚠️  NO SESSION FOUND")
        print("You need to login first to save your LinkedIn session.")
        print()
        print("Run this command:")
        print("  python3 cli_extractor.py login")
        print()
        print("This will:")
        print("  1. Open a visible browser window")
        print("  2. Let you log in to LinkedIn")
        print("  3. Save your session to linkedin_session.json")
        print("  4. Close the browser")
        print()
        print("After that, you can run this demo again and it will work invisibly!")
        return
    
    print("✅ Session file found: linkedin_session.json")
    print()
    
    # Create browser instance
    browser = HeadlessBrowser("linkedin_session.json")
    
    try:
        # Step 1: Start headless browser
        print_step("1/6", "Starting headless browser...")
        await browser.start(headless=True)
        print("     ✅ Browser started (INVISIBLE - no window)")
        print()
        
        # Step 2: Check login status
        print_step("2/6", "Checking LinkedIn session...")
        is_logged_in = await browser.is_logged_in()
        
        if not is_logged_in:
            print("     ❌ Session expired or invalid")
            print()
            print("     Please re-login:")
            print("       python3 cli_extractor.py login")
            await browser.close()
            return
        
        print("     ✅ Logged in with saved session")
        print()
        
        # Step 3: Navigate to company page
        print_step("3/6", f"Navigating to {company_name}...")
        await browser.navigate(company_url)
        print(f"     ✅ Navigated to: {company_url}")
        print()
        
        # Step 4: Parse HTML and find People tab
        print_step("4/6", "Parsing HTML to find People tab...")
        html = await browser.get_html()
        navigator = LinkedInHTMLNavigator()
        navigator.parse_page(html)
        
        # Get company info
        company_info = navigator.extract_company_info()
        if company_info.get('name'):
            print(f"     ✅ Found company: {company_info['name']}")
        
        # Navigate to people page
        people_url = f"{company_url.rstrip('/')}/people/"
        print(f"     ✅ People URL: {people_url}")
        print()
        
        # Step 5: Extract employees
        print_step("5/6", "Extracting employees (invisible browsing)...")
        await browser.navigate(people_url)
        await browser.scroll_to_bottom()
        
        html = await browser.get_html()
        navigator.parse_page(html)
        
        employees = navigator.extract_employee_cards()
        total_count = navigator.get_total_employee_count()
        
        print(f"     ✅ Found {len(employees)} employees on first page")
        if total_count:
            print(f"     ✅ Total employees: {total_count}")
        print()
        
        # Step 6: Display results
        print_step("6/6", "Extraction complete!")
        print()
        
        print_header("📊 RESULTS")
        
        print(f"Company: {company_info.get('name', 'Unknown')}")
        print(f"Total Employees: {total_count or len(employees)}")
        print(f"Extracted: {len(employees)}")
        print()
        
        if employees:
            print("📋 Employees Found:\n")
            for i, emp in enumerate(employees[:10], 1):
                print(f"{i:2d}. {emp.get('name', 'Unknown')}")
                if emp.get('headline'):
                    headline = emp['headline'][:70]
                    print(f"    └─ {headline}")
                if emp.get('location'):
                    print(f"    └─ 📍 {emp['location']}")
                print()
            
            if len(employees) > 10:
                print(f"... and {len(employees) - 10} more employees\n")
        
        # Save results
        result = {
            'company_name': company_info.get('name', 'Unknown'),
            'company_url': company_url,
            'total_employees': total_count or len(employees),
            'extracted_count': len(employees),
            'employees': employees,
            'company_info': company_info
        }
        
        output_file = "demo_extraction_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {output_file}\n")
        
        print_header("✅ DEMO COMPLETE")
        
        print("🎯 Key Points:")
        print("  • No visible browser window appeared")
        print("  • HTML was parsed to identify elements")
        print("  • Navigation happened in the background")
        print("  • All output in terminal only")
        print("  • Session was reused (no login needed)")
        print()
        
        print("🚀 To extract from other companies:")
        print("  python3 cli_extractor.py extract \"Company Name\"")
        print()
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}\n")
    
    finally:
        await browser.close()
        print("🔒 Browser closed\n")


async def quick_test():
    """Quick test to verify system is working."""
    print_header("🔧 QUICK SYSTEM TEST")
    
    print("Testing components...")
    print()
    
    # Test 1: Check dependencies
    print("[1/3] Checking dependencies...")
    try:
        from playwright.async_api import async_playwright
        from bs4 import BeautifulSoup
        print("     ✅ Playwright installed")
        print("     ✅ BeautifulSoup installed")
    except ImportError as e:
        print(f"     ❌ Missing dependency: {e}")
        print()
        print("     Run: pip install -r requirements.txt")
        return
    print()
    
    # Test 2: Check session file
    print("[2/3] Checking session file...")
    session_file = Path("linkedin_session.json")
    if session_file.exists():
        print("     ✅ Session file found")
    else:
        print("     ⚠️  No session file")
        print("     Run: python3 cli_extractor.py login")
    print()
    
    # Test 3: Test browser start
    print("[3/3] Testing headless browser...")
    try:
        browser = HeadlessBrowser()
        await browser.start(headless=True)
        print("     ✅ Headless browser works")
        await browser.close()
    except Exception as e:
        print(f"     ❌ Browser test failed: {e}")
        return
    print()
    
    print_header("✅ SYSTEM TEST PASSED")
    print("All components working correctly!")
    print()
    print("Ready to extract! Run:")
    print("  python3 demo.py demo")
    print()


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            asyncio.run(quick_test())
        elif command == "demo":
            asyncio.run(demo_extraction())
        else:
            print("Unknown command. Use 'test' or 'demo'")
    else:
        # Default: run demo
        asyncio.run(demo_extraction())


if __name__ == '__main__':
    main()
