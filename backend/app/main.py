"""SentinelX FastAPI application entry point.

Configures middleware, exception handling, and API routers. Versioned routes
live under `/api/v1/*`. Interactive API docs are available at `/docs`.
"""

import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import configure_logging, logger
from app.api import api_router


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="SentinelX API",
        description="Open-source SOC and SIEM platform API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/api/v1/openapi.json",
    )

    # CORS — restricted to configured origins.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Request timing + security headers middleware.
    @app.middleware("http")
    async def timing_and_security_headers(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = (time.time() - start) * 1000
        response.headers["X-Process-Time"] = f"{duration:.2f}ms"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

    # Global exception handler for AppException.
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    # Health check.
    @app.get("/health", tags=["health"])
    async def health():
        return {"status": "ok", "service": settings.APP_NAME}

    # Versioned API router.
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
