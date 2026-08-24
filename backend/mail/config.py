from fastapi_mail import ConnectionConfig, FastMail

from backend.core.config import settings

config = ConnectionConfig(
    MAIL_USERNAME=settings.mail.MAIL_USERNAME,
    MAIL_PASSWORD=settings.mail.MAIL_PASSWORD,
    MAIL_FROM=settings.mail.MAIL_FROM,
    MAIL_PORT=settings.mail.MAIL_PORT,
    MAIL_SERVER=settings.mail.MAIL_SERVER,
    MAIL_STARTTLS=settings.mail.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.mail.MAIL_SSL_TLS,
    TEMPLATE_FOLDER=settings.mail.TEMPLATE_FOLDER,
    USE_CREDENTIALS=settings.mail.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.mail.VALIDATE_CERTS,
)
mail = FastMail(config)
