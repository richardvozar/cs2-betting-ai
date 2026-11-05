from app.api.adapter import extract_data, normalize_match, as_utc_datetime

def test_extract_data_envelope():
    assert extract_data({"success": True, "data": [{"id": "m1"}]}) == [{"id": "m1"}]

def test_normalize_match():
    row = {"id": "m1", "eventName": "IEM", "startsAt": "2026-10-01T09:00:00Z",
           "bestOf": 3, "status": "completed", "team1Name": "Legacy",
           "team2Name": "The MongolZ", "team1Score": 1, "team2Score": 2}
    n = normalize_match(row)
    assert n["external_id"] == "m1"
    assert n["best_of"] == 3
    assert n["team2_score"] == 2
    assert n["starts_at"].tzinfo is not None

def test_naive_datetime_assumed_utc():
    assert as_utc_datetime("2026-01-01T12:00:00").utcoffset().total_seconds() == 0
