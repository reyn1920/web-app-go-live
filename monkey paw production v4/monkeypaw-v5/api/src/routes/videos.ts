import { FastifyPluginAsync } from "fastify";
import { connectTenant } from "../db/tenant/connect";
import { getTenantDsn } from "../db/tenant/registry";

const plugin: FastifyPluginAsync = async (app) => {
  app.get("/videos", async (req: any, reply) => {
    const t = req.headers["x-tenant-id"] as string;
    if (!t) return reply.code(400).send({ error: "X-Tenant-Id required" });
    const dsn = await getTenantDsn(t);
    if (!dsn) return reply.code(404).send({ error: "tenant not found" });
    const db = connectTenant(dsn);
    const rows = await db.selectFrom("videos").selectAll().execute();
    await db.destroy();
    return rows;
  });

  app.post("/videos", async (req: any, reply) => {
    const t = req.headers["x-tenant-id"] as string;
    const { id, title, status, metadata } = req.body as any;
    if (!t || !id || !title) return reply.code(400).send({ error: "missing fields" });
    const dsn = await getTenantDsn(t);
    if (!dsn) return reply.code(404).send({ error: "tenant not found" });
    const db = connectTenant(dsn);
    await db
      .insertInto("videos")
      .values({ id, title, status: status ?? "ideation", metadata: metadata ?? {} })
      .execute();
    await db.destroy();
    return { ok: true };
  });
};

export default plugin;
