from app.api.adapter import (
    extract_data, normalize_match, normalize_map, normalize_player_stat,
    normalize_player_stats, as_utc_datetime,
)


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


def test_normalize_player_stat_preserves_nulls_and_side_fields():
    row = normalize_player_stat({
        "id": "stat1", "mapId": "map1", "matchId": "match1",
        "playerId": "player1", "playerName": "Example", "teamId": "team1",
        "kills": 20, "deaths": 15, "assists": None, "plusMinus": 5,
        "headshots": 10, "headshotPercent": 50.0, "firstKills": None,
        "firstDeaths": 2, "adr": 80.5, "kast": 72.3, "rating": 1.12,
        "ratingVersion": "2.1", "ctKills": 8, "ctDeaths": 7,
        "ctAdr": 75.2, "ctKast": 70.0, "ctRating": 1.1,
        "tKills": 12, "tDeaths": 8, "tAdr": 85.0, "tKast": 74.0,
        "tRating": 1.14, "sideDataAvailable": True,
        "dataQuality": "partial", "confidence": "medium", "confidenceScore": 0.7,
    })
    assert row["player_external_id"] == "player1"
    assert row["map_external_id"] == "map1"
    assert row["assists"] is None
    assert row["first_kills"] is None
    assert row["ct_kills"] == 8
    assert row["confidence_score"] == 0.7


def test_normalize_player_stats_ignores_non_dict_rows():
    assert len(normalize_player_stats([{"id": "1"}, None, "bad"])) == 1


def test_naive_datetime_assumed_utc():
    assert as_utc_datetime("2026-01-01T12:00:00").utcoffset().total_seconds() == 0
