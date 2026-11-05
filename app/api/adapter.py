from datetime import datetime, timezone


def extract_data(payload):
    """Unwrap the standard API response envelope when a data field is present."""
    return payload.get("data") if isinstance(payload, dict) and "data" in payload else payload


def as_utc_datetime(value):
    """Parse an ISO-8601 timestamp and normalize it to timezone-aware UTC.

Naive timestamps are interpreted as UTC. Invalid or empty values return None."""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    # Apply one consistent timezone policy to timestamps without an offset.
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _int(value):
    """Convert an optional provider value to int without replacing missing data with zero."""
    try:
        return int(value) if value is not None else None
    except (ValueError, TypeError):
        return None


def _float(value):
    """Convert an optional provider value to float; invalid or missing values return None."""
    try:
        return float(value) if value is not None else None
    except (ValueError, TypeError):
        return None


def _bool(value):
    """Accept actual booleans only; unknown or missing values remain None."""
    return value if isinstance(value, bool) else None


def _provider_id(value):
    """Normalize provider identifiers to strings while preserving missing IDs as None."""
    return str(value) if value is not None else None


def normalize_match(item):
    """Normalize one Cito match object into the application's match representation.

Team data may be nested or supplied at the top level. The original payload is
retained so fields not yet modeled are not lost."""
    team1 = item.get("team1") if isinstance(item.get("team1"), dict) else {}
    team2 = item.get("team2") if isinstance(item.get("team2"), dict) else {}
    return {
        "external_id": _provider_id(item.get("id")),
        "event_external_id": _provider_id(item.get("eventId")),
        "event_name": item.get("eventName"),
        "starts_at": as_utc_datetime(item.get("startsAt")),
        "best_of": _int(item.get("bestOf")),
        "status": item.get("status"),
        "result_type": item.get("resultType"),
        "is_forfeit": _bool(item.get("isForfeit")),
        "stats_eligible": _bool(item.get("statsEligible")),
        "unavailable_reason": item.get("unavailableReason"),
        "team1_id": _provider_id(item.get("team1Id") or team1.get("id")),
        "team2_id": _provider_id(item.get("team2Id") or team2.get("id")),
        "team1_name": item.get("team1Name") or team1.get("name"),
        "team2_name": item.get("team2Name") or team2.get("name"),
        "team1_metadata": team1,
        "team2_metadata": team2,
        "team1_score": _int(item.get("team1Score")),
        "team2_score": _int(item.get("team2Score")),
        "maps": normalize_maps(item.get("maps") or []),
        # Keep the original object for auditing and future schema expansion.
        "raw": item,
    }


def normalize_maps(maps):
    """Normalize map objects, using their list position when mapNumber is absent."""
    if not isinstance(maps, list):
        return []
    normalized = []
    for position, item in enumerate(maps, start=1):
        if not isinstance(item, dict):
            continue
        normalized.append(normalize_map(item, fallback_number=position))
    return normalized


def normalize_map(item, fallback_number=1):
    """Normalize one map result without fabricating scores or round counts."""
    return {
        "external_id": _provider_id(item.get("id")),
        "map_number": _int(item.get("mapNumber")) or fallback_number,
        "map_name": item.get("mapName"),
        "status": item.get("status"),
        "team1_score": _int(item.get("team1Score")),
        "team2_score": _int(item.get("team2Score")),
        "winner_team_external_id": _provider_id(item.get("winnerTeamId")),
        "picker_team_external_id": _provider_id(item.get("pickTeamId")),
        "duration_rounds": _int(item.get("durationRounds")),
        "result_type": item.get("resultType"),
        "result_status": item.get("resultStatus"),
        "is_forfeit": _bool(item.get("isForfeit")),
        "stats_eligible": _bool(item.get("statsEligible")),
        "unavailable_reason": item.get("unavailableReason"),
        "raw": item,
    }


def normalize_player_stat(item):
    """Normalize one player's performance row for a single map.

Aggregate and CT/T split metrics remain separate. Missing numeric fields stay
None so downstream code can distinguish missing data from a genuine zero."""
    player = item.get("player") if isinstance(item.get("player"), dict) else {}
    team = item.get("team") if isinstance(item.get("team"), dict) else {}
    return {
        "external_id": _provider_id(item.get("id")),
        "map_external_id": _provider_id(item.get("mapId")),
        "match_external_id": _provider_id(item.get("matchId")),
        "player_external_id": _provider_id(item.get("playerId") or player.get("id")),
        "player_name": item.get("playerName") or player.get("nickname") or player.get("name"),
        "player_slug": player.get("slug"),
        "player_country": player.get("country"),
        "player_country_code": player.get("countryCode"),
        "player_primary_role": player.get("primaryRole") or player.get("role"),
        "team_external_id": _provider_id(item.get("teamId") or team.get("id")),
        "team_name": item.get("teamName") or team.get("name"),
        "kills": _int(item.get("kills")),
        "deaths": _int(item.get("deaths")),
        "assists": _int(item.get("assists")),
        "plus_minus": _int(item.get("plusMinus")),
        "headshot_kills": _int(item.get("headshots")),
        "headshot_percent": _float(item.get("headshotPercent")),
        "first_kills": _int(item.get("firstKills")),
        "first_deaths": _int(item.get("firstDeaths")),
        "adr": _float(item.get("adr")),
        "kast": _float(item.get("kast")),
        "rating": _float(item.get("rating")),
        "rating_version": item.get("ratingVersion"),
        "ct_kills": _int(item.get("ctKills")),
        "ct_deaths": _int(item.get("ctDeaths")),
        "ct_adr": _float(item.get("ctAdr")),
        "ct_kast": _float(item.get("ctKast")),
        "ct_rating": _float(item.get("ctRating")),
        "t_kills": _int(item.get("tKills")),
        "t_deaths": _int(item.get("tDeaths")),
        "t_adr": _float(item.get("tAdr")),
        "t_kast": _float(item.get("tKast")),
        "t_rating": _float(item.get("tRating")),
        "side_data_available": _bool(item.get("sideDataAvailable")),
        "data_quality": item.get("dataQuality"),
        "confidence": item.get("confidence"),
        "confidence_score": _float(item.get("confidenceScore")),
        "raw": item,
    }


def normalize_player_stats(items):
    """Normalize dictionary rows from a player-statistics response; ignore malformed rows."""
    if not isinstance(items, list):
        return []
    return [normalize_player_stat(item) for item in items if isinstance(item, dict)]
