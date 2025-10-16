import { FastifyPluginAsync } from "fastify";

const plugin: FastifyPluginAsync = async (app) => {
  app.post("/analytics/ingest", async (req: any) => {
    // TODO: persist metrics and feed data flywheel later
    return { ok: true };
  });
};

export default plugin;
