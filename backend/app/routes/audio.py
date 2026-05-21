"""Audio generation routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Config as ConfigModel
from app.schemas import AudioGenerateRequest, AudioGenerateResponse
from app.services.magnific_client import magnific_client
from app.services.key_rotation import KeyRotationService
from app.services.quota_manager import QuotaManager, QuotaExhaustedError
from app.services.task_manager import TaskManager
from app.services.logger_service import logger

router = APIRouter(prefix="/api/audio", tags=["audio"])


@router.post("/generate", response_model=AudioGenerateResponse)
async def generate_audio(
    request: AudioGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate audio (voiceover, sound effects, or audio isolation)"""
    
    # Map type to service
    service_map = {
        "voiceover": "elevenlabs-turbo-v2-5",
        "sound-effects": "sound-effects",
        "audio-isolation": "audio-isolation"
    }
    
    service = service_map.get(request.type)
    
    if not service:
        raise HTTPException(400, f"Invalid audio type: {request.type}")
    
    logger.info(
        "Audio generation requested",
        type=request.type,
        prompt=request.prompt[:100]
    )
    
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
        
        # Call appropriate method based on type
        if request.type == "voiceover":
            if not request.voice_id:
                raise HTTPException(400, "voice_id is required for voiceover generation")
            response = await magnific_client.create_voiceover(
                api_key=api_key,
                text=request.prompt,
                voice_id=request.voice_id,
                webhook_url=webhook_url,
                stability=request.stability,
                similarity_boost=request.similarity_boost,
                speed=request.speed,
                use_speaker_boost=request.use_speaker_boost,
            )
        elif request.type == "sound-effects":
            response = await magnific_client.create_sound_effect(
                api_key=api_key,
                prompt=request.prompt,
                webhook_url=webhook_url,
                duration=request.duration
            )
        else:  # audio-isolation
            # For isolation, prompt should contain audio URL and description
            raise HTTPException(400, "Audio isolation requires audio_url parameter")
        
        await quota_manager.increment_quota(key_hash, service)
        
        task = await task_manager.create_task(
            task_id=response.get("data", {}).get("task_id") or response.get("task_id") or response.get("id"),
            service=service,
            type="audio",
            api_key_hash=key_hash,
            request_params={
                "prompt": request.prompt,
                "type": request.type,
                "duration": request.duration,
                "voice_id": request.voice_id,
                "stability": request.stability,
                "similarity_boost": request.similarity_boost,
                "speed": request.speed,
                "use_speaker_boost": request.use_speaker_boost,
            }
        )
        
        logger.info("Audio task created", task_id=task.task_id, type=request.type)
        
        return AudioGenerateResponse(
            task_id=task.task_id,
            status="pending",
            message=f"{request.type} generation started"
        )
        
    except QuotaExhaustedError as e:
        logger.error("Quota exhausted", service=service, error=str(e))
        raise HTTPException(429, detail=str(e))
    
    except Exception as e:
        logger.error("Audio generation failed", error=str(e))
        raise HTTPException(500, detail=f"Audio generation failed: {str(e)}")
