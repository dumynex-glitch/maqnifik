"""Key rotation service for round-robin API key selection"""
import hashlib
from typing import List, Tuple, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import ApiKey
from app.services.quota_manager import QuotaManager, QuotaExhaustedError
from app.services.logger_service import logger


class NoApiKeysError(Exception):
    """Raised when no API keys are configured"""
    pass


class KeyRotationService:
    """Round-robin key rotation with quota checking"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.quota_manager = QuotaManager(db)
        self.current_index = 0
        self._keys_cache: List[Tuple[str, str]] = []  # (actual_key, key_hash)
    
    async def load_keys(self) -> List[Tuple[str, str]]:
        """Load active API keys from database"""
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.is_active == True)
        )
        keys = result.scalars().all()
        
        if not keys:
            logger.warning("No active API keys found")
            return []
        
        # Note: In production, keys should be encrypted in DB
        # For now, we store hash and reconstruct from config
        self._keys_cache = [(k.key_hash, k.key_hash) for k in keys]
        
        logger.info(f"Loaded {len(self._keys_cache)} active API keys")
        
        return self._keys_cache
    
    async def get_next_available_key(self, service: str) -> Tuple[str, str]:
        """
        Get next available API key with quota remaining
        Returns: (actual_key, key_hash)
        """
        # Load keys if cache is empty
        if not self._keys_cache:
            await self.load_keys()
        
        if not self._keys_cache:
            raise NoApiKeysError("No API keys configured")
        
        attempts = 0
        start_index = self.current_index
        
        while attempts < len(self._keys_cache):
            actual_key, key_hash = self._keys_cache[self.current_index]
            
            # Check if this key has quota remaining
            has_quota = await self.quota_manager.check_quota(key_hash, service)
            
            if has_quota:
                logger.debug(
                    "Selected API key",
                    key_masked=f"****{key_hash[-4:]}",
                    service=service
                )
                return actual_key, key_hash
            
            # Try next key
            self.current_index = (self.current_index + 1) % len(self._keys_cache)
            attempts += 1
        
        # All keys exhausted
        raise QuotaExhaustedError(
            f"All {len(self._keys_cache)} API keys exhausted quota for service: {service}"
        )
    
    async def add_key(self, api_key: str) -> str:
        """Add new API key to database"""
        # Hash the key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Check if already exists
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.key_hash == key_hash)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.info("API key already exists", key_masked=f"****{api_key[-4:]}")
            return key_hash
        
        # Create new key record
        key_record = ApiKey(
            key_hash=key_hash,
            key_masked=f"****{api_key[-4:]}",
            is_active=True
        )
        
        self.db.add(key_record)
        await self.db.commit()
        
        logger.info("API key added", key_masked=f"****{api_key[-4:]}")
        
        # Reload cache
        await self.load_keys()
        
        return key_hash
    
    async def remove_key(self, key_hash: str):
        """Remove API key (mark as inactive)"""
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.key_hash == key_hash)
        )
        key_record = result.scalar_one_or_none()
        
        if key_record:
            key_record.is_active = False
            await self.db.commit()
            
            logger.info("API key removed", key_masked=key_record.key_masked)
            
            # Reload cache
            await self.load_keys()
    
    async def get_all_keys(self) -> List[dict]:
        """Get all active keys (masked)"""
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.is_active == True)
        )
        keys = result.scalars().all()
        
        return [
            {
                "key_hash": k.key_hash,
                "key_masked": k.key_masked,
                "created_at": k.created_at.isoformat()
            }
            for k in keys
        ]
