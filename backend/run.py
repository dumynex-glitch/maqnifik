#!/usr/bin/env python3
"""Single entry point for running the Magnific API Integration app"""
import uvicorn
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import app
from app.database import init_db
import asyncio


async def initialize():
    """Initialize database"""
    print("🔧 Initializing database...")
    await init_db()
    print("✅ Database initialized")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Magnific API Integration App")
    print("=" * 60)
    
    # Initialize database
    asyncio.run(initialize())
    
    print("\n📊 Server Information:")
    print(f"   • URL: http://localhost:8000")
    print(f"   • API Docs: http://localhost:8000/docs")
    print(f"   • Health Check: http://localhost:8000/api/health")
    print("\n💡 Press CTRL+C to stop the server\n")
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
