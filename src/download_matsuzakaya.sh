#!/usr/bin/env bash
set -euo pipefail

START_URL="https://reielegance.com/matsuzakaya/"
OUTPUT_DIR="/home/amil/beauty/site-mirror"
DOMAIN="reielegance.com"

mkdir -p "$OUTPUT_DIR"

# Avoid recursive query-string traps like ?close?close?... while mirroring.
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
  --reject-regex='.*\?close.*|.*\?.*close.*|.*\?.*popup.*|.*\?.*modal.*' \
  --user-agent="Mozilla/5.0 (compatible; SiteMirror/1.0)" \
  "$START_URL"

echo "Mirror complete: $OUTPUT_DIR"
