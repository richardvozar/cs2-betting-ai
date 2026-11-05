from datetime import datetime, timezone


def extract_data(payload):
    return payload.get("data") if isinstance(payload, dict) and "data" in payload else payload


def as_utc_datetime(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _int(value):
    try:
        return int(value) if value is not None else None
    except (ValueError, TypeError):
        return None


def _bool(value):
    return value if isinstance(value, bool) else None


def _provider_id(value):
    return str(value) if value is not None else None


def normalize_match(item):
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
        "raw": item,
    }


def normalize_maps(maps):
    if not isinstance(maps, list):
        return []
    normalized = []
    for position, item in enumerate(maps, start=1):
        if not isinstance(item, dict):
            continue
        normalized.append(normalize_map(item, fallback_number=position))
    return normalized


def normalize_map(item, fallback_number=1):
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
