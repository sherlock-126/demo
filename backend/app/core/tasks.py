"""Background task management for async operations"""

import asyncio
import uuid
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    """Represents a background task"""

    def __init__(self, task_id: str, task_type: str):
        self.id = task_id
        self.type = task_type
        self.status = TaskStatus.PENDING
        self.progress = 0
        self.result = None
        self.error = None
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.metadata = {}

    def start(self):
        """Mark task as started"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()

    def update_progress(self, progress: int):
        """Update task progress"""
        self.progress = min(100, max(0, progress))

    def complete(self, result: Any = None):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.progress = 100
        self.result = result
        self.completed_at = datetime.utcnow()

    def fail(self, error: str):
        """Mark task as failed"""
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "id": self.id,
            "type": self.type,
            "status": self.status,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata
        }


class TaskManager:
    """Manages background tasks"""

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}

    def create_task(self, task_type: str) -> str:
        """Create a new task"""
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = Task(task_id, task_type)
        return task_id

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)

    async def run_task(
        self,
        task_id: str,
        func: Callable,
        *args,
        **kwargs
    ):
        """Run a task asynchronously"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        try:
            task.start()
            result = await func(task, *args, **kwargs)
            task.complete(result)
        except Exception as e:
            task.fail(str(e))
            raise

    def cancel_task(self, task_id: str):
        """Cancel a running task"""
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            task = self.get_task(task_id)
            if task:
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.utcnow()


# Global task manager instance
task_manager = TaskManager()