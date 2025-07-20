from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from src.auth import service, schemas
from src.core.database import SessionLocal
from fastapi.responses import RedirectResponse
from datetime import datetime
from src.core.database import SessionLocal
from src.auth.models import OAuthSession
from src.dependencies import get_token_cookie, get_current_user
from src.core.config import settings
from src.auth.models import OAuthSession, User
from sqlalchemy.orm import Session


router = APIRouter(prefix="/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

BACKEND_URL = settings.BACKEND_URL

@router.get("/login")
def login():
    redirect = (
        "https://accounts.google.com/o/oauth2/auth?"
        f"response_type=code&client_id={service.settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={BACKEND_URL}/auth/callback&scope=openid email profile"
    )
    return RedirectResponse(url=redirect)


@router.get("/callback", response_model=schemas.UserOut)
def callback(code: str, response: Response, db: Session = Depends(get_db)):
    info = service.exchange_code(
        code, redirect_uri=f"{BACKEND_URL}/auth/callback"
    )
    user = service.get_or_create_user(db, info)
    token = service.create_session(db, user)
    redirect = RedirectResponse(
        url=settings.FRONTEND_URL_DEV + "/auth/callback-success", status_code=303
    )
    redirect.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=service.settings.COOKIE_SECURE,
        samesite="lax",
        max_age=30 * 24 * 3600,
        path="/",
    )

    return redirect


@router.post("/logout")
def logout(
    response: Response,
    token: str = Depends(get_token_cookie),
    db: Session = Depends(get_db),
):
    sess = db.query(OAuthSession).filter_by(session_token=token).first()
    if sess:
        db.delete(sess)
        db.commit()
    response.delete_cookie(
        key="session_token",
        path="/",
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return {"message": "Logged out"}


@router.get("/me", response_model=schemas.UserOut)
def me(
    user: User = Depends(get_current_user),
):
    return user


@router.get("/check")
def protected(user: User = Depends(get_current_user)):
    return {"status": "ok"}
