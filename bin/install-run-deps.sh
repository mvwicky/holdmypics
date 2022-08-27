#!/bin/bash

set -euo pipefail

set -x
RUN_DEPS=(libpcre3 mime-support)
seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{}
apt-get update && apt-get install -y --no-install-recommends "${RUN_DEPS[@]}"
rm -rf /var/lib/apt/lists/*
set +x
