"""Utility functions"""
import hashlib


def hash_api_key(api_key: str) -> str:
    """Hash API key using SHA256"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def mask_api_key(api_key: str) -> str:
    """Mask API key showing only last 4 characters"""
    if len(api_key) <= 4:
        return "****"
    return f"****{api_key[-4:]}"
