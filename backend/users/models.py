from fastapi_users.db import SQLAlchemyBaseUserTable

from backend.core.database import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"

    def __str__(self) -> str:
        return self.email
