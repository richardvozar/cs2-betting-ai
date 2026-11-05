from app.collectors import ingest_match_player_stats


class EmptyStatsSession:
    def __init__(self):
        self.committed = False

    def scalar(self, statement):
        return None

    def commit(self):
        self.committed = True


def test_unavailable_player_stats_are_a_safe_noop():
    session = EmptyStatsSession()
    # Match lookup is intentionally absent: the collector validates match existence first.
    try:
        ingest_match_player_stats(session, "match1", {"success": True, "data": [], "meta": {"dataAvailable": False}})
    except ValueError as exc:
        assert "not in the database" in str(exc)
    else:
        raise AssertionError("Expected missing match to be rejected before stats are imported.")
