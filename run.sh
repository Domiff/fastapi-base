#!/bin/sh
alembic upgrade head
fastapi run --port "${APP_PORT}"
