"""Task routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from app.database import get_db
from app.models import ApiKey
from app.schemas import TaskResponse
from app.services.task_manager import TaskManager
from app.services.gallery_service import GalleryService
from app.services.magnific_client import magnific_client
from app.services.logger_service import logger

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


@router.post("/{task_id}/check-status", response_model=TaskResponse)
async def check_task_status(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Check task status from Magnific API and update local record"""
    
    task_manager = TaskManager(db)
    task = await task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(404, f"Task not found: {task_id}")
    
    # Get the API key used for this task
    result = await db.execute(
        select(ApiKey).where(ApiKey.key_hash == task.api_key_hash)
    )
    api_key_record = result.scalar_one_or_none()
    
    if not api_key_record or not api_key_record.key_value:
        raise HTTPException(400, "API key not found for this task")
    
    api_key = api_key_record.key_value
    service = task.service
    
    try:
        # Call Magnific task status API
        response = await magnific_client.get_task_status(
            api_key=api_key,
            service=service,
            task_id=task_id
        )
        
        # Extract status from response
        payload = response.get("data", response)
        remote_status = payload.get("status", "").lower()
        result_url = payload.get("generated", [None])[0] if isinstance(payload.get("generated"), list) else payload.get("result_url")
        error_message = payload.get("error") or payload.get("error_message")
        
        # Map Magnific status to our status
        status_map = {
            "created": "pending",
            "in_progress": "running",
            "completed": "completed",
            "failed": "failed",
        }
        local_status = status_map.get(remote_status, "pending")
        
        # Update task
        await task_manager.update_task(
            task_id=task_id,
            status=local_status,
            result_url=result_url,
            error_message=error_message
        )
        
        logger.info(
            "Task status checked via API",
            task_id=task_id,
            status=remote_status
        )
        
        # Add to gallery if completed
        if local_status == "completed" and result_url:
            gallery_service = GalleryService(db)
            await gallery_service.add_from_task(task_id)
        
        # Refresh task from DB
        task = await task_manager.get_task(task_id)
        return TaskResponse.model_validate(task)
        
    except Exception as e:
        logger.error("Failed to check task status", task_id=task_id, error=str(e))
        raise HTTPException(500, f"Failed to check task status: {str(e)}")
