"""Logs routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import json
from pathlib import Path

from app.database import get_db
from app.schemas import LogsResponse, LogEntry
from app.config import LOG_DIR

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("", response_model=LogsResponse)
async def get_logs(
    level: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get application logs with optional filtering"""
    
    log_file = Path(LOG_DIR) / "app.log"
    
    if not log_file.exists():
        return LogsResponse(logs=[], total=0)
    
    logs = []
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    
                    # Filter by level
                    if level and log_entry.get('level') != level:
                        continue
                    
                    # Filter by search term
                    if search and search.lower() not in json.dumps(log_entry).lower():
                        continue
                    
                    logs.append(LogEntry(**log_entry))
                    
                except json.JSONDecodeError:
                    continue
                except Exception:
                    continue
        
        # Reverse to show newest first
        logs.reverse()
        
        # Apply pagination
        paginated_logs = logs[offset:offset+limit]
        
        return LogsResponse(
            logs=paginated_logs,
            total=len(logs)
        )
        
    except Exception as e:
        return LogsResponse(logs=[], total=0)
