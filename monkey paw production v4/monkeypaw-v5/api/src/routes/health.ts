import { FastifyPluginAsync } from "fastify";

const plugin: FastifyPluginAsync = async (app) => {
  app.get("/health", async () => ({ status: "ok" }));
};

export default plugin;
