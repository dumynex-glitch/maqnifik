"""Pydantic schemas for request/response validation"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# Config schemas
class ApiKeyConfigRequest(BaseModel):
    keys: List[str] = Field(..., min_length=1, max_length=5, description="1-5 API keys")
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None


class ApiKeyConfigResponse(BaseModel):
    keys: List[str]  # Masked keys
    webhook_url: Optional[str]
    key_count: int


# Task schemas
class TaskCreate(BaseModel):
    service: str
    type: str
    request_params: dict


class TaskResponse(BaseModel):
    id: int
    task_id: str
    service: str
    type: str
    status: str
    result_url: Optional[str]
    thumbnail_url: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Video generation schemas
class VideoGenerateRequest(BaseModel):
    prompt: Optional[str] = Field(default="", max_length=2500)
    image_url: Optional[str] = None
    duration: int = Field(default=5, ge=5, le=10)
    mode: Optional[str] = Field(default="text-to-video")
    model: str = Field(default="kling-v26-pro")
    negative_prompt: Optional[str] = Field(default=None, max_length=2500)
    cfg_scale: Optional[float] = Field(default=None, ge=0, le=1)
    aspect_ratio: Optional[str] = Field(default=None)
    generate_audio: Optional[bool] = Field(default=None)
    video_url: Optional[str] = None
    character_orientation: Optional[str] = Field(default=None)


class VideoGenerateResponse(BaseModel):
    task_id: str
    status: str
    message: str


# Image generation schemas
class ImageGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    model: str = Field(default="mystic")
    width: Optional[int] = Field(default=1024, ge=512, le=2048)
    height: Optional[int] = Field(default=1024, ge=512, le=2048)
    num_images: Optional[int] = Field(default=1, ge=1, le=4)


class ImageGenerateResponse(BaseModel):
    task_id: str
    status: str
    message: str


# Image editing schemas
class ImageEditRequest(BaseModel):
    image_url: str
    operation: str  # upscale, remove-background, relight, style-transfer


class ImageEditResponse(BaseModel):
    task_id: str
    status: str
    message: str


# Audio generation schemas
class AudioGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)
    type: str  # voiceover, sound-effects, audio-isolation
    duration: Optional[float] = Field(default=5.0, ge=0.5, le=22.0)


class AudioGenerateResponse(BaseModel):
    task_id: str
    status: str
    message: str


# Gallery schemas
class GalleryItemResponse(BaseModel):
    id: int
    task_id: str
    type: str
    title: Optional[str]
    prompt: Optional[str]
    result_url: str
    thumbnail_url: Optional[str]
    favorited: bool
    tags: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class GalleryUpdateRequest(BaseModel):
    title: Optional[str] = None
    tags: Optional[List[str]] = None


# Quota schemas
class QuotaByService(BaseModel):
    service: str
    used: int
    limit: int
    percentage: float


class KeyStats(BaseModel):
    key_masked: str
    tasks_created: int
    quota_remaining: int


# Dashboard schemas
class DashboardStats(BaseModel):
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    pending_tasks: int
    tasks_today: int
    tasks_this_week: int
    gallery_item_count: int
    quota_by_service: List[QuotaByService]
    recent_tasks: List[TaskResponse]
    key_stats: List[KeyStats]


# Log schemas
class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    task_id: Optional[str] = None
    service: Optional[str] = None
    error: Optional[str] = None


class LogsResponse(BaseModel):
    logs: List[LogEntry]
    total: int


# Webhook payload schema
class WebhookPayload(BaseModel):
    task_id: str
    status: str
    result_url: Optional[str] = None
    error: Optional[str] = None
