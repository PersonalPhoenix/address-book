ARG REPO=docker.io
ARG IMAGE_NAME=python
ARG IMAGE_TAG=3.12.12-slim-bookworm
ARG IMAGE_HASH=sha256:4a8e0824201e50fc44ee8d208a2b3e44f33e00448907e524066fca5a96eb5567

FROM $REPO/$IMAGE_NAME:$IMAGE_TAG@$IMAGE_HASH AS base

ENV \
  DEBIAN_FRONTEND=noninteractive \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DEFAULT_TIMEOUT=100 \
  REDIS_HOST=redis \
  REDIS_PORT=6379 \
  REDIS_DB=0

SHELL ["/bin/bash", "-exo", "pipefail", "-c"]

RUN \
    rm -f /etc/apt/sources.list.d/debian.sources \
    && echo -e '\
deb http://deb.debian.org/debian bookworm main\n\
deb http://deb.debian.org/debian bookworm-updates main\n\
deb http://security.debian.org/debian-security bookworm-security main\n\
' > /etc/apt/sources.list \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
        libexpat1 \
        tini=0.19.0-1+b3 \
    && mkdir /app \
    && pip config --user set global.index-url https://pypi.org/simple \
    && pip install --upgrade pip==25.2 \
    && pip install --upgrade setuptools==78.1.1 \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/

WORKDIR /app

FROM base AS dependencies

ENV \
  POETRY_VERSION=2.0.0 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_HOME='/usr/local'

COPY ./poetry.lock ./pyproject.toml /app/

RUN \
    apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential \
        python3-dev \
        redis-tools \
    && pip install --no-cache-dir "poetry==$POETRY_VERSION" \
    && pip install --no-cache-dir poetry-plugin-export \
    && python -m venv --upgrade-deps /app/venv \
    && /app/venv/bin/pip install --no-cache-dir --upgrade pip \
    && cd /app && poetry export --without-hashes --without-urls --format requirements.txt --output requirements.txt \
    && /app/venv/bin/pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
        build-essential python3-dev \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/ /root/.cache/pypoetry

FROM base AS final

ARG UID=1000
ARG GID=1000

RUN groupadd -r web --gid "$GID" && useradd -d /app -r -g web web --uid "$UID"
RUN chown -R web:web /app

USER web

COPY --chown=web:web --from=dependencies /app/venv /app/venv

COPY --chown=web:web ./src /app/src

ENV PATH="/app/venv/bin:$PATH"

CMD ["gunicorn", "src.main:app", "--bind", "0.0.0.0:8000", "--worker-class", "uvicorn.workers.UvicornWorker"]
