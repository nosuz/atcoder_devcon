# syntax=docker/dockerfile:1
# enable here documents.
# RUN cat <<EOF >> /home/vscode/.bashrc
#
# EOF

FROM ubuntu:latest
# suppress clear apt cache
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Install packages
ENV DEBIAN_FRONTEND=noninteractive

# Set locale and timezone
ENV LANG=ja_JP.UTF-8
ENV LC_ALL=ja_JP.UTF-8
ENV LC_CTYPE=ja_JP.UTF-8
ENV TZ=Asia/Tokyo

ARG USERNAME=vscode
ARG UID=10000
ARG GID=$UID

# Setup user and group id
# Remove all general users and create a new user for USER direction.
RUN set -eux; \
    for i in $(awk -F: '$3 >= 1000 && $3 <= 60000 { print $1 }' /etc/passwd); do \
    userdel $i; \
    done; \
    for i in $(awk -F: '$3 >= 1000 && $3 <= 60000 { print $1 }' /etc/passwd); do \
    groupdel $i; \
    done; \
    rm -rf /home/*; \
    groupadd --gid "${GID}" "${USERNAME}"; \
    useradd --uid "${UID}" --gid "${GID}" -s /bin/bash -m "${USERNAME}"

# Enable sudo
# RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
#     --mount=type=cache,target=/var/lib/apt,sharing=locked \
#     apt-get update \
#     && apt-get install -y sudo \
#     && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
#     && chmod 0440 /etc/sudoers.d/$USERNAME

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
    python3 python3-venv python-is-python3 \
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

# Default user
USER vscode

# install library
COPY requirements.txt .
ARG PIP_CACHE_DIR=/home/vscode/.cache/pip
RUN mkdir -p $PIP_CACHE_DIR
RUN --mount=type=cache,target=/home/vscode/.cache/pip,sharing=locked  \
    chown vscode:vscode /home/vscode/.cache/pip \
    && python3 -m venv $HOME/venv \
    && $HOME/venv/bin/pip install --upgrade pip \
    && $HOME/venv/bin/pip install -r requirements.txt

# activate venv
RUN cat <<'EOF' >> /home/vscode/.bashrc

export LANG=$LANG

if [ -f "$HOME/venv/bin/activate" ] && [ -z "$VIRTUAL_ENV" ]; then
    . "$HOME/venv/bin/activate"
fi
EOF
