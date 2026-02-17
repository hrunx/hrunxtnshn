"""
API Request/Response Models
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ActionType(str, Enum):
    """Action type enum"""
    LOAD_PAGE = "LOAD_PAGE"
    FETCH = "FETCH"
    EXTRACT_LINKEDIN = "EXTRACT_LINKEDIN"
    EXTRACT_INSTAGRAM = "EXTRACT_INSTAGRAM"
    EXTRACT_MAPS = "EXTRACT_MAPS"
    WAIT = "WAIT"
    NAVIGATE = "NAVIGATE"


class Action(BaseModel):
    """Action model"""
    action: ActionType
    url: Optional[str] = None
    duration: Optional[int] = None
    params: Optional[Dict[str, Any]] = None


class TaskRequest(BaseModel):
    """Task request model"""
    prompt: Optional[str] = None
    description: Optional[str] = None
    action: Optional[ActionType] = None
    actions: Optional[List[Action]] = None
    url: Optional[str] = None
    needsPlanning: bool = False
    metadata: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    """Task response model"""
    task_id: str
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    plan: Optional[List[Action]] = None
    metadata: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str = "1.0.0"
    agent_ready: bool


class StreamEvent(BaseModel):
    """Stream event model"""
    type: str  # "plan", "action", "result", "error"
    data: Any
    timestamp: str
