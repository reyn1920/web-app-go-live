import { FastifyPluginAsync } from "fastify";
import { sql } from "kysely";
import { core } from "../db/tenant/registry";

const plugin: FastifyPluginAsync = async (app) => {
  // Keep channels in core 'public.channels' for directory (optional)
  await core.executeQuery(
    sql`CREATE TABLE IF NOT EXISTS public.channels (
      id TEXT PRIMARY KEY,
      tenant_id TEXT NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
      youtube_channel_id TEXT,
      title TEXT,
      created_at TIMESTAMPTZ DEFAULT now()
    )`.compile(core)
  );

  app.get("/channels", async (req: any) => {
    const t = req.headers["x-tenant-id"] as string;
    if (!t) return [];
    const rows = await core
      .selectFrom("public.channels")
      .selectAll()
      .where("tenant_id", "=", t)
      .execute();
    return rows;
  });

  app.post("/channels", async (req: any, reply) => {
    const t = req.headers["x-tenant-id"] as string;
    const { id, title, youtube_channel_id } = req.body as any;
    if (!t || !id) return reply.code(400).send({ error: "X-Tenant-Id header and id required" });
    await core
      .insertInto("public.channels")
      .values({ id, tenant_id: t, title, youtube_channel_id })
      .execute();
    return { ok: true };
  });
};

export default plugin;
