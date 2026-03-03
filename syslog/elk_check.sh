#!/usr/bin/env bash
set -euo pipefail

echo "[ELK] Elasticsearch health:"
curl -s http://localhost:9200/_cluster/health?pretty

echo "[ELK] Current indices:"
curl -s 'http://localhost:9200/_cat/indices?v'

echo "[ELK] Opsie index sample:"
curl -s 'http://localhost:9200/opsie-firewall-*/_search?size=5&sort=@timestamp:desc' \
  -H 'Content-Type: application/json' \
  -d '{"query":{"match_all":{}}}' | sed 's/\\n/\n/g'

echo "[ELK] Logstash status API:"
curl -s http://localhost:9600/?pretty || true

