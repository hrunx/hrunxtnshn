#!/usr/bin/env python3
"""
CLI tool for testing invisible LinkedIn extraction.
Run completely in terminal with no visible browser.
"""

import asyncio
import json
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.headless_browser import HeadlessBrowser, LinkedInSessionManager
from services.searxng_client import SearXNGClient
from config import settings

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def login_flow():
    """Interactive login flow to save LinkedIn session."""
    print("\n🔐 LinkedIn Login Flow")
    print("="*60)
    
    session_manager = LinkedInSessionManager()
    success = await session_manager.manual_login_flow()
    
    if success:
        print("\n✅ Session saved successfully!")
        print("You can now run extractions without logging in again.\n")
    else:
        print("\n❌ Login failed. Please try again.\n")


async def extract_company(company_name: str, max_pages: int = 10):
    """
    Extract employees from a company.
    Completely invisible - all in terminal.
    """
    print(f"\n🔍 Extracting employees from: {company_name}")
    print("="*60)
    
    # Step 1: Search for company LinkedIn URL
    print("\n[1/4] Searching for company LinkedIn URL...")
    search_client = SearXNGClient(settings.SEARXNG_URL)
    
    query = f"{company_name} site:linkedin.com/company"
    results = await search_client.search(query)
    
    company_url = None
    for result in results:
        if '/company/' in result['url'] and 'linkedin.com' in result['url']:
            company_url = result['url'].split('?')[0]  # Remove query params
            print(f"✅ Found: {company_url}")
            break
    
    if not company_url:
        print(f"❌ Could not find LinkedIn page for: {company_name}")
        return None
    
    # Step 2: Check LinkedIn session
    print("\n[2/4] Checking LinkedIn session...")
    session_manager = LinkedInSessionManager()
    
    if not await session_manager.ensure_logged_in():
        print("❌ Not logged in. Please run: python cli_extractor.py login")
        await session_manager.browser.close()
        return None
    
    print("✅ Logged in with saved session")
    
    # Step 3: Extract employees (invisible browsing)
    print(f"\n[3/4] Extracting employees (max {max_pages} pages)...")
    print("⏳ This happens completely in the background...")
    
    browser = session_manager.browser
    result = await browser.extract_company_employees(company_url, max_pages=max_pages)
    
    # Step 4: Display results
    print(f"\n[4/4] Extraction complete!")
    print("="*60)
    print(f"Company: {result['company_name']}")
    print(f"Total Employees: {result['total_employees']}")
    print(f"Extracted: {result['extracted_count']}")
    print(f"Pages Scraped: {result['pages_scraped']}")
    print("="*60)
    
    # Show first 10 employees
    print(f"\n📋 First 10 employees:")
    for i, emp in enumerate(result['employees'][:10], 1):
        print(f"\n{i}. {emp.get('name', 'Unknown')}")
        if emp.get('headline'):
            print(f"   Position: {emp['headline']}")
        if emp.get('location'):
            print(f"   Location: {emp['location']}")
        if emp.get('connection_degree'):
            print(f"   Connection: {emp['connection_degree']}")
    
    if len(result['employees']) > 10:
        print(f"\n... and {len(result['employees']) - 10} more employees")
    
    # Save to file
    output_file = f"{company_name.replace(' ', '_').lower()}_employees.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Full results saved to: {output_file}")
    
    await browser.close()
    return result


async def extract_url(url: str, max_pages: int = 10):
    """Extract employees from a direct LinkedIn company URL."""
    print(f"\n🔍 Extracting employees from URL: {url}")
    print("="*60)
    
    # Check LinkedIn session
    print("\n[1/3] Checking LinkedIn session...")
    session_manager = LinkedInSessionManager()
    
    if not await session_manager.ensure_logged_in():
        print("❌ Not logged in. Please run: python cli_extractor.py login")
        await session_manager.browser.close()
        return None
    
    print("✅ Logged in with saved session")
    
    # Extract employees
    print(f"\n[2/3] Extracting employees (max {max_pages} pages)...")
    print("⏳ This happens completely in the background...")
    
    browser = session_manager.browser
    result = await browser.extract_company_employees(url, max_pages=max_pages)
    
    # Display results
    print(f"\n[3/3] Extraction complete!")
    print("="*60)
    print(f"Company: {result['company_name']}")
    print(f"Total Employees: {result['total_employees']}")
    print(f"Extracted: {result['extracted_count']}")
    print(f"Pages Scraped: {result['pages_scraped']}")
    print("="*60)
    
    # Show first 10 employees
    print(f"\n📋 First 10 employees:")
    for i, emp in enumerate(result['employees'][:10], 1):
        print(f"\n{i}. {emp.get('name', 'Unknown')}")
        if emp.get('headline'):
            print(f"   Position: {emp['headline']}")
        if emp.get('location'):
            print(f"   Location: {emp['location']}")
    
    if len(result['employees']) > 10:
        print(f"\n... and {len(result['employees']) - 10} more employees")
    
    # Save to file
    company_name = result['company_name'].replace(' ', '_').lower()
    output_file = f"{company_name}_employees.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Full results saved to: {output_file}")
    
    await browser.close()
    return result


def main():
    parser = argparse.ArgumentParser(
        description='Invisible LinkedIn Employee Extractor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Login to LinkedIn (one-time setup)
  python cli_extractor.py login
  
  # Extract employees by company name
  python cli_extractor.py extract "Hysabat Solutions"
  
  # Extract from direct URL
  python cli_extractor.py url "https://www.linkedin.com/company/hysabatsolutions/"
  
  # Extract with custom page limit
  python cli_extractor.py extract "Gasable" --max-pages 5
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Login command
    subparsers.add_parser('login', help='Login to LinkedIn and save session')
    
    # Extract by company name
    extract_parser = subparsers.add_parser('extract', help='Extract employees by company name')
    extract_parser.add_argument('company', help='Company name to search for')
    extract_parser.add_argument('--max-pages', type=int, default=10, help='Maximum pages to scrape (default: 10)')
    
    # Extract by URL
    url_parser = subparsers.add_parser('url', help='Extract employees from LinkedIn URL')
    url_parser.add_argument('url', help='LinkedIn company URL')
    url_parser.add_argument('--max-pages', type=int, default=10, help='Maximum pages to scrape (default: 10)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Run command
    if args.command == 'login':
        asyncio.run(login_flow())
    elif args.command == 'extract':
        asyncio.run(extract_company(args.company, args.max_pages))
    elif args.command == 'url':
        asyncio.run(extract_url(args.url, args.max_pages))


if __name__ == '__main__':
    main()
