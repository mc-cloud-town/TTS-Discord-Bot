FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apk update && apk add --no-cache \
  ffmpeg \
  libsndfile

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "run.py"]
