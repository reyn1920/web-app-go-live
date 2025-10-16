import { Kysely, PostgresDialect, sql } from "kysely";
import pkg from "pg";
import { env } from "../../env";
const { Pool } = pkg;

export const core = new Kysely<any>({
  dialect: new PostgresDialect({ pool: new Pool({ connectionString: env.DATABASE_URL }) })
});

export async function ensureCore() {
  await sql`CREATE TABLE IF NOT EXISTS public.tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    dsn TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
  )`.execute(core);
}

export async function addTenant(id: string, name: string, dsn: string) {
  await core
    .insertInto("public.tenants")
    .values({ id, name, dsn })
    .onConflict((o) => o.column("id").doUpdateSet({ name, dsn }))
    .execute();
}

export async function getTenantDsn(id: string): Promise<string | null> {
  const row = await core
    .selectFrom("public.tenants")
    .select(["dsn"])
    .where("id", "=", id)
    .executeTakeFirst();
  return row?.dsn ?? null;
}

