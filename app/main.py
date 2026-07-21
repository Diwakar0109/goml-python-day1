from fastapi import FastAPI

from app.api.ticket import router as ticket_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
)

app.include_router(ticket_router)


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.API_VERSION,
    }