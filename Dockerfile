FROM python:3.12-alpine

WORKDIR /app

RUN apk update && apk add --no-cache \
  ffmpeg \
  opus \
  opus-dev \
  libsndfile \
  curl

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:/root/.cargo/bin:$PATH"

COPY . .

RUN uv sync --no-install-project

ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "python", "run.py"]
