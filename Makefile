BASE_DIR ?= $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

VENV ?= $(BASE_DIR)/_venv
PYTHON_SYSTEM ?= /usr/bin/python3
PYTHON ?= "${VENV}/bin/python"
PIP ?= "${VENV}/bin/pip"
ALEMBIC ?= "${VENV}/bin/alembic"
FLAKE8 ?= "${VENV}/bin/flake8"
DOCKER ?= DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker


tea: env env_dev lint test initdb run


env:  # create vrtual env
	$(PYTHON_SYSTEM) -m venv $(VENV)
	$(PIP) install -U pip
	# pip install sqlalchemy alembic fastapi uvicorn
	$(PIP) install -r requirements.txt


env_dev: env
	# pip install black flake8 pytest pydocstyle pycodestyle
	$(PIP) install -r requirements-dev.txt


run: DATABASE_URL ?= $(BASE_DIR)/db.sqlite
run:  # run demo server
	cd "$(BASE_DIR)"; \
	PYTHONPATH=.:"$(BASE_DIR)" \
	TMTRKR_DATABASE_URL="sqlite:///$(DATABASE_URL)" \
	$(PYTHON) server/server.py


initdb: DATABASE_URL ?= $(BASE_DIR)/db.sqlite
initdb:  # apply all db migrations
	cd "$(BASE_DIR)"; \
	TMTRKR_DATABASE_URL="sqlite:///$(DATABASE_URL)" \
	$(ALEMBIC) upgrade head; \
	TMTRKR_DATABASE_URL="sqlite:///$(DATABASE_URL)" \
	$(ALEMBIC) current


lint:
	$(FLAKE8) --statistics tmtrkr server


test: DATABASE_URL ?= $(shell mktemp)
test:
	TMTRKR_DATABASE_URL="sqlite:///$(DATABASE_URL)" $(PYTHON) -u -m unittest -v
	@rm -v "$(DATABASE_URL)"


clean:
	find ./tmtrkr -iname '*.pyc' -print -delete
	find ./tmtrkr -iname '*.pyo' -print -delete
	find ./tmtrkr -iname __pycache__ -print -delete


container_build:
	$(DOCKER) build . -f tmtrkr.dockerfile -t tmtrkr


container_run:
	-mkdir -pv _db
	$(DOCKER) run --publish 8181:8181 --volume "$$(pwd)/_db:/tmtrkr/db" --tty --interactive tmtrkr

