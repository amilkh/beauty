#!/usr/bin/env bash
set -euo pipefail

START_URL="https://beauty.hotpepper.jp/slnH000702503/review/"
OUTPUT_DIR="/home/amil/beauty/site-mirror"
DOMAIN="beauty.hotpepper.jp"

mkdir -p "$OUTPUT_DIR"

# Mirror only the review subtree and avoid common tracking/query traps.
wget \
  --mirror \
  --convert-links \
  --adjust-extension \
  --page-requisites \
  --no-parent \
  --domains "$DOMAIN" \
  --directory-prefix "$OUTPUT_DIR" \
  --execute robots=on \
  --wait=1 \
  --random-wait \
  --reject-regex='.*\?.*(utm_|gclid|fbclid|yclid|ref|sort|page|callback|session|sid|scid).*' \
  --user-agent="Mozilla/5.0 (compatible; SiteMirror/1.0)" \
  "$START_URL"

echo "Mirror complete: $OUTPUT_DIR"
