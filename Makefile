COPY=cp
YARN=yarn
YARN_RUN=$(YARN) run
PARCEL=$(YARN_RUN) parcel
PARCEL_BUILD=$(PARCEL) build

INPUT_DIR=src
ROOT_DIR=holdmypics
TEMPLATES_DIR=$(ROOT_DIR)/templates
STATIC_DIR=$(ROOT_DIR)/static/dist

PARCEL_INPUT=$(INPUT_DIR)/*.html
OUTPUT_DIR=dist
PARCEL_OUTPUT=--out-dir $(OUTPUT_DIR)
PUBLIC_URL=/static/dist/
PARCEL_URL=--public-url $(PUBLIC_URL)
PARCEL_OPTS=$(PARCEL_INPUT) $(PARCEL_URL) $(PARCEL_OUTPUT)
DEV_OPTS=--no-minify

.PHONY: prod
prod: export NODE_ENV=production
prod: clean build copy

.PHONY: dev_opts
dev_opts: export NODE_ENV=development
dev_opts: PARCEL_OPTS := $(PARCEL_OPTS) $(DEV_OPTS)

.PHONY: dev
dev: PARCEL_OPTS := $(PARCEL_OPTS) $(DEV_OPTS)
dev: export NODE_ENV=development
dev: clean build copy

.PHONY: build
build:
	$(PARCEL_BUILD) $(PARCEL_OPTS)

copy: $(STATIC_DIR) $(TEMPLATES_DIR)
	$(COPY) $(OUTPUT_DIR)/*.html $(TEMPLATES_DIR)
	$(COPY) $(OUTPUT_DIR)/*.css $(STATIC_DIR)
	$(COPY) $(OUTPUT_DIR)/*.js $(STATIC_DIR)
	$(COPY) $(OUTPUT_DIR)/*.map $(STATIC_DIR)

$(STATIC_DIR):
	mkdir $(STATIC_DIR)

$(TEMPLATES_DIR):
	mkdir $(TEMPLATES_DIR)

.PHONY: watch
watch: export NODE_ENV=development
watch:
	$(PARCEL) watch $(PARCEL_OPTS)

.PHONY: clean
clean:
	-rm -rf $(OUTPUT_DIR)/*
	-rm -f $(STATIC_DIR)/*

.PHONY: full_clean
full_clean: clean
	-rm -rf .cache

