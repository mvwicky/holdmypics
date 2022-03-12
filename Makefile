SHELL:=bash
.SHELLFLAGS:=-eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

YARN=yarn
YARN_RUN=$(YARN) --silent run
WEBPACK=$(YARN_RUN) webpack
NODE_ENV_VALUE?=development
CACHE_DIR=.cache
SENTINEL_DIR=$(CACHE_DIR)/sentinels

DOCKER=docker
DOCKER_COMPOSE=docker-compose
CONTAINER_NAME?=hold

GFIND=$(shell command -v gfind)
ESLINT_D=$(shell command -v eslint_d)
ESLINT=$(or $(ESLINT_D),$(ESLINT_D),$(YARN_RUN) eslint)
FIND:=$(or $(GFIND),$(GFIND),find)
LS_FILES:=$(sort $(wildcard $(shell git ls-files) $(shell git ls-files --others --exclude-standard)))
LS_PYTHON=$(filter %.py,$(LS_FILES))
RM_CMD:=$(or $(shell command -v trash),trash,rm -rf)

SENTINEL_FILE=$(SENTINEL_DIR)/$(1).last-run

ISORT_SENTINEL=$(call SENTINEL_FILE,isort)
FLAKE8_SENTINEL=$(call SENTINEL_FILE,flake8)
ESLINT_SENTINEL=$(call SENTINEL_FILE,eslint)
STYLELINT_SENTINEL=$(call SENTINEL_FILE,stylelint)
PYRIGHT_SENTINEL=$(call SENTINEL_FILE,pyright)
DOCKERFILE_SENTINEL=$(call SENTINEL_FILE,dockerfiles)

VERSION_FILE=holdmypics/__version__.py
VERSION_FILE_CTS=$(file < $(VERSION_FILE))
VERSION=$(shell echo $(lastword $(VERSION_FILE_CTS)))
VERSION_TAG=v$(VERSION)

MODE?=dev
CONFIG_DIR=config
DOCKERFILE=$(CONFIG_DIR)/$(MODE)/Dockerfile
DOCKER_TAG=holdmypics-$(MODE):$(VERSION_TAG)
BUILD_CPU_SHARES?=512
COMPILE_OPTS?=--port 8080 -y

COMPILE_DEPS=$(CONFIG_DIR)/Dockerfile.jinja holdmypics/generate.py
COMPILE_OUT=$(CONFIG_DIR)/dev/Dockerfile $(CONFIG_DIR)/prod/Dockerfile

ESLINT_DEPS=$(filter %.ts,$(LS_FILES)) $(filter %.js,$(LS_FILES)) $(filter .eslintrc.%,$(LS_FILES))
STYLELINT_DEPS=$(filter %.css,$(LS_FILES)) $(filter .stylelintrc.%,$(LS_FILES))
ISORT_DEPS=$(filter-out %/__version__.py,$(LS_PYTHON))

WEBPACK_ARGS=--config webpack.config.ts --progress

.PHONY: compile compose dbuilddev dbuildprod docker docker-build run stop version-tag \
	lint isort flake8 eslint stylelint clean-lint clean-webpack

compile: $(COMPILE_OUT)

$(COMPILE_OUT): $(COMPILE_DEPS)
	flask dockerfiles $(COMPILE_OPTS)
	date > $(DOCKERFILE_SENTINEL)


dbuilddev: MODE=dev
dbuilddev: docker-build

dbuildprod: MODE=prod
dbuildprod: docker-build

docker-build: DOCKER_ARGS=build -f $(DOCKERFILE) -c $(BUILD_CPU_SHARES) --tag=$(DOCKER_TAG) -o out .
docker-build: compile docker

rundev: MODE=dev
rundev: DOCKER_ARGS=run --publish 8080:8080 --detach --name=$(CONTAINER_NAME) $(DOCKER_TAG)
rundev: docker

stop: MODE=dev
stop: DOCKER_ARGS=stop $(CONTAINER_NAME)

docker:
	$(DOCKER) $(DOCKER_ARGS)

compose:
	$(DOCKER_COMPOSE) $(COMPOSE_ARGS)

dev: NODE_ENV_VALUE=development
dev: export TAILWIND_MODE=build
dev: webpack

prod: NODE_ENV_VALUE=production
prod: webpack

webpack: export NODE_ENV=$(NODE_ENV_VALUE)
webpack:
	@$(WEBPACK) $(WEBPACK_ARGS)


version-commit:
ifdef DRY_RUN
	@echo $(VERSION_TAG)
else
	@git commit --no-verify -m $(VERSION_TAG)
endif

version-tag:
ifdef DRY_RUN
	@echo $(VERSION_TAG)
else
	@git tag $(VERSION_TAG) -m $(VERSION_TAG)
endif

lint: isort flake8 eslint stylelint pyright

isort: $(SENTINEL_DIR) $(ISORT_SENTINEL)
flake8: $(SENTINEL_DIR) $(FLAKE8_SENTINEL)
eslint: $(SENTINEL_DIR) $(ESLINT_SENTINEL)
stylelint: $(SENTINEL_DIR) $(STYLELINT_SENTINEL)
pyright: $(SENTINEL_DIR) $(PYRIGHT_SENTINEL)

$(ISORT_SENTINEL): $(ISORT_DEPS) pyproject.toml
	@echo "Running isort. $(words $?) outdated."
	@isort --check-only $(filter %.py,$?)
	@date > $@

$(FLAKE8_SENTINEL): $(LS_PYTHON) .flake8
	@echo "Running flake8. $(words $?) outdated."
	@flake8 $(filter %.py,$?)
	@date > $@

$(ESLINT_SENTINEL): $(ESLINT_DEPS)
	@echo "Running eslint. $(words $?) outdated."
	@$(ESLINT) '**/*.ts' '**/*.js'
	@date > $@

$(STYLELINT_SENTINEL): $(STYLELINT_DEPS)
	@echo "Running stylelint. $(words $?) outdated."
	@$(YARN_RUN) stylelint 'src/css/**/*.css'
	@date > $@

$(PYRIGHT_SENTINEL): $(LS_PYTHON) pyproject.toml poetry.lock pyrightconfig.json
	@echo "Running pyright. $(words $?) outdated."
	@pyright
	@date > $@

$(SENTINEL_DIR):
	mkdir $@

clean-lint:
	$(RM_CMD) $(SENTINEL_DIR)

clean-webpack:
	$(RM_CMD) static/dist holdmypics/web/templates/base-out.html

clean-webpack-cache:
	$(RM_CMD)  node_modules/.cache/webpack
