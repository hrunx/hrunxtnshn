"""
Agent State Management
"""

from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph


class AgentState(TypedDict):
    """Agent state structure"""
    
    # Input
    task: str
    task_type: Optional[str]
    
    # Planning
    plan: List[Dict[str, Any]]
    current_step: int
    
    # Execution
    actions_executed: List[Dict[str, Any]]
    results: List[Any]
    
    # Context
    context: Dict[str, Any]
    
    # Output
    final_result: Optional[Any]
    error: Optional[str]
    
    # Metadata
    metadata: Dict[str, Any]
