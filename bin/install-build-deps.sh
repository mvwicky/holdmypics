#!/bin/bash

set -euo pipefail

requirements=${1:-}
if [ -z "$requirements" ]; then
  echo "No requirements file specified"
  exit 1
fi

mkdir /pip-cache

set -x
BUILD_DEPS=(build-essential libpcre3-dev)
apt-get update
apt-get install -y --no-install-recommends "${BUILD_DEPS[@]}"
XDG_CACHE_HOME="/pip-cache" pip install -r "$requirements"
apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false "${BUILD_DEPS[@]}"
rm "$requirements"
set +x
