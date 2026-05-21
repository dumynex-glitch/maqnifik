"""Webhook verification utilities"""
import hmac
import hashlib
import base64
from typing import Optional


def verify_webhook_signature(
    webhook_id: str,
    webhook_timestamp: str,
    body: str,
    signature_header: str,
    secret_key: str
) -> bool:
    """
    Verify HMAC-SHA256 webhook signature
    
    Args:
        webhook_id: Unique webhook request ID
        webhook_timestamp: Timestamp when webhook was sent
        body: Raw request body
        signature_header: webhook-signature header value
        secret_key: Webhook secret key
    
    Returns:
        True if signature is valid, False otherwise
    """
    # Create content to sign
    content = f"{webhook_id}.{webhook_timestamp}.{body}"
    
    # Generate expected signature
    secret_bytes = secret_key.encode('utf-8')
    hmac_obj = hmac.new(secret_bytes, content.encode('utf-8'), hashlib.sha256)
    expected_signature = base64.b64encode(hmac_obj.digest()).decode('utf-8')
    
    # Parse signature header (format: "v1,signature1 v2,signature2")
    signatures = signature_header.split(' ')
    
    for sig in signatures:
        if ',' not in sig:
            continue
        
        version, sig_value = sig.split(',', 1)
        
        # Use constant-time comparison to prevent timing attacks
        if hmac.compare_digest(sig_value, expected_signature):
            return True
    
    return False


def generate_webhook_signature(
    webhook_id: str,
    webhook_timestamp: str,
    body: str,
    secret_key: str
) -> str:
    """
    Generate webhook signature for testing
    
    Args:
        webhook_id: Unique webhook request ID
        webhook_timestamp: Timestamp when webhook was sent
        body: Raw request body
        secret_key: Webhook secret key
    
    Returns:
        Signature in format "v1,signature"
    """
    content = f"{webhook_id}.{webhook_timestamp}.{body}"
    
    secret_bytes = secret_key.encode('utf-8')
    hmac_obj = hmac.new(secret_bytes, content.encode('utf-8'), hashlib.sha256)
    signature = base64.b64encode(hmac_obj.digest()).decode('utf-8')
    
    return f"v1,{signature}"
