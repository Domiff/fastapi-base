from enum import StrEnum


class MessageCode(StrEnum):
    REGISTER = "register"
    VERIFY = "verify"
    RESET_PASSWORD = "reset_password"
