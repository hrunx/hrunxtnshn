"""
Invisible Browser Service - Orchestrator-driven invisible browsing
Controls extension to perform invisible background browsing tasks
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class BrowsingTask:
    """Represents a single browsing task"""
    
    def __init__(
        self,
        task_id: str,
        url: str,
        action: str,
        params: Optional[Dict] = None
    ):
        self.task_id = task_id
        self.url = url
        self.action = action
        self.params = params or {}
        self.status = "pending"
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "url": self.url,
            "action": self.action,
            "params": self.params,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class InvisibleBrowser:
    """Manages invisible browsing tasks through extension"""
    
    def __init__(self, extension_bridge, session_manager):
        self.extension_bridge = extension_bridge
        self.session_manager = session_manager
        self.tasks: Dict[str, BrowsingTask] = {}
        self.active_tasks: List[str] = []
        self.max_concurrent = 5
        logger.info("Invisible browser initialized")
    
    async def browse_and_extract(
        self,
        url: str,
        extraction_type: str,
        params: Optional[Dict] = None,
        use_session: bool = True
    ) -> Dict:
        """
        Browse to URL invisibly and extract data
        
        Args:
            url: URL to browse
            extraction_type: Type of extraction (company_employees, profile, etc.)
            params: Additional parameters
            use_session: Whether to use saved session cookies
        
        Returns:
            Extraction result
        """
        task_id = str(uuid.uuid4())
        task = BrowsingTask(task_id, url, extraction_type, params)
        self.tasks[task_id] = task
        
        logger.info(f"Starting invisible browsing task: {task_id} - {url}")
        
        try:
            # Prepare command for extension
            command = {
                "task_id": task_id,
                "action": "INVISIBLE_BROWSE",
                "url": url,
                "extraction_type": extraction_type,
                "params": params or {},
                "use_session": use_session
            }
            
            # Add session cookies if available
            if use_session and "linkedin.com" in url:
                cookies = self.session_manager.get_session_cookies("linkedin")
                if cookies:
                    command["cookies"] = cookies
                    logger.info(f"Using LinkedIn session for task {task_id}")
            
            # Send to extension
            task.status = "running"
            task.started_at = datetime.now()
            self.active_tasks.append(task_id)
            
            result = await self.extension_bridge.send_command(command)
            
            # Process result
            if result.get("success"):
                task.status = "completed"
                task.result = result.get("data")
                logger.info(f"Task {task_id} completed successfully")
            else:
                task.status = "failed"
                task.error = result.get("error", "Unknown error")
                logger.error(f"Task {task_id} failed: {task.error}")
            
            task.completed_at = datetime.now()
            self.active_tasks.remove(task_id)
            
            return task.to_dict()
        
        except Exception as e:
            logger.error(f"Error in browsing task {task_id}: {e}")
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.now()
            
            if task_id in self.active_tasks:
                self.active_tasks.remove(task_id)
            
            return task.to_dict()
    
    async def extract_company_employees(
        self,
        company_url: str,
        max_pages: int = 6
    ) -> Dict:
        """
        Extract employees from LinkedIn company page
        
        Args:
            company_url: LinkedIn company URL
            max_pages: Maximum pages to scrape
        
        Returns:
            Employee data
        """
        # Ensure we have people page URL
        if not company_url.endswith("/people/"):
            company_url = company_url.rstrip("/") + "/people/"
        
        logger.info(f"Extracting employees from: {company_url}")
        
        result = await self.browse_and_extract(
            url=company_url,
            extraction_type="company_employees",
            params={"max_pages": max_pages},
            use_session=True
        )
        
        return result
    
    async def extract_multiple_companies(
        self,
        company_urls: List[str],
        max_pages: int = 3
    ) -> List[Dict]:
        """
        Extract employees from multiple companies in parallel
        
        Args:
            company_urls: List of LinkedIn company URLs
            max_pages: Maximum pages per company
        
        Returns:
            List of extraction results
        """
        logger.info(f"Extracting from {len(company_urls)} companies in parallel")
        
        # Create tasks
        tasks = [
            self.extract_company_employees(url, max_pages)
            for url in company_urls
        ]
        
        # Execute in parallel with concurrency limit
        results = []
        for i in range(0, len(tasks), self.max_concurrent):
            batch = tasks[i:i + self.max_concurrent]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)
        
        logger.info(f"Completed extraction from {len(company_urls)} companies")
        
        return results
    
    async def search_and_extract_companies(
        self,
        company_names: List[str],
        searxng_client,
        max_pages: int = 3
    ) -> Dict[str, Dict]:
        """
        Search for companies and extract employee data
        
        Args:
            company_names: List of company names to search
            searxng_client: SearXNG client instance
            max_pages: Maximum pages per company
        
        Returns:
            Dictionary mapping company names to extraction results
        """
        logger.info(f"Searching and extracting {len(company_names)} companies")
        
        # Step 1: Search for LinkedIn URLs
        logger.info("Step 1: Searching for LinkedIn company URLs...")
        company_urls = await searxng_client.search_multiple_companies(company_names)
        
        # Filter out companies not found
        found_companies = {
            name: url
            for name, url in company_urls.items()
            if url is not None
        }
        
        logger.info(f"Found {len(found_companies)} company URLs")
        
        # Step 2: Extract employees from found companies
        logger.info("Step 2: Extracting employee data...")
        extraction_results = await self.extract_multiple_companies(
            list(found_companies.values()),
            max_pages
        )
        
        # Step 3: Map results back to company names
        results = {}
        for company_name, company_url in found_companies.items():
            # Find matching result
            for result in extraction_results:
                if isinstance(result, dict) and result.get("url") == company_url:
                    results[company_name] = result
                    break
        
        logger.info(f"Extraction complete for {len(results)} companies")
        
        return results
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a specific task"""
        task = self.tasks.get(task_id)
        return task.to_dict() if task else None
    
    def get_active_tasks(self) -> List[Dict]:
        """Get all active tasks"""
        return [
            self.tasks[task_id].to_dict()
            for task_id in self.active_tasks
            if task_id in self.tasks
        ]
    
    def get_all_tasks(self) -> List[Dict]:
        """Get all tasks"""
        return [task.to_dict() for task in self.tasks.values()]
