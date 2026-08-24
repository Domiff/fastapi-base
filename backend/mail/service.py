from fastapi_mail.schemas import MessageType, MessageSchema as MailMessage
from pydantic import EmailStr

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.mail.config import mail
from backend.mail.enums import MessageCode
from backend.mail.messages import MessageSchema, get_message

logger = get_logger(__name__)

TEMPLATE_NAME = "email_message.html"


class MailService:
    """Тексты писем лежат в backend/mail/messages.py, вёрстка — в templates/mail."""

    def __init__(self):
        self.fm = mail

    @staticmethod
    def _build_context(
        message: MessageSchema, link: str | None = None
    ) -> dict[str, str]:
        context = {
            "app_name": settings.app.APP_TITLE,
            "subject": message.subject,
            "title": message.title,
            "body": message.body,
            "action": message.action,
        }

        if link:
            context["link"] = link

        return context

    async def _send(
        self, code: MessageCode, email: EmailStr, link: str | None = None
    ) -> None:
        message = get_message(code)
        mail_message = MailMessage(
            subject=message.subject,
            recipients=[email],
            template_body=self._build_context(message, link),
            subtype=MessageType.html,
        )
        await self.fm.send_message(mail_message, template_name=TEMPLATE_NAME)
        logger.info("Email sent", extra={"code": code, "email": email})

    async def send_register(self, email: EmailStr) -> None:
        await self._send(MessageCode.REGISTER, email)

    async def send_verify(self, email: EmailStr, token: str) -> None:
        link = settings.users.VERIFY_URL.format(
            base_url=settings.app.BASE_URL, token=token
        )
        await self._send(MessageCode.VERIFY, email, link)

    async def send_reset_password(self, email: EmailStr, token: str) -> None:
        link = settings.users.RESET_PASSWORD_URL.format(
            base_url=settings.app.BASE_URL, token=token
        )
        await self._send(MessageCode.RESET_PASSWORD, email, link)


def get_mail_service() -> MailService:
    return MailService()
