import { sql } from 'kysely'
import { db } from '../client.js'

export async function provisionTenant(tenantId: string): Promise<void> {
  console.log(`Provisioning tenant: ${tenantId}`)

  // Create tenant schema
  await sql`CREATE SCHEMA IF NOT EXISTS ${sql.raw('"' + tenantId + '"')}`.execute(db)

  // Create tenant-specific tables
  await sql`CREATE TABLE IF NOT EXISTS ${sql.raw('"' + tenantId + '"')}.videos (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ideation',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
  )`.execute(db)

  console.log(`✅ Tenant ${tenantId} provisioned`)
}

