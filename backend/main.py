"""
SentinelOS Backend - FastAPI Application

Main application entry point. Initializes FastAPI, configures middleware,
and sets up all routes.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.logging import LoggingMiddleware
from app.api.routes import router as api_router
from app.models.database import init_db, close_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up SentinelOS backend...")
    logger.info(f"DEBUG mode: {settings.DEBUG}")
    logger.info(f"Database: {settings.DATABASE_URL}")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down SentinelOS backend...")
    try:
        await close_db()
    except Exception as e:
        logger.error(f"Error closing database: {e}")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)


# Add middleware (order matters - add from outermost to innermost)

# 1. Trusted Host Middleware - restricts hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.example.com"]
)

# 2. CORS Middleware - handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# 3. Custom Logging Middleware - log all requests
app.add_middleware(LoggingMiddleware)

# 4. Error Handler Middleware - catch and format errors
app.add_middleware(ErrorHandlerMiddleware)


# Health Check Endpoint
@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    Returns: Application status and dependencies check.
    """
    return {
        "status": "healthy",
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
    }


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint.
    Returns: API information and usage guide.
    """
    return {
        "message": f"Welcome to {settings.API_TITLE}",
        "version": settings.API_VERSION,
        "docs": "/api/docs" if settings.DEBUG else "Not available",
        "health": "/api/health",
    }


# Include API routers
app.include_router(api_router)


# Exception handlers
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
