from typing import Annotated

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase

from backend.core.config import settings
from backend.core.database import SessionDep
from backend.core.logging import get_logger
from backend.mail.tasks import (
    send_register_task,
    send_reset_password_task,
    send_verify_task,
)
from backend.users.models import User

logger = get_logger(__name__)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.users.RESET_SECRET_KEY
    verification_token_secret = settings.users.VERIFICATION_SECRET_KEY

    async def on_after_register(
        self, user: User, request: Request | None = None
    ) -> None:
        await self.request_verify(user, request)

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ) -> None:
        await send_verify_task.kiq(user.email, token)
        logger.info("Verification email queued", extra={"email": user.email})

    async def on_after_verify(self, user: User, request: Request | None = None) -> None:
        await send_register_task.kiq(user.email)
        logger.info("Welcome email queued", extraнатсройик={"email": user.email})

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ) -> None:
        await send_reset_password_task.kiq(user.email, token)
        logger.info("Password reset email queued", extra={"email": user.email})


async def get_user_manager(session: SessionDep) -> UserManager:
    return UserManager(SQLAlchemyUserDatabase(session, User))


UserManagerDep = Annotated[UserManager, Depends(get_user_manager)]
