import secrets, datetime, requests
from jose import jwt
from src.auth.models import User, OAuthSession
from src.core.config import settings
from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as grequests
from fastapi import HTTPException

def get_or_create_user(db: Session, userinfo: dict):
    user = db.query(User).filter_by(email=userinfo["email"]).first()
    if not user:
        user = User(email=userinfo["email"], name=userinfo.get("name"), picture=userinfo.get("picture"))
        db.add(user); db.commit(); db.refresh(user)
    return user

def create_session(db: Session, user: User):
    token = secrets.token_urlsafe(32)
    expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
    sess = OAuthSession(user_id=user.id, session_token=token, expires=expires)
    db.add(sess); db.commit()
    return token

def exchange_code(code: str, redirect_uri: str):
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    r = requests.post("https://oauth2.googleapis.com/token", data=data)
    resp = r.json()
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {resp}")
    
    token = resp.get("id_token")
    if not token:
        raise HTTPException(status_code=400, detail="Missing ID token")

    # Verify ID token (check signature, expiration, audience automatically)
    try:
        user_info = google_id_token.verify_oauth2_token(
            token,
            grequests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID token: {e}")

    # user_info is a dict with user data (email, name, etc)
    return user_info
