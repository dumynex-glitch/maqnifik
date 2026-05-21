"""Task routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.database import get_db
from app.schemas import TaskResponse
from app.services.task_manager import TaskManager

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskResponse])
async def get_all_tasks(
    status: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get all tasks with optional filters"""
    
    task_manager = TaskManager(db)
    tasks = await task_manager.get_all_tasks(status, type, limit, offset)
    
    return [TaskResponse.model_validate(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get task by ID"""
    
    task_manager = TaskManager(db)
    task = await task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(404, f"Task not found: {task_id}")
    
    return TaskResponse.model_validate(task)
