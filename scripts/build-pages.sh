#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
uv run --locked python -m scripts.build_pages_data --public-base "${PAGES_PUBLIC_BASE_URL:-https://jgmikael.github.io/metatietovaranto}"
npm run test:help --prefix apps/web
npm run build:pages --prefix apps/web
