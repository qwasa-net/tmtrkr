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


help:
	-@echo 'How to `make` it:'
	-@grep ' \ ##' $(realpath $(firstword $(MAKEFILE_LIST))) | sed 's/^/  - /ig'


tea: env env_dev lint test initdb run  ## do magic, start from here


env:  ## create vrtual env
	@$(PYTHON_SYSTEM) --version
	[ -e $(PYTHON) ] || $(PYTHON_SYSTEM) -m venv --clear $(VENV) && ls -l $(PYTHON)
	$(PIP) install -U pip
	# pip install sqlalchemy alembic fastapi uvicorn
	$(PIP) install -r requirements.txt


env_dev: env
	# pip install black flake8 pytest pydocstyle pycodestyle
	$(PIP) install -r requirements-dev.txt


run: DATABASE_URL ?= $(BASE_DIR)/db.sqlite
run:  ## run demo server
	cd "$(BASE_DIR)"; \
	PYTHONPATH=.:"$(BASE_DIR)" \
	TMTRKR_DATABASE_URL="sqlite:///$(DATABASE_URL)" \
	$(PYTHON) tmtrkr/server/server.py


initdb: DATABASE_URL ?= $(BASE_DIR)/db.sqlite
initdb:  ## apply all db migrations
	cd "$(BASE_DIR)"; \
	TMTRKR_DATABASE_URL="sqlite:///$(DATABASE_URL)" \
	$(ALEMBIC) upgrade head; \
	TMTRKR_DATABASE_URL="sqlite:///$(DATABASE_URL)" \
	$(ALEMBIC) current


demodb: DATABASE_URL ?= $(BASE_DIR)/db.sqlite
demodb: initdb  ## create demo db
	cd "$(BASE_DIR)"; \
	TMTRKR_DATABASE_URL="sqlite:///$(DATABASE_URL)" \
	$(PYTHON) tmtrkr/misc/demodb.py


lint:  # run source code linters
	$(FLAKE8) --statistics tmtrkr
	$(FORMATTER_PY) --check tmtrkr tests


format:  # run source code formatters
	$(FORMATTER_PY) tmtrkr tests
	$(FORMATTER_WWW_JS) www/js/tmtrkr.js
	$(FORMATTER_WWW_CSS) www/css/tmtrkr.css


test: DATABASE_URL ?= $(shell mktemp)
test:  # run test
	TMTRKR_DATABASE_URL="sqlite:///$(DATABASE_URL)" $(PYTHON) -u -m unittest -v
	@rm -v "$(DATABASE_URL)"


clean:  # cleanup python cache
	find ./tmtrkr -iname '*.py[co]' -print -delete
	find ./tmtrkr -iname __pycache__ -print -delete


container_build:  ## build container
	$(DOCKER) build . --file tmtrkr.dockerfile --tag tmtrkr


container_run:  ## run container
	-$(DOCKER) run --publish 8181:8181 --rm=true --tty --interactive tmtrkr


container_run_db:
	-mkdir -pv _db
	-$(DOCKER) run --publish 8181:8181 --mount "type=bind,src=$$(pwd)/_db,dst=/tmtrkr/db" --rm=true --tty --interactive tmtrkr


zipapp_build: ZIPAPP_BUILD_PATH := $(shell mktemp --directory --dry-run)/tmtrkr_app
zipapp_build: clean  ## pack app into .pyz
	mkdir -pv "$(ZIPAPP_BUILD_PATH)"
	$(PIP) install -r requirements.txt --target "$(ZIPAPP_BUILD_PATH)"
	# copy app and statics
	cp -rv tmtrkr "$(ZIPAPP_BUILD_PATH)"
	cp -rv zipapp/__main__.py "$(ZIPAPP_BUILD_PATH)"
	cp -rv www "$(ZIPAPP_BUILD_PATH)/tmtrkr/"
	# build a zippapp
	$(PYTHON) -m zipapp --compress --output "tmtrkr.pyz" --python $(PYTHON_SYSTEM) "$(ZIPAPP_BUILD_PATH)"
	# rm -rfv "$(ZIPAPP_BUILD_PATH)
