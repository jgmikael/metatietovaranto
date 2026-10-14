# syntax=docker/dockerfile:1
FROM node:24-alpine@sha256:ebfe2f90462722a7a4de65e91990e97fe0d401c70e0e762c5b53302f905ec1c1 AS web
WORKDIR /build
COPY apps/web/package*.json ./
RUN --mount=type=secret,id=environment_ca \
    if [ -f /run/secrets/environment_ca ]; then export NODE_EXTRA_CA_CERTS=/run/secrets/environment_ca; fi; npm ci
COPY apps/web/ ./
RUN npm run build

FROM python:3.12-slim@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1
WORKDIR /app
COPY --chown=1000:1000 pyproject.toml uv.lock ./
RUN --mount=type=secret,id=environment_ca \
    if [ -f /run/secrets/environment_ca ]; then export PIP_CERT=/run/secrets/environment_ca SSL_CERT_FILE=/run/secrets/environment_ca; fi; \
    pip install --no-cache-dir uv==0.12.23 && uv sync --locked --no-dev
COPY --chown=1000:1000 alembic.ini ./
COPY --chown=1000:1000 migrations/ migrations/
COPY --chown=1000:1000 apps/api/ apps/api/
COPY --chown=1000:1000 fixtures/ fixtures/
COPY --from=web --chown=1000:1000 /build/dist/ apps/web/dist/
USER 1000:1000
EXPOSE 8000
CMD [".venv/bin/uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
