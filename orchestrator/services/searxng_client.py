"""
SearXNG Client - Open-source search engine integration
Provides privacy-focused search capabilities for the orchestrator
"""

import httpx
import logging
from typing import List, Dict, Optional
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class SearXNGClient:
    """Client for SearXNG open-source search engine"""
    
    def __init__(self, instance_url: str = "https://searx.be"):
        """
        Initialize SearXNG client
        
        Args:
            instance_url: SearXNG instance URL (default: public instance)
                         For self-hosted: http://localhost:8080
        """
        self.instance_url = instance_url.rstrip('/')
        self.search_endpoint = f"{self.instance_url}/search"
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"SearXNG client initialized with instance: {self.instance_url}")
    
    async def search(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        engines: Optional[List[str]] = None,
        language: str = "en",
        time_range: Optional[str] = None,
        safesearch: int = 0,
        format: str = "json"
    ) -> Dict:
        """
        Perform search query
        
        Args:
            query: Search query string
            categories: List of categories (general, images, news, etc.)
            engines: List of specific engines to use
            language: Search language code
            time_range: Time range filter (day, week, month, year)
            safesearch: Safe search level (0=off, 1=moderate, 2=strict)
            format: Response format (json, csv, rss)
        
        Returns:
            Search results dictionary
        """
        params = {
            "q": query,
            "format": format,
            "language": language,
            "safesearch": safesearch
        }
        
        if categories:
            params["categories"] = ",".join(categories)
        
        if engines:
            params["engines"] = ",".join(engines)
        
        if time_range:
            params["time_range"] = time_range
        
        try:
            logger.info(f"Searching SearXNG: {query}")
            response = await self.client.get(self.search_endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Found {len(data.get('results', []))} results")
            
            return data
        
        except httpx.HTTPError as e:
            logger.error(f"SearXNG search error: {e}")
            return {"error": str(e), "results": []}
    
    async def search_linkedin_company(self, company_name: str) -> Optional[str]:
        """
        Search for LinkedIn company page URL
        
        Args:
            company_name: Company name to search
        
        Returns:
            LinkedIn company URL or None
        """
        query = f"{company_name} site:linkedin.com/company"
        results = await self.search(query, engines=["google", "bing", "duckduckgo"])
        
        for result in results.get("results", []):
            url = result.get("url", "")
            if "linkedin.com/company/" in url:
                # Clean URL (remove query params)
                clean_url = url.split("?")[0]
                logger.info(f"Found LinkedIn company URL: {clean_url}")
                return clean_url
        
        logger.warning(f"No LinkedIn company URL found for: {company_name}")
        return None
    
    async def search_linkedin_profile(self, person_name: str, company: Optional[str] = None) -> Optional[str]:
        """
        Search for LinkedIn profile URL
        
        Args:
            person_name: Person's name
            company: Optional company name to narrow search
        
        Returns:
            LinkedIn profile URL or None
        """
        query = f"{person_name}"
        if company:
            query += f" {company}"
        query += " site:linkedin.com/in"
        
        results = await self.search(query, engines=["google", "bing"])
        
        for result in results.get("results", []):
            url = result.get("url", "")
            if "linkedin.com/in/" in url:
                clean_url = url.split("?")[0]
                logger.info(f"Found LinkedIn profile URL: {clean_url}")
                return clean_url
        
        return None
    
    async def search_company_website(self, company_name: str) -> Optional[str]:
        """
        Search for company website
        
        Args:
            company_name: Company name
        
        Returns:
            Company website URL or None
        """
        query = f"{company_name} official website"
        results = await self.search(query, engines=["google", "bing", "duckduckgo"])
        
        if results.get("results"):
            # Return first result URL
            url = results["results"][0].get("url", "")
            logger.info(f"Found company website: {url}")
            return url
        
        return None
    
    async def search_multiple_companies(self, company_names: List[str]) -> Dict[str, Optional[str]]:
        """
        Search for multiple LinkedIn company URLs in parallel
        
        Args:
            company_names: List of company names
        
        Returns:
            Dictionary mapping company names to LinkedIn URLs
        """
        import asyncio
        
        tasks = [
            self.search_linkedin_company(name)
            for name in company_names
        ]
        
        results = await asyncio.gather(*tasks)
        
        return {
            name: url
            for name, url in zip(company_names, results)
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Self-hosted SearXNG setup instructions
SEARXNG_SETUP = """
# Self-Hosted SearXNG Setup (Docker)

## Quick Start

1. Install Docker and Docker Compose

2. Create docker-compose.yml:

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

3. Start SearXNG:

```bash
docker-compose up -d
```

4. Access at: http://localhost:8080

5. Update orchestrator config:

```python
SEARXNG_URL = "http://localhost:8080"
```

## Configuration

Edit `searxng/settings.yml` to:
- Enable/disable search engines
- Set rate limits
- Configure privacy settings
- Add API keys for specific engines

## Public Instances (Alternative)

If you don't want to self-host, use public instances:
- https://searx.be
- https://searx.tiekoetter.com
- https://search.sapti.me

Note: Public instances may have rate limits.
"""
