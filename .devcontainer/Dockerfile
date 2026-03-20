# syntax=docker/dockerfile:1.4
FROM ubuntu:latest
# suppress clear apt cache
RUN rm /etc/apt/apt.conf.d/docker-clean

ENV LANG=ja_JP.UTF-8
ENV LC_ALL=ja_JP.UTF-8
ENV LC_CTYPE=ja_JP.UTF-8
ENV TZ=Asia/Tokyo

# ARG USERNAME=ubuntu
# ARG UID=$UID
# ARG GID=$GID

# # Remove user if already exist and create new user.
# RUN set -eux; \
#     if getent passwd "${UID}" > /dev/null; then \
#     echo "UID ${UID} already exists. Deleting..."; \
#     userdel -f $(getent passwd "${UID}" | cut -d: -f1) || true; \
#     fi; \
#     if getent group "${GID}" > /dev/null; then \
#     echo "GID ${GID} already exists. Deleting..."; \
#     groupdel $(getent group "${GID}" | cut -d: -f1) || true; \
#     fi; \
#     groupadd --gid "${GID}" "${USERNAME}"; \
#     useradd --uid "${UID}" --gid "${GID}" -s /bin/bash -m "${USERNAME}"

# install packages
ENV DEBIAN_FRONTEND=noninteractive

# https://github.com/moby/buildkit/issues/1662#issuecomment-683962222
# https://docs.docker.com/reference/dockerfile/?__readwiseLocation=#example-cache-apt-packages
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
    && apt-get install --no-install-recommends -y \
    # Basic tools
    # ssh is required to handle GitHub in the container
    git ssh \
    # install python
    python3 \
    # install java
    default-jdk-headless \
    # required to install sdkman and gradle
    # Both zip and unzip are required to install.
    curl unzip zip \
    # System tools
    locales tzdata \
    # Configure locale
    && locale-gen ja_JP.UTF-8 \
    && update-locale LANG=ja_JP.UTF-8 \
    # Configure timezone
    && ln -fs /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ARG UV_CACHE_DIR=/opt/.cache/uv
RUN mkdir -p $UV_CACHE_DIR
# Disable development dependencies
ENV UV_NO_DEV=1
# specify `__pycache__` directory
ENV PYTHONPYCACHEPREFIX=/tmp/pycache

COPY pyproject.toml uv.lock ./
# set `--frozen` to `uv sync` on runtime
RUN --mount=type=cache,target=$UV_CACHE_DIR,sharing=locked \
    uv venv /opt/venv \
    && if [ -s uv.lock ]; then uv sync --frozen; fi

RUN chmod -R a+rX /opt/venv \
    && find /opt/venv -type d -perm -u+w -exec chmod a+w {} +

# activate venv
RUN cat <<'EOF' >> /etc/bash.bashrc

export LANG=$LANG

if [ -n "$UV_PROJECT_ENVIRONMENT" ] &&
    [ -f "$UV_PROJECT_ENVIRONMENT/bin/activate" ] &&
    [ -z "$VIRTUAL_ENV" ]; then
    . "$UV_PROJECT_ENVIRONMENT/bin/activate"
fi
EOF
