"""Webhook receiver route"""
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.database import get_db
from app.models import Config as ConfigModel
from app.services.task_manager import TaskManager
from app.services.gallery_service import GalleryService
from app.services.logger_service import logger
from app.utils.webhook_verify import verify_webhook_signature

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/magnific")
async def receive_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Receive webhook from Magnific API"""
    
    # Extract headers
    webhook_id = request.headers.get("webhook-id")
    webhook_timestamp = request.headers.get("webhook-timestamp")
    webhook_signature = request.headers.get("webhook-signature")
    
    if not all([webhook_id, webhook_timestamp, webhook_signature]):
        logger.warning("Webhook missing required headers")
        raise HTTPException(400, "Missing webhook headers")
    
    # Get raw body
    body = await request.body()
    body_str = body.decode('utf-8')
    
    # Get webhook secret from config
    result = await db.execute(
        select(ConfigModel).where(ConfigModel.key == "webhook_secret")
    )
    secret_config = result.scalar_one_or_none()
    
    if not secret_config or not secret_config.value:
        logger.warning("Webhook secret not configured")
        raise HTTPException(500, "Webhook secret not configured")
    
    secret_key = secret_config.value
    
    # Verify signature
    is_valid = verify_webhook_signature(
        webhook_id=webhook_id,
        webhook_timestamp=webhook_timestamp,
        body=body_str,
        signature_header=webhook_signature,
        secret_key=secret_key
    )
    
    if not is_valid:
        logger.warning(
            "Invalid webhook signature",
            webhook_id=webhook_id
        )
        raise HTTPException(401, "Invalid webhook signature")
    
    # Parse payload
    try:
        data = json.loads(body_str)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(400, "Invalid JSON payload")
    
    # Extract task info
    task_id = data.get("task_id") or data.get("id")
    status = data.get("status")
    result_url = data.get("result_url") or data.get("output_url")
    thumbnail_url = data.get("thumbnail_url")
    error_message = data.get("error") or data.get("error_message")
    
    if not task_id:
        logger.error("Webhook missing task_id")
        raise HTTPException(400, "Missing task_id in payload")
    
    # Update task
    task_manager = TaskManager(db)
    await task_manager.update_task(
        task_id=task_id,
        status=status,
        result_url=result_url,
        thumbnail_url=thumbnail_url,
        error_message=error_message
    )
    
    logger.info(
        "Webhook processed",
        task_id=task_id,
        status=status,
        webhook_id=webhook_id
    )
    
    # Add to gallery if completed successfully
    if status == "completed" and result_url:
        gallery_service = GalleryService(db)
        await gallery_service.add_from_task(task_id)
    
    return {"status": "ok", "task_id": task_id}
