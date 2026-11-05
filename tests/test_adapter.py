from app.api.adapter import extract_data, normalize_match, normalize_map, as_utc_datetime


def test_extract_data_envelope():
    assert extract_data({"success": True, "data": [{"id": "m1"}]}) == [{"id": "m1"}]


def test_normalize_match():
    row = {"id": "m1", "eventId": "e1", "eventName": "IEM", "startsAt": "2026-10-01T09:00:00Z",
           "bestOf": 3, "status": "completed", "team1Id": "t1", "team2Id": "t2",
           "team1Name": "Legacy", "team2Name": "The MongolZ", "team1Score": 1, "team2Score": 2,
           "statsEligible": True, "maps": [{"id": "map1", "mapNumber": 1, "mapName": "Ancient",
           "team1Score": 13, "team2Score": 10, "winnerTeamId": "t1", "durationRounds": 23}]}
    n = normalize_match(row)
    assert n["external_id"] == "m1"
    assert n["event_external_id"] == "e1"
    assert n["best_of"] == 3
    assert n["team2_score"] == 2
    assert n["team1_id"] == "t1"
    assert n["stats_eligible"] is True
    assert n["maps"][0]["map_name"] == "Ancient"
    assert n["maps"][0]["duration_rounds"] == 23
    assert n["starts_at"].tzinfo is not None


def test_forfeit_and_null_map_fields_are_preserved():
    n = normalize_match({"id": "m2", "isForfeit": True, "statsEligible": False,
                         "resultType": "forfeit", "maps": [
                             {"mapNumber": 1, "resultType": "forfeit", "isForfeit": True,
                              "statsEligible": False, "team1Score": None}]})
    assert n["is_forfeit"] is True
    assert n["stats_eligible"] is False
    assert n["maps"][0]["is_forfeit"] is True
    assert n["maps"][0]["team1_score"] is None


def test_normalize_map_keeps_overtime_scores():
    row = normalize_map({"mapNumber": 1, "team1Score": 24, "team2Score": 28})
    assert row["team1_score"] == 24
    assert row["team2_score"] == 28


def test_naive_datetime_assumed_utc():
    assert as_utc_datetime("2026-01-01T12:00:00").utcoffset().total_seconds() == 0
