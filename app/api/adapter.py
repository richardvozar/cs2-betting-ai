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

def normalize_match(item):
    return {
        "external_id": str(item["id"]) if item.get("id") is not None else None,
        "event_name": item.get("eventName"),
        "starts_at": as_utc_datetime(item.get("startsAt")),
        "best_of": _int(item.get("bestOf")),
        "status": item.get("status"),
        "team1_name": item.get("team1Name"),
        "team2_name": item.get("team2Name"),
        "team1_score": _int(item.get("team1Score")),
        "team2_score": _int(item.get("team2Score")),
        "raw": item,
    }
