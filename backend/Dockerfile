FROM python:3.14-slim
WORKDIR /backend
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .