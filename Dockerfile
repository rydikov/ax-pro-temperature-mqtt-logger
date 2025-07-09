FROM python:3.13.3-slim

ENV PYTHONDONTWRITEBYTECODE yes

RUN apt-get update
RUN apt-get install -y git

WORKDIR /app

COPY requires.txt requires.txt
RUN python3 -m pip install --upgrade pip
RUN pip install -r requires.txt

RUN pip install -e git+https://github.com/rydikov/ax-pro.git@3eee067bc3e15ac5b004d885ef2e213a3380ff8b#egg=axpro

COPY logger logger
COPY logger.py logger.py