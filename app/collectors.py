import re
from sqlalchemy import select
from app.api.adapter import extract_data, normalize_match
from app.models import Team, Tournament, Match, RawApiRecord

def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def upsert_team(session, name):
    if not name:
        return None
    ext_id = "name:" + slugify(name)
    row = session.scalar(select(Team).where(Team.external_id == ext_id))
    if row is None:
        row = Team(external_id=ext_id, name=name, slug=slugify(name))
        session.add(row)
        session.flush()
    return row

def ingest_recent_matches(session, payload, endpoint="/cs2/matches/recent"):
    records = extract_data(payload)
    if not isinstance(records, list):
        raise ValueError("Expected response data to be a list; inspect saved API sample.")
    imported = 0
    for item in records:
        if not isinstance(item, dict):
            continue
        n = normalize_match(item)
        if not n["external_id"]:
            continue
        session.add(RawApiRecord(provider="citoapi_cs2", endpoint=endpoint,
                                 external_id=n["external_id"], payload=item))
        event_id = None
        if n["event_name"]:
            ext_id = "name:" + slugify(n["event_name"])
            event = session.scalar(select(Tournament).where(Tournament.external_id == ext_id))
            if event is None:
                event = Tournament(external_id=ext_id, name=n["event_name"])
                session.add(event)
                session.flush()
            event_id = event.id
        t1, t2 = upsert_team(session, n["team1_name"]), upsert_team(session, n["team2_name"])
        match = session.scalar(select(Match).where(Match.external_id == n["external_id"]))
        if match is None:
            match = Match(external_id=n["external_id"])
            session.add(match)
        match.tournament_id = event_id or match.tournament_id
        match.team1_id = t1.id if t1 else match.team1_id
        match.team2_id = t2.id if t2 else match.team2_id
        match.starts_at = n["starts_at"] or match.starts_at
        match.status = n["status"] or match.status
        match.best_of = n["best_of"] or match.best_of
        match.team1_score = n["team1_score"] if n["team1_score"] is not None else match.team1_score
        match.team2_score = n["team2_score"] if n["team2_score"] is not None else match.team2_score
        if match.team1_score is not None and match.team2_score is not None:
            if match.team1_score > match.team2_score and t1:
                match.winner_team_id = t1.id
            elif match.team2_score > match.team1_score and t2:
                match.winner_team_id = t2.id
        match.source_payload = item
        imported += 1
    session.commit()
    return imported
