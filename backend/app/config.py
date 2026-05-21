"""Application configuration"""
import os
from pathlib import Path
from typing import Optional

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
LOG_DIR = DATA_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Database
DATABASE_URL = f"sqlite+aiosqlite:///{DATA_DIR}/database.db"

# Magnific API
MAGNIFIC_API_BASE_URL = "https://api.magnific.com/v1"

# Cache settings
CACHE_TTL_HOURS = 24  # Cache results for 24 hours

# Rate limits (Free tier from Magnific docs)
DAILY_LIMITS = {
    # Video
    "kling-v3-pro": 100,
    "kling-v3-std": 150,
    "kling-v26-std": 5,
    "kling-v26-pro": 11,
    "kling-v26-motion-control-std": 5,
    "kling-v26-motion-control-pro": 5,
    "kling-v2": 5,
    "kling-v21-master": 5,
    "kling-v21-pro": 11,
    "kling-v21-std": 20,
    "kling-v25-pro": 11,
    "kling-o1-pro": 5,
    "kling-o1-std": 5,
    "minimax-hailuo02-1080p": 11,
    "minimax-hailuo02-768p": 20,
    "ltx-2-fast": 20,
    "ltx-2-pro": 11,
    "pixverse-v5": 125,
    "pixverse-v5-transition": 125,
    "pixverse-v5-5": 125,
    "pixverse-v6": 125,
    "wan-2-5": 20,
    "wan-2-7": 11,
    "runway-4-5": 5,
    "happy-horse-1": 5,
    "veo-3-1": 5,
    
    # Image generation
    "mystic": 125,
    "mystic-ultra": 125,
    "mystic-v2": 125,
    "mystic-lightning": 125,
    "flux-pro": 100,
    "flux-pro-v2": 100,
    "flux-dev": 100,
    "flux-2-pro": 100,
    "flux-2-turbo": 100,
    "nano-banana-pro": 100,
    "nano-banana-pro-flash": 100,
    "imagen4-fast": 100,
    "imagen4-ultra": 100,
    "seedream": 500,
    "seedream-v4": 500,
    "hyperflux": 100,
    
    # Image editing
    "upscaler": 125,
    "upscaler-precision": 125,
    "upscaler-precision-v2": 125,
    "upscaler-classic": 125,
    "remove-background": 300,
    "relight": 125,
    "style-transfer": 125,
    "image-expand-seedream-v4-5": 500,
    "image-expand-ideogram": 100,
    "ideogram-image-edit": 100,
    "image-change-camera": 125,
    "reimagine": 125,
    "reimagine-flux": 100,
    
    # Audio
    "sound-effects": 125,
    "elevenlabs-turbo-v2-5": 125,
    "audio-isolation": 125,

    # Lip Sync
    "latent-sync": 20,
    "veed-fabric-1-0-fast": 20,
    "veed-fabric-1-0": 20,
    
    # Other
    "image-to-prompt": 125,
    "improve-prompt": 125,
    "ai-classifier": 125,
    "icon-generation": 25,
    "text-to-icon": 25,
}

# Per-second rate limits (applies to all services)
RATE_LIMIT_BURST = 50  # Max 50 requests per second (5-second window)
RATE_LIMIT_AVERAGE = 10  # Average 10 requests per second (2-minute window)

class Config:
    """Runtime configuration loaded from database"""
    _instance: Optional['Config'] = None
    
    def __init__(self):
        self.webhook_url: Optional[str] = None
        self.webhook_secret: Optional[str] = None
        self.api_keys: list[str] = []
    
    @classmethod
    def get_instance(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def update(self, webhook_url: Optional[str] = None, 
               webhook_secret: Optional[str] = None,
               api_keys: Optional[list[str]] = None):
        """Update configuration"""
        if webhook_url is not None:
            self.webhook_url = webhook_url
        if webhook_secret is not None:
            self.webhook_secret = webhook_secret
        if api_keys is not None:
            self.api_keys = api_keys

# Global config instance
config = Config.get_instance()
