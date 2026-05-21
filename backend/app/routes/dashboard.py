"""Dashboard statistics route"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date, timedelta

from app.database import get_db
from app.models import Task, Gallery, ApiKey, QuotaUsage
from app.schemas import DashboardStats, QuotaByService, KeyStats, TaskResponse
from app.services.task_manager import TaskManager
from app.services.quota_manager import QuotaManager
from app.services.gallery_service import GalleryService
from app.config import DAILY_LIMITS

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get comprehensive dashboard statistics"""
    
    task_manager = TaskManager(db)
    quota_manager = QuotaManager(db)
    gallery_service = GalleryService(db)
    
    # Get task counts
    task_counts = await task_manager.get_task_counts()
    
    # Get tasks today and this week
    tasks_today = await task_manager.get_tasks_today()
    tasks_this_week = await task_manager.get_tasks_this_week()
    
    # Get gallery count
    gallery_count = await gallery_service.get_count()
    
    # Get quota by service
    quota_by_service = await quota_manager.get_quota_by_service()
    
    # Get recent tasks
    recent_tasks = await task_manager.get_recent_tasks(limit=10)
    
    # Get key stats
    result = await db.execute(
        select(ApiKey).where(ApiKey.is_active == True)
    )
    active_keys = result.scalars().all()
    
    key_stats = []
    today = date.today()
    
    for key in active_keys:
        # Count tasks created with this key
        result = await db.execute(
            select(func.count(Task.id))
            .where(Task.api_key_hash == key.key_hash)
        )
        tasks_created = result.scalar() or 0
        
        # Calculate remaining quota (sum across all services)
        result = await db.execute(
            select(QuotaUsage)
            .where(QuotaUsage.api_key_hash == key.key_hash)
            .where(QuotaUsage.date == today)
        )
        usage_records = result.scalars().all()
        
        total_used = sum(record.count for record in usage_records)
        total_limit = sum(DAILY_LIMITS.values())
        quota_remaining = total_limit - total_used
        
        key_stats.append(KeyStats(
            key_masked=key.key_masked,
            tasks_created=tasks_created,
            quota_remaining=quota_remaining
        ))
    
    return DashboardStats(
        total_tasks=task_counts["total"],
        completed_tasks=task_counts["completed"],
        failed_tasks=task_counts["failed"],
        pending_tasks=task_counts["pending"],
        tasks_today=tasks_today,
        tasks_this_week=tasks_this_week,
        gallery_item_count=gallery_count,
        quota_by_service=[QuotaByService(**q) for q in quota_by_service],
        recent_tasks=[TaskResponse.model_validate(t) for t in recent_tasks],
        key_stats=key_stats
    )
