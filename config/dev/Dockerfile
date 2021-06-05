FROM node:14-alpine3.12 AS client-builder

RUN mkdir /app/
WORKDIR /app/
COPY ./package.json ./yarn.lock /app/

RUN yarn install --prod

FROM python:3.9.5-slim

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONUNBUFFERED=1

WORKDIR /app/
COPY ./bin/install-run-deps.sh /
RUN ["/bin/bash", "-c", "/install-run-deps.sh"]

COPY requirements-dev.txt ./bin/install-build-deps.sh /
RUN ["/bin/bash", "-c", "/install-build-deps.sh /requirements-dev.txt"]
VOLUME ["/pip-cache"]

COPY . /app
COPY --from=client-builder /app/node_modules /app/node_modules

ARG APP_USER=appuser
RUN groupadd -r ${APP_USER} && useradd --create-home --no-log-init -r -g ${APP_USER} ${APP_USER}

RUN mkdir -p /app/.cache/images
RUN chown -R ${APP_USER}:${APP_USER} /app/
# RUN chmod +x /app/bin/docker-entrypoint.sh

EXPOSE 8080
USER ${APP_USER}:${APP_USER}

CMD ["gunicorn", "wsgi:application", "--config", "file:config/gunicorn_config.py"]