"""
Main Application Entry Point
============================
FastAPI application instance with middleware and routing setup.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.core.config import settings
from app.api.v1.api import api_router

# ... inside the rest of the file (skipping down to the router inclusion)



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Handles Redis connection for caching.
    """
    # Startup logic
    import redis.asyncio as redis
    from fastapi_cache import FastAPICache
    from fastapi_cache.backends.redis import RedisBackend

    redis_client = redis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    
    yield
    
    # Shutdown logic
    await redis_client.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health Check"])
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {"status": "healthy", "project": settings.PROJECT_NAME}
