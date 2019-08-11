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

COPY_HTML=$(COPY) $(OUTPUT_DIR)/*.html $(TEMPLATES_DIR)
COPY_CSS=$(COPY) $(OUTPUT_DIR)/*.css $(STATIC_DIR)
COPY_JS=$(COPY) $(OUTPUT_DIR)/*.js $(STATIC_DIR)
COPY_MAP=$(COPY) $(OUTPUT_DIR)/*.map $(STATIC_DIR)

COPY_ALL=$(COPY_HTML) && $(COPY_JS) && $(COPY_MAP) && $(COPY_CSS)

.PHONY: prod
prod: clean
prod: export NODE_ENV=production
prod:
	mkdir $(TEMPLATES_DIR)
	mkdir $(STATIC_DIR)
	$(PARCEL) $(PARCEL_OPTS)
	$(COPY_ALL)

.PHONY: dev
dev: clean
dev: export NODE_ENV=development
dev:
	$(PARCEL) $(PARCEL_OPTS) $(DEV_OPTS)
	$(COPY_ALL)


.PHONY: clean
clean:
	-rm -rf $(OUTPUT_DIR)/*
	-rm -f $(STATIC_DIR)/*

.PHONY: full_clean
full_clean: clean
full_clean:
	-rm -rf .cache

