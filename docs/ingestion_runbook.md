# Ingestion runbook (Phase 1)

## Prerequisites

- Docker
- Python 3.10+

## Environment

Copy `.env.example` to `.env` and set values:

- `ARANGO_URL`
- `ARANGO_USERNAME`
- `ARANGO_PASSWORD`
- `ARANGO_DB`

## Option A: local ArangoDB via Docker

```bash
docker compose up -d
curl http://localhost:8529/_api/version
```

UI: `http://localhost:8529`

## Generate sample data

```bash
python scripts/generate_data.py --output data/sample --size sample --seed 42
```

## Ingest data (local or remote)

```bash
python scripts/ingest.py --data-dir data/sample
```

Re-import (truncate then import):

```bash
python scripts/ingest.py --data-dir data/sample --force
```

## Validate

- Run Python tests:

```bash
pytest -q
```

## Reset DB (dev only)

Dry run:

```bash
python scripts/reset_db.py
```

Execute (local only):

```bash
python scripts/reset_db.py --execute --confirm
```

