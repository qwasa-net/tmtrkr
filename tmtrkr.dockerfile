# syntax=docker/dockerfile:experimental
FROM python:3.10-slim-buster

WORKDIR /tmtrkr

COPY  requirements*txt Makefile alembic.ini /tmtrkr/
COPY  tmtrkr /tmtrkr/tmtrkr
COPY  alembic /tmtrkr/alembic
COPY  www /tmtrkr/www
COPY  tests /tmtrkr/tests

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .
ENV TMTRKR_SERVER_BIND_PORT 8181
ENV TMTRKR_SERVER_BIND_HOST 0.0.0.0
ENV TMTRKR_DATABASE_URL sqlite:////tmtrkr/db/db.sqlite

RUN --mount=type=cache,mode=0755,id=pip-cache,target=/var/pip-cache \
    python3 -m venv _venv && \
    _venv/bin/pip install --cache-dir /var/pip-cache --upgrade pip && \
    _venv/bin/pip install --cache-dir /var/pip-cache -r requirements.txt && \
    mkdir -pv /tmtrkr/db/ && chmod 777 /tmtrkr/db && \
    _venv/bin/alembic --name alembic-container upgrade head

CMD _venv/bin/alembic --name alembic-container upgrade head && \
    _venv/bin/python tmtrkr/server/server.py


