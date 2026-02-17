"""
Main FastAPI Application
"""

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import settings
from api.routes import router
from agent.graph import BrowsingAgent
from services.extension_bridge import extension_bridge
from services.task_queue import task_queue


# Create FastAPI app
app = FastAPI(
    title="hrunxtnshn Orchestrator",
    description="Autonomous browsing orchestrator backend",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Global agent instance
agent: BrowsingAgent = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global agent
    
    print("Starting hrunxtnshn orchestrator...")
    print(f"OpenAI Model: {settings.openai_model}")
    print(f"Server: {settings.host}:{settings.port}")
    
    # Initialize agent
    agent = BrowsingAgent(extension_bridge)
    print("Agent initialized")
    
    # Start task queue processor
    asyncio.create_task(task_queue.process_queue(agent))
    print("Task queue processor started")
    
    print("Orchestrator ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down orchestrator...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "hrunxtnshn Orchestrator",
        "version": "1.0.0",
        "status": "running",
        "extension_connected": extension_bridge.is_connected()
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
