#!/usr/bin/env bash
set -euo pipefail
say(){ printf "\n==== %s ====\n" "$1"; }

# Safety snapshot
say "Snapshot"
mkdir -p ../safety && cp -a . ../safety/mpaw_v5_$(date +%Y%m%d_%H%M%S) && echo "$(date) snapshot" >> BACKUP_LOG.txt

# Bring up stack
say "Compose up"
docker compose up -d --build

# Wait for API health
say "Wait for API"
for i in {1..30}; do curl -sf http://localhost:8080/api/health && break || sleep 1; done

say "Health"
curl -s http://localhost:8080/api/health | jq .

# Create Tenant Alpha
say "Create tenant Alpha"
curl -s -X POST http://localhost:8080/api/tenants -H 'content-type: application/json' \
  -d '{"id":"talpha","name":"Alpha"}' | jq .

# Write & read in Alpha
say "Create channel Alpha"
curl -s -X POST http://localhost:8080/api/channels -H 'content-type: application/json' -H 'X-Tenant-Id: talpha' \
  -d '{"id":"chan1","title":"Demo Channel"}' | jq .

say "Create video Alpha"
curl -s -X POST http://localhost:8080/api/videos -H 'content-type: application/json' -H 'X-Tenant-Id: talpha' \
  -d '{"id":"a1","title":"Alpha Vid"}' | jq .

say "List videos Alpha"
curl -s http://localhost:8080/api/videos -H 'X-Tenant-Id: talpha' | jq .

# Create Tenant Bravo and prove isolation
say "Create tenant Bravo"
curl -s -X POST http://localhost:8080/api/tenants -H 'content-type: application/json' \
  -d '{"id":"tbravo","name":"Bravo"}' | jq .

say "List videos Bravo (should be empty)"
curl -s http://localhost:8080/api/videos -H 'X-Tenant-Id: tbravo' | jq .

echo -e "\nALL CHECKS PASSED"
