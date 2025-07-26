# src/auth/dependencies.py
from fastapi import Depends, Cookie, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from src.core.database import SessionLocal
from src.auth.models import OAuthSession, User

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_token_cookie(session_token: str | None = Cookie(default=None)):
    print(f"Session token from cookie: {session_token}")
    # session_token = "n8khfyIjqmYVuBLRJOh4HxtzXogbIpdfBjX0RvuFFGs"
    if not session_token:
        raise HTTPException(status_code=401, detail="Missing session cookie")
    return session_token

def get_current_user(
    token: str = Depends(get_token_cookie),
    db: Session = Depends(get_db)
) -> User:
    sess = db.query(OAuthSession).filter_by(session_token=token).first()
    if not sess or sess.expires < datetime.now(sess.expires.tzinfo):
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    user = db.query(User).get(sess.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    print(f"Current user: {user.email}")
    return user
