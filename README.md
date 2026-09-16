# FastAPI Base

A starter backend for FastAPI projects: user accounts with JWT auth, email delivery through a task queue,
Redis caching, S3 file storage and an admin panel — wired together and ready to build on.

## Features

- **Users and auth** on fastapi-users — registration, JWT login, email verification, password reset,
  user management endpoints
- **Admin panel** on SQLAdmin at `/admin` — sign-in with a real superuser from the database, a
  django-unfold–style theme with light and dark modes
- **Background tasks** on Taskiq with RabbitMQ — retries with exponential backoff, dead-letter and delay
  queues
- **Email** through fastapi-mail with HTML templates; sent from the worker, never from the request
- **Caching** with fastapi-cache2 on Redis, plus a thin Redis client
- **File storage** in S3-compatible buckets through fastapi-storages
- **Health check** at `/health` covering the database and Redis
- **Alembic migrations**, JSON logging in production, Docker Compose for the full stack

## Stack

| Layer | Choice |
|---|---|
| Web framework | FastAPI |
| Auth | fastapi-users, JWT, Argon2 via pwdlib |
| Admin | SQLAdmin |
| ORM | SQLAlchemy 2 (async) |
| Migrations | Alembic |
| Database | SQLite in debug, PostgreSQL via asyncpg otherwise |
| Cache | Redis, fastapi-cache2 |
| Task queue | Taskiq + RabbitMQ |
| Email | fastapi-mail, Mailpit for local testing |
| Storage | S3 via fastapi-storages |
| Settings | pydantic-settings |

Requires Python 3.14+.

## Project layout

```
backend/
  admin/          admin panel: setup, superuser auth, base view
  core/           settings, database, cache, broker, storage, logging, health check
  mail/           email texts, sending service, Taskiq tasks
  users/          user model, manager, auth backend, routers, schemas
  main.py         ASGI entry point
migrations/       Alembic
scripts/          management scripts (create_superuser)
static/           admin assets: css/admin.css theme
templates/
  mail/           email templates
  sqladmin/       SQLAdmin template overrides
run.sh            container entry point — migrations, then the API
taskiq.sh         container entry point — Taskiq worker
```

## Setup

Install dependencies:

```bash
uv sync
```

Create `.env` from the template and fill in the secrets:

```bash
cp .env.template .env
```

The keys below have no defaults, so the app won't start without them:

```dotenv
STRATEGY_SECRET_KEY=
RESET_SECRET_KEY=
VERIFICATION_SECRET_KEY=
ADMIN_SECRET_KEY=
```

Generate a value for each of them:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Create a superuser. The password is prompted for when `-p` is omitted:

```bash
uv run python scripts/create_superuser.py -e admin@example.com
```

## Running

### Locally

With `IS_DEBUG=true` the app uses SQLite. Redis, RabbitMQ and Mailpit still have to be running:

```bash
docker compose up -d redis rabbitmq mailpit
```

In `docker-compose.yaml` only RabbitMQ and Mailpit publish ports to the host. To reach Redis from a local
process, add `ports: ["6379:6379"]` to the `redis` service.

The API:

```bash
uv run fastapi dev --port 8080
```

The worker, which sends the emails:

```bash
uv run taskiq worker backend.core.broker:broker --fs-discover --tasks-pattern "backend/**/tasks.py"
```

| URL | What |
|---|---|
| `http://localhost:8080/docs` | Swagger UI, debug only |
| `http://localhost:8080/admin` | Admin panel |
| `http://localhost:8080/health` | Health check |
| `http://localhost:8025` | Mailpit inbox |
| `http://localhost:15672` | RabbitMQ management |

### Docker Compose

```bash
docker compose up -d --build
```

This starts the API, the worker, PostgreSQL, Redis, RabbitMQ and Mailpit. Compose forces `IS_DEBUG=false`
and points hosts at the service names. `run.sh` applies migrations before starting the API on `APP_PORT`.

Create the superuser inside the container:

```bash
docker compose exec backend python scripts/create_superuser.py -e admin@example.com
```

## API

| Prefix | Endpoints |
|---|---|
| `/auth` | `register`, `login`, `logout`, `forgot-password`, `reset-password`, `request-verify-token`, `verify` |
| `/users` | `me` (read, update), `{id}` (read, update, delete; superuser only) |
| `/health` | Database and Redis status; `503` if either is down |

After registration a verification email is queued. Once the address is verified, a welcome email follows.
Links in emails point to the frontend: `VERIFY_URL` and `RESET_PASSWORD_URL` are templates filled with
`{base_url}` and `{token}`.

## Admin panel

The admin lives at `/admin` (`ADMIN_BASE_URL`). There are no admin credentials in `.env`: you sign in with
the email and password of a user from the database, and only **active superusers** are let in. The password
check goes through `UserManager.authenticate`, the same one the API login uses.

The user is re-read from the database on every request. The session is dropped when the user is deactivated,
loses superuser rights or changes their password. `ADMIN_SECRET_KEY` only signs the session cookie, and with
`IS_DEBUG=false` the cookie is sent over HTTPS only.

