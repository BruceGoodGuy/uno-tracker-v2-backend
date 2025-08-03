from sqlalchemy import Column, Integer, String, DateTime, Text
from src.core.database import Base
import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Player(Base):
    __tablename__ = "players"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    name = Column(String(200), nullable=False)
    player_group = Column(String(50), nullable=True)
    avatar = Column(String)
    win = Column(Integer, default=0, nullable=False)
    loss = Column(Integer, default=0, nullable=False)
    games_played = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )


class Game(Base):
    __tablename__ = "games"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    name = Column(String(200), nullable=False)
    player_group = Column(String(50), nullable=True)
    end_condition = Column(String(50), nullable=False)
    score_to_win = Column(Integer, default=500, nullable=True)
    max_rounds = Column(Integer, default=10, nullable=True)
    time_limit = Column(Integer, default=120, nullable=True)  # in seconds
    status = Column(
        String(20), default="active", nullable=False
    )  # ongoing, completed, cancelled
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )


class GamePlayer(Base):
    __tablename__ = "game_players"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    game_id = Column(UUID(as_uuid=True), nullable=False)
    player_id = Column(UUID(as_uuid=True), nullable=False)
    total_win = Column(Integer, default=0, nullable=False)
    score = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default="active", nullable=False)  # active, inactive
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )


class GameDetail(Base):
    __tablename__ = "game_details"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    game_id = Column(UUID(as_uuid=True), nullable=False)
    winner_id = Column(UUID(as_uuid=True), nullable=True)
    total_score = Column(Integer, default=0, nullable=False)
    details = Column(Text, nullable=True)  # JSON string or text for game details
    round_number = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )


class GameLog(Base):
    __tablename__ = "game_logs"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    game_id = Column(UUID(as_uuid=True), nullable=False)
    player_id = Column(UUID(as_uuid=True), nullable=True)
    action = Column(String(200), nullable=False)  # e.g., "draw_card", "play_card"
    details = Column(Text, nullable=True)  # Additional details about the action
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    created_by = Column(
        UUID(as_uuid=True), nullable=True
    )  # User who performed the action


class GameMatch(Base):
    __tablename__ = "game_matches"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    game_id = Column(UUID(as_uuid=True), nullable=False)
    round = Column(Integer, nullable=False)
    winner_id = Column(UUID(as_uuid=True), nullable=True)
    score = Column(Integer, default=0, nullable=True)
    details = Column(Text, nullable=True)  # JSON string or text for match details
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )


class Winner(Base):
    __tablename__ = "winners"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    game_id = Column(UUID(as_uuid=True), nullable=False)
    player_id = Column(UUID(as_uuid=True), nullable=False)
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )
