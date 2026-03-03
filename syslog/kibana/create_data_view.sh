#!/usr/bin/env bash
set -euo pipefail

KIBANA_URL="${KIBANA_URL:-http://localhost:5601}"

curl -s -X POST "${KIBANA_URL}/api/data_views/data_view" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d '{
    "data_view": {
      "name": "opsie-firewall-*",
      "title": "opsie-firewall-*",
      "timeFieldName": "@timestamp"
    }
  }' | sed 's/\\n/\n/g'

echo
echo "Data view created/updated for pattern: opsie-firewall-*"

