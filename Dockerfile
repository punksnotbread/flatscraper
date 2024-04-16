FROM python:3.11-slim

ARG SPIDER
ENV SPIDER=${SPIDER}
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN apt-get update && apt-get install --no-install-recommends -y curl \
    && curl -sSL https://install.python-poetry.org | python

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
COPY README.md /app/

RUN poetry config virtualenvs.create false && poetry install --only main

COPY . /app/

CMD scrapy crawl $SPIDER
