"""
Agent Tools
Tools that the agent can use to interact with the browser extension
"""

from typing import Dict, Any, List
import httpx
import asyncio


class ExtensionTools:
    """Tools for interacting with browser extension"""
    
    def __init__(self, extension_bridge):
        self.bridge = extension_bridge
    
    async def load_page(self, url: str) -> Dict[str, Any]:
        """
        Load a page in the offscreen browser
        
        Args:
            url: URL to load
            
        Returns:
            HTML content of the page
        """
        return await self.bridge.send_action({
            "action": "LOAD_PAGE",
            "url": url
        })
    
    async def fetch_with_session(self, url: str) -> Dict[str, Any]:
        """
        Fetch URL with user session cookies
        
        Args:
            url: URL to fetch
            
        Returns:
            Response data
        """
        return await self.bridge.send_action({
            "action": "FETCH",
            "url": url
        })
    
    async def extract_linkedin(self, url: str) -> Dict[str, Any]:
        """
        Extract LinkedIn profile data
        
        Args:
            url: LinkedIn profile URL
            
        Returns:
            Structured profile data
        """
        return await self.bridge.send_action({
            "action": "EXTRACT_LINKEDIN",
            "url": url
        })
    
    async def extract_instagram(self, url: str) -> Dict[str, Any]:
        """
        Extract Instagram profile data
        
        Args:
            url: Instagram profile URL
            
        Returns:
            Structured profile data
        """
        return await self.bridge.send_action({
            "action": "EXTRACT_INSTAGRAM",
            "url": url
        })
    
    async def extract_maps(self, url: str) -> Dict[str, Any]:
        """
        Extract Google Maps place data
        
        Args:
            url: Google Maps place URL
            
        Returns:
            Structured place data
        """
        return await self.bridge.send_action({
            "action": "EXTRACT_MAPS",
            "url": url
        })
    
    async def wait(self, duration: int = 1000) -> Dict[str, Any]:
        """
        Wait for a specified duration
        
        Args:
            duration: Duration in milliseconds
            
        Returns:
            Success status
        """
        await asyncio.sleep(duration / 1000)
        return {"ok": True}
    
    def get_tool_descriptions(self) -> List[Dict[str, str]]:
        """
        Get descriptions of available tools for LLM
        
        Returns:
            List of tool descriptions
        """
        return [
            {
                "name": "load_page",
                "description": "Load a web page invisibly in the background browser",
                "parameters": {
                    "url": "URL to load"
                }
            },
            {
                "name": "fetch_with_session",
                "description": "Fetch a URL using the user's logged-in session",
                "parameters": {
                    "url": "URL to fetch"
                }
            },
            {
                "name": "extract_linkedin",
                "description": "Extract structured data from a LinkedIn profile page",
                "parameters": {
                    "url": "LinkedIn profile URL (e.g., https://linkedin.com/in/username)"
                }
            },
            {
                "name": "extract_instagram",
                "description": "Extract structured data from an Instagram profile page",
                "parameters": {
                    "url": "Instagram profile URL (e.g., https://instagram.com/username)"
                }
            },
            {
                "name": "extract_maps",
                "description": "Extract structured data from a Google Maps place page",
                "parameters": {
                    "url": "Google Maps place URL"
                }
            },
            {
                "name": "wait",
                "description": "Wait for a specified duration before continuing",
                "parameters": {
                    "duration": "Duration in milliseconds (default: 1000)"
                }
            }
        ]
