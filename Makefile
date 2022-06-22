BASE_DIR ?= $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

VENV ?= $(BASE_DIR)/_venv
PYTHON_SYSTEM ?= /usr/bin/python3
PYTHON ?= "${VENV}/bin/python"
PIP ?= "${VENV}/bin/pip"
ALEMBIC ?= "${VENV}/bin/alembic"
FLAKE8 ?= "${VENV}/bin/flake8"
FORMATTER_PY ?= "${VENV}/bin/black"
FORMATTER_WWW_JS ?= "${VENV}/bin/js-beautify" --replace --end-with-newline --brace-style=collapse,preserve-inline
FORMATTER_WWW_CSS ?= "${VENV}/bin/css-beautify" --replace --end-with-newline
DOCKER ?= DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker
DATABASE_URL ?= $(BASE_DIR)/db.sqlite
VERSION_HASH ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown-version")


help:
	-@echo 'How to `make` it:'
	-@grep ' \ ##' $(realpath $(firstword $(MAKEFILE_LIST))) | sed 's/^/  - /ig'


tea: env env_dev lint test initdb demodb run  ## do magic, start from here


env:  ## create python vrtual env
	@$(PYTHON_SYSTEM) --version
	[ -e $(PYTHON) ] || $(PYTHON_SYSTEM) -m venv --clear $(VENV) && ls -l $(PYTHON)
	$(PIP) install -U pip
	# pip install sqlalchemy alembic fastapi uvicorn
	$(PIP) install -r requirements.txt


env_dev: env
	# pip install black flake8 pytest pydocstyle pycodestyle
	$(PIP) install -r requirements-dev.txt


run:  ## run demo server
	cd "$(BASE_DIR)"; \
	PYTHONPATH=.:"$(BASE_DIR)" \
	TMTRKR_DATABASE_URL="sqlite:///$(DATABASE_URL)" \
	$(PYTHON) tmtrkr/server/server.py


initdb:  ## apply all db migrations
	cd "$(BASE_DIR)"; \
	TMTRKR_DATABASE_URL="sqlite:///$(DATABASE_URL)" \
	$(ALEMBIC) upgrade head; \
	TMTRKR_DATABASE_URL="sqlite:///$(DATABASE_URL)" \
	$(ALEMBIC) current


demodb: initdb  ## create demo db
	cd "$(BASE_DIR)"; \
	TMTRKR_DATABASE_URL="sqlite:///$(DATABASE_URL)" \
	$(PYTHON) tmtrkr/misc/demodb.py --only-if-empty


lint:  # run source code linters
	$(FLAKE8) --statistics tmtrkr
	$(FORMATTER_PY) --check tmtrkr tests


format:  # run source code formatters
	$(FORMATTER_PY) tmtrkr tests
	$(FORMATTER_WWW_JS) www/js/tmtrkr.js
	$(FORMATTER_WWW_CSS) www/css/tmtrkr.css


test: TEST_DATABASE_URL ?= $(shell mktemp)
test:  # run tests
	TMTRKR_DATABASE_URL="sqlite:///$(TEST_DATABASE_URL)" $(PYTHON) -u -m unittest -v
	-rm -v "$(TEST_DATABASE_URL)"


clean:  # cleanup python cache
	find ./tmtrkr -iname '*.py[co]' -print -delete
	find ./tmtrkr -iname __pycache__ -print -delete


container_build:  ## build tmtrkr image
	$(DOCKER) build . --file tmtrkr.dockerfile --tag tmtrkr


container_run:  ## run tmtrkr container
	-$(DOCKER) run --publish 8181:8181 --rm=true --tty --interactive tmtrkr


container_run_db: # run container and mount database from './_db/'
	-mkdir -pv _db
	-$(DOCKER) run --publish 8181:8181 --mount "type=bind,src=$$(pwd)/_db,dst=/tmtrkr/db" --rm=true --tty --interactive tmtrkr


zipapp_build: ZIPAPP_BUILD_PATH := $(shell mktemp --directory --dry-run)/tmtrkr_app
zipapp_build: ZIPAPP_BUILD_OUTPUT := "tmtrkr-$(VERSION_HASH).pyz"
zipapp_build: env clean  ## pack app into .pyz, run it: 'python3 tmtrtk.pyz'
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
	$(PYTHON) -m zipapp --compress --output $(ZIPAPP_BUILD_OUTPUT) --python $(PYTHON_SYSTEM) "$(ZIPAPP_BUILD_PATH)"
	rm -rfv "$(ZIPAPP_BUILD_PATH)"

zipapp_run: ZIPAPP_BUILD_OUTPUT := "tmtrkr-$(VERSION_HASH).pyz"
zipapp_run: zipapp_build
	$(PYTHON) "$(ZIPAPP_BUILD_OUTPUT)"
