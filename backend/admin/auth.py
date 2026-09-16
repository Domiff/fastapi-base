import hashlib
from types import SimpleNamespace

from fastapi_users.db import SQLAlchemyUserDatabase
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from backend.core.database import session_maker
from backend.core.logging import get_logger
from backend.users.managers import UserManager
from backend.users.models import User

logger = get_logger(__name__)


def _password_fingerprint(user: User) -> str:
    """Смена пароля меняет отпечаток, и старые сессии админки перестают действовать."""
    return hashlib.sha256(user.hashed_password.encode()).hexdigest()[:32]


def _can_access(user: User | None) -> bool:
    return user is not None and user.is_active and user.is_superuser


class AdminAuth(AuthenticationBackend):
    USER_ID_KEY = "admin_user_id"
    EMAIL_KEY = "admin_email"
    FINGERPRINT_KEY = "admin_password_fp"

    async def login(self, request: Request) -> bool:
        form = await request.form()
        credentials = SimpleNamespace(
            username=str(form.get("username", "")).strip(),
            password=str(form.get("password", "")),
        )

        async with session_maker() as session:
            manager = UserManager(SQLAlchemyUserDatabase(session, User))
            user = await manager.authenticate(credentials)

        if not _can_access(user):
            logger.warning("admin_login_failed", extra={"email": credentials.username})
            return False

        request.session.update(
            {
                self.USER_ID_KEY: user.id,
                self.EMAIL_KEY: user.email,
                self.FINGERPRINT_KEY: _password_fingerprint(user),
            }
        )
        logger.info("admin_login_success", extra={"email": user.email})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get(self.USER_ID_KEY)
        if user_id is None:
            return False

        async with session_maker() as session:
            user = await session.get(User, user_id)

        fingerprint = request.session.get(self.FINGERPRINT_KEY)
        if not _can_access(user) or fingerprint != _password_fingerprint(user):
            request.session.clear()
            return False

        return True
