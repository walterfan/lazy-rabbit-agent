import logging
import sys
import time
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.api import api_router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),  # Output to stdout
    ],
)

# Set specific loggers to appropriate levels
logger = logging.getLogger(__name__)
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # Reduce access log noise
logging.getLogger("httpx").setLevel(logging.WARNING)  # Reduce HTTP client noise


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests with method, path, status code, and duration."""
    
    async def dispatch(self, request: Request, call_next):
        # Get request details
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        query = str(request.url.query) if request.url.query else ""
        
        # Log incoming request
        if query:
            logger.info(f"📨 [HTTP] {method} {path}?{query} from {client_ip}")
        else:
            logger.info(f"📨 [HTTP] {method} {path} from {client_ip}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response with status code and duration
            status_emoji = "✅" if response.status_code < 400 else "❌"
            logger.info(
                f"{status_emoji} [HTTP] {method} {path} -> {response.status_code} ({duration_ms:.2f}ms)"
            )
            
            return response
        except Exception as exc:
            # Log error
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"💥 [HTTP] {method} {path} -> ERROR ({duration_ms:.2f}ms): {str(exc)}")
            raise


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors with detailed messages."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred. Please try again later.",
        },
    )


# Health check endpoint
@app.get("/api/health")
def health_check() -> dict[str, str]:
    """Health check endpoint to verify server is running."""
    return {"status": "healthy"}


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Mount static files (frontend)
FRONTEND_DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")
    
    # Serve index.html for all non-API routes (SPA fallback)
    from fastapi.responses import FileResponse
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        Serve the Vue.js SPA for all non-API routes.
        This allows Vue Router to handle client-side routing.
        """
        # If it's an API route, let FastAPI handle it (404)
        if full_path.startswith("api/"):
            return JSONResponse(
                status_code=404,
                content={"detail": "Not Found"}
            )
        
        # Check if file exists in dist
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        # Otherwise, serve index.html (SPA fallback)
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        else:
            return JSONResponse(
                status_code=404,
                content={"detail": "Frontend not built. Run: cd frontend && npm run build"}
            )
else:
    logger.warning(f"Frontend dist directory not found: {FRONTEND_DIST}")
    logger.warning("Frontend will not be served. Run: cd frontend && npm run build")


# Startup event
@app.on_event("startup")
async def startup_event() -> None:
    """Run on application startup."""
    logger.info(f"🚀 {settings.PROJECT_NAME} starting up...")
    logger.info(f"📚 API Documentation: http://localhost:8000/docs")
    logger.info(f"🔧 Environment: {settings.ENVIRONMENT}")
    logger.info(f"📊 Logging level: {logging.getLevelName(logger.level)}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Run on application shutdown."""
    logger.info(f"👋 {settings.PROJECT_NAME} shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


