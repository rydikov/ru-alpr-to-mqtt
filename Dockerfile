FROM python:3.13.3-slim

ENV TZ Europe/Moscow
ENV PYTHONDONTWRITEBYTECODE yes

RUN apt update && apt install -y --no-install-recommends libgl1 libglib2.0-0

WORKDIR /app

COPY requires.txt requires.txt
RUN python3 -m pip install --upgrade pip
RUN pip install -r requires.txt

COPY server.py server.py