FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
  ffmpeg \
  libopus \
  libsndfile1 \
  && rm -rf /var/lib/apt/lists/*

COPY uv.lock pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --locked --no-install-project

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "python", "run.py"]
