BASE_DIR ?= $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

VENV ?= $(BASE_DIR)/_venv
PYTHON_SYSTEM ?= /usr/bin/python3
PYTHON ?= "$(VENV)/bin/python"
PIP ?= "$(VENV)/bin/pip"
ALEMBIC ?= "$(VENV)/bin/alembic"

LINTER_PY ?= "$(VENV)/bin/flake8" --statistics
FORMATTER1_PY ?= "$(VENV)/bin/isort"
FORMATTER2_PY ?= "$(VENV)/bin/black"
FORMATTER_WWW_JS ?= "$(VENV)/bin/js-beautify" --replace --end-with-newline --brace-style=collapse,preserve-inline
FORMATTER_WWW_CSS ?= "$(VENV)/bin/css-beautify" --replace --end-with-newline

DOCKER ?= DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker
IMAGE_NAME ?= tmtrkr:latest
CONTAINER_NAME ?= tmtrkr

DATABASE_URL ?= "sqlite:///$(BASE_DIR)/db.sqlite"

VERSION_HASH := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown-version")
PYTHONPATH := "$(BASE_DIR)":$(PYTHONPATH)


help:
	-@echo 'How to `make` it:'
	-@grep ' \ ##' $(realpath $(firstword $(MAKEFILE_LIST))) | sed 's/^/  - /ig'


## all in one
tea: env env-dev lint test initdb demodb run  ## do magic, start from here


## envs
env:  ## create python vrtual env
	@$(PYTHON_SYSTEM) --version
	[ -e $(PYTHON) ] || $(PYTHON_SYSTEM) -m venv --clear $(VENV) && ls -l $(PYTHON)
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-psql.txt || echo "WARNING: PostgreSQL drivers is not installed!"

env-dev: env ## add dev tools
	# pip install black flake8 pytest
	$(PIP) install --upgrade --upgrade-strategy eager -r requirements-dev.txt


## init and run
run:  ## run demo server
	PYTHONPATH=$(PYTHONPATH) \
	TMTRKR_DATABASE_URL=$(DATABASE_URL) \
	$(PYTHON) tmtrkr/server/server.py


initdb:  ## apply all db migrations
	PYTHONPATH=$(PYTHONPATH) \
	TMTRKR_DATABASE_URL=$(DATABASE_URL) \
	$(ALEMBIC) upgrade head
	PYTHONPATH=$(PYTHONPATH) \
	TMTRKR_DATABASE_URL=$(DATABASE_URL) \
	$(ALEMBIC) current


demodb: initdb  ## create demo db
	PYTHONPATH=$(PYTHONPATH) \
	TMTRKR_DATABASE_URL="$(DATABASE_URL)" \
	$(PYTHON) tmtrkr/misc/demodb.py --only-if-empty


## dev tools
lint:  # run source code linters
	$(LINTER_PY) tmtrkr tests
	$(FORMATTER1_PY) --check tmtrkr tests
	$(FORMATTER2_PY) --check tmtrkr tests


format:  # run source code formatters
	$(FORMATTER1_PY) tmtrkr tests
	$(FORMATTER2_PY) tmtrkr tests
	$(FORMATTER_WWW_JS) www/js/tmtrkr.js
	$(FORMATTER_WWW_CSS) www/css/tmtrkr.css


test: TEST_DATABASE_DIR := $(shell mktemp)
test:  # run tests
	PYTHONPATH=$(PYTHONPATH) \
	TMTRKR_DATABASE_URL="sqlite:///$(TEST_DATABASE_DIR)" \
	$(PYTHON) -u -m unittest -v --failfast
	-rm -v "$(TEST_DATABASE_DIR)"


clean:  # cleanup python cache
	find ./tmtrkr -iname '*.py[co]' -print -delete
	find ./tmtrkr -iname __pycache__ -print -delete


## container stuff
container-build:  ## build tmtrkr image
	$(DOCKER) build . --file tmtrkr.dockerfile --tag $(IMAGE_NAME)


container-run:  ## run tmtrkr container
	-$(DOCKER) run --publish 8181:8181 \
	--rm=true --tty --interactive --name $(CONTAINER_NAME) $(IMAGE_NAME)


container-run-db-sqlite: TMTRKR_DATABASE_PATH ?= "$(shell pwd)"/_db
container-run-db-sqlite: ## run container and mount database from './_db/'
	-mkdir -pv $(TMTRKR_DATABASE_PATH)
	-$(DOCKER) run --publish 8181:8181 \
	--mount "type=bind,src=$(TMTRKR_DATABASE_PATH),dst=/tmtrkr/db" \
	--rm=true --tty --interactive  --name $(CONTAINER_NAME) $(IMAGE_NAME)


## zipapp fun
zipapp-build: ZIPAPP_BUILD_PATH := $(shell mktemp --directory --dry-run)/tmtrkr_app
zipapp-build: ZIPAPP_BUILD_OUTPUT := "tmtrkr-$(VERSION_HASH).pyz"
zipapp-build: env clean  ## pack app into .pyz, run it: 'python3 tmtrtk.pyz'
	mkdir -pv "$(ZIPAPP_BUILD_PATH)"
	$(PIP) install -r requirements.txt --no-deps --target "$(ZIPAPP_BUILD_PATH)"
	# FIXME: UGLY HACK -- cryptography binary bindings do not work from zipapp, do not pack them, use system
	# $(PIP) uninstall --target "$(ZIPAPP_BUILD_PATH)" cffi cryptography # and this does not work
	-find "$(ZIPAPP_BUILD_PATH)/cryptography/" -iname '*.py' -print -delete
	# copy app and statics
	cp -rv tmtrkr "$(ZIPAPP_BUILD_PATH)"
	cp -rv zipapp/__main__.py "$(ZIPAPP_BUILD_PATH)"
	cp -rv www "$(ZIPAPP_BUILD_PATH)/tmtrkr/"
	# build a zippapp
	$(PYTHON_SYSTEM) -m zipapp --compress --output $(ZIPAPP_BUILD_OUTPUT) --python $(PYTHON_SYSTEM) "$(ZIPAPP_BUILD_PATH)"
	rm -rfv "$(ZIPAPP_BUILD_PATH)"
	ls -lh "$(ZIPAPP_BUILD_OUTPUT)"


	### === === === === === === === === === === === === === === ===
	### 2FIXME: zipapp is broken for now, do not use it
	### === === === === === === === === === === === === === === ===
	### ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'
	### a C extension … cannot be run from a zip file
	### https://docs.python.org/3/library/zipapp.html#caveats
	### === === === === === === === === === === === === === === ===

zipapp-run: ZIPAPP_BUILD_OUTPUT := "tmtrkr-$(VERSION_HASH).pyz"
zipapp-run: zipapp-build
	$(PYTHON) "$(ZIPAPP_BUILD_OUTPUT)"
