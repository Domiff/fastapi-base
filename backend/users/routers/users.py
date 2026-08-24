from fastapi import APIRouter

from backend.users.auth import fastapi_users
from backend.users.schemas import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])

router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))
