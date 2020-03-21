FROM node:13.6-slim AS client-builder

RUN mkdir /app/
WORKDIR /app/
COPY ./package.json ./yarn.lock /app/
RUN yarn install

COPY ./webpack.config.ts ./tsconfig.json /app/
COPY ./src /app/src
ARG PRODUCTION
RUN yarn run build \
  && yarn install --prod

FROM python:3.8-slim

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONUNBUFFERED=1

RUN set -ex \
  && RUN_DEPS=" \
  libpcre3 \
  mime-support \
  " \
  && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \
  && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN set -ex \
  && BUILD_DEPS=" \
  build-essential \
  libpcre3-dev \
  " \
  && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
  && pip install --no-cache-dir -r /requirements.txt \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
  && rm -rf /var/lib/apt/lists/*

COPY . /app
COPY --from=client-builder /app/holdmypics/static/dist /app/holdmypics/static/dist
COPY --from=client-builder /app/holdmypics/core/templates/base-out.html /app/holdmypics/core/templates/base-out.html

ARG APP_USER=appuser
RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER}

RUN chmod +x /app/docker-entrypoint.sh

USER ${APP_USER}:${APP_USER}

# ENTRYPOINT ["/app/docker-entrypoint.sh"]

CMD ["gunicorn", "wsgi:application", "--config", "file:/app/gunicorn_config.py"]