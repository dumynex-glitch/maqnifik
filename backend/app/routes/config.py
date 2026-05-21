"""Configuration routes for API keys and webhook settings"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import hashlib

from app.database import get_db
from app.models import ApiKey, Config as ConfigModel
from app.schemas import ApiKeyConfigRequest, ApiKeyConfigResponse
from app.services.logger_service import logger
from app.utils import hash_api_key, mask_api_key
from app.services.magnific_client import magnific_client
import httpx

router = APIRouter(prefix="/api/config", tags=["config"])


@router.post("/keys", response_model=ApiKeyConfigResponse)
async def save_api_keys(
    config: ApiKeyConfigRequest,
    db: AsyncSession = Depends(get_db)
):
    """Save API keys and webhook configuration"""
    
    if len(config.keys) > 5:
        raise HTTPException(400, "Maximum 5 API keys allowed")
    
    if len(config.keys) == 0:
        raise HTTPException(400, "At least 1 API key required")
    
    # Deactivate all existing keys
    result = await db.execute(select(ApiKey))
    existing_keys = result.scalars().all()
    for key in existing_keys:
        key.is_active = False
    
    # Add new keys
    key_hashes = []
    for api_key in config.keys:
        if not api_key.strip():
            continue
        
        key_hash = hash_api_key(api_key)
        key_hashes.append(key_hash)
        
        # Check if key already exists
        result = await db.execute(
            select(ApiKey).where(ApiKey.key_hash == key_hash)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.is_active = True
            existing.key_value = api_key
        else:
            new_key = ApiKey(
                key_hash=key_hash,
                key_value=api_key,
                key_masked=mask_api_key(api_key),
                is_active=True
            )
            db.add(new_key)
    
    # Save webhook URL
    if config.webhook_url:
        result = await db.execute(
            select(ConfigModel).where(ConfigModel.key == "webhook_url")
        )
        webhook_config = result.scalar_one_or_none()
        
        if webhook_config:
            webhook_config.value = config.webhook_url
        else:
            webhook_config = ConfigModel(
                key="webhook_url",
                value=config.webhook_url
            )
            db.add(webhook_config)
    
    # Save webhook secret
    if config.webhook_secret:
        result = await db.execute(
            select(ConfigModel).where(ConfigModel.key == "webhook_secret")
        )
        secret_config = result.scalar_one_or_none()
        
        if secret_config:
            secret_config.value = config.webhook_secret
        else:
            secret_config = ConfigModel(
                key="webhook_secret",
                value=config.webhook_secret
            )
            db.add(secret_config)
    
    await db.commit()
    
    logger.info(f"Configuration saved: {len(key_hashes)} API keys")
    
    # Return masked keys
    result = await db.execute(
        select(ApiKey).where(ApiKey.is_active == True)
    )
    active_keys = result.scalars().all()
    
    return ApiKeyConfigResponse(
        keys=[key.key_masked for key in active_keys],
        webhook_url=config.webhook_url,
        key_count=len(active_keys)
    )


@router.get("/keys", response_model=ApiKeyConfigResponse)
async def get_api_keys(db: AsyncSession = Depends(get_db)):
    """Get current API key configuration (masked)"""
    
    # Get active keys
    result = await db.execute(
        select(ApiKey).where(ApiKey.is_active == True)
    )
    active_keys = result.scalars().all()
    
    # Get webhook URL
    result = await db.execute(
        select(ConfigModel).where(ConfigModel.key == "webhook_url")
    )
    webhook_config = result.scalar_one_or_none()
    webhook_url = webhook_config.value if webhook_config else None
    
    return ApiKeyConfigResponse(
        keys=[key.key_masked for key in active_keys],
        webhook_url=webhook_url,
        key_count=len(active_keys)
    )


@router.get("/webhook-secret")
async def get_webhook_secret(db: AsyncSession = Depends(get_db)):
    """Get webhook secret (for internal use)"""
    result = await db.execute(
        select(ConfigModel).where(ConfigModel.key == "webhook_secret")
    )
    secret_config = result.scalar_one_or_none()
    
    return {
        "webhook_secret": secret_config.value if secret_config else None
    }


@router.post("/verify-key")
async def verify_api_key_endpoint(payload: dict):
    """Verify a provided API key with Magnific."""
    api_key = payload.get("api_key", "")
    if not api_key or not isinstance(api_key, str):
        raise HTTPException(400, "api_key is required")

    headers = {"x-magnific-api-key": api_key}
    # Try multiple lightweight GET endpoints because some accounts may not have
    # access to every product family even with a valid key.
    checks = [
        "https://api.magnific.com/v1/icons?page=1",
        "https://api.magnific.com/v1/resources?page=1",
    ]

    responses = []

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            for url in checks:
                resp = await client.get(url, headers=headers)
                responses.append({
                    "url": url,
                    "status_code": resp.status_code,
                    "reason": resp.reason_phrase,
                    "raw_response": resp.text,
                    "response_headers": dict(resp.headers),
                })

        statuses = [r["status_code"] for r in responses]
        any_success = any(200 <= s < 300 for s in statuses)
        any_forbidden = any(s == 403 for s in statuses)
        any_rate_limited = any(s == 429 for s in statuses)
        all_unauthorized = all(s == 401 for s in statuses)

        if any_success:
            return {
                "valid": True,
                "authenticated": True,
                "authorized": True,
                "checks": responses,
                "message": "API key is valid and has access to at least one endpoint."
            }

        if all_unauthorized:
            return {
                "valid": False,
                "authenticated": False,
                "authorized": False,
                "checks": responses,
                "message": "API key appears invalid (401 Unauthorized on all verification endpoints)."
            }

        if any_rate_limited:
            return {
                "valid": True,
                "authenticated": True,
                "authorized": False,
                "checks": responses,
                "message": "API key is valid but rate-limited (429). Your free trial quota may be exhausted. Upgrade at https://www.magnific.com/developers/dashboard/billing"
            }

        if any_forbidden:
            return {
                "valid": True,
                "authenticated": True,
                "authorized": False,
                "checks": responses,
                "message": "API key is recognized but lacks permission for tested endpoint(s) (403 Forbidden)."
            }

        return {
            "valid": False,
            "authenticated": False,
            "authorized": False,
            "checks": responses,
            "message": "Verification inconclusive. Check raw responses for details."
        }
    except Exception as e:
        return {
            "valid": False,
            "authenticated": False,
            "authorized": False,
            "checks": responses,
            "message": f"Verification request failed: {str(e)}"
        }
