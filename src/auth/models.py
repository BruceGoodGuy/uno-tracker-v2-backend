from sqlalchemy import Column, Integer, String, DateTime, Text
from src.core.database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    picture = Column(String)

class OAuthSession(Base):
    __tablename__ = "oauth_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    session_token = Column(String, unique=True, index=True)
    expires = Column(DateTime, default=lambda: datetime.datetime.utcnow())
