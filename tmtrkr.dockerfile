# syntax=docker/dockerfile:experimental
FROM python:3.10-slim-buster

RUN useradd --uid 9999  --shell /bin/bash --create-home --home-dir /tmtrkr tmtrkr

USER tmtrkr
WORKDIR /tmtrkr

COPY --chown=tmtrkr requirements*txt Makefile alembic.ini /tmtrkr/
COPY --chown=tmtrkr tmtrkr /tmtrkr/tmtrkr
COPY --chown=tmtrkr alembic /tmtrkr/alembic
COPY --chown=tmtrkr server /tmtrkr/server
COPY --chown=tmtrkr client /tmtrkr/client
COPY --chown=tmtrkr tests /tmtrkr/tests

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .
ENV TMTRKR_SERVER_BIND_PORT 8181
ENV TMTRKR_SERVER_BIND_HOST 0.0.0.0
ENV TMTRKR_DATABASE_URL sqlite:////tmtrkr/db/db.sqlite

RUN --mount=type=cache,mode=0755,uid=9999,id=pip-cache,target=/tmtrkr/.cache/pip \
    python3 -m venv _venv && \
    _venv/bin/pip install -U pip && \
    _venv/bin/pip install -r requirements.txt && \
    mkdir -pv /tmtrkr/db/ && \
    _venv/bin/alembic --name alembic-container upgrade head

CMD _venv/bin/python server/server.py


