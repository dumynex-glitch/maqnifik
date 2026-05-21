"""Database models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class ApiKey(Base):
    """API key storage"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key_hash = Column(String(64), nullable=False, unique=True, index=True)
    key_value = Column(Text, nullable=False)  # Plaintext API key
    key_masked = Column(String(20), nullable=False)  # Last 4 chars for display
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Config(Base):
    """Application configuration"""
    __tablename__ = "config"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Task(Base):
    """Task tracking"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(100), nullable=False, unique=True, index=True)
    service = Column(String(100), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # video, image, audio, editing
    status = Column(String(50), nullable=False, default="pending", index=True)
    api_key_hash = Column(String(64), ForeignKey("api_keys.key_hash"))
    request_params = Column(Text)  # JSON blob
    result_url = Column(Text)
    thumbnail_url = Column(Text)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)


class QuotaUsage(Base):
    """Daily quota tracking per API key per service"""
    __tablename__ = "quota_usage"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key_hash = Column(String(64), ForeignKey("api_keys.key_hash"), nullable=False)
    service = Column(String(100), nullable=False)
    date = Column(Date, nullable=False, index=True)
    count = Column(Integer, default=0)
    
    __table_args__ = (
        # Unique constraint on key + service + date
        {'sqlite_autoincrement': True},
    )


class Gallery(Base):
    """Gallery items"""
    __tablename__ = "gallery"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(100), ForeignKey("tasks.task_id"), nullable=False)
    type = Column(String(50), nullable=False, index=True)  # image, video, audio
    title = Column(String(200))
    prompt = Column(Text)
    result_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text)
    favorited = Column(Boolean, default=False, index=True)
    tags = Column(Text)  # JSON array
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class CacheMetadata(Base):
    """Cache metadata for tracking cached API responses"""
    __tablename__ = "cache_metadata"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_key = Column(String(64), nullable=False, unique=True, index=True)
    service = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