Register model views in `backend/admin/`, subclassing `BaseAdmin` from `backend/admin/base.py`. Its defaults
are 25 rows per page and timestamped export file names. Then add the views in `setup_admin`:

```python
admin = Admin(...)
admin.add_view(UserAdmin)
```

### Theme

The theme is built on top of the Tabler CSS that SQLAdmin already ships, so it needs no extra frontend
dependencies. Templates in `templates/sqladmin/` take precedence over SQLAdmin's own. To tweak a page
without copying it whole, extend the original through the `sqladmin_original/` prefix.

| File | Role |
|---|---|
| `static/css/admin.css` | Design tokens, layout, restyled Tabler components |
| `templates/sqladmin/base.html` | Loads the Inter font and `admin.css`, applies the saved theme before first paint |
| `templates/sqladmin/layout.html` | Page shell: sidebar, breadcrumbs, language switcher, theme toggle |
| `templates/sqladmin/_menu.html` | Sidebar macros — categories render as headed sections |
| `templates/sqladmin/index.html` | Dashboard with a card per admin view |
| `templates/sqladmin/login.html` | Email and password sign-in |
| `templates/sqladmin/create.html`, `edit.html` | Form submit buttons |

Colors are CSS variables at the top of `admin.css`: `:root` holds the light theme, `[data-bs-theme="dark"]`
the dark one. Change the accent with `--ta-primary` / `--ta-primary-rgb`. The chosen theme is stored in
`localStorage`; on first visit it follows the system preference. Without a `favicon_url`, the sidebar and
login page show the first letter of `APP_TITLE` as the logo.

## Configuration

All settings are read from `.env`; see `.env.template` for the full list. Anything with a default can be
omitted.

| Variable | Default | Purpose |
|---|---|---|
| `APP_NAME` | `app` | Cache prefix, queue and container names |
| `APP_TITLE` | `FastAPI Base` | OpenAPI title, admin title, app name in emails |
| `APP_PORT` | — | Port for `run.sh` and Compose |
| `IS_DEBUG` | `true` | SQLite vs PostgreSQL, log format, OpenAPI docs, secure admin cookie |
| `BASE_URL` | `http://localhost:8080` | Frontend URL used in email links |
| `LOG_LEVEL` | `INFO` | |
| `CORS_ORIGINS` | `["127.0.0.1", "localhost"]` | Allowed origins |
| `CORS_ALLOW_CREDENTIALS` | `true` | |
| `CORS_ALLOW_METHODS` / `CORS_ALLOW_HEADERS` | `["*"]` | |
| `STRATEGY_SECRET_KEY` | — | JWT signing key |
| `RESET_SECRET_KEY` / `VERIFICATION_SECRET_KEY` | — | Password reset and verification token keys |
| `LIFETIME_SECONDS` | `3600` | JWT lifetime |
| `ADMIN_SECRET_KEY` | — | Admin session cookie signing key |
| `ADMIN_BASE_URL` | `/admin` | Admin mount path |
| `DB_URL` | — | Overrides the SQLite/PostgreSQL choice when set |
| `SQLITE_URL` | `sqlite+aiosqlite:///db.sqlite3` | Used when `IS_DEBUG=true` |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_HOST` / `POSTGRES_PORT` | `localhost:5432` | Used when `IS_DEBUG=false` |
| `REDIS_URL` or `REDIS_HOST` / `REDIS_PORT` / `REDIS_DB` | `localhost:6379/0` | |
| `EXPIRE` | `3600` | Default cache TTL in seconds |
| `RABBITMQ_URL` or `RABBITMQ_USER` / `RABBITMQ_PASSWORD` / `RABBITMQ_HOST` / `RABBITMQ_PORT` | `guest@localhost:5672` | |
| `TASKIQ_RETRY_COUNT` / `TASKIQ_RETRY_DELAY` | `5` / `10` | Task retry policy |
| `MAIL_*`, `USE_CREDENTIALS`, `VALIDATE_CERTS` | Mailpit on `localhost:1025` | SMTP settings |
| `AWS_*` | — | S3 credentials, bucket and endpoint |

## Development

### Models and migrations

Models inherit from `Base` in `backend/core/database.py`, which adds `id`, `created_at` and `updated_at`.
Import new models in `migrations/env.py` so autogenerate can see them, then:

```bash
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
```

Generated migrations are formatted with black through an Alembic post-write hook.

### Files

Use `FileType` from `backend/core/database.py` for file columns. It stores files in the configured S3 bucket:

```python
avatar: Mapped[str | None] = mapped_column(FileType("avatars"))
```

The S3 client is created on first use, so the app starts without S3 configured.

### Tasks

Put tasks in a `tasks.py` module inside any package under `backend/`; the worker discovers them by pattern.
Enqueue with `.kiq()`:

```python
await send_verify_task.kiq(user.email, token)
```

### Emails

Email texts live in `backend/mail/messages.py`, keyed by `MessageCode`. Markup lives in
`templates/mail/email_message.html`.

### Logging

Readable output in debug, JSON in production. Pass structured fields through `extra`:

```python
logger.info("Email sent", extra={"email": email})
```
