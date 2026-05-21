"""Video generation routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Config as ConfigModel
from app.schemas import VideoGenerateRequest, VideoGenerateResponse
from app.services.magnific_client import magnific_client
from app.services.key_rotation import KeyRotationService
from app.services.quota_manager import QuotaManager, QuotaExhaustedError
from app.services.task_manager import TaskManager
from app.services.logger_service import logger

router = APIRouter(prefix="/api/video", tags=["video"])


@router.post("/generate", response_model=VideoGenerateResponse)
async def generate_video(
    request: VideoGenerateRequest,
    db: AsyncSession = Depends(get_db)
): 
    """Generate video using Kling 2.6 Standard (text-to-video or image-to-video)"""

    allowed_models = {
        "kling-v26-pro",
        "kling-v25-pro",
        "kling-v26-motion-control-pro",
        "kling-v26-motion-control-std",
    }
    service = request.model
    if service not in allowed_models:
        raise HTTPException(400, f"Unsupported model: {service}")
    
    logger.info(
        "Video generation requested",
        prompt=(request.prompt or "")[:100],
        model=service,
        mode=request.mode,
        duration=request.duration
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
        response = await magnific_client.create_video(
            api_key=api_key,
            service=service,
            prompt=request.prompt,
            webhook_url=webhook_url,
            image_url=request.image_url,
            video_url=request.video_url,
            duration=request.duration,
            negative_prompt=request.negative_prompt,
            cfg_scale=request.cfg_scale,
            aspect_ratio=request.aspect_ratio,
            generate_audio=request.generate_audio,
            character_orientation=request.character_orientation,
        )
        
        # Increment quota
        await quota_manager.increment_quota(key_hash, service)
        
        # Save task
        task = await task_manager.create_task(
            task_id=response.get("data", {}).get("task_id") or response.get("task_id") or response.get("id"),
            service=service,
            type="video",
            api_key_hash=key_hash,
            request_params={
                "prompt": request.prompt,
                "image_url": request.image_url,
                "duration": request.duration,
                "mode": request.mode,
                "model": request.model,
                "negative_prompt": request.negative_prompt,
                "cfg_scale": request.cfg_scale,
                "aspect_ratio": request.aspect_ratio,
                "generate_audio": request.generate_audio,
                "video_url": request.video_url,
                "character_orientation": request.character_orientation,
            }
        )
        
        logger.info("Video task created", task_id=task.task_id)
        
        return VideoGenerateResponse(
            task_id=task.task_id,
            status="pending",
            message="Video generation started. You will receive a webhook notification when complete."
        )
        
    except QuotaExhaustedError as e:
        logger.error("Quota exhausted", service=service, error=str(e))
        raise HTTPException(429, detail=str(e))
    
    except Exception as e:
        logger.error("Video generation failed", error=str(e))
        raise HTTPException(500, detail=f"Video generation failed: {str(e)}")
