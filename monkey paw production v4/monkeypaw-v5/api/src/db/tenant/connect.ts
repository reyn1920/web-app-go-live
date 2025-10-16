import { Kysely, PostgresDialect } from "kysely";
import pkg from "pg";
const { Pool } = pkg;

export function connectTenant(dsn: string) {
  return new Kysely<any>({
    dialect: new PostgresDialect({ pool: new Pool({ connectionString: dsn }) })
  });
}

