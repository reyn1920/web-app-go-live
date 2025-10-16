## 2025-10-11 — v5 scaffold

- Added Node+TS Fastify API
- Postgres multi-tenant (database-per-tenant)
- Routes: /api/health, /api/tenants, /api/channels, /api/videos, /api/workflows/trigger, /api/analytics/ingest, /api/events
- Docker compose for db/api/n8n
- n8n workflow stub
- Desktop shell placeholder
- Verify script (per-tenant isolation)

## 2025-10-11 — v5r2 upgrades

- Switched from schema-per-tenant to **database-per-tenant** with registry
- Events → n8n mediator bridge
- HITL approvals table (stub)
- Remote desktop gateway guidance & envs
- Verifier updated to prove isolation across tenants

