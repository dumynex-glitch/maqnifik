"""Quota manager for tracking daily API usage per key per service"""
from datetime import date, datetime
from typing import Dict, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import QuotaUsage, ApiKey
from app.config import DAILY_LIMITS
from app.services.logger_service import logger


class QuotaExhaustedError(Exception):
    """Raised when quota is exhausted"""
    pass


class QuotaManager:
    """Manage daily quota tracking per API key per service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.daily_limits = DAILY_LIMITS
    
    async def check_quota(self, api_key_hash: str, service: str) -> bool:
        """Check if API key has quota remaining for service today"""
        today = date.today()
        
        # Get usage count for this key + service + date
        result = await self.db.execute(
            select(QuotaUsage).where(
                and_(
                    QuotaUsage.api_key_hash == api_key_hash,
                    QuotaUsage.service == service,
                    QuotaUsage.date == today
                )
            )
        )
        usage_record = result.scalar_one_or_none()
        
        current_count = usage_record.count if usage_record else 0
        limit = self.daily_limits.get(service, 100)
        
        has_quota = current_count < limit
        
        if not has_quota:
            logger.warning(
                "Quota exhausted",
                service=service,
                used=current_count,
                limit=limit
            )
        
        return has_quota
    
    async def increment_quota(self, api_key_hash: str, service: str):
        """Increment usage count for this key + service"""
        today = date.today()
        
        # Try to get existing record
        result = await self.db.execute(
            select(QuotaUsage).where(
                and_(
                    QuotaUsage.api_key_hash == api_key_hash,
                    QuotaUsage.service == service,
                    QuotaUsage.date == today
                )
            )
        )
        usage_record = result.scalar_one_or_none()
        
        if usage_record:
            # Increment existing
            usage_record.count += 1
        else:
            # Create new
            usage_record = QuotaUsage(
                api_key_hash=api_key_hash,
                service=service,
                date=today,
                count=1
            )
            self.db.add(usage_record)
        
        await self.db.commit()
        
        logger.debug(
            "Quota incremented",
            service=service,
            count=usage_record.count
        )
    
    async def get_remaining_quota(
        self,
        api_key_hash: str,
        service: str
    ) -> Dict[str, int]:
        """Get remaining quota for display"""
        today = date.today()
        
        result = await self.db.execute(
            select(QuotaUsage).where(
                and_(
                    QuotaUsage.api_key_hash == api_key_hash,
                    QuotaUsage.service == service,
                    QuotaUsage.date == today
                )
            )
        )
        usage_record = result.scalar_one_or_none()
        
        used = usage_record.count if usage_record else 0
        limit = self.daily_limits.get(service, 100)
        
        return {
            "service": service,
            "used": used,
            "limit": limit,
            "remaining": limit - used
        }
    
    async def get_all_quota_status(
        self,
        api_key_hash: Optional[str] = None
    ) -> Dict[str, Dict[str, int]]:
        """Get quota status for all services (optionally filtered by key)"""
        today = date.today()
        
        query = select(QuotaUsage).where(QuotaUsage.date == today)
        
        if api_key_hash:
            query = query.where(QuotaUsage.api_key_hash == api_key_hash)
        
        result = await self.db.execute(query)
        usage_records = result.scalars().all()
        
        # Build quota status dict
        quota_status = {}
        
        for record in usage_records:
            service = record.service
            limit = self.daily_limits.get(service, 100)
            
            if service not in quota_status:
                quota_status[service] = {
                    "used": 0,
                    "limit": limit,
                    "remaining": limit
                }
            
            quota_status[service]["used"] += record.count
            quota_status[service]["remaining"] = limit - quota_status[service]["used"]
        
        return quota_status
    
    async def get_quota_by_service(self) -> list:
        """Get aggregated quota usage across all keys by service"""
        today = date.today()
        
        result = await self.db.execute(
            select(QuotaUsage).where(QuotaUsage.date == today)
        )
        usage_records = result.scalars().all()
        
        # Aggregate by service
        service_usage = {}
        
        for record in usage_records:
            service = record.service
            if service not in service_usage:
                service_usage[service] = 0
            service_usage[service] += record.count
        
        # Build response
        quota_list = []
        for service, used in service_usage.items():
            limit = self.daily_limits.get(service, 100)
            percentage = (used / limit * 100) if limit > 0 else 0
            
            quota_list.append({
                "service": service,
                "used": used,
                "limit": limit,
                "percentage": round(percentage, 1)
            })
        
        # Sort by percentage descending
        quota_list.sort(key=lambda x: x["percentage"], reverse=True)
        
        return quota_list
