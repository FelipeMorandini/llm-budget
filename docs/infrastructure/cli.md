# CLI Dashboard

## Overview

The `llm-toll` CLI provides terminal-based access to cost and usage statistics. It is installed automatically as a console script.

## Commands

### `--stats` -- Show Usage Statistics

```bash
# All projects summary
llm-toll --stats

# Filter by project
llm-toll --stats --project my_scraper

# Filter by model
llm-toll --stats --model gpt-4o
```

Output is a formatted table with color-coded costs:

- Green: < $0.01
- Yellow: $0.01 - $0.10
- Red: > $0.10

Colors are suppressed when the `NO_COLOR` environment variable is set.

### `--reset` -- Reset Budget

```bash
llm-toll --reset --project my_scraper
```

Resets the accumulated cost for a project to zero. Requires `--project`.

### `--export csv` -- Export Usage Logs

```bash
# Export all logs to stdout
llm-toll --export csv

# Export with filters
llm-toll --export csv --project my_scraper
llm-toll --export csv --model gpt-4o

# Export to a file
llm-toll --export csv --output report.csv
llm-toll --export csv --project my_scraper --output report.csv
```

CSV columns: `project`, `model`, `input_tokens`, `output_tokens`, `cost`, `created_at`.

### `--update-pricing` -- Fetch Latest Pricing

```bash
llm-toll --update-pricing
```

Fetches the latest model pricing from the remote source and caches it locally. See [Pricing Updates](pricing-updates.md).

### `--dashboard` -- Launch Web Dashboard

```bash
llm-toll --dashboard
llm-toll --dashboard --port 9000
```

Starts a browser-based dashboard at `http://127.0.0.1:8050` (or the specified port). See [Web Dashboard](web-dashboard.md).

## Global Options

| Option | Description |
|--------|-------------|
| `--version` | Show version and exit |
| `--db PATH` | Path to the SQLite database (default: `~/.llm_toll.db`) |
| `--store-url URL` | Store URL for PostgreSQL (e.g., `postgresql://user:pass@host/db`) |
| `--project NAME` | Filter by project name |
| `--model NAME` | Filter by model name |
| `--output FILE` | Output file for `--export` (default: stdout) |
| `--port PORT` | Port for `--dashboard` (default: 8050) |

## Examples

```bash
# View all projects
llm-toll --stats

# View per-model breakdown for a project
llm-toll --stats --project my_app

# View per-project breakdown for a model
llm-toll --stats --model gpt-4o

# Reset a project's budget counter
llm-toll --reset --project my_app

# Export to CSV file
llm-toll --export csv --output monthly_report.csv

# Use PostgreSQL backend
llm-toll --stats --store-url postgresql://user:pass@host/llm_costs

# Use a custom SQLite database
llm-toll --stats --db /path/to/my.db
```
