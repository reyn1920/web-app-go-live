import { FastifyPluginAsync } from "fastify";

const plugin: FastifyPluginAsync = async (app) => {
  app.post("/workflows/trigger", async (req: any) => {
    // TODO: call n8n webhook with payload; for now just ack
    return { queued: true, payload: req.body ?? {} };
  });
};

export default plugin;
