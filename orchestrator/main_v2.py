"""
hrunxtnshn Orchestrator V2 - Orchestrator-driven invisible browsing
Main application with SearXNG integration and session management
"""

import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List, Optional

from services.extension_bridge_v2 import ExtensionBridge, websocket_endpoint
from services.session_manager import SessionManager, BrowserSessionBridge
from services.searxng_client import SearXNGClient
from services.invisible_browser import InvisibleBrowser
from config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
extension_bridge = ExtensionBridge()
session_manager = SessionManager()
session_bridge = BrowserSessionBridge(session_manager)
searxng_client = None
invisible_browser = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global searxng_client, invisible_browser
    
    logger.info("=" * 60)
    logger.info("Starting hrunxtnshn Orchestrator V2")
    logger.info("=" * 60)
    
    # Initialize SearXNG client
    searxng_url = settings.SEARXNG_URL
    searxng_client = SearXNGClient(searxng_url)
    logger.info(f"SearXNG: {searxng_url}")
    
    # Initialize invisible browser
    invisible_browser = InvisibleBrowser(extension_bridge, session_manager)
    logger.info("Invisible browser initialized")
    
    # Check session status
    session_status = session_manager.get_session_status()
    if session_status:
        logger.info(f"Active sessions: {list(session_status.keys())}")
    else:
        logger.info("No active sessions")
    
    logger.info("=" * 60)
    logger.info(f"Server: {settings.HOST}:{settings.PORT}")
    logger.info(f"WebSocket: ws://{settings.HOST}:{settings.PORT}/ws")
    logger.info("Orchestrator ready!")
    logger.info("=" * 60)
    
    yield
    
    # Cleanup
    logger.info("Shutting down orchestrator...")
    await searxng_client.close()
    logger.info("Orchestrator stopped")


# Create FastAPI app
app = FastAPI(
    title="hrunxtnshn Orchestrator",
    description="Orchestrator-driven invisible browsing system",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws")
async def websocket_handler(websocket: WebSocket):
    """WebSocket endpoint for extension communication"""
    await websocket.accept()
    await websocket_endpoint(websocket, extension_bridge)


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "extension_connected": extension_bridge.is_connected(),
        "connections": extension_bridge.get_connection_count(),
        "sessions": list(session_manager.get_session_status().keys())
    }


@app.get("/status")
async def get_status():
    """Get orchestrator status"""
    return {
        "orchestrator": "running",
        "extension_connected": extension_bridge.is_connected(),
        "connection_count": extension_bridge.get_connection_count(),
        "connection_ids": extension_bridge.get_connection_ids(),
        "sessions": session_manager.get_session_status(),
        "active_tasks": invisible_browser.get_active_tasks() if invisible_browser else [],
        "searxng_url": settings.SEARXNG_URL
    }


@app.post("/search/company")
async def search_company(company_name: str):
    """
    Search for company LinkedIn URL
    
    Args:
        company_name: Company name to search
    
    Returns:
        LinkedIn company URL
    """
    if not searxng_client:
        raise HTTPException(500, "SearXNG client not initialized")
    
    url = await searxng_client.search_linkedin_company(company_name)
    
    if not url:
        raise HTTPException(404, f"LinkedIn company not found: {company_name}")
    
    return {"company_name": company_name, "linkedin_url": url}


@app.post("/extract/company")
async def extract_company_employees(
    company_name: Optional[str] = None,
    company_url: Optional[str] = None,
    max_pages: int = 6
):
    """
    Extract employees from LinkedIn company
    
    Args:
        company_name: Company name (will search for URL)
        company_url: Direct LinkedIn company URL
        max_pages: Maximum pages to scrape
    
    Returns:
        Employee extraction results
    """
    if not invisible_browser:
        raise HTTPException(500, "Invisible browser not initialized")
    
    if not extension_bridge.is_connected():
        raise HTTPException(503, "No extension connected")
    
    # Ensure LinkedIn session
    has_session = await session_bridge.ensure_linkedin_session(extension_bridge)
    if not has_session:
        return {
            "status": "waiting_for_login",
            "message": "Please log in to LinkedIn in your browser",
            "action": "open_linkedin_login"
        }
    
    # Get company URL if name provided
    if company_name and not company_url:
        logger.info(f"Searching for company: {company_name}")
        company_url = await searxng_client.search_linkedin_company(company_name)
        
        if not company_url:
            raise HTTPException(404, f"Company not found: {company_name}")
    
    if not company_url:
        raise HTTPException(400, "Either company_name or company_url required")
    
    # Extract employees
    logger.info(f"Extracting employees from: {company_url}")
    result = await invisible_browser.extract_company_employees(company_url, max_pages)
    
    return result


@app.post("/extract/multiple")
async def extract_multiple_companies(
    company_names: List[str],
    max_pages: int = 3
):
    """
    Extract employees from multiple companies
    
    Args:
        company_names: List of company names
        max_pages: Maximum pages per company
    
    Returns:
        Dictionary of extraction results
    """
    if not invisible_browser:
        raise HTTPException(500, "Invisible browser not initialized")
    
    if not extension_bridge.is_connected():
        raise HTTPException(503, "No extension connected")
    
    # Ensure LinkedIn session
    has_session = await session_bridge.ensure_linkedin_session(extension_bridge)
    if not has_session:
        return {
            "status": "waiting_for_login",
            "message": "Please log in to LinkedIn in your browser"
        }
    
    # Search and extract
    logger.info(f"Extracting from {len(company_names)} companies")
    results = await invisible_browser.search_and_extract_companies(
        company_names,
        searxng_client,
        max_pages
    )
    
    return {
        "total_companies": len(company_names),
        "extracted_companies": len(results),
        "results": results
    }


@app.get("/tasks")
async def get_tasks():
    """Get all browsing tasks"""
    if not invisible_browser:
        return {"tasks": []}
    
    return {
        "active_tasks": invisible_browser.get_active_tasks(),
        "all_tasks": invisible_browser.get_all_tasks()
    }


@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status of specific task"""
    if not invisible_browser:
        raise HTTPException(404, "Task not found")
    
    task = invisible_browser.get_task_status(task_id)
    
    if not task:
        raise HTTPException(404, "Task not found")
    
    return task


@app.post("/session/clear")
async def clear_session(platform: str = "linkedin"):
    """Clear saved session"""
    if platform == "linkedin":
        session_manager.clear_linkedin_session()
    
    return {"success": True, "platform": platform}


@app.get("/sessions")
async def get_sessions():
    """Get all session statuses"""
    return session_manager.get_session_status()


# ============================================================================
# Event Handlers
# ============================================================================

async def handle_session_captured(data: dict):
    """Handle session captured event from extension"""
    logger.info("Session captured from extension")
    await session_bridge.handle_session_captured(
        platform=data.get("platform"),
        cookies=data.get("cookies"),
        user_id=data.get("user_id", "default")
    )

# Register event handlers
extension_bridge.on_event("session_captured", handle_session_captured)


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main_v2:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
