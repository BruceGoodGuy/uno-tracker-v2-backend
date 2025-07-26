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
from src.game import schemas as player_schemas
from sqlalchemy import select, exists
from src.game import models as player_models
from fastapi import Query


router = APIRouter(prefix="/game", tags=["game"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/test")
def test(
    response: Response,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"message": "Game test endpoint", "user": user.email}


@router.get("/players")
def get_players(
    response: Response,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    user_group = "usergroup_" + str(user.id)
    query = db.query(player_models.Player).filter(
        player_models.Player.player_group == user_group
    )
    total = query.count()
    players = (
        query.order_by(player_models.Player.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {
        "players": players,
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.delete("/player/{player_id}")
def delete_player(
    player_id: str,
    response: Response,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_group = "usergroup_" + str(user.id)

    player = (
        db.query(player_models.Player)
        .filter(
            player_models.Player.id == player_id,
            player_models.Player.player_group == user_group,
        )
        .first()
    )

    if not player:
        raise HTTPException(status_code=404, detail=[{"msg": "Player not found"}])

    db.delete(player)
    db.commit()

    return {"message": "Player deleted successfully", "player": player.name}


@router.put("/player/{player_id}")
def update_player(
    player_id: str,
    player: player_schemas.Player,
    response: Response,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_group = "usergroup_" + str(user.id)

    existing_player = (
        db.query(player_models.Player)
        .filter(
            player_models.Player.id == player_id,
            player_models.Player.player_group == user_group,
        )
        .first()
    )

    if not existing_player:
        raise HTTPException(status_code=404, detail=[{"msg": "Player not found"}])

    stmt = select(
        exists().where(
            player_models.Player.name.ilike(player.name.lower()),
            player_models.Player.player_group == user_group,
            player_models.Player.id != existing_player.id,
        )
    )
    exists_result = db.scalar(stmt)

    if exists_result:
        raise HTTPException(
            status_code=422, detail=[{"msg": "Player with this name already exists"}]
        )

    for key, value in player.dict().items():
        setattr(existing_player, key, value)

    db.commit()
    db.refresh(existing_player)

    return {"message": "Player updated successfully", "player": existing_player.name}


@router.post("/player")
def create_player(
    player: player_schemas.Player,
    response: Response,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_group = "usergroup_" + str(user.id)

    stmt = select(
        exists().where(
            player_models.Player.name.ilike(player.name.lower()),
            player_models.Player.player_group == user_group,
        )
    )
    exists_result = db.scalar(stmt)

    if exists_result:
        raise HTTPException(
            status_code=422, detail=[{"msg": "Player with this name already exists"}]
        )

    player_data = player.dict()
    player_data["player_group"] = user_group
    db_player = player_models.Player(**player_data)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)

    return {"message": "Player created successfully", "player": db_player.name}
