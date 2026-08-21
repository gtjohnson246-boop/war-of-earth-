#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

mkdir -p "$TMP_DIR/app"
rsync -a --delete \
  --exclude='.git' \
  --exclude='.venv' \
  --exclude='build' \
  --exclude='web-cache' \
  --exclude='.github' \
  "$ROOT"/ "$TMP_DIR/app"/

cd "$TMP_DIR/app"
python -m pygbag --build .

mkdir -p "$ROOT/build"
rm -rf "$ROOT/build/web"
cp -R "$TMP_DIR/app/build/web" "$ROOT/build/web"
