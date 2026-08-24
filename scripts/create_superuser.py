import argparse
import asyncio
import getpass
import sys

from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from backend.core.database import session_maker
from backend.core.security import hash_password
from backend.users.models import User


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Создание суперпользователя")
    parser.add_argument("-e", "--email", required=True, help="почта")
    parser.add_argument("-p", "--password", help="пароль; спросим, если не указан")
    return parser.parse_args()


async def create_superuser(email: str, password: str) -> None:
    async with session_maker() as session:
        query = insert(User).values(
            email=email,
            hashed_password=hash_password(password),
            is_active=True,
            is_superuser=True,
            is_verified=True,
        )
        await session.execute(query)
        await session.commit()


def main() -> int:
    args = parse_args()

    password = args.password or getpass.getpass("Пароль: ")

    if not password:
        print("Пароль не может быть пустым", file=sys.stderr)
        return 1

    try:
        asyncio.run(create_superuser(args.email, password))
    except IntegrityError:
        print(f"Пользователь {args.email!r} уже существует", file=sys.stderr)
        return 1

    print(f"Создан суперпользователь {args.email!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
