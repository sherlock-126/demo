"""Main FastAPI application"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.api.v1 import api_router
from app.core.config import settings
import os

# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    debug=settings.debug,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "fastapi-backend"}


# API status endpoint
@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "version": "0.1.0",
        "debug": settings.debug
    }


# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


# Serve static files (images and videos)
@app.get("/api/v1/files/images/{filename}")
async def serve_image(filename: str):
    """Serve generated images"""
    file_path = os.path.join(settings.output_dir, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(status_code=404, content={"detail": "File not found"})


@app.get("/api/v1/files/videos/{filename}")
async def serve_video(filename: str):
    """Serve generated videos"""
    file_path = os.path.join(settings.videos_dir, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(status_code=404, content={"detail": "File not found"})


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    import traceback
    error_detail = str(exc)
    if settings.debug:
        error_detail = traceback.format_exc()

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": error_detail
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    # Ensure required directories exist
    os.makedirs(settings.data_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)
    os.makedirs(settings.videos_dir, exist_ok=True)
    print(f"FastAPI server starting on {settings.backend_host}:{settings.backend_port}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug
    )