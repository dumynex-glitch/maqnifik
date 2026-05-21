"""Image editing routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Config as ConfigModel
from app.schemas import ImageEditRequest, ImageEditResponse
from app.services.magnific_client import magnific_client
from app.services.key_rotation import KeyRotationService
from app.services.quota_manager import QuotaManager, QuotaExhaustedError
from app.services.task_manager import TaskManager
from app.services.logger_service import logger

router = APIRouter(prefix="/api/editing", tags=["editing"])


@router.post("/upscale", response_model=ImageEditResponse)
async def upscale_image(
    request: ImageEditRequest,
    db: AsyncSession = Depends(get_db)
):
    """Upscale image using Magnific upscaler"""
    
    service = "upscaler-precision-v2"
    
    logger.info("Image upscale requested", image_url=request.image_url[:100])
    
    # Get webhook URL
    result = await db.execute(
        select(ConfigModel).where(ConfigModel.key == "webhook_url")
    )
    webhook_config = result.scalar_one_or_none()
    
    if not webhook_config or not webhook_config.value:
        raise HTTPException(400, "Webhook URL not configured")
    
    webhook_url = webhook_config.value
    
    # Initialize services
    key_rotation = KeyRotationService(db)
    quota_manager = QuotaManager(db)
    task_manager = TaskManager(db)
    
    try:
        await key_rotation.load_keys()
        api_key, key_hash = await key_rotation.get_next_available_key(service)
        
        response = await magnific_client.upscale_image(
            api_key=api_key,
            image_url=request.image_url,
            webhook_url=webhook_url,
            service=service
        )
        
        await quota_manager.increment_quota(key_hash, service)
        
        task = await task_manager.create_task(
            task_id=response.get("task_id") or response.get("id"),
            service=service,
            type="editing",
            api_key_hash=key_hash,
            request_params={"image_url": request.image_url, "operation": "upscale"}
        )
        
        logger.info("Upscale task created", task_id=task.task_id)
        
        return ImageEditResponse(
            task_id=task.task_id,
            status="pending",
            message="Image upscaling started"
        )
        
    except QuotaExhaustedError as e:
        raise HTTPException(429, detail=str(e))
    except Exception as e:
        logger.error("Upscale failed", error=str(e))
        raise HTTPException(500, detail=str(e))


@router.post("/remove-background", response_model=ImageEditResponse)
async def remove_background(
    request: ImageEditRequest,
    db: AsyncSession = Depends(get_db)
):
    """Remove background from image"""
    
    service = "remove-background"
    
    logger.info("Background removal requested")
    
    result = await db.execute(
        select(ConfigModel).where(ConfigModel.key == "webhook_url")
    )
    webhook_config = result.scalar_one_or_none()
    
    if not webhook_config or not webhook_config.value:
        raise HTTPException(400, "Webhook URL not configured")
    
    webhook_url = webhook_config.value
    
    key_rotation = KeyRotationService(db)
    quota_manager = QuotaManager(db)
    task_manager = TaskManager(db)
    
    try:
        await key_rotation.load_keys()
        api_key, key_hash = await key_rotation.get_next_available_key(service)
        
        response = await magnific_client.remove_background(
            api_key=api_key,
            image_url=request.image_url,
            webhook_url=webhook_url
        )
        
        await quota_manager.increment_quota(key_hash, service)
        
        task = await task_manager.create_task(
            task_id=response.get("task_id") or response.get("id"),
            service=service,
            type="editing",
            api_key_hash=key_hash,
            request_params={"image_url": request.image_url, "operation": "remove-background"}
        )
        
        return ImageEditResponse(
            task_id=task.task_id,
            status="pending",
            message="Background removal started"
        )
        
    except QuotaExhaustedError as e:
        raise HTTPException(429, detail=str(e))
    except Exception as e:
        logger.error("Background removal failed", error=str(e))
        raise HTTPException(500, detail=str(e))


@router.post("/relight", response_model=ImageEditResponse)
async def relight_image(
    request: ImageEditRequest,
    db: AsyncSession = Depends(get_db)
):
    """Relight image"""
    
    service = "relight"
    
    logger.info("Image relight requested")
    
    result = await db.execute(
        select(ConfigModel).where(ConfigModel.key == "webhook_url")
    )
    webhook_config = result.scalar_one_or_none()
    
    if not webhook_config or not webhook_config.value:
        raise HTTPException(400, "Webhook URL not configured")
    
    webhook_url = webhook_config.value
    
    key_rotation = KeyRotationService(db)
    quota_manager = QuotaManager(db)
    task_manager = TaskManager(db)
    
    try:
        await key_rotation.load_keys()
        api_key, key_hash = await key_rotation.get_next_available_key(service)
        
        response = await magnific_client.relight_image(
            api_key=api_key,
            image_url=request.image_url,
            webhook_url=webhook_url
        )
        
        await quota_manager.increment_quota(key_hash, service)
        
        task = await task_manager.create_task(
            task_id=response.get("task_id") or response.get("id"),
            service=service,
            type="editing",
            api_key_hash=key_hash,
            request_params={"image_url": request.image_url, "operation": "relight"}
        )
        
        return ImageEditResponse(
            task_id=task.task_id,
            status="pending",
            message="Image relighting started"
        )
        
    except QuotaExhaustedError as e:
        raise HTTPException(429, detail=str(e))
    except Exception as e:
        logger.error("Relight failed", error=str(e))
        raise HTTPException(500, detail=str(e))


@router.post("/style-transfer", response_model=ImageEditResponse)
async def style_transfer(
    image_url: str,
    style_image_url: str,
    db: AsyncSession = Depends(get_db)
):
    """Apply style transfer"""
    
    service = "style-transfer"
    
    logger.info("Style transfer requested")
    
    result = await db.execute(
        select(ConfigModel).where(ConfigModel.key == "webhook_url")
    )
    webhook_config = result.scalar_one_or_none()
    
    if not webhook_config or not webhook_config.value:
        raise HTTPException(400, "Webhook URL not configured")
    
    webhook_url = webhook_config.value
    
    key_rotation = KeyRotationService(db)
    quota_manager = QuotaManager(db)
    task_manager = TaskManager(db)
    
    try:
        await key_rotation.load_keys()
        api_key, key_hash = await key_rotation.get_next_available_key(service)
        
        response = await magnific_client.style_transfer(
            api_key=api_key,
            image_url=image_url,
            style_image_url=style_image_url,
            webhook_url=webhook_url
        )
        
        await quota_manager.increment_quota(key_hash, service)
        
        task = await task_manager.create_task(
            task_id=response.get("task_id") or response.get("id"),
            service=service,
            type="editing",
            api_key_hash=key_hash,
            request_params={
                "image_url": image_url,
                "style_image_url": style_image_url,
                "operation": "style-transfer"
            }
        )
        
        return ImageEditResponse(
            task_id=task.task_id,
            status="pending",
            message="Style transfer started"
        )
        
    except QuotaExhaustedError as e:
        raise HTTPException(429, detail=str(e))
    except Exception as e:
        logger.error("Style transfer failed", error=str(e))
        raise HTTPException(500, detail=str(e))
