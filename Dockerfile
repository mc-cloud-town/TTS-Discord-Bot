FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y \
  ffmpeg \
  libsndfile1 \
  rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "run.py"]
