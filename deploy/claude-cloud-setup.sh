#!/bin/bash
# Setup script for the Claude Code cloud environment used with this repo.
# Paste the whole file into the environment's "Setup script" field at claude.ai/code.
#
# Network access for the environment: choose "Custom", add download.blender.org to
# Allowed domains, and tick "Also include default list of common package managers".
#
# Runs as root on Ubuntu 24.04 before Claude starts. The result is cached for later
# sessions if it finishes in under about five minutes.
set -euo pipefail

BLENDER_VERSION=4.2.23   # Blender 4.2 LTS, the version build_ring.py was written for
BLENDER_URL="https://download.blender.org/release/Blender4.2/blender-${BLENDER_VERSION}-linux-x64.tar.xz"

if ! /opt/blender/blender --version 2>/dev/null | grep -q "Blender ${BLENDER_VERSION}"; then
  # Libraries headless Blender needs, and the Blender download, in parallel.
  (apt-get update -qq && apt-get install -y -qq --no-install-recommends \
      xz-utils libgl1 libegl1 libxi6 libxxf86vm1 libxfixes3 libxrender1 libxkbcommon0 libsm6 libice6) &
  apt_pid=$!
  curl -fsSL --retry 3 "$BLENDER_URL" -o /tmp/blender.tar.xz &
  dl_pid=$!
  wait "$apt_pid"
  wait "$dl_pid"

  rm -rf /opt/blender && mkdir -p /opt/blender
  tar -xJf /tmp/blender.tar.xz -C /opt/blender --strip-components=1
  rm -f /tmp/blender.tar.xz
  ln -sf /opt/blender/blender /usr/local/bin/blender
fi

# Pillow and numpy for the comparison scripts in blender/ (run with system python3).
python3 -m pip install --quiet --break-system-packages pillow numpy

blender --version | head -n 1
