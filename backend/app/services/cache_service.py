"""File-based cache service for API responses"""
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import CacheMetadata
from app.config import CACHE_DIR, CACHE_TTL_HOURS
from app.services.logger_service import logger


class CacheService:
    """File-based caching for API responses"""
    
    def __init__(self, db: AsyncSession, cache_dir: str = str(CACHE_DIR)):
        self.db = db
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_hours = CACHE_TTL_HOURS
    
    def _generate_cache_key(self, service: str, params: Dict[str, Any]) -> str:
        """Generate cache key from service and parameters"""
        # Sort params for consistent hashing
        sorted_params = json.dumps(params, sort_keys=True)
        content = f"{service}:{sorted_params}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Get file path for cache key"""
        return self.cache_dir / f"{cache_key}.json"
    
    async def get(
        self,
        service: str,
        params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get cached response if exists and not expired"""
        cache_key = self._generate_cache_key(service, params)
        
        # Check metadata
        result = await self.db.execute(
            select(CacheMetadata).where(CacheMetadata.cache_key == cache_key)
        )
        metadata = result.scalar_one_or_none()
        
        if not metadata:
            logger.debug("Cache miss - no metadata", cache_key=cache_key[:8])
            return None
        
        # Check expiration
        if datetime.utcnow() > metadata.expires_at:
            logger.debug("Cache miss - expired", cache_key=cache_key[:8])
            await self._delete_cache(cache_key)
            return None
        
        # Read cache file
        cache_file = self._get_cache_file_path(cache_key)
        
        if not cache_file.exists():
            logger.warning("Cache file missing", cache_key=cache_key[:8])
            await self._delete_cache(cache_key)
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            logger.info(
                "Cache hit",
                cache_key=cache_key[:8],
                service=service
            )
            
            return cached_data
            
        except Exception as e:
            logger.error(
                "Cache read error",
                cache_key=cache_key[:8],
                error=str(e)
            )
            await self._delete_cache(cache_key)
            return None
    
    async def set(
        self,
        service: str,
        params: Dict[str, Any],
        data: Dict[str, Any]
    ):
        """Cache API response"""
        cache_key = self._generate_cache_key(service, params)
        cache_file = self._get_cache_file_path(cache_key)
        
        try:
            # Write cache file
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            
            # Create/update metadata
            expires_at = datetime.utcnow() + timedelta(hours=self.ttl_hours)
            
            result = await self.db.execute(
                select(CacheMetadata).where(CacheMetadata.cache_key == cache_key)
            )
            metadata = result.scalar_one_or_none()
            
            if metadata:
                metadata.expires_at = expires_at
            else:
                metadata = CacheMetadata(
                    cache_key=cache_key,
                    service=service,
                    file_path=str(cache_file),
                    expires_at=expires_at
                )
                self.db.add(metadata)
            
            await self.db.commit()
            
            logger.info(
                "Cache set",
                cache_key=cache_key[:8],
                service=service,
                expires_at=expires_at.isoformat()
            )
            
        except Exception as e:
            logger.error(
                "Cache write error",
                cache_key=cache_key[:8],
                error=str(e)
            )
    
    async def _delete_cache(self, cache_key: str):
        """Delete cache entry"""
        # Delete metadata
        result = await self.db.execute(
            select(CacheMetadata).where(CacheMetadata.cache_key == cache_key)
        )
        metadata = result.scalar_one_or_none()
        
        if metadata:
            await self.db.delete(metadata)
            await self.db.commit()
        
        # Delete file
        cache_file = self._get_cache_file_path(cache_key)
        if cache_file.exists():
            cache_file.unlink()
    
    async def cleanup_expired(self):
        """Clean up expired cache entries"""
        now = datetime.utcnow()
        
        result = await self.db.execute(
            select(CacheMetadata).where(CacheMetadata.expires_at < now)
        )
        expired = result.scalars().all()
        
        for metadata in expired:
            cache_file = Path(metadata.file_path)
            if cache_file.exists():
                cache_file.unlink()
            
            await self.db.delete(metadata)
        
        await self.db.commit()
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired cache entries")
