import { Kysely, PostgresDialect, sql } from "kysely";
import pkg from "pg";
import { env } from "../env";
const { Pool } = pkg;

export const db = new Kysely<any>({
  dialect: new PostgresDialect({ pool: new Pool({ connectionString: env.DATABASE_URL }) })
});

// tiny migration runner for the core admin DB
if (process.argv[2] === "migrate") {
  (async () => {
    await sql`CREATE SCHEMA IF NOT EXISTS public`.execute(db);
    await sql`CREATE TABLE IF NOT EXISTS public.tenants (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      dsn TEXT NOT NULL,
      created_at TIMESTAMPTZ DEFAULT now()
    )`.execute(db);
    console.log("Core migrations applied");
    process.exit(0);
  })().catch((e) => {
    console.error(e);
    process.exit(1);
  });
}
