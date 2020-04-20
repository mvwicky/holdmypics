SHELL:=bash
.ONESHELL:
.SHELLFLAGS:=-eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

YARN=yarn
YARN_RUN=$(YARN) run
NODE_BIN=node_modules/.bin
WEBPACK=$(NODE_BIN)/webpack
DOCKER=docker
DOCKER_COMPOSE=docker-compose
CONTAINER_NAME?=hold

VERSION_FILE=holdmypics/__version__.py
VERSION_FILE_CTS=$(shell cat $(VERSION_FILE))
VERSION=$(subst ",,$(lastword $(VERSION_FILE_CTS)))
VERSION_TAG=v$(VERSION)

MODE?=dev
CONFIG_DIR=config
DOCKERFILE=$(CONFIG_DIR)/$(MODE)/Dockerfile
DOCKER_TAG=holdmypics-$(MODE):$(VERSION_TAG)
BUILD_CPU_SHARES?=512

TEMPLATE=$(CONFIG_DIR)/Dockerfile.template
COMPILE_OUT=$(CONFIG_DIR)/dev/Dockerfile $(CONFIG_DIR)/prod/Dockerfile

.PHONY: compile compose dbuilddev dbuildprod docker docker-build run stop version-tag

compile: $(COMPILE_OUT)

$(COMPILE_OUT): $(TEMPLATE)
	flask generate-dockerfiles

dbuilddev: MODE=dev
dbuilddev: docker-build

dbuildprod: MODE=prod
dbuildprod: docker-build

docker-build: DOCKER_ARGS=build -f $(DOCKERFILE) -c $(BUILD_CPU_SHARES) --tag=$(DOCKER_TAG) .
docker-build: docker

dev: MODE=dev
dev: DOCKER_ARGS=run --publish 8080:8080 --detach --name=$(CONTAINER_NAME) $(DOCKER_TAG)
dev: docker

stop: MODE=dev
stop: DOCKER_ARGS=stop $(CONTAINER_NAME)

docker:
	$(DOCKER) $(DOCKER_ARGS)

compose:
	$(DOCKER_COMPOSE) $(COMPOSE_ARGS)

version-tag:
	@git tag $(VERSION_TAG)
