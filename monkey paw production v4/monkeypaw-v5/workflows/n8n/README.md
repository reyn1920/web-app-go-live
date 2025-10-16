# n8n Workflows

## Import Instructions

1. Open http://localhost:5678 (admin/admin)
2. Click "Workflows" → "Import from File"
3. Select `breaking_news_example.json`
4. Activate the workflow

## Breaking News Example

This stub workflow:
- Runs every 15 minutes (Cron trigger)
- Sends HTTP POST to `http://api:8080/api/workflows/trigger`
- Payload: `{source: "cron"}`

Expand this to:
- Check RSS feed for breaking news
- Call AI scriptwriting service
- Trigger rendering pipeline
- Publish to YouTube
