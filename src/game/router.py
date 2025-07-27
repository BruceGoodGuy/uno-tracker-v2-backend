from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from src.auth import service, schemas
from src.core.database import SessionLocal
from fastapi.responses import RedirectResponse
from datetime import datetime
from src.core.database import SessionLocal
from src.dependencies import get_token_cookie, get_current_user
from src.core.config import settings
from src.auth.models import OAuthSession, User
from sqlalchemy.orm import Session
from src.game import schemas as player_schemas
from sqlalchemy import select, exists
from src.game import models as player_models
from src.game.models import Game, Player, GamePlayer
from fastapi import Query
from typing import Annotated
from fastapi import Form

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
    q: str = Query(default=None, max_length=100),
):
    user_group = "usergroup_" + str(user.id)
    query = db.query(player_models.Player).filter(
        player_models.Player.player_group == user_group
    )
    if q:
        query = query.filter(player_models.Player.name.ilike(f"%{q}%"))
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


@router.post("/create")
def create_game(
    data: player_schemas.Game,
    response: Response,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_group = "usergroup_" + str(user.id)

    existing_game = (
        db.query(player_models.Game)
        .filter(
            player_models.Game.player_group == user_group,
            player_models.Game.status == "ongoing",
        )
        .first()
    )
    if existing_game:
        raise HTTPException(
            status_code=422,
            detail=[{"msg": "There is already an ongoing game for this user"}],
        )

    # Validate that all player IDs in data.game_players exist in the players table
    if not hasattr(data, "game_players") or not isinstance(data.game_players, list):
        raise HTTPException(
            status_code=400, detail=[{"msg": "game_players must be a list"}]
        )

    valid_players = (
        db.query(player_models.Player.id)
        .filter(
            player_models.Player.id.in_(data.game_players),
            player_models.Player.player_group == user_group,
        )
        .all()
    )
    valid_player_ids = {p.id for p in valid_players}
    if not valid_player_ids:
        raise HTTPException(
            status_code=400, detail=[{"msg": "No valid players found for the game"}]
        )

    game_data = {
        "name": data.name,
        "end_condition": data.end_condition,
        "score_to_win": data.score_to_win,
        "max_rounds": data.max_rounds,
        "time_limit": data.time_limit,
        "player_group": user_group,
        "status": "ongoing",
        "start_time": datetime.utcnow(),
    }

    game = player_models.Game(**game_data)
    db.add(game)
    db.commit()
    db.refresh(game)

    # Create GamePlayer entries for each player
    for player_id in valid_player_ids:
        game_player = player_models.GamePlayer(
            game_id=game.id,
            player_id=player_id,
            status="active",
        )
        db.add(game_player)
    db.commit()

    return {"message": "Game created successfully", "game_id": game.id}


@router.get("/ongoing")
def get_ongoing_game(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    mode: str = Query(default=None, regex="^(play)$"),
):
    user_group = "usergroup_" + str(user.id)

    ongoing_game = (
        db.query(player_models.Game)
        .filter(
            player_models.Game.player_group == user_group,
            player_models.Game.status == "ongoing",
        )
        .first()
    )

    if not ongoing_game:
        raise HTTPException(status_code=404, detail=[{"msg": "No ongoing game found"}])

    players = []

    if mode == "play":
        players = (
            db.query(
                player_models.GamePlayer.id.label("gp_id"),
                player_models.GamePlayer.total_win,
                player_models.Player.name,
                player_models.Player.avatar,
                player_models.GamePlayer.score,
                player_models.GamePlayer.status,
            )
            .join(
                player_models.Player,
                player_models.GamePlayer.player_id == player_models.Player.id,
            )
            .filter(player_models.GamePlayer.game_id == ongoing_game.id)
            .all()
        )

        players_data = [
            {
                "gp_id": player.gp_id,
                "total_win": player.total_win,
                "name": player.name,
                "avatar": player.avatar,
                "score": player.score,
                "status": player.status,
            }
            for player in players
        ]

        # return RedirectResponse(
        #     f"{settings.FRONTEND_URL}/auth/game/play/{ongoing_game.id}"
        # )
        print("Redirecting to play mode")

    if ongoing_game:
        total_players = (
            db.query(player_models.GamePlayer)
            .join(
                player_models.Player,
                player_models.GamePlayer.player_id == player_models.Player.id,
            )
            .filter(player_models.GamePlayer.game_id == ongoing_game.id)
            .count()
        )

        ongoing_game_data = {
            "id": ongoing_game.id,
            "name": ongoing_game.name,
            "status": ongoing_game.status,
            "start_time": ongoing_game.start_time,
            "end_condition": ongoing_game.end_condition,
            "score_to_win": ongoing_game.score_to_win,
            "max_rounds": ongoing_game.max_rounds,
            "time_limit": ongoing_game.time_limit,
            "total_players": total_players,
            "players": players_data,
        }
    else:
        ongoing_game_data = None

    return {"data": ongoing_game_data}
