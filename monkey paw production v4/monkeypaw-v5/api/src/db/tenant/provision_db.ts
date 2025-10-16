import pkg from "pg";
import { addTenant, ensureCore } from "./registry";
const { Client } = pkg;

// adminDsn points to the admin DB on the server (e.g., postgres://user:pass@db:5432/mpaw)
// We'll create a new database per tenant, run minimal tables, and store its DSN in the registry.
export async function provisionDatabase(tenantId: string, name: string, adminDsn: string) {
  const admin = new Client({ connectionString: adminDsn });
  await admin.connect();
  const dbName = `mpaw_${tenantId}`;
  
  // Check if database exists
  const exists = await admin.query(`SELECT 1 FROM pg_database WHERE datname = $1`, [dbName]);
  if (exists.rows.length === 0) {
    await admin.query(`CREATE DATABASE ${dbName}`);
  }
  await admin.end();

  const dsn = adminDsn.replace(/\/[^/]+$/, `/${dbName}`);

  const client = new Client({ connectionString: dsn });
  await client.connect();
  await client.query(`CREATE TABLE IF NOT EXISTS videos (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ideation',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
  )`);
  await client.query(`CREATE TABLE IF NOT EXISTS approvals (
    id TEXT PRIMARY KEY,
    entity TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
  )`);
  await client.end();

  await ensureCore();
  await addTenant(tenantId, name, dsn);
  return { dbName, dsn };
}

