# syntax=docker/dockerfile:1

FROM python:3.12-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1

# Install locked runtime dependencies before the source so this layer stays
# cached when only application code changes.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY . /app

ENV PATH="/app/.venv/bin:$PATH"

# Dummy values exist only for this build step. They are not stored as image ENV.
RUN DJANGO_DEBUG=0 \
    DJANGO_SECRET_KEY=collectstatic-build-key \
    DATABASE_URL=sqlite:////tmp/collectstatic.sqlite3 \
    python manage.py collectstatic --noinput

FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_DEBUG=0

RUN useradd --create-home --uid 1000 --shell /usr/sbin/nologin app

COPY --from=builder --chown=app:app /app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/')"

# Gunicorn serves the site. WhiteNoise serves collected static files.
# DJANGO_DEBUG defaults to 0; pass a real DJANGO_SECRET_KEY and DATABASE_URL.
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers ${WEB_CONCURRENCY:-2} --timeout 60 --access-logfile - --error-logfile -"]
