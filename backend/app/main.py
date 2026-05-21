"""FastAPI main application"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os

from app.database import init_db
from app.routes import config, dashboard, video, image, editing, audio, gallery, tasks, logs, webhooks, lip_sync
from app.services.logger_service import logger

# Create FastAPI app
app = FastAPI(
    title="Magnific API Integration",
    description="Single-stack app for Magnific API with multi-key support, quota tracking, and webhook handling",
    version="1.0.0"
)

# CORS middleware (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(config.router)
app.include_router(dashboard.router)
app.include_router(video.router)
app.include_router(image.router)
app.include_router(editing.router)
app.include_router(audio.router)
app.include_router(gallery.router)
app.include_router(tasks.router)
app.include_router(logs.router)
app.include_router(webhooks.router)
app.include_router(lip_sync.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting Magnific API Integration App")
    await init_db()
    logger.info("Database initialized")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Magnific API Integration is running"}


# Serve Next.js static files
static_dir = Path(__file__).parent.parent / "static"

if static_dir.exists():
    # Serve static assets
    app.mount("/_next", StaticFiles(directory=static_dir / "_next"), name="next-static")
    
    # Serve other static files if they exist
    if (static_dir / "assets").exists():
        app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")
    
    # Catch-all route for SPA (must be last)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve exported Next.js routes and fallback index"""
        # Don't serve API routes
        if full_path.startswith("api/"):
            return {"error": "Not found"}

        # Try exact file first
        exact_file = static_dir / full_path
        if exact_file.is_file():
            return FileResponse(exact_file)

        # Try route as directory index (e.g. /settings -> /settings/index.html)
        route_index = static_dir / full_path / "index.html"
        if route_index.is_file():
            return FileResponse(route_index)

        # Try route as html file (e.g. /settings -> /settings.html)
        route_html = static_dir / f"{full_path}.html"
        if route_html.is_file():
            return FileResponse(route_html)

        # Fallback to root index
        index_file = static_dir / "index.html"
        if index_file.is_file():
            return FileResponse(index_file)
        
        return {"error": "Frontend not built. Run build.sh first."}
else:
    @app.get("/")
    async def root():
        """Root endpoint when frontend not built"""
        return {
            "message": "Magnific API Integration Backend",
            "status": "Frontend not built yet",
            "instructions": "Run build.sh to build the frontend, or access API docs at /docs"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
