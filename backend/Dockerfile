FROM python:3.14-slim
WORKDIR /backend
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libheif1 \
    && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt
COPY . .