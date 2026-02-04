#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

usage() {
  echo "Usage: $0 <attachment_name> [version]"
  echo "Example: $0 camera_mount v1"
}

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage
  exit 1
fi

ATTACHMENT_NAME="$1"
VERSION="${2:-v1}"

if [[ ! "$ATTACHMENT_NAME" =~ ^[a-z0-9_]+$ ]]; then
  echo "Error: attachment_name must match ^[a-z0-9_]+$"
  exit 1
fi

if [[ ! "$VERSION" =~ ^v[0-9]+$ ]]; then
  echo "Error: version must match ^v[0-9]+$ (for example: v1, v2)"
  exit 1
fi

TARGET_DIR="${ROOT_DIR}/attachments/${ATTACHMENT_NAME}/${VERSION}"
ATTACHMENT_FILE="${ATTACHMENT_NAME}_${VERSION}.scad"
NOTES_FILE="notes.md"
DATE_STAMP="$(date +%F)"

if [[ -e "$TARGET_DIR" ]]; then
  echo "Error: target already exists: $TARGET_DIR"
  exit 1
fi

mkdir -p "$TARGET_DIR"

SCAD_TEMPLATE="${ROOT_DIR}/templates/attachment_v1.scad"
NOTES_TEMPLATE="${ROOT_DIR}/templates/attachment_notes.md"

if [[ ! -f "$SCAD_TEMPLATE" || ! -f "$NOTES_TEMPLATE" ]]; then
  echo "Error: missing template files in ${ROOT_DIR}/templates"
  exit 1
fi

sed \
  -e "s/__ATTACHMENT_NAME__/${ATTACHMENT_NAME}/g" \
  -e "s/__VERSION__/${VERSION}/g" \
  "$SCAD_TEMPLATE" > "${TARGET_DIR}/${ATTACHMENT_FILE}"

sed \
  -e "s/__ATTACHMENT_NAME__/${ATTACHMENT_NAME}/g" \
  -e "s/__VERSION__/${VERSION}/g" \
  -e "s/__ATTACHMENT_FILE__/${ATTACHMENT_FILE}/g" \
  -e "s/__DATE__/${DATE_STAMP}/g" \
  "$NOTES_TEMPLATE" > "${TARGET_DIR}/${NOTES_FILE}"

echo "Created attachment scaffold:"
echo "  ${TARGET_DIR}/${ATTACHMENT_FILE}"
echo "  ${TARGET_DIR}/${NOTES_FILE}"
echo
echo "Next steps:"
echo "  1) Edit parameters in ${ATTACHMENT_FILE}"
echo "  2) Run: make check"
