VENV ?= _venv
PYTHON_SYSTEM ?= /usr/bin/python3
PYTHON ?= "${VENV}/bin/python"
PIP ?= "${VENV}/bin/pip"
ALEMBIC ?= "${VENV}/bin/alembic"
FLAKE8 ?= "${VENV}/bin/flake8"
DOCKER ?= DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker

env:  # create vrtual env
	$(PYTHON_SYSTEM) -m venv $(VENV)
	$(PIP) install -U pip
	# pip install sqlalchemy alembic fastapi uvicorn
	$(PIP) install -r requirements.txt


env_dev: env
	# pip install black flake8 pytest pydocstyle pycodestyle
	$(PIP) install -r requirements-dev.txt


run:  # run demo server
	PYTHONPATH=. $(PYTHON) server/server.py


initdb:  # apply all db migrations
	$(ALEMBIC) upgrade head


lint:
	$(FLAKE8) --statistics tmtrkr server


clean:
	find ./tmtrkr -iname '*.pyc' -print -delete
	find ./tmtrkr -iname '*.pyo' -print -delete
	find ./tmtrkr -iname __pycache__ -print -delete


container_build:
	$(DOCKER) build . -f tmtrkr.dockerfile -t tmtrkr


container_run:
	-mkdir -pv _db
	$(DOCKER) run --publish 8181:8181 --volume "$$(pwd)/_db:/tmtrkr/db" -ti tmtrkr

