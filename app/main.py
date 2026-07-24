from contextlib import asynccontextmanager
import logging
import time

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from app.api.ticket import router as ticket_router
from app.api.ai import router as ai_router
from app.core.config import settings
from app.core.deps import get_db
from app.db.session import engine

# Configure structured application logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application is starting...")
    yield
    logger.info("Shutting down application and disposing database engine...")
    await engine.dispose()
    logger.info("Database engine disposed. Shutdown complete.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info("Request started: %s %s", request.method, request.url.path)

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    logger.info("Request completed: %s %s status=%d duration=%.4fs", 
                request.method, request.url.path, response.status_code, process_time)

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error("Database exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred processing your request."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )


app.include_router(ticket_router)
app.include_router(ai_router)


@app.get(
    "/",
    summary="Root Welcome Endpoint",
    description="Returns welcome message and API version.",
)
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.API_VERSION,
    }


@app.get(
    "/health",
    summary="Service Health Check",
    description="Verifies API service and database connectivity.",
)
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("Health check failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.API_VERSION,
    }


@app.get(
    "/ready",
    summary="Service Readiness Check",
    description="Confirms database is ready to accept traffic.",
)
async def ready(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("Readiness check failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not ready"
        )
    return {
        "status": "ready",
    }