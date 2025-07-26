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
