# syntax=docker/dockerfile:experimental
ARG BASE_IMAGE=python:3.11-slim
FROM ${BASE_IMAGE}

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /tmtrkr
ENV TMTRKR_SERVER_BIND_PORT 8181
ENV TMTRKR_SERVER_BIND_HOST 0.0.0.0
ENV TMTRKR_DATABASE_URL sqlite:////tmtrkr/db/db.sqlite

RUN apt-get update && \
    apt-get upgrade --yes --only-upgrade && \
    apt-get install --yes --no-install-recommends libpq5 && \
    apt-get clean

WORKDIR /tmtrkr

COPY  requirements*txt Makefile alembic.ini /tmtrkr/
COPY  tmtrkr /tmtrkr/tmtrkr
COPY  alembic /tmtrkr/alembic
COPY  www /tmtrkr/www
COPY  tests /tmtrkr/tests

RUN --mount=type=cache,mode=0755,id=pip-cache,target=/var/pip-cache \
    python3 -m venv _venv && \
    _venv/bin/pip install --cache-dir /var/pip-cache --upgrade pip wheel && \
    _venv/bin/pip install --cache-dir /var/pip-cache --prefer-binary -r requirements.txt && \
    _venv/bin/pip install --cache-dir /var/pip-cache --prefer-binary -r requirements-psql.txt && \
    mkdir -pv /tmtrkr/db/ && chmod 777 /tmtrkr/db && \
    _venv/bin/alembic --name alembic-container upgrade head && \
    _venv/bin/python tmtrkr/misc/demodb.py >/dev/null

CMD _venv/bin/alembic --name alembic-container upgrade head && \
    _venv/bin/python tmtrkr/server/server.py


