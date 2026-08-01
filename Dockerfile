# syntax=docker/dockerfile:1
# Cloud Run bundle: Vite static build + FastAPI on one port.

FROM node:22-alpine AS web

WORKDIR /app/frontend

COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install --frozen-lockfile

COPY frontend/ ./

ENV VITE_API_URL=

RUN yarn build

FROM python:3.13-slim AS api

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

COPY --from=web /app/frontend/dist /app/static

ENV API_HOST=0.0.0.0
ENV API_PORT=8000
ENV STATIC_DIR=/app/static
ENV DB_PATH=/app/backend/data/policritique.db
ENV CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
ENV LLM_PROVIDER=openai
ENV DATABASE_SCHEMA=policritique

RUN mkdir -p /app/backend/data

EXPOSE 8000

CMD ["sh", "-c", "uv run policritique init-db && exec uv run policritique-api"]
