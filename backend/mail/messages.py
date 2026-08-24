from backend.core.schemas import BaseSchema
from backend.mail.enums import MessageCode


class MessageSchema(BaseSchema):
    subject: str
    title: str
    body: str
    action: str | None = None


MESSAGES: dict[MessageCode, MessageSchema] = {
    MessageCode.REGISTER: MessageSchema(
        subject="Добро пожаловать",
        title="Аккаунт подтверждён",
        body="Почта подтверждена, аккаунтом можно пользоваться.",
    ),
    MessageCode.VERIFY: MessageSchema(
        subject="Подтверждение почты",
        title="Подтвердите адрес",
        body="Чтобы закончить регистрацию, подтвердите адрес почты.",
        action="Подтвердить",
    ),
    MessageCode.RESET_PASSWORD: MessageSchema(
        subject="Сброс пароля",
        title="Новый пароль",
        body="Если сброс пароля запрашивали не вы, просто проигнорируйте письмо.",
        action="Сбросить пароль",
    ),
}


def get_message(code: MessageCode) -> MessageSchema:
    return MESSAGES[code]
