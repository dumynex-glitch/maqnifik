"""Gallery service for managing gallery items"""
import json
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Gallery, Task
from app.services.logger_service import logger


class GalleryService:
    """Manage gallery items"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def add_from_task(self, task_id: str):
        """Automatically add completed task to gallery"""
        # Get task
        result = await self.db.execute(
            select(Task).where(Task.task_id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if not task or task.status != "completed":
            logger.debug("Task not ready for gallery", task_id=task_id)
            return
        
        # Check if already in gallery
        result = await self.db.execute(
            select(Gallery).where(Gallery.task_id == task_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.debug("Task already in gallery", task_id=task_id)
            return
        
        # Extract prompt from request params
        try:
            params = json.loads(task.request_params)
            prompt = params.get("prompt", "")
        except:
            prompt = ""
        
        # Determine type
        type_map = {
            "video": "video",
            "image": "image",
            "audio": "audio",
            "editing": "image"
        }
        item_type = type_map.get(task.type, "image")
        
        # Create gallery item
        gallery_item = Gallery(
            task_id=task_id,
            type=item_type,
            title=prompt[:100] if prompt else f"{task.service} output",
            prompt=prompt,
            result_url=task.result_url,
            thumbnail_url=task.thumbnail_url,
            tags=json.dumps([task.service, task.type])
        )
        
        self.db.add(gallery_item)
        await self.db.commit()
        
        logger.info("Added to gallery", task_id=task_id, type=item_type)
    
    async def get_items(
        self,
        type: Optional[str] = None,
        favorited: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Gallery]:
        """Get gallery items with filters"""
        query = select(Gallery)
        
        if type:
            query = query.where(Gallery.type == type)
        
        if favorited is not None:
            query = query.where(Gallery.favorited == favorited)
        
        query = query.order_by(Gallery.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_item(self, item_id: int) -> Optional[Gallery]:
        """Get gallery item by ID"""
        result = await self.db.execute(
            select(Gallery).where(Gallery.id == item_id)
        )
        return result.scalar_one_or_none()
    
    async def toggle_favorite(self, item_id: int) -> bool:
        """Toggle favorite status"""
        item = await self.get_item(item_id)
        
        if not item:
            return False
        
        item.favorited = not item.favorited
        await self.db.commit()
        
        logger.info(
            "Gallery item favorite toggled",
            item_id=item_id,
            favorited=item.favorited
        )
        
        return item.favorited
    
    async def update_item(
        self,
        item_id: int,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None
    ):
        """Update gallery item"""
        item = await self.get_item(item_id)
        
        if not item:
            return
        
        if title:
            item.title = title
        
        if tags:
            item.tags = json.dumps(tags)
        
        await self.db.commit()
        
        logger.info("Gallery item updated", item_id=item_id)
    
    async def delete_item(self, item_id: int):
        """Delete gallery item"""
        item = await self.get_item(item_id)
        
        if not item:
            return
        
        await self.db.delete(item)
        await self.db.commit()
        
        logger.info("Gallery item deleted", item_id=item_id)
    
    async def get_count(self) -> int:
        """Get total gallery item count"""
        from sqlalchemy import func
        
        result = await self.db.execute(
            select(func.count(Gallery.id))
        )
        
        return result.scalar() or 0
