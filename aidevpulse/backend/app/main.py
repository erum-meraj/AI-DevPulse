from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.tasks.celery_app import start_scheduler, stop_scheduler

settings = get_settings()
configure_logging(settings.ENVIRONMENT)
logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="AI DevPulse API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api/v1")

    @app.on_event("startup")
    async def on_startup() -> None:
        start_scheduler()
        logger.info("app_startup", environment=settings.ENVIRONMENT)

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        stop_scheduler()
        logger.info("app_shutdown", environment=settings.ENVIRONMENT)

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
