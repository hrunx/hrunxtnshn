"""
Task Queue Service
Manages task execution queue
"""

import asyncio
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
from api.models import TaskStatus


class Task:
    """Task object"""
    
    def __init__(self, task_id: str, request: Dict[str, Any]):
        self.task_id = task_id
        self.request = request
        self.status = TaskStatus.PENDING
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None


class TaskQueue:
    """Task queue manager"""
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.tasks: Dict[str, Task] = {}
        self.queue: asyncio.Queue = asyncio.Queue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
    
    def create_task(self, request: Dict[str, Any]) -> str:
        """
        Create a new task
        
        Args:
            request: Task request
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        task = Task(task_id, request)
        self.tasks[task_id] = task
        return task_id
    
    async def enqueue_task(self, task_id: str):
        """
        Add task to queue
        
        Args:
            task_id: Task ID
        """
        await self.queue.put(task_id)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get task by ID
        
        Args:
            task_id: Task ID
            
        Returns:
            Task object or None
        """
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskStatus):
        """
        Update task status
        
        Args:
            task_id: Task ID
            status: New status
        """
        task = self.tasks.get(task_id)
        if task:
            task.status = status
            if status == TaskStatus.RUNNING:
                task.started_at = datetime.now()
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                task.completed_at = datetime.now()
    
    def set_task_result(self, task_id: str, result: Any):
        """
        Set task result
        
        Args:
            task_id: Task ID
            result: Task result
        """
        task = self.tasks.get(task_id)
        if task:
            task.result = result
            self.update_task_status(task_id, TaskStatus.COMPLETED)
    
    def set_task_error(self, task_id: str, error: str):
        """
        Set task error
        
        Args:
            task_id: Task ID
            error: Error message
        """
        task = self.tasks.get(task_id)
        if task:
            task.error = error
            self.update_task_status(task_id, TaskStatus.FAILED)
    
    async def process_queue(self, agent):
        """
        Process task queue
        
        Args:
            agent: BrowsingAgent instance
        """
        while True:
            # Wait for task
            task_id = await self.queue.get()
            
            # Wait if at max concurrent tasks
            while len(self.running_tasks) >= self.max_concurrent:
                await asyncio.sleep(0.1)
            
            # Start task
            task = self.get_task(task_id)
            if task:
                self.update_task_status(task_id, TaskStatus.RUNNING)
                
                # Create async task
                async_task = asyncio.create_task(
                    self._execute_task(task_id, task, agent)
                )
                self.running_tasks[task_id] = async_task
    
    async def _execute_task(self, task_id: str, task: Task, agent):
        """
        Execute a task
        
        Args:
            task_id: Task ID
            task: Task object
            agent: BrowsingAgent instance
        """
        try:
            # Get task prompt
            prompt = task.request.get("prompt") or task.request.get("description")
            
            # Execute with agent
            result = await agent.execute_task(
                task=prompt,
                metadata=task.request.get("metadata")
            )
            
            # Set result
            self.set_task_result(task_id, result)
            
        except Exception as e:
            # Set error
            self.set_task_error(task_id, str(e))
        
        finally:
            # Remove from running tasks
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]


# Global task queue instance
task_queue = TaskQueue()
