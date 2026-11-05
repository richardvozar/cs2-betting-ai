from types import SimpleNamespace
from app.collectors import ingest_match_player_stats
from app.models import Match


class UnavailableStatsSession:
    """Minimal session double that returns a known match for the unavailable-data test."""
    def __init__(self):
        self.committed = False

    def scalar(self, statement):
        entity = statement.column_descriptions[0]["entity"]
        if entity is Match:
            return SimpleNamespace(id=1, external_id="match1")
        return None

    def commit(self):
        self.committed = True


def test_unavailable_player_stats_are_a_safe_noop():
    """Unavailable provider data is retained without creating player/stat rows."""
    session = UnavailableStatsSession()
    result = ingest_match_player_stats(
        session,
        "match1",
        {"success": True, "data": [], "meta": {"dataAvailable": False}},
    )
    assert result == {"players": 0, "stats": 0, "skipped": 0, "available": False}
    assert session.committed
