"""
StudyEnglish - Offline English Learning Application

Main FastAPI application entry point.
All AI models run locally for 100% offline operation.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.config import settings
from app.database import init_db, close_db
from app.routers import (
    vocabulary_router,
    quiz_router,
    translation_router,
    progress_router,
    srs_router,
    exercises_router,
    chat_router,
    reading_router,
    writing_router,
    flashcards_router,
    errors_router,
    learning_paths_router,
    topics_router,
    practice_router,
    recommendations_router,
    export_import_router,
    analytics_router,
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting StudyEnglish application...")
    init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Offline English Learning Application with Local AI Models",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": str(exc)}
    )


# Include all routers
app.include_router(topics_router)
app.include_router(vocabulary_router)
app.include_router(quiz_router)
app.include_router(translation_router)
app.include_router(progress_router)
app.include_router(srs_router)
app.include_router(exercises_router)
app.include_router(chat_router)
app.include_router(reading_router)
app.include_router(writing_router)
app.include_router(flashcards_router)
app.include_router(errors_router)
app.include_router(learning_paths_router)
app.include_router(practice_router)
app.include_router(recommendations_router)
app.include_router(export_import_router)
app.include_router(analytics_router)


# API Health check
@app.get("/api/health")
def health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# AI Model status
@app.get("/api/models/status")
def get_model_status():
    """Get AI model loading status."""
    from app.services.ai_model_manager import ai_manager

    return {
        "success": True,
        "status": ai_manager.get_model_status(),
        "files_exist": ai_manager.check_model_files()
    }


# Memory usage
@app.get("/api/system/memory")
def get_memory_usage():
    """Get system memory usage."""
    from app.services.ai_model_manager import ai_manager

    return {
        "success": True,
        "memory": ai_manager.get_memory_usage()
    }


# Mount static files for frontend
frontend_dir = settings.FRONTEND_DIR
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    # Serve frontend pages
    @app.get("/")
    async def serve_index():
        """Serve the main index.html."""
        index_path = frontend_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return JSONResponse(
            status_code=404,
            content={"message": "Frontend not found. Please build the frontend first."}
        )

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        """Serve frontend files."""
        # Check for specific file
        file_path = frontend_dir / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))

        # Check for HTML page
        html_path = frontend_dir / f"{path}.html"
        if html_path.exists():
            return FileResponse(str(html_path))

        # Check in pages directory
        pages_path = frontend_dir / "pages" / f"{path}.html"
        if pages_path.exists():
            return FileResponse(str(pages_path))

        # Fall back to index.html for SPA routing
        index_path = frontend_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))

        return JSONResponse(
            status_code=404,
            content={"message": f"Page not found: {path}"}
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )
