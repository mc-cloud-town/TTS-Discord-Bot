FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apk update && apk add --no-cache \
  ffmpeg \
  opus-dev \
  libsndfile

ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]
