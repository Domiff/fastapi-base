from fastapi import APIRouter, Response, status

from backend.core.cache import redis
from backend.core.database import ping_database

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health(response: Response) -> dict[str, bool | str]:
    database = await ping_database()
    cache = await redis.ping()

    if not (database and cache):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "Good" if database and cache else "Bad",
        "database": database,
        "cache": cache,
    }
