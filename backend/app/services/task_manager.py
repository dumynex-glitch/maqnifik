"""Task manager service for task lifecycle management"""
import json
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Task
from app.services.logger_service import logger


class TaskManager:
    """Manage task lifecycle"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_task(
        self,
        task_id: str,
        service: str,
        type: str,
        api_key_hash: str,
        request_params: dict
    ) -> Task:
        """Create new task"""
        task = Task(
            task_id=task_id,
            service=service,
            type=type,
            status="pending",
            api_key_hash=api_key_hash,
            request_params=json.dumps(request_params)
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        logger.info(
            "Task created",
            task_id=task_id,
            service=service,
            type=type
        )
        
        return task
    
    async def update_task(
        self,
        task_id: str,
        status: Optional[str] = None,
        result_url: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Update task status and results"""
        result = await self.db.execute(
            select(Task).where(Task.task_id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if not task:
            logger.warning("Task not found for update", task_id=task_id)
            return
        
        if status:
            task.status = status
        
        if result_url:
            task.result_url = result_url
        
        if thumbnail_url:
            task.thumbnail_url = thumbnail_url
        
        if error_message:
            task.error_message = error_message
        
        if status == "completed":
            task.completed_at = datetime.utcnow()
        
        task.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        logger.info(
            "Task updated",
            task_id=task_id,
            status=status
        )
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        result = await self.db.execute(
            select(Task).where(Task.task_id == task_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_tasks(
        self,
        status: Optional[str] = None,
        type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """Get all tasks with optional filters"""
        query = select(Task)
        
        if status:
            query = query.where(Task.status == status)
        
        if type:
            query = query.where(Task.type == type)
        
        query = query.order_by(Task.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_recent_tasks(self, limit: int = 10) -> List[Task]:
        """Get recent tasks"""
        result = await self.db.execute(
            select(Task)
            .order_by(Task.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_task_counts(self) -> dict:
        """Get task counts by status"""
        result = await self.db.execute(
            select(
                Task.status,
                func.count(Task.id).label('count')
            ).group_by(Task.status)
        )
        
        counts = {
            "total": 0,
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0
        }
        
        for row in result:
            status, count = row
            counts[status] = count
            counts["total"] += count
        
        return counts
    
    async def get_tasks_today(self) -> int:
        """Get count of tasks created today"""
        from datetime import date
        today = date.today()
        
        result = await self.db.execute(
            select(func.count(Task.id))
            .where(func.date(Task.created_at) == today)
        )
        
        return result.scalar() or 0
    
    async def get_tasks_this_week(self) -> int:
        """Get count of tasks created this week"""
        from datetime import date, timedelta
        today = date.today()
        week_ago = today - timedelta(days=7)
        
        result = await self.db.execute(
            select(func.count(Task.id))
            .where(Task.created_at >= week_ago)
        )
        
        return result.scalar() or 0
