FROM python:3.12-slim AS builder

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY uv.lock pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-install-project

COPY . .
RUN uv sync

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
  ffmpeg \
  libopus0 \
  libsndfile1 \
  && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY --from=builder /app /app

ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "python", "run.py"]
