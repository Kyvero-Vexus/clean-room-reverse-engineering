#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="crre-autoresearch-dashboard.service"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
UNIT_SRC="$ROOT_DIR/systemd/$SERVICE_NAME"
UNIT_DST_DIR="$HOME/.config/systemd/user"
UNIT_DST="$UNIT_DST_DIR/$SERVICE_NAME"

mkdir -p "$UNIT_DST_DIR"
cp "$UNIT_SRC" "$UNIT_DST"

systemctl --user daemon-reload
systemctl --user enable --now "$SERVICE_NAME"

echo "Installed and started: $SERVICE_NAME"
echo "Status:"
systemctl --user --no-pager --full status "$SERVICE_NAME" | sed -n '1,30p'
