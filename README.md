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
If you already initialized the Phase 1 database, run the additive migration before importing the updated code:
```powershell
python -m app.cli migrate-schema
```
This adds the new match/map metadata columns and a unique index for provider map IDs. It does not drop or rewrite existing rows. Run it once; it is safe to repeat.

## 5. Import a small sample
```powershell
python -m app.cli ingest-recent --limit 20 --pages 1
```
The importer now upserts matches, teams, tournaments and embedded map results. Re-running the same page updates the existing rows rather than creating duplicate match/map records. Existing name-based team records are retained; new imports use provider team IDs when available. Forfeit and non-played maps remain stored but are not marked as training-eligible when the API says otherwise.

Increase pages only after checking your API quota. The recent response already includes map results in the inspected sample, so this command does not make extra per-match map requests.

## 6. Tests
```powershell
python -m pytest -q
```

## Scope
No trained models or automated betting. Actual bets remain manual. The objective is a trustworthy, reproducible data foundation. Keep raw JSON, UTC timestamps, provider IDs, and historical snapshots. Use chronological splits later to prevent data leakage.
