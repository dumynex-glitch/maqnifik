"""Image generation routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Config as ConfigModel
from app.schemas import ImageGenerateRequest, ImageGenerateResponse
from app.services.magnific_client import magnific_client
from app.services.key_rotation import KeyRotationService
from app.services.quota_manager import QuotaManager, QuotaExhaustedError
from app.services.task_manager import TaskManager
from app.services.logger_service import logger

router = APIRouter(prefix="/api/image", tags=["image"])


@router.post("/generate", response_model=ImageGenerateResponse)
async def generate_image(
    request: ImageGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate image using specified model (Mystic, Flux, etc.)"""
    
    service = request.model
    
    logger.info(
        "Image generation requested",
        prompt=request.prompt[:100],
        model=service
    )
    
    # Get webhook URL
    result = await db.execute(
        select(ConfigModel).where(ConfigModel.key == "webhook_url")
    )
    webhook_config = result.scalar_one_or_none()
    
    if not webhook_config or not webhook_config.value:
        raise HTTPException(400, "Webhook URL not configured. Please configure in Settings.")
    
    webhook_url = webhook_config.value
    
    # Initialize services
    key_rotation = KeyRotationService(db)
    quota_manager = QuotaManager(db)
    task_manager = TaskManager(db)
    
    try:
        # Get available API key
        await key_rotation.load_keys()
        api_key, key_hash = await key_rotation.get_next_available_key(service)
        
        # Make API call to Magnific
        response = await magnific_client.create_image(
            api_key=api_key,
            service=service,
            prompt=request.prompt,
            webhook_url=webhook_url,
            width=request.width,
            height=request.height,
            num_images=request.num_images
        )
        
        # Increment quota
        await quota_manager.increment_quota(key_hash, service)
        
        # Save task
        task = await task_manager.create_task(
            task_id=response.get("data", {}).get("task_id") or response.get("task_id") or response.get("id"),
            service=service,
            type="image",
            api_key_hash=key_hash,
            request_params={
                "prompt": request.prompt,
                "model": service,
                "width": request.width,
                "height": request.height,
                "num_images": request.num_images
            }
        )
        
        logger.info("Image task created", task_id=task.task_id)
        
        return ImageGenerateResponse(
            task_id=task.task_id,
            status="pending",
            message="Image generation started. You will receive a webhook notification when complete."
        )
        
    except QuotaExhaustedError as e:
        logger.error("Quota exhausted", service=service, error=str(e))
        raise HTTPException(429, detail=str(e))
    
    except Exception as e:
        logger.error("Image generation failed", error=str(e))
        raise HTTPException(500, detail=f"Image generation failed: {str(e)}")
