# CS2 Betting AI — Phase 1

Windows 11, native Python, PostgreSQL. Establishes the database, API client, recent-match importer and tests.

## Verified provider details
- Base URL: https://api.citoapi.com/api/v1
- Authentication: `x-api-key` header
- JSON envelope: `success`, `data`; list responses include `meta`
- Pagination: `limit`, `page`
- Free plan: 500 requests/month, 30 days of history. Full archive requires a paid plan.
- Routes: `GET /cs2`, `/cs2/matches/recent`, `/cs2/matches/{matchId}`, `/cs2/matches/{matchId}/maps`, `/cs2/matches/{matchId}/player-stats`.

Docs: https://cs2-api.org/docs/ and https://cs2-api.org/endpoints/

## 1. PostgreSQL
Install PostgreSQL 15+ for Windows: https://www.postgresql.org/download/windows/

In pgAdmin Query Tool or psql:
```sql
CREATE USER cs2ai WITH PASSWORD 'change_this_password';
CREATE DATABASE cs2_betting_ai OWNER cs2ai;
```

## 2. Python setup
Use Python 3.14 (64-bit), then PowerShell in this directory:
```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env`: set `DATABASE_URL` and `CS2_API_KEY`. Never commit `.env`.

## 3. Initialize and verify
```powershell
python -m app.cli init-db
python -m app.cli db-check
python -m app.cli probe
```
`probe` calls only documented routes `/cs2` and `/cs2/matches/recent?limit=1&page=1`. It saves sample JSON under `data/api_samples/` and never prints the key.

## 4. Upgrade an existing database
Run all additive migrations before importing the updated code:
```powershell
python -m app.cli migrate-schema
```
The command applies every numbered SQL migration in order and is safe to repeat. Migration 001 adds match/map metadata; migration 002 expands player profiles and map-level statistics. No existing rows are dropped. The team reference on player statistics is nullable because the API may omit reliable team context.

## 5. Import matches and maps
```powershell
python -m app.cli ingest-recent --limit 20 --pages 1
```
The importer upserts matches, teams, tournaments and embedded map results. Re-running the same page updates existing rows rather than creating duplicate match/map records.

## 6. Import player statistics for one match
First make sure the match and its maps have been imported. Then run:
```powershell
python -m app.cli ingest-match-stats --match-id cs2-match-2400060
```
Replace the example with a provider match ID already stored in the database. The command makes one API request to `/cs2/matches/{matchId}/player-stats`. It upserts players by provider player ID and statistics by map/player, preserves null values and raw payloads, and skips rows that cannot be safely linked to a known map/player. A response with `meta.dataAvailable=false` is treated as unavailable rather than as an error.

The importer stores aggregate K/D/A, plus/minus, headshots, headshot percentage, first kills/deaths, ADR, KAST and rating, plus CT/T side splits and API data-quality/confidence fields when supplied. Missing fields remain NULL; no zeros or statistics are fabricated.

## 7. Tests
```powershell
python -m pytest -q
```

## Scope
No trained models or automated betting. Actual bets remain manual. The objective is a trustworthy, reproducible data foundation. Keep raw JSON, UTC timestamps, provider IDs, and historical snapshots. Use chronological splits later to prevent data leakage.
