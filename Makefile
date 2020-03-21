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

CONFIG_DIR=config
DOCKER_TAG=holdmypics-$(MODE)
BUILD_CPU_SHARES=512

dbuilddev: MODE=dev
dbuilddev: docker-build

dbuildprod: MODE=prod
dbuildprod: docker-build

docker-build: DOCKER_ARGS=build -f $(CONFIG_DIR)/$(MODE)/Dockerfile -c $(BUILD_CPU_SHARES) --tag=$(DOCKER_TAG) .
docker-build: docker

docker:
	$(DOCKER) $(DOCKER_ARGS)

compose:
	$(DOCKER_COMPOSE) $(COMPOSE_ARGS)