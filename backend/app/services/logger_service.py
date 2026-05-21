"""Structured logging service with JSON output"""
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from app.config import LOG_DIR


class StructuredLogger:
    """JSON-based structured logger"""
    
    def __init__(self, log_dir: str = str(LOG_DIR)):
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("magnific_app")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # JSON file handler
        file_handler = logging.FileHandler(f"{log_dir}/app.log")
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(file_handler)
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(console_handler)
    
    def _log(self, level: str, message: str, **context):
        """Internal log method"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "message": message,
            **context
        }
        
        log_method = getattr(self.logger, level.lower())
        log_method(json.dumps(log_entry))
    
    def info(self, message: str, **context):
        """Log info message"""
        self._log("INFO", message, **context)
    
    def error(self, message: str, **context):
        """Log error message"""
        self._log("ERROR", message, **context)
    
    def warning(self, message: str, **context):
        """Log warning message"""
        self._log("WARNING", message, **context)
    
    def debug(self, message: str, **context):
        """Log debug message"""
        self._log("DEBUG", message, **context)


# Global logger instance
logger = StructuredLogger()
