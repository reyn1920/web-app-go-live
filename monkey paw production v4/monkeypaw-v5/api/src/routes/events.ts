import { FastifyPluginAsync } from "fastify";
import fetch from "node-fetch";
import { env } from "../env";

const plugin: FastifyPluginAsync = async (app) => {
  app.post("/events", async (req: any, reply) => {
    const event = req.body ?? {};
    if (!env.N8N_WEBHOOK_URL) return { queued: true, note: "N8N_WEBHOOK_URL not set" };
    try {
      const r = await fetch(env.N8N_WEBHOOK_URL, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(event)
      });
      return { forwarded: true, status: r.status };
    } catch (e) {
      app.log.error(e);
      return reply.code(502).send({ error: "n8n unreachable" });
    }
  });
};

export default plugin;

