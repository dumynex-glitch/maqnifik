"""Gallery routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.database import get_db
from app.schemas import GalleryItemResponse, GalleryUpdateRequest
from app.services.gallery_service import GalleryService
from app.services.logger_service import logger

router = APIRouter(prefix="/api/gallery", tags=["gallery"])


@router.get("", response_model=List[GalleryItemResponse])
async def get_gallery(
    type: Optional[str] = None,
    favorited: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get gallery items with optional filters"""
    
    gallery_service = GalleryService(db)
    items = await gallery_service.get_items(type, favorited, limit, offset)
    
    return [GalleryItemResponse.model_validate(item) for item in items]


@router.post("/{item_id}/favorite")
async def toggle_favorite(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Toggle favorite status of gallery item"""
    
    gallery_service = GalleryService(db)
    favorited = await gallery_service.toggle_favorite(item_id)
    
    if favorited is False and favorited is not None:
        return {"favorited": favorited}
    elif favorited is True:
        return {"favorited": favorited}
    else:
        raise HTTPException(404, "Gallery item not found")


@router.patch("/{item_id}")
async def update_gallery_item(
    item_id: int,
    update: GalleryUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update gallery item"""
    
    gallery_service = GalleryService(db)
    
    await gallery_service.update_item(
        item_id=item_id,
        title=update.title,
        tags=update.tags
    )
    
    item = await gallery_service.get_item(item_id)
    
    if not item:
        raise HTTPException(404, "Gallery item not found")
    
    return GalleryItemResponse.model_validate(item)


@router.delete("/{item_id}")
async def delete_gallery_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete gallery item"""
    
    gallery_service = GalleryService(db)
    await gallery_service.delete_item(item_id)
    
    logger.info("Gallery item deleted via API", item_id=item_id)
    
    return {"status": "deleted", "item_id": item_id}
