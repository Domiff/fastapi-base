from typing import Annotated

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from backend.core.config import settings
from backend.users.managers import get_user_manager
from backend.users.models import User


def get_authentication_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.users.STRATEGY_SECRET_KEY,
        lifetime_seconds=settings.users.LIFETIME_SECONDS,
    )


bearer_transport = BearerTransport(tokenUrl=settings.users.TOKEN_URL)

auth_backend = AuthenticationBackend(
    name="jwt", transport=bearer_transport, get_strategy=get_authentication_strategy
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)

CurrentUserDep = Annotated[User, Depends(current_active_user)]
CurrentSuperuserDep = Annotated[User, Depends(current_superuser)]
