FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev


FROM python:3.13-slim

RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid 1000 --create-home app

WORKDIR /app

COPY --from=builder /app /app

RUN mkdir -p /app/logs && chown -R app:app /app/logs

USER app

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["python", "main.py"]
