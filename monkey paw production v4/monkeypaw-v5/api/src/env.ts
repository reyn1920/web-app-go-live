export const env = {
  NODE_ENV: process.env.NODE_ENV ?? "development",
  PORT: Number(process.env.PORT ?? 8080),
  DATABASE_URL: process.env.DATABASE_URL ?? "postgres://mpaw:mpaw@localhost:5432/mpaw",
  JWT_SECRET: process.env.JWT_SECRET ?? "devsecret",
  YOUTUBE_API_KEY: process.env.YOUTUBE_API_KEY ?? "",
  N8N_WEBHOOK_URL: process.env.N8N_WEBHOOK_URL ?? "",
  COMMAND_RUNNER_URL: process.env.COMMAND_RUNNER_URL ?? "",
  COMMAND_RUNNER_TOKEN: process.env.COMMAND_RUNNER_TOKEN ?? ""
};
