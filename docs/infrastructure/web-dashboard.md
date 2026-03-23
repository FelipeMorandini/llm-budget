# Web Dashboard

## Overview

The web dashboard provides a browser-based interface for viewing cost trends, project breakdowns, and model usage analytics.

## Launching

```bash
llm-toll --dashboard
llm-toll --dashboard --port 9000
```

The dashboard starts at `http://127.0.0.1:8050` by default. Press `Ctrl+C` to stop.

## Features

The dashboard displays:

- **Summary cards** -- Total cost, total calls, number of projects, number of models
- **Daily cost trend chart** -- Line chart showing cost per day over the last 30 days (powered by Chart.js)
- **Projects table** -- Per-project breakdown with calls, input/output tokens, and total cost
- **Models table** -- Per-model breakdown with calls, input/output tokens, and total cost

The dashboard auto-refreshes every 30 seconds.

## API Endpoints

The dashboard is served by a lightweight HTTP server (Python's `http.server`). The following JSON API endpoints are available:

| Endpoint | Description |
|----------|-------------|
| `GET /` | Dashboard HTML page |
| `GET /api/summary` | Total cost, calls, project count, model count |
| `GET /api/trends?days=30` | Daily cost aggregation for the last N days |
| `GET /api/projects` | Per-project usage summaries |
| `GET /api/models` | Per-model usage summaries |
| `GET /api/budgets` | Budget utilization for all projects |
| `GET /api/logs?project=X&limit=N` | Raw usage log entries with optional filters |

All API endpoints return JSON.

## Architecture

The dashboard uses a single-file implementation with:

- An embedded HTML/CSS/JavaScript page (dark theme)
- Chart.js loaded from CDN for the cost trend chart
- No additional Python dependencies required
- `http.server.HTTPServer` for the backend

The `DashboardHandler` class reads data from the same `BaseStore` used by the decorator and CLI.

## With PostgreSQL

```bash
llm-toll --dashboard --store-url postgresql://user:pass@host/llm_costs
```

The dashboard works with both SQLite and PostgreSQL backends.

## Programmatic Usage

```python
from llm_toll.dashboard import serve_dashboard
from llm_toll import SQLiteStore

store = SQLiteStore()
serve_dashboard(store, port=8050)
```
