COPY=cp
YARN=yarn
YARN_RUN=$(YARN) run
PARCEL=$(YARN_RUN) parcel build

INPUT_DIR=src
TEMPLATES_DIR=dummy_flask/templates
STATIC_DIR=dummy_flask/static/dist

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

.PHONY: dev
dev: export NODE_ENV=development
dev: PARCEL_OPTS := $(PARCEL_OPTS) $(DEV_OPTS)
dev: clean build copy

build:
	$(PARCEL) $(PARCEL_OPTS)

copy: $(STATIC_DIR) $(TEMPLATES_DIR)
	$(COPY) $(OUTPUT_DIR)/*.html $(TEMPLATES_DIR)
	$(COPY) $(OUTPUT_DIR)/*.css $(STATIC_DIR)
	$(COPY) $(OUTPUT_DIR)/*.js $(STATIC_DIR)
	$(COPY) $(OUTPUT_DIR)/*.map $(STATIC_DIR)

$(STATIC_DIR):
	mkdir $(STATIC_DIR)

$(TEMPLATES_DIR):
	mkdir $(TEMPLATES_DIR)

.PHONY: clean
clean:
	-rm -rf $(OUTPUT_DIR)/*
	-rm -f $(STATIC_DIR)/*

.PHONY: full_clean
full_clean: clean
	-rm -rf .cache

