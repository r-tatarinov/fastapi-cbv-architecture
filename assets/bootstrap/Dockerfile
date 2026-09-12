FROM python:3.12-slim

ENV TZ=Europe/Moscow
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /src/app

RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel
COPY src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/app/ ./
