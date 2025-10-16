import { env } from "./env";
import analytics from "./routes/analytics";
import channels from "./routes/channels";
import events from "./routes/events";
import health from "./routes/health";
import tenants from "./routes/tenants";
import videos from "./routes/videos";
import workflows from "./routes/workflows";
import { buildServer } from "./server";

const app = buildServer();

app.register(health, { prefix: "/api" });
app.register(tenants, { prefix: "/api" });
app.register(channels, { prefix: "/api" });
app.register(videos, { prefix: "/api" });
app.register(workflows, { prefix: "/api" });
app.register(analytics, { prefix: "/api" });
app.register(events, { prefix: "/api" });

app
  .listen({ port: env.PORT, host: "0.0.0.0" })
  .then((addr) => app.log.info(`API on ${addr}`))
  .catch((err) => {
    app.log.error(err);
    process.exit(1);
  });
