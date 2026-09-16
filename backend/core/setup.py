from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.admin.setup import setup_admin
from backend.core.broker import broker
from backend.core.cache import setup_cache
from backend.core.config import settings
from backend.core.health import router as health_router
from backend.core.logging import get_logger, setup_logging
from backend.users.routers import auth_router, users_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application")

    setup_cache(settings.app.APP_NAME)

    if not broker.is_worker_process:
        await broker.startup()
        logger.info("Starting broker")

    yield

    if not broker.is_worker_process:
        await broker.shutdown()
        logger.info("Stopping broker")

    logger.info("Stopping application")


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.app.APP_TITLE,
        version=settings.app.APP_VERSION,
        lifespan=lifespan,
        openapi_url="/openapi.json" if settings.app.IS_DEBUG else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.CORS_ORIGINS,
        allow_credentials=settings.cors.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.cors.CORS_ALLOW_METHODS,
        allow_headers=settings.cors.CORS_ALLOW_HEADERS,
    )

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(users_router)

    setup_admin(app)

    return app
