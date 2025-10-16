# Monkey Paw Productions v5 (Optional Node.js Service)

## Overview

This is an **optional** Node.js/TypeScript/Postgres service that complements the main Python system.

**Main System:** Python/FastAPI on port 8000 (149 routes)  
**V5 Service:** Node.js/Fastify on port 8080 (optional add-on)

## Features

- DB-per-tenant (each tenant gets separate Postgres database)
- Event-driven architecture (EDA mediator)
- n8n orchestration integration
- Tenant isolation for B2B SaaS

## Quick Start

```bash
# 1) Safety snapshot
mkdir -p ../safety && cp -a . ../safety/mpaw_v5_$(date +%Y%m%d_%H%M%S)

# 2) Env
cp .env.example .env

# 3) Bring up services
docker compose up -d --build

# 4) Verify end-to-end
chmod +x scripts/verify.sh
./scripts/verify.sh
```

## n8n

- Open http://localhost:5678 (admin/admin)
- Import `workflows/n8n/breaking_news_example.json`
- Set `N8N_WEBHOOK_URL` in `.env` if you want `/api/events` to forward

## Remote Desktop Gateway (Blender/Resolve)

- Install RustDesk or Apache Guacamole on render workstation
- Expose token-guarded HTTP command runner
- Set `COMMAND_RUNNER_URL`, `COMMAND_RUNNER_TOKEN` in `.env`
- n8n HTTP Request node calls runner to launch Blender/Resolve scripts

## Multi-tenancy

- `POST /api/tenants` creates separate Postgres database for tenant
- Use `X-Tenant-Id` header with `/api/videos` to read/write in tenant DB
- `/api/channels` is core registry stored in admin DB

## Events (Mediator topology)

- `POST /api/events` forwards to `N8N_WEBHOOK_URL`
- Add retries/backoff in n8n or extend server logic

## HITL Guardrails

- `approvals` table exists in each tenant DB (stub)
- Add `/api/approvals` when you wire UI

## Integration with Main Python System

This service is **optional** and runs alongside the main Python system:
- Python system: port 8000 (all existing features)
- Node.js V5: port 8080 (optional orchestration)
- Both can run simultaneously
- Use for visual n8n workflows and Postgres multi-tenant if needed
