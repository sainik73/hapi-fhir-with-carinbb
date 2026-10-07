#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-upsert}"
BASE_URL="${BASE_URL:-http://localhost:8080/fhir}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMOKETEST_DIR="$SCRIPT_DIR/smoketest"

if [[ "$MODE" == "-h" || "$MODE" == "--help" || "$MODE" == "help" ]]; then
  echo "Usage: $0 [upsert|delete|cleanup|--delete]"
  exit 0
fi

if [[ "$MODE" != "upsert" && "$MODE" != "delete" && "$MODE" != "cleanup" && "$MODE" != "--delete" ]]; then
  echo "Unknown mode: $MODE" >&2
  echo "Usage: $0 [upsert|delete|cleanup|--delete]" >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required but not installed." >&2
  exit 1
fi

if [ ! -d "$SMOKETEST_DIR" ]; then
  echo "Smoke test directory not found: $SMOKETEST_DIR" >&2
  exit 1
fi

FILES=(
  "$SMOKETEST_DIR/01-organization.json"
  "$SMOKETEST_DIR/02-practitioner.json"
  "$SMOKETEST_DIR/03-patient.json"
  "$SMOKETEST_DIR/04-relatedperson.json"
  "$SMOKETEST_DIR/05-coverage.json"
  "$SMOKETEST_DIR/06-encounter.json"
  "$SMOKETEST_DIR/07-condition.json"
  "$SMOKETEST_DIR/08-observation.json"
)

if [[ "$MODE" == "delete" || "$MODE" == "cleanup" || "$MODE" == "--delete" ]]; then
  ORDERED_FILES=("${FILES[@]}")
  ORDERED_FILES=($(printf '%s\n' "${ORDERED_FILES[@]}" | tac))
else
  ORDERED_FILES=("${FILES[@]}")
fi

for file in "${ORDERED_FILES[@]}"; do
  if [ ! -f "$file" ]; then
    echo "Missing required smoke file: $file" >&2
    exit 1
  fi

  RESOURCE_TYPE="$(python - <<'PY' "$file"
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    data = json.load(f)
print(data.get('resourceType', ''))
PY
)"
  RESOURCE_ID="$(python - <<'PY' "$file"
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    data = json.load(f)
print(data.get('id', ''))
PY
)"

  if [ -z "$RESOURCE_TYPE" ]; then
    echo "Unable to determine resourceType from $file" >&2
    exit 1
  fi

  if [ -z "$RESOURCE_ID" ]; then
    echo "Unable to determine resource id from $file" >&2
    exit 1
  fi

  name="$(basename "$file")"
  if [[ "$MODE" == "delete" || "$MODE" == "cleanup" || "$MODE" == "--delete" ]]; then
    echo "Deleting $name as $RESOURCE_TYPE/$RESOURCE_ID from $BASE_URL"
    curl -sS -X DELETE "$BASE_URL/$RESOURCE_TYPE/$RESOURCE_ID" || true
  else
    echo "Running $name as $RESOURCE_TYPE/$RESOURCE_ID against $BASE_URL"
    curl -sS -X PUT "$BASE_URL/$RESOURCE_TYPE/$RESOURCE_ID" \
      -H "Content-Type: application/fhir+json" \
      --data-binary "@$file" \
      | jq -r '.resourceType // .issue // .message // .id // "OK"' || true
  fi

  echo
  echo "----------------------------------------"
  echo
done
