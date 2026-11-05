from app.db import Base
from app import models

def test_expected_tables_registered():
    expected = {"teams", "tournaments", "matches", "match_maps", "players",
                "player_map_stats", "raw_api_records", "model_runs", "predictions"}
    assert expected.issubset(set(Base.metadata.tables))
