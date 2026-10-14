#!/usr/bin/env bash
# Cloud-specific builder: preserve proxy routing and certificate verification.
set -euo pipefail
cd "$(dirname "$0")/.."
export DOCKER_CONFIG="${DOCKER_CONFIG:-/workspace/.cache/docker}"
args=(--build-arg HTTP_PROXY --build-arg HTTPS_PROXY --build-arg NO_PROXY)
if [[ -n "${HTTPS_PROXY:-}" ]]; then
  proxy_mapping=$(python3 - <<'PY'
import os, socket, urllib.parse
hostname = urllib.parse.urlparse(os.environ['HTTPS_PROXY']).hostname
print(hostname + ':' + socket.gethostbyname(hostname))
PY
)
  args+=(--add-host "$proxy_mapping" --network=host)
fi
if [[ -n "${SSL_CERT_FILE:-}" ]]; then
  args+=(--secret "id=environment_ca,src=$SSL_CERT_FILE")
fi
docker build "${args[@]}" -t metatietovaranto-app .
