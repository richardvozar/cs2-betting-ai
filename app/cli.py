import json
from pathlib import Path
import typer
from rich import print
from rich.panel import Panel
from sqlalchemy import text
from app.config import get_settings
from app.db import engine, init_db, SessionLocal
from app.api.client import CS2APIClient
from app.collectors import ingest_recent_matches

app = typer.Typer(help="CS2 Betting AI — Phase 1 data tools")


@app.command("init-db")
def init_database():
    init_db()
    print("[green]Database tables created.[/green]")


@app.command("migrate-schema")
def migrate_schema():
    migration = Path(__file__).resolve().parent.parent / "migrations" / "001_match_map_ingestion.sql"
    statements = [part.strip() for part in migration.read_text(encoding="utf-8").split(";") if part.strip()]
    with engine.begin() as conn:
        for statement in statements:
            conn.exec_driver_sql(statement)
    print("[green]Match/map schema migration applied.[/green]")


@app.command("db-check")
def db_check():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("[green]PostgreSQL connection OK.[/green]")


@app.command()
def probe():
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
    s = get_settings()
    if not s.cs2_api_key:
        raise typer.BadParameter("Set CS2_API_KEY in .env")
    client = CS2APIClient(s.cs2_api_base_url, s.cs2_api_key, s.cs2_api_timeout)
    total_matches = 0
    total_maps = 0
    with SessionLocal() as session:
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


if __name__ == "__main__":
    app()
