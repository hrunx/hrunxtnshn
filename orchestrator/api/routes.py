"""
API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse
from typing import Optional
import json
from datetime import datetime

from .models import (
    TaskRequest, TaskResponse, HealthResponse, 
    TaskStatus, StreamEvent
)
from services.task_queue import task_queue
from services.extension_bridge import extension_bridge
from config import settings


router = APIRouter()


def verify_api_key(authorization: Optional[str] = Header(None)):
    """Verify API key if configured"""
    if settings.api_key:
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing authorization header")
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        token = authorization.replace("Bearer ", "")
        if token != settings.api_key:
            raise HTTPException(status_code=401, detail="Invalid API key")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        agent_ready=extension_bridge.is_connected()
    )


@router.post("/api/tasks", response_model=TaskResponse, dependencies=[Depends(verify_api_key)])
async def create_task(request: TaskRequest):
    """
    Create and execute a task
    
    Args:
        request: Task request
        
    Returns:
        Task response
    """
    # Create task
    task_id = task_queue.create_task(request.dict())
    
    # Enqueue task
    await task_queue.enqueue_task(task_id)
    
    # Wait for task completion (with timeout)
    max_wait = 60  # seconds
    waited = 0
    
    while waited < max_wait:
        task = task_queue.get_task(task_id)
        if task and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            return TaskResponse(
                task_id=task_id,
                status=task.status,
                result=task.result,
                error=task.error,
                plan=task.result.get("plan") if task.result else None,
                metadata=request.metadata
            )
        
        await asyncio.sleep(0.5)
        waited += 0.5
    
    # Timeout
    return TaskResponse(
        task_id=task_id,
        status=TaskStatus.RUNNING,
        error="Task is still running (timeout reached)",
        metadata=request.metadata
    )


@router.get("/api/tasks/{task_id}", response_model=TaskResponse, dependencies=[Depends(verify_api_key)])
async def get_task(task_id: str):
    """
    Get task status and result
    
    Args:
        task_id: Task ID
        
    Returns:
        Task response
    """
    task = task_queue.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(
        task_id=task_id,
        status=task.status,
        result=task.result,
        error=task.error,
        plan=task.result.get("plan") if task.result else None
    )


@router.post("/api/tasks/stream", dependencies=[Depends(verify_api_key)])
async def stream_task(request: TaskRequest):
    """
    Stream task execution
    
    Args:
        request: Task request
        
    Returns:
        Server-sent events stream
    """
    async def event_generator():
        # Create task
        task_id = task_queue.create_task(request.dict())
        
        # Send initial event
        yield f"data: {json.dumps({'type': 'start', 'task_id': task_id, 'timestamp': datetime.now().isoformat()})}\n\n"
        
        # Enqueue task
        await task_queue.enqueue_task(task_id)
        
        # Stream updates
        max_wait = 60
        waited = 0
        
        while waited < max_wait:
            task = task_queue.get_task(task_id)
            
            if task:
                if task.status == TaskStatus.COMPLETED:
                    yield f"data: {json.dumps({'type': 'result', 'data': task.result, 'timestamp': datetime.now().isoformat()})}\n\n"
                    break
                elif task.status == TaskStatus.FAILED:
                    yield f"data: {json.dumps({'type': 'error', 'data': task.error, 'timestamp': datetime.now().isoformat()})}\n\n"
                    break
                else:
                    yield f"data: {json.dumps({'type': 'status', 'data': task.status, 'timestamp': datetime.now().isoformat()})}\n\n"
            
            await asyncio.sleep(1)
            waited += 1
        
        # Send end event
        yield f"data: {json.dumps({'type': 'end', 'timestamp': datetime.now().isoformat()})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@router.post("/api/extension/register")
async def register_extension(extension_id: str):
    """
    Register browser extension
    
    Args:
        extension_id: Extension ID
    """
    extension_bridge.register_extension(extension_id)
    return {"ok": True}


@router.post("/api/extension/unregister")
async def unregister_extension():
    """Unregister browser extension"""
    extension_bridge.unregister_extension()
    return {"ok": True}


@router.post("/api/extension/response")
async def extension_response(request_id: str, response: dict):
    """
    Receive response from extension
    
    Args:
        request_id: Request ID
        response: Response data
    """
    extension_bridge.receive_response(request_id, response)
    return {"ok": True}


import asyncio
