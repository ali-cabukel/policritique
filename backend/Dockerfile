# syntax=docker/dockerfile:1
# API-only image for split docker-compose (frontend runs separately).

FROM python:3.13-slim

WORKDIR /app/backend

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY README.md /app/README.md
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY backend/README.md ./
COPY backend/src ./src
RUN uv sync --frozen --no-dev

ENV API_HOST=0.0.0.0
ENV API_PORT=8000
ENV DB_PATH=/app/backend/data/policritique.db

RUN mkdir -p /app/backend/data

EXPOSE 8000

CMD ["sh", "-c", "uv run policritique init-db && exec uv run policritique-api"]
