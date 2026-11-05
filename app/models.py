from datetime import datetime
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, Index, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class Team(Base):
    """A CS2 team identified by its provider ID, with optional ranking metadata."""
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str | None] = mapped_column(String(160))
    tag: Mapped[str | None] = mapped_column(String(40))
    country_code: Mapped[str | None] = mapped_column(String(8))
    world_ranking: Mapped[int | None] = mapped_column(Integer)
    vrs_ranking: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (Index("ix_teams_name", "name"),)


class Tournament(Base):
    """An event or tournament associated with one or more matches."""
    __tablename__ = "tournaments"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    external_id: Mapped[str | None] = mapped_column(String(120), unique=True)
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    tier: Mapped[str | None] = mapped_column(String(40))


class Match(Base):
    """A best-of match between two teams, including result and stats-eligibility metadata."""
    __tablename__ = "matches"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    tournament_id: Mapped[int | None] = mapped_column(ForeignKey("tournaments.id"))
    event_external_id: Mapped[str | None] = mapped_column(String(120))
    team1_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    team2_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    winner_team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str | None] = mapped_column(String(40))
    result_type: Mapped[str | None] = mapped_column(String(40))
    is_forfeit: Mapped[bool | None] = mapped_column()
    stats_eligible: Mapped[bool | None] = mapped_column()
    unavailable_reason: Mapped[str | None] = mapped_column(Text)
    best_of: Mapped[int | None] = mapped_column(Integer)
    team1_score: Mapped[int | None] = mapped_column(Integer)
    team2_score: Mapped[int | None] = mapped_column(Integer)
    source_payload: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MatchMap(Base):
    """A single map in a match, including score, veto and result metadata."""
    __tablename__ = "match_maps"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(120))
    map_number: Mapped[int] = mapped_column(Integer, nullable=False)
    map_name: Mapped[str | None] = mapped_column(String(60))
    status: Mapped[str | None] = mapped_column(String(40))
    team1_score: Mapped[int | None] = mapped_column(Integer)
    team2_score: Mapped[int | None] = mapped_column(Integer)
    winner_team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    picker_team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    duration_rounds: Mapped[int | None] = mapped_column(Integer)
    result_type: Mapped[str | None] = mapped_column(String(40))
    result_status: Mapped[str | None] = mapped_column(String(40))
    is_forfeit: Mapped[bool | None] = mapped_column()
    stats_eligible: Mapped[bool | None] = mapped_column()
    unavailable_reason: Mapped[str | None] = mapped_column(Text)
    source_payload: Mapped[dict | None] = mapped_column(JSONB)
    __table_args__ = (
        UniqueConstraint("match_id", "map_number", name="uq_match_map_number"),
        Index("ix_match_maps_external_id", "external_id", unique=True, postgresql_where=text("external_id IS NOT NULL")),
    )


class Player(Base):
    """A player profile keyed by the stable identifier supplied by the provider."""
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str | None] = mapped_column(String(60))
    slug: Mapped[str | None] = mapped_column(String(160))
    country_code: Mapped[str | None] = mapped_column(String(8))
    primary_role: Mapped[str | None] = mapped_column(String(60))


class PlayerMapStats(Base):
    """One player's performance statistics on one specific match map."""
    __tablename__ = "player_map_stats"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    external_id: Mapped[str | None] = mapped_column(String(120))
    map_id: Mapped[int] = mapped_column(ForeignKey("match_maps.id", ondelete="CASCADE"), nullable=False)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    kills: Mapped[int | None] = mapped_column(Integer)
    deaths: Mapped[int | None] = mapped_column(Integer)
    assists: Mapped[int | None] = mapped_column(Integer)
    plus_minus: Mapped[int | None] = mapped_column(Integer)
    # Provider headshots are stored as a count; the percentage is a separate metric.
    headshot_kills: Mapped[int | None] = mapped_column(Integer)
    headshot_percent: Mapped[float | None] = mapped_column(Numeric(6, 2))
    first_kills: Mapped[int | None] = mapped_column(Integer)
    first_deaths: Mapped[int | None] = mapped_column(Integer)
    adr: Mapped[float | None] = mapped_column(Numeric(7, 2))
    kast: Mapped[float | None] = mapped_column(Numeric(6, 2))
    rating: Mapped[float | None] = mapped_column(Numeric(5, 2))
    rating_version: Mapped[str | None] = mapped_column(String(40))
    # CT and T splits are optional and must not be inferred from aggregate values.
    ct_kills: Mapped[int | None] = mapped_column(Integer)
    ct_deaths: Mapped[int | None] = mapped_column(Integer)
    ct_adr: Mapped[float | None] = mapped_column(Numeric(7, 2))
    ct_kast: Mapped[float | None] = mapped_column(Numeric(6, 2))
    ct_rating: Mapped[float | None] = mapped_column(Numeric(5, 2))
    t_kills: Mapped[int | None] = mapped_column(Integer)
    t_deaths: Mapped[int | None] = mapped_column(Integer)
    t_adr: Mapped[float | None] = mapped_column(Numeric(7, 2))
    t_kast: Mapped[float | None] = mapped_column(Numeric(6, 2))
    t_rating: Mapped[float | None] = mapped_column(Numeric(5, 2))
    side_data_available: Mapped[bool | None] = mapped_column()
    data_quality: Mapped[str | None] = mapped_column(String(40))
    confidence: Mapped[str | None] = mapped_column(String(40))
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 4))
    # Preserve provider fields that are not represented by dedicated columns.
    source_payload: Mapped[dict | None] = mapped_column(JSONB)
    __table_args__ = (
        UniqueConstraint("map_id", "player_id", name="uq_player_map_stats"),
        Index("ix_player_map_stats_external_id", "external_id", unique=True, postgresql_where=text("external_id IS NOT NULL")),
    )


class RawApiRecord(Base):
    """A raw provider payload retained for reproducibility and later reprocessing."""
    __tablename__ = "raw_api_records"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(240), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(120))
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)


class ModelRun(Base):
    """Metadata and evaluation metrics for a trained prediction model version."""
    __tablename__ = "model_runs"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(60), nullable=False)
    training_cutoff: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metrics: Mapped[dict | None] = mapped_column(JSONB)


class Prediction(Base):
    """A model probability and fair-odds estimate for a specific betting market."""
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    model_run_id: Mapped[int] = mapped_column(ForeignKey("model_runs.id"), nullable=False)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False)
    map_id: Mapped[int | None] = mapped_column(ForeignKey("match_maps.id"))
    market_type: Mapped[str] = mapped_column(String(80), nullable=False)
    selection: Mapped[str] = mapped_column(String(100), nullable=False)
    probability: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    fair_odds: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    feature_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
