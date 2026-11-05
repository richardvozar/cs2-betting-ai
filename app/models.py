from datetime import datetime
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str | None] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (Index("ix_teams_name", "name"),)

class Tournament(Base):
    __tablename__ = "tournaments"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    external_id: Mapped[str | None] = mapped_column(String(120), unique=True)
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    tier: Mapped[str | None] = mapped_column(String(40))

class Match(Base):
    __tablename__ = "matches"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    tournament_id: Mapped[int | None] = mapped_column(ForeignKey("tournaments.id"))
    team1_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    team2_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    winner_team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str | None] = mapped_column(String(40))
    best_of: Mapped[int | None] = mapped_column(Integer)
    team1_score: Mapped[int | None] = mapped_column(Integer)
    team2_score: Mapped[int | None] = mapped_column(Integer)
    source_payload: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class MatchMap(Base):
    __tablename__ = "match_maps"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(120))
    map_number: Mapped[int] = mapped_column(Integer, nullable=False)
    map_name: Mapped[str | None] = mapped_column(String(60))
    team1_score: Mapped[int | None] = mapped_column(Integer)
    team2_score: Mapped[int | None] = mapped_column(Integer)
    winner_team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    picker_team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    __table_args__ = (UniqueConstraint("match_id", "map_number", name="uq_match_map_number"),)

class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str | None] = mapped_column(String(60))

class PlayerMapStats(Base):
    __tablename__ = "player_map_stats"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    map_id: Mapped[int] = mapped_column(ForeignKey("match_maps.id", ondelete="CASCADE"), nullable=False)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    kills: Mapped[int | None] = mapped_column(Integer)
    deaths: Mapped[int | None] = mapped_column(Integer)
    assists: Mapped[int | None] = mapped_column(Integer)
    headshot_kills: Mapped[int | None] = mapped_column(Integer)
    adr: Mapped[float | None] = mapped_column(Numeric(7, 2))
    kast: Mapped[float | None] = mapped_column(Numeric(6, 2))
    rating: Mapped[float | None] = mapped_column(Numeric(5, 2))
    __table_args__ = (UniqueConstraint("map_id", "player_id", name="uq_player_map_stats"),)

class RawApiRecord(Base):
    __tablename__ = "raw_api_records"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(240), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(120))
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

class ModelRun(Base):
    __tablename__ = "model_runs"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(60), nullable=False)
    training_cutoff: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metrics: Mapped[dict | None] = mapped_column(JSONB)

class Prediction(Base):
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
