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

MODE?=dev
VERSION=$(shell jq -r .version package.json)
VERSION_TAG=v$(VERSION)

CONFIG_DIR=config
DOCKER_TAG=holdmypics-$(MODE):$(VERSION_TAG)
BUILD_CPU_SHARES=512

TEMPLATE=$(CONFIG_DIR)/Dockerfile.template
DEV_FILE=$(CONFIG_DIR)/dev/Dockerfile
PROD_FILE=$(CONFIG_DIR)/prod/Dockerfile
COMPILE_OUT=$(DEV_FILE) $(PROD_FILE)

.PHONY: version-tag compile

compile: $(COMPILE_OUT)

$(COMPILE_OUT): $(TEMPLATE)
	flask generate-dockerfiles

dbuilddev: MODE=dev
dbuilddev: docker-build

dbuildprod: MODE=prod
dbuildprod: docker-build

docker-build: DOCKER_ARGS=build -f $(CONFIG_DIR)/$(MODE)/Dockerfile -c $(BUILD_CPU_SHARES) --tag=$(DOCKER_TAG) .
docker-build: docker

rundev: MODE=dev
rundev: DOCKER_ARGS=run --publish 8080:8080 --detach --name=$(CONTAINER_NAME) $(DOCKER_TAG)
rundev: docker

stop: MODE=dev
stop: DOCKER_ARGS=stop $(CONTAINER_NAME)

docker:
	$(DOCKER) $(DOCKER_ARGS)

compose:
	$(DOCKER_COMPOSE) $(COMPOSE_ARGS)

version-tag:
	@git tag $(VERSION_TAG)
