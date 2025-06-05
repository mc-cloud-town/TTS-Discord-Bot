FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apk update && apk add --no-cache \
  ffmpeg \
  opus \
  opus-dev \
  libsndfile

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]
