"""Lip Sync routes"""
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Config as ConfigModel
from app.schemas import LipSyncGenerateRequest, LipSyncGenerateResponse
from app.services.magnific_client import magnific_client
from app.services.key_rotation import KeyRotationService
from app.services.quota_manager import QuotaManager, QuotaExhaustedError
from app.services.task_manager import TaskManager
from app.services.logger_service import logger

router = APIRouter(prefix="/api/lip-sync", tags=["lip-sync"])


def _validate_https_url(url: str | None, name: str):
    if url and not url.startswith("https://"):
        raise HTTPException(400, f"{name} must use HTTPS. Only HTTPS URLs are allowed.")


@router.post("/generate", response_model=LipSyncGenerateResponse)
async def generate_lip_sync(
    request: LipSyncGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate lip-sync video"""

    allowed_models = {"latent-sync", "veed-fabric-1-0-fast", "veed-fabric-1-0"}
    if request.model not in allowed_models:
        raise HTTPException(400, f"Unsupported model: {request.model}")

    if request.model == "latent-sync" and not request.video_url:
        raise HTTPException(400, "video_url is required for latent-sync")
    if request.model != "latent-sync" and not request.image_url:
        raise HTTPException(400, "image_url is required for veed models")
    if request.model != "latent-sync" and not request.resolution:
        raise HTTPException(400, "resolution (720p or 480p) is required for veed models")

    _validate_https_url(request.audio_url, "audio_url")
    _validate_https_url(request.video_url, "video_url")
    _validate_https_url(request.image_url, "image_url")

    result = await db.execute(
        select(ConfigModel).where(ConfigModel.key == "webhook_url")
    )
    webhook_config = result.scalar_one_or_none()
    if not webhook_config or not webhook_config.value:
        raise HTTPException(400, "Webhook URL not configured")
    webhook_url = webhook_config.value

    service = request.model
    key_rotation = KeyRotationService(db)
    quota_manager = QuotaManager(db)
    task_manager = TaskManager(db)

    try:
        await key_rotation.load_keys()
        api_key, key_hash = await key_rotation.get_next_available_key(service)

        response = await magnific_client.create_lip_sync(
            api_key=api_key,
            model=service,
            audio_url=request.audio_url,
            video_url=request.video_url,
            image_url=request.image_url,
            resolution=request.resolution,
            seed=request.seed,
            guidance_scale=request.guidance_scale,
            return_private_url=request.return_private_url,
            webhook_url=webhook_url,
        )

        await quota_manager.increment_quota(key_hash, service)

        task = await task_manager.create_task(
            task_id=response.get("data", {}).get("task_id") or response.get("task_id") or response.get("id"),
            service=service,
            type="lip-sync",
            api_key_hash=key_hash,
            request_params={
                "model": request.model,
                "audio_url": request.audio_url,
                "video_url": request.video_url,
                "image_url": request.image_url,
                "resolution": request.resolution,
                "seed": request.seed,
                "guidance_scale": request.guidance_scale,
            }
        )

        logger.info("Lip-sync task created", task_id=task.task_id, model=service)

        return LipSyncGenerateResponse(
            task_id=task.task_id,
            status="pending",
            message=f"{service} lip-sync generation started"
        )

    except QuotaExhaustedError as e:
        raise HTTPException(429, detail=str(e))
    except httpx.HTTPStatusError as e:
        resp_body = e.response.text[:1000] if e.response.text else ""
        logger.error("Lip-sync API error", error=resp_body, status_code=e.response.status_code)
        raise HTTPException(e.response.status_code, detail=resp_body)
    except Exception as e:
        logger.error("Lip-sync generation failed", error=str(e))
        raise HTTPException(500, detail=f"Lip-sync generation failed: {str(e)}")
