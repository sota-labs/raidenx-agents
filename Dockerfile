FROM python:3.10-slim-bullseye

WORKDIR /app
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

ENV APP_MODULE=app:app \
    HOST=0.0.0.0 \
    PORT=4009 \
    WORKERS=5

EXPOSE 4009

CMD uvicorn ${APP_MODULE} --host ${HOST} --port ${PORT} --workers ${WORKERS}