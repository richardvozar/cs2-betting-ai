import re
from sqlalchemy import select
from app.api.adapter import extract_data, normalize_match
from app.models import Team, Tournament, Match, MatchMap, RawApiRecord


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _int_or_none(value):
    try:
        return int(value) if value is not None else None
    except (ValueError, TypeError):
        return None


def upsert_team(session, name, external_id=None, metadata=None):
    if not name and not external_id:
        return None
    metadata = metadata if isinstance(metadata, dict) else {}
    ext_id = str(external_id) if external_id else "name:" + slugify(name)
    row = session.scalar(select(Team).where(Team.external_id == ext_id))
    if row is None:
        row = Team(external_id=ext_id, name=name or ext_id)
        session.add(row)
    if name:
        row.name = name
        row.slug = metadata.get("slug") or slugify(name)
    row.tag = metadata.get("teamTag") or row.tag
    row.country_code = metadata.get("countryCode") or row.country_code
    row.world_ranking = _int_or_none(metadata.get("worldRanking")) if metadata.get("worldRanking") is not None else row.world_ranking
    row.vrs_ranking = _int_or_none(metadata.get("vrsRanking")) if metadata.get("vrsRanking") is not None else row.vrs_ranking
    session.flush()
    return row


def _upsert_tournament(session, external_id, name):
    if not external_id and not name:
        return None
    ext_id = str(external_id) if external_id else "name:" + slugify(name)
    row = session.scalar(select(Tournament).where(Tournament.external_id == ext_id))
    if row is None:
        row = Tournament(external_id=ext_id, name=name or ext_id)
        session.add(row)
    elif name:
        row.name = name
    session.flush()
    return row


def _save_raw_record(session, endpoint, external_id, payload):
    row = session.scalar(
        select(RawApiRecord).where(
            RawApiRecord.provider == "citoapi_cs2",
            RawApiRecord.endpoint == endpoint,
            RawApiRecord.external_id == external_id,
        ).order_by(RawApiRecord.id.desc())
    )
    if row is None:
        session.add(RawApiRecord(
            provider="citoapi_cs2", endpoint=endpoint,
            external_id=external_id, payload=payload,
        ))
    else:
        row.payload = payload


def _upsert_map(session, match, item, team1, team2):
    row = None
    if item["external_id"]:
        row = session.scalar(select(MatchMap).where(MatchMap.external_id == item["external_id"]))
    if row is None:
        row = session.scalar(select(MatchMap).where(
            MatchMap.match_id == match.id,
            MatchMap.map_number == item["map_number"],
        ))
    if row is None:
        row = MatchMap(match_id=match.id, map_number=item["map_number"])
        session.add(row)
    row.match_id = match.id
    row.external_id = item["external_id"] or row.external_id
    row.map_number = item["map_number"]
    row.map_name = item["map_name"] or row.map_name
    row.status = item["status"] or row.status
    row.team1_score = item["team1_score"] if item["team1_score"] is not None else row.team1_score
    row.team2_score = item["team2_score"] if item["team2_score"] is not None else row.team2_score
    winner_id = item["winner_team_external_id"]
    picker_id = item["picker_team_external_id"]
    row.winner_team_id = _team_pk(team1, team2, winner_id) or row.winner_team_id
    row.picker_team_id = _team_pk(team1, team2, picker_id) or row.picker_team_id
    row.duration_rounds = item["duration_rounds"] if item["duration_rounds"] is not None else row.duration_rounds
    row.result_type = item["result_type"] or row.result_type
    row.result_status = item["result_status"] or row.result_status
    row.is_forfeit = item["is_forfeit"] if item["is_forfeit"] is not None else row.is_forfeit
    row.stats_eligible = item["stats_eligible"] if item["stats_eligible"] is not None else row.stats_eligible
    row.unavailable_reason = item["unavailable_reason"] or row.unavailable_reason
    row.source_payload = item["raw"]
    session.flush()
    return row


def _team_pk(team1, team2, external_id):
    if not external_id:
        return None
    if team1 and team1.external_id == external_id:
        return team1.id
    if team2 and team2.external_id == external_id:
        return team2.id
    return None


def ingest_recent_matches(session, payload, endpoint="/cs2/matches/recent"):
    records = extract_data(payload)
    if not isinstance(records, list):
        raise ValueError("Expected response data to be a list; inspect saved API sample.")
    imported = 0
    maps_imported = 0
    for item in records:
        if not isinstance(item, dict):
            continue
        n = normalize_match(item)
        if not n["external_id"]:
            continue
        _save_raw_record(session, endpoint, n["external_id"], item)
        event = _upsert_tournament(session, n["event_external_id"], n["event_name"])
        t1 = upsert_team(session, n["team1_name"], n["team1_id"], n["team1_metadata"])
        t2 = upsert_team(session, n["team2_name"], n["team2_id"], n["team2_metadata"])
        match = session.scalar(select(Match).where(Match.external_id == n["external_id"]))
        if match is None:
            match = Match(external_id=n["external_id"])
            session.add(match)
            session.flush()
        match.tournament_id = event.id if event else match.tournament_id
        match.event_external_id = n["event_external_id"] or match.event_external_id
        match.team1_id = t1.id if t1 else match.team1_id
        match.team2_id = t2.id if t2 else match.team2_id
        match.starts_at = n["starts_at"] or match.starts_at
        match.status = n["status"] or match.status
        match.result_type = n["result_type"] or match.result_type
        match.is_forfeit = n["is_forfeit"] if n["is_forfeit"] is not None else match.is_forfeit
        match.stats_eligible = n["stats_eligible"] if n["stats_eligible"] is not None else match.stats_eligible
        match.unavailable_reason = n["unavailable_reason"] or match.unavailable_reason
        match.best_of = n["best_of"] if n["best_of"] is not None else match.best_of
        match.team1_score = n["team1_score"] if n["team1_score"] is not None else match.team1_score
        match.team2_score = n["team2_score"] if n["team2_score"] is not None else match.team2_score
        if match.team1_score is not None and match.team2_score is not None:
            if match.team1_score > match.team2_score and t1:
                match.winner_team_id = t1.id
            elif match.team2_score > match.team1_score and t2:
                match.winner_team_id = t2.id
        match.source_payload = item
        session.flush()
        for map_item in n["maps"]:
            _upsert_map(session, match, map_item, t1, t2)
            maps_imported += 1
        imported += 1
    session.commit()
    return {"matches": imported, "maps": maps_imported}
