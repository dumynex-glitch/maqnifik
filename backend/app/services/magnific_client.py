"""Magnific API client wrapper"""
import httpx
from typing import Optional, Dict, Any
from app.config import MAGNIFIC_API_BASE_URL
from app.services.logger_service import logger


class MagnificClient:
    """Client for interacting with Magnific API"""
    
    def __init__(self):
        self.base_url = MAGNIFIC_API_BASE_URL
        self.timeout = 30.0
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        api_key: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Magnific API"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "x-magnific-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(
                "Magnific API HTTP error",
                status_code=e.response.status_code,
                error=str(e),
                endpoint=endpoint
            )
            raise
        except httpx.RequestError as e:
            logger.error(
                "Magnific API request error",
                error=str(e),
                endpoint=endpoint
            )
            raise
        except Exception as e:
            logger.error(
                "Magnific API unexpected error",
                error=str(e),
                endpoint=endpoint
            )
            raise
    
    # Video generation
    async def create_video(
        self,
        api_key: str,
        service: str,
        prompt: str,
        webhook_url: str,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        duration: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """Create video generation task"""
        is_kling3 = service in {"kling-v3-pro", "kling-v3-std"}

        if is_kling3:
            endpoint = f"/ai/video/{service}"
            data = {"webhook_url": webhook_url, **kwargs}
            if prompt:
                data["prompt"] = prompt
            data["duration"] = str(duration)
            if image_url:
                data["start_image_url"] = image_url
            if kwargs.get("start_image_url"):
                data["start_image_url"] = kwargs.pop("start_image_url")
            if kwargs.get("end_image_url"):
                data["end_image_url"] = kwargs.pop("end_image_url")
            return await self._request("POST", endpoint, api_key, data)

        service_endpoint = {
            "kling-v25-pro": "kling-v2-5-pro",
            "kling-v26-pro": "kling-v2-6-pro",
            "kling-v26-motion-control-pro": "kling-v2-6-motion-control-pro",
            "kling-v26-motion-control-std": "kling-v2-6-motion-control-std",
        }.get(service, service)

        if service == "kling-v25-pro" and not image_url:
            raise ValueError("kling-v25-pro requires image_url (image-to-video only)")

        is_motion_control = service in {"kling-v26-motion-control-pro", "kling-v26-motion-control-std"}

        if is_motion_control:
            if not image_url or not video_url:
                raise ValueError(f"{service} requires image_url and video_url")
            endpoint = f"/ai/video/{service_endpoint}"
        elif service == "kling-v26-pro":
            endpoint = f"/ai/image-to-video/{service_endpoint}"
        else:
            endpoint = f"/ai/image-to-video/{service_endpoint}" if image_url else f"/ai/text-to-video/{service_endpoint}"
        
        data = {"webhook_url": webhook_url, **kwargs}

        if prompt:
            data["prompt"] = prompt

        if not is_motion_control:
            data["duration"] = str(duration) if service in {"kling-v25-pro", "kling-v26-pro"} else duration

        if image_url:
            if is_motion_control:
                data["image_url"] = image_url
            else:
                data["image"] = image_url

        if video_url:
            data["video_url"] = video_url
        
        logger.info(
            "Creating video task",
            service=service,
            has_image=bool(image_url),
            duration=duration
        )
        
        return await self._request("POST", endpoint, api_key, data)
    
    # Image generation
    async def create_image(
        self,
        api_key: str,
        service: str,
        prompt: str,
        webhook_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create image generation task"""
        service_endpoint = {
            "flux-pro": "flux-pro-v1-1",
            "flux-pro-v2": "flux-2-pro",
            "flux-dev": "flux-dev",
            "flux-2-pro": "flux-2-pro",
            "flux-2-turbo": "flux-2-turbo",
            "hyperflux": "hyperflux",
            "mystic": "mystic",
            "mystic-ultra": "mystic",
            "mystic-v2": "mystic",
            "mystic-lightning": "mystic",
            "imagen4-fast": "imagen-4-fast",
            "imagen4-ultra": "imagen-4-ultra",
            "seedream": "seedream",
            "seedream-v4": "seedream-v4",
            "nano-banana-pro": "nano-banana-pro",
            "nano-banana-pro-flash": "nano-banana-pro-flash",
        }.get(service, service)
        
        endpoint = f"/ai/text-to-image/{service_endpoint}" if service_endpoint != "mystic" else "/ai/mystic"
        
        data = {
            "prompt": prompt,
            "webhook_url": webhook_url,
            **kwargs
        }
        
        logger.info("Creating image task", service=service)
        
        return await self._request("POST", endpoint, api_key, data)
    
    # Image editing
    async def upscale_image(
        self,
        api_key: str,
        image_url: str,
        webhook_url: str,
        service: str = "upscaler-precision-v2",
        **kwargs
    ) -> Dict[str, Any]:
        """Upscale image"""
        service_endpoint = {
            "upscaler": "image-upscaler",
            "upscaler-precision": "image-upscaler-precision",
            "upscaler-precision-v2": "image-upscaler-precision",
            "upscaler-classic": "image-upscaler",
        }.get(service, service)
        endpoint = f"/ai/{service_endpoint}"
        
        data = {
            "image": image_url,
            "webhook_url": webhook_url,
            **kwargs
        }
        
        logger.info("Creating upscale task", service=service)
        
        return await self._request("POST", endpoint, api_key, data)
    
    async def remove_background(
        self,
        api_key: str,
        image_url: str,
        webhook_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Remove background from image"""
        endpoint = "/ai/beta/remove-background"
        
        data = {
            "image_url": image_url,
            **kwargs
        }
        
        logger.info("Creating background removal task")
        
        return await self._request("POST", endpoint, api_key, data)
    
    async def relight_image(
        self,
        api_key: str,
        image_url: str,
        webhook_url: str,
        lighting_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Relight image"""
        endpoint = "/ai/image-relight"
        
        data = {
            "image": image_url,
            "webhook_url": webhook_url,
            **kwargs
        }
        
        if lighting_prompt:
            data["lighting_prompt"] = lighting_prompt
        
        logger.info("Creating relight task")
        
        return await self._request("POST", endpoint, api_key, data)
    
    async def style_transfer(
        self,
        api_key: str,
        image_url: str,
        style_image_url: str,
        webhook_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Apply style transfer"""
        endpoint = "/ai/style-transfer"
        
        data = {
            "image": image_url,
            "style_image": style_image_url,
            "webhook_url": webhook_url,
            **kwargs
        }
        
        logger.info("Creating style transfer task")
        
        return await self._request("POST", endpoint, api_key, data)
    
    # Audio generation
    async def create_voiceover(
        self,
        api_key: str,
        text: str,
        voice_id: str,
        webhook_url: str,
        stability: Optional[float] = None,
        similarity_boost: Optional[float] = None,
        speed: Optional[float] = None,
        use_speaker_boost: Optional[bool] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create voiceover"""
        endpoint = "/ai/voiceover/elevenlabs-turbo-v2-5"
        
        data = {
            "text": text,
            "voice_id": voice_id,
            "webhook_url": webhook_url,
            **kwargs
        }
        
        if stability is not None:
            data["stability"] = stability
        if similarity_boost is not None:
            data["similarity_boost"] = similarity_boost
        if speed is not None:
            data["speed"] = speed
        if use_speaker_boost is not None:
            data["use_speaker_boost"] = use_speaker_boost
        
        logger.info("Creating voiceover task", voice_id=voice_id)
        
        return await self._request("POST", endpoint, api_key, data)
    
    async def create_sound_effect(
        self,
        api_key: str,
        prompt: str,
        webhook_url: str,
        duration: float = 5.0,
        **kwargs
    ) -> Dict[str, Any]:
        """Create sound effect"""
        endpoint = "/ai/sound-effects"
        
        data = {
            "text": prompt,
            "duration_seconds": duration,
            "webhook_url": webhook_url,
            **kwargs
        }
        
        logger.info("Creating sound effect task", duration=duration)
        
        return await self._request("POST", endpoint, api_key, data)
    
    async def isolate_audio(
        self,
        api_key: str,
        audio_url: str,
        description: str,
        webhook_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Isolate audio"""
        endpoint = "/ai/audio-isolation"
        
        data = {
            "audio": audio_url,
            "description": description,
            "webhook_url": webhook_url,
            **kwargs
        }
        
        logger.info("Creating audio isolation task")
        
        return await self._request("POST", endpoint, api_key, data)
    
    # Task status
    async def get_task_status(
        self,
        api_key: str,
        service: str,
        task_id: str
    ) -> Dict[str, Any]:
        """Get task status"""
        # Map internal service names to API endpoint names
        image_endpoint_map = {
            "flux-pro": "flux-pro-v1-1",
            "flux-pro-v2": "flux-2-pro",
            "flux-dev": "flux-dev",
            "flux-2-pro": "flux-2-pro",
            "flux-2-turbo": "flux-2-turbo",
            "hyperflux": "hyperflux",
            "mystic": "mystic",
            "mystic-ultra": "mystic",
            "mystic-v2": "mystic",
            "mystic-lightning": "mystic",
            "imagen4-fast": "imagen-4-fast",
            "imagen4-ultra": "imagen-4-ultra",
            "seedream": "seedream",
            "seedream-v4": "seedream-v4",
            "nano-banana-pro": "nano-banana-pro",
            "nano-banana-pro-flash": "nano-banana-pro-flash",
        }
        
        video_endpoint_map = {
            "kling-v3-pro": "kling-v3-pro",
            "kling-v3-std": "kling-v3-std",
            "kling-v25-pro": "kling-v2-5-pro",
            "kling-v26-pro": "kling-v2-6-pro",
            "kling-v26-motion-control-pro": "kling-v2-6-motion-control-pro",
            "kling-v26-motion-control-std": "kling-v2-6-motion-control-std",
        }
        
        audio_endpoint_map = {
            "elevenlabs-turbo-v2-5": "voiceover/elevenlabs-turbo-v2-5",
            "sound-effects": "sound-effects",
            "audio-isolation": "audio-isolation",
        }
        
        # Determine endpoint based on service type
        if service in video_endpoint_map:
            ep_service = video_endpoint_map[service]
            if service in {"kling-v3-pro", "kling-v3-std"}:
                endpoint = f"/ai/video/{ep_service}/{task_id}"
            else:
                endpoint = f"/ai/image-to-video/{ep_service}/{task_id}"
        elif service in image_endpoint_map:
            ep_service = image_endpoint_map[service]
            if ep_service == "mystic":
                endpoint = f"/ai/mystic/{task_id}"
            else:
                endpoint = f"/ai/text-to-image/{ep_service}/{task_id}"
        elif service in audio_endpoint_map:
            ep_service = audio_endpoint_map[service]
            endpoint = f"/ai/{ep_service}/{task_id}"
        else:
            endpoint = f"/ai/{service}/{task_id}"
        
        return await self._request("GET", endpoint, api_key)

    async def verify_api_key(self, api_key: str) -> Dict[str, Any]:
        """Verify API key by calling a lightweight authenticated endpoint."""
        return await self._request("GET", "/resources", api_key, params={"page": 1})


# Global client instance
magnific_client = MagnificClient()
