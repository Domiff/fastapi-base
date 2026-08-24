from backend.core.broker import broker
from backend.mail.service import get_mail_service


@broker.task("send_register_task", retry_on_error=True)
async def send_register_task(email: str) -> None:
    await get_mail_service().send_register(email)


@broker.task("send_verify_task", retry_on_error=True)
async def send_verify_task(email: str, token: str) -> None:
    await get_mail_service().send_verify(email, token)


@broker.task("send_reset_password_task", retry_on_error=True)
async def send_reset_password_task(email: str, token: str) -> None:
    await get_mail_service().send_reset_password(email, token)
