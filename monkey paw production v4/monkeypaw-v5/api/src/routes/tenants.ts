import { FastifyPluginAsync } from "fastify";
import { provisionDatabase } from "../db/tenant/provision_db";
import { core, getTenantDsn } from "../db/tenant/registry";

const ADMIN_DSN = process.env.DATABASE_URL!;

const plugin: FastifyPluginAsync = async (app) => {
  app.get("/tenants", async () => {
    const rows = await core.selectFrom("public.tenants").selectAll().execute();
    return rows;
  });

  app.post("/tenants", async (req, reply) => {
    const { id, name } = (req.body as any) ?? {};
    if (!id || !name) return reply.code(400).send({ error: "id and name required" });
    const out = await provisionDatabase(id, name, ADMIN_DSN);
    return { ok: true, ...out };
  });

  app.get("/tenants/:id/dsn", async (req: any, reply) => {
    const dsn = await getTenantDsn(req.params.id);
    if (!dsn) return reply.code(404).send({ error: "unknown tenant" });
    return { dsn };
  });
};

export default plugin;
