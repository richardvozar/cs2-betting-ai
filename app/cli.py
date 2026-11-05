import json
from pathlib import Path
import typer
from rich import print
from rich.panel import Panel
from sqlalchemy import text
from app.config import get_settings
from app.db import engine, init_db, SessionLocal
from app.api.client import CS2APIClient
from app.collectors import ingest_recent_matches, ingest_match_player_stats

app = typer.Typer(help="CS2 Betting AI — Phase 1 data tools")


@app.command("init-db")
def init_database():
    """Create all database tables declared by the SQLAlchemy models."""
    init_db()
    print("[green]Database tables created.[/green]")


def _run_migration(path):
    """Execute the SQL statements in one migration file within a transaction."""
    statements = [part.strip() for part in path.read_text(encoding="utf-8").split(";") if part.strip()]
    with engine.begin() as conn:
        for statement in statements:
            conn.exec_driver_sql(statement)


@app.command("migrate-schema")
def migrate_schema():
    """Apply numbered SQL migration files in filename order."""
    root = Path(__file__).resolve().parent.parent / "migrations"
    # Zero-padded migration filenames ensure schema changes run in sequence.
    for migration in sorted(root.glob("*.sql")):
        _run_migration(migration)
        print(f"[green]Applied {migration.name}.[/green]")


@app.command("db-check")
def db_check():
    """Verify that PostgreSQL accepts a simple query."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("[green]PostgreSQL connection OK.[/green]")


@app.command()
def probe():
    """Call lightweight API endpoints and save response samples for inspection."""
    s = get_settings()
    if not s.cs2_api_key:
        raise typer.BadParameter("Set CS2_API_KEY in .env")
    client = CS2APIClient(s.cs2_api_base_url, s.cs2_api_key, s.cs2_api_timeout)
    out = Path(s.cs2_api_sample_dir)
    out.mkdir(parents=True, exist_ok=True)
    for label, path, params in [
        ("api_info", "/cs2", None),
        ("recent_matches", "/cs2/matches/recent", {"limit": 1, "page": 1}),
    ]:
        payload = client.get_json(path, params)
        (out / f"{label}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        data = payload.get("data") if isinstance(payload, dict) else None
        count = len(data) if isinstance(data, list) else "n/a"
        print(Panel(f"Endpoint: {path}\nTop-level keys: {list(payload.keys()) if isinstance(payload, dict) else type(payload).__name__}\nData count: {count}\nSaved: {out / (label + '.json')}", title=label))


@app.command()
def ingest_recent(limit: int = typer.Option(25, min=1, max=100),
                  pages: int = typer.Option(1, min=1, max=10)):
    """Fetch recent match pages and upsert their match and map records."""
    s = get_settings()
    if not s.cs2_api_key:
        raise typer.BadParameter("Set CS2_API_KEY in .env")
    client = CS2APIClient(s.cs2_api_base_url, s.cs2_api_key, s.cs2_api_timeout)
    total_matches = 0
    total_maps = 0
    with SessionLocal() as session:
        # Stop when the API returns an empty page or explicitly reports no next page.
        for page in range(1, pages + 1):
            payload = client.get_json("/cs2/matches/recent", {"limit": limit, "page": page})
            result = ingest_recent_matches(session, payload)
            total_matches += result["matches"]
            total_maps += result["maps"]
            data = payload.get("data", []) if isinstance(payload, dict) else []
            meta = payload.get("meta", {}) if isinstance(payload, dict) else {}
            if not data or (isinstance(meta, dict) and meta.get("hasNext") is False):
                break
    print(f"[green]Imported/updated {total_matches} matches and {total_maps} map records.[/green]")


@app.command("ingest-match-stats")
def ingest_match_stats(match_id: str = typer.Option(..., "--match-id", help="Cito provider match ID")):
    """Fetch and import per-map player statistics for one provider match ID."""
    s = get_settings()
    if not s.cs2_api_key:
        raise typer.BadParameter("Set CS2_API_KEY in .env")
    client = CS2APIClient(s.cs2_api_base_url, s.cs2_api_key, s.cs2_api_timeout)
    endpoint = f"/cs2/matches/{match_id}/player-stats"
    payload = client.get_json(endpoint)
    with SessionLocal() as session:
        result = ingest_match_player_stats(session, match_id, payload, endpoint=endpoint)
    print(
        f"[green]Player-stat import finished.[/green] "
        f"Stats: {result['stats']}, players in response: {result['players']}, "
        f"skipped: {result['skipped']}, available: {result['available']}."
    )


if __name__ == "__main__":
    app()
