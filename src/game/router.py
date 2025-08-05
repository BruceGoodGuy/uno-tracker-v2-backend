from itertools import count
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from src.auth import service, schemas
from src.core.database import SessionLocal
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone
from src.core.database import SessionLocal
from src.dependencies import get_token_cookie, get_current_user
from src.core.config import settings
from src.auth.models import OAuthSession, User
from sqlalchemy.orm import Session
from src.game import schemas as player_schemas
from sqlalchemy import select, exists
from src.game import models as player_models
from src.game.models import Game, Player, GamePlayer, GameMatch
from fastapi import Query
from typing import Annotated
from fastapi import Form
from sqlalchemy.dialects import postgresql
from sqlalchemy import func
import json

router = APIRouter(prefix="/game", tags=["game"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
            player_models.Player.status == "active",
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
        "start_time": datetime.now(timezone.utc),
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

    match_data = 0

    if mode == "play":
        matches = (
            db.query(
                player_models.GameMatch.round,
            )
            .filter(player_models.GameMatch.game_id == ongoing_game.id)
            .count()
        )

        match_data = matches

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
            "match_data": match_data + 1,
        }
    else:
        ongoing_game_data = None

    return {"data": ongoing_game_data}


@router.get("/players/{game_id}")
def get_players_by_game(
    game_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user_group = "usergroup_" + str(user.id)

    players = (
        db.query(
            player_models.GamePlayer.player_id,
            player_models.GamePlayer.total_win,
            player_models.Player.name,
            player_models.Player.avatar,
            player_models.GamePlayer.score,
            player_models.GamePlayer.status,
        )
        .join(
            player_models.GamePlayer,
            player_models.Player.id == player_models.GamePlayer.player_id,
        )
        .join(
            player_models.Game,
            player_models.Game.id == player_models.GamePlayer.game_id,
        )
        .filter(
            player_models.GamePlayer.game_id == game_id,
            player_models.Game.player_group == user_group,
        )
        .all()
    )

    if not players:
        raise HTTPException(
            status_code=404, detail=[{"msg": "No players found for this game"}]
        )

    players_data = [
        {
            "id": player.player_id,
            "total_win": player.total_win,
            "name": player.name,
            "avatar": player.avatar,
            "score": player.score,
            "status": player.status,
        }
        for player in players
    ]

    return {"players": players_data}


@router.put("/play/player/status")
def disable_player(
    data: player_schemas.PlayerStatus,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user_group = "usergroup_" + str(user.id)
    game_player = (
        db.query(player_models.GamePlayer)
        .join(
            player_models.Game,
            player_models.Game.id == player_models.GamePlayer.game_id,
        )
        .filter(
            player_models.Game.id == data.game_id,
            player_models.GamePlayer.player_id == data.player_id,
            player_models.Game.status == "ongoing",
            player_models.Game.player_group == user_group,
        )
        .first()
    )

    # print(game_player.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))

    if not game_player:
        raise HTTPException(
            status_code=404, detail=[{"msg": "Player not found in ongoing game"}]
        )

    game_player.status = data.status
    db.commit()

    return {"message": "Player status updated successfully"}


@router.put("/play/winner")
def add_winner(
    data: player_schemas.PlayerWinner,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_group = "usergroup_" + str(user.id)
    winner = (
        db.query(
            player_models.Player,
            player_models.GamePlayer.total_win,
            player_models.GamePlayer.score,
        )
        .join(
            player_models.GamePlayer,
            player_models.Player.id == player_models.GamePlayer.player_id,
        )
        .join(
            player_models.Game,
            player_models.Game.id == player_models.GamePlayer.game_id,
        )
        .filter(
            player_models.Game.id == data.game_id,
            player_models.Player.id == data.player_id,
            player_models.Game.player_group == user_group,
        )
        .first()
    )

    if not winner:
        raise HTTPException(
            status_code=404, detail=[{"msg": "No winner found for this game"}]
        )

    add_score = (
        db.query(player_models.GamePlayer)
        .filter(
            player_models.GamePlayer.game_id == data.game_id,
            player_models.GamePlayer.player_id != winner.Player.id,
            player_models.GamePlayer.status == "active",
        )
        .count()
    )

    if add_score == 0:
        raise HTTPException(
            status_code=404, detail=[{"msg": "No active players found for this game"}]
        )

    score = winner.score + add_score

    # Update the winner's score and total_win
    db.query(player_models.GamePlayer).filter(
        player_models.GamePlayer.game_id == data.game_id,
        player_models.GamePlayer.player_id == winner.Player.id,
    ).update(
        {
            player_models.GamePlayer.score: score,
            player_models.GamePlayer.total_win: winner.total_win + 1,
        }
    )

    # Minus the score from other players
    db.query(player_models.GamePlayer).filter(
        player_models.GamePlayer.game_id == data.game_id,
        player_models.GamePlayer.player_id != winner.Player.id,
        player_models.GamePlayer.status == "active",
    ).update(
        {
            player_models.GamePlayer.score: player_models.GamePlayer.score - 1,
        },
        synchronize_session=False,
    )

    db.commit()

    game_match_count = (
        db.query(GameMatch)
        .filter(
            GameMatch.game_id == data.game_id,
        )
        .count()
    )

    # create detail data
    game_players = (
        db.query(
            player_models.GamePlayer.player_id,
            player_models.GamePlayer.status,
            player_models.GamePlayer.score,
            player_models.Player.name,
        )
        .join(
            player_models.Player,
            player_models.GamePlayer.player_id == player_models.Player.id,
        )
        .filter(player_models.GamePlayer.game_id == data.game_id)
        .all()
    )

    previous_match = (
        db.query(GameMatch.created_at)
        .filter(GameMatch.game_id == data.game_id)
        .order_by(GameMatch.round.desc())
        .first()
    )
    if not previous_match:
        previous_match_time = (
            db.query(Game.created_at).filter(Game.id == data.game_id).first()
        )
        previous_match_time = (
            previous_match_time.created_at.replace(tzinfo=timezone.utc) if previous_match_time else datetime.now(timezone.utc)
        )
    else:
        if previous_match.created_at.tzinfo is None:
            created_at_utc = previous_match.created_at.replace(tzinfo=timezone.utc)
        else:
            created_at_utc = previous_match.created_at

        previous_match_time = created_at_utc

    end_time = datetime.now(timezone.utc)
    game_details = []
    for player in game_players:
        game_details.append(
            {
                "name": player.name,
                "start_time": (
                    previous_match_time.isoformat() if previous_match_time else None
                ),
                "end_time": end_time.isoformat() if end_time else None,
                "status": player.status,
                "score": player.score,
                "is_winner": player.player_id == winner.Player.id,
                "score_added": (
                    add_score
                    if player.player_id == winner.Player.id
                    else (-1 if player.status == "active" else 0)
                ),
            }
        )

    # Create a new GameMatch entry
    game_match = GameMatch(
        game_id=data.game_id,
        round=game_match_count + 1,  # Assuming this is the first round for the match
        winner_id=winner.Player.id,
        score=add_score,
        details=json.dumps(game_details),
        created_at=end_time,
    )
    db.add(game_match)
    db.commit()

    winner_data = {
        "player_id": winner.Player.id,
        "name": winner.Player.name,
        "avatar": winner.Player.avatar,
        "total_win": winner.total_win + 1,
        "score": score,
    }

    return {"winner": winner_data}


@router.get("/play/player/available/{game_id}")
def get_available_players(
    game_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    user_group = "usergroup_" + str(user.id)
    print(user_group)
    players = (
        db.query(
            player_models.Player, player_models.GamePlayer.id.label("game_player_id")
        )
        .outerjoin(
            player_models.GamePlayer,
            player_models.GamePlayer.player_id == player_models.Player.id,
        )
        .filter(
            ~player_models.Player.id.in_(
                db.query(player_models.GamePlayer.player_id).filter(
                    player_models.GamePlayer.game_id == game_id
                )
            ),
            player_models.Player.status == "active",
            player_models.Player.player_group == user_group,
        )
        .distinct(player_models.Player.id)
        .all()
    )

    available_players = [
        {
            "id": player.Player.id,
            "name": player.Player.name,
            "avatar": player.Player.avatar,
            "game_player_id": player.game_player_id,
        }
        for player in players
    ]

    return {"available_players": available_players}


@router.post("/play/player/add")
def add_player_to_game(
    data: player_schemas.AddPlayerToGame,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user_group = "usergroup_" + str(user.id)

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
            player_models.Player.status == "active",
        )
        .all()
    )
    valid_player_ids = {p.id for p in valid_players}

    # Check if player is already in the game_players table for this game
    existing_players = (
        db.query(player_models.GamePlayer.player_id)
        .filter(
            player_models.GamePlayer.game_id == data.game_id,
            player_models.GamePlayer.player_id.in_(valid_player_ids),
        )
        .all()
    )
    existing_player_ids = {p.player_id for p in existing_players}

    new_players = valid_player_ids - existing_player_ids
    print(f"New players to add: {new_players}")

    if not new_players:
        raise HTTPException(
            status_code=400,
            detail=[{"msg": "No new players to add to the game"}],
        )

    for player_id in new_players:
        new_game_player = player_models.GamePlayer(
            game_id=data.game_id,
            player_id=player_id,
            status="active",
        )
        db.add(new_game_player)

    db.commit()

    return {
        "message": "Players added to the game successfully",
    }


@router.post("/ongoing/end")
def end_ongoing_game(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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

    # We can have many winners, so we will get the top players based on their scores.
    winners = (
        db.query(player_models.GamePlayer.player_id, player_models.GamePlayer.score)
        .filter(
            player_models.GamePlayer.game_id == ongoing_game.id,
        )
        .order_by(player_models.GamePlayer.score.desc())
        .all()
    )

    if not winners:
        raise HTTPException(
            status_code=404, detail=[{"msg": "No players found in the game"}]
        )

    winner_score = winners[0].score
    for winner in winners:
        if winner.score < winner_score:
            continue
        new_winner = player_models.Winner(
            game_id=ongoing_game.id,
            player_id=winner.player_id,
            score=winner_score,
        )
        db.add(new_winner)
        db.commit()

    ongoing_game.status = "completed"
    ongoing_game.end_time = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Game ended successfully", "game_id": ongoing_game.id}


@router.get("/history/{game_id}")
def get_game_history(
    game_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user_group = "usergroup_" + str(user.id)

    game = (
        db.query(player_models.Game)
        .filter(
            player_models.Game.id == game_id,
            player_models.Game.player_group == user_group,
        )
        .first()
    )

    if not game:
        raise HTTPException(status_code=404, detail=[{"msg": "Game not found"}])

    matches = (
        db.query(
            player_models.GameMatch,
            player_models.Player.name,
            player_models.GameMatch.round,
            player_models.GameMatch.winner_id,
            player_models.GameMatch.score,
            player_models.GameMatch.details,
            player_models.GameMatch.created_at,
        )
        .filter(player_models.GameMatch.game_id == game_id)
        .join(
            player_models.Player,
            player_models.GameMatch.winner_id == player_models.Player.id,
        )
        .order_by(player_models.GameMatch.round.asc())
        .all()
    )

    players = (
        db.query(player_models.GamePlayer, player_models.Player.name)
        .join(
            player_models.Player,
            player_models.GamePlayer.player_id == player_models.Player.id,
        )
        .filter(
            player_models.GamePlayer.game_id == game_id,
            player_models.Player.player_group == user_group,
        )
        .all()
    )

    winners = (
        db.query(player_models.Winner, player_models.Player.name)
        .join(
            player_models.Player,
            player_models.Winner.player_id == player_models.Player.id,
        )
        .filter(
            player_models.Winner.game_id == game_id,
            player_models.Player.player_group == user_group,
        )
        .all()
    )

    return {
        "game": {
            "id": game.id,
            "name": game.name,
            "status": game.status,
            "start_time": game.start_time.isoformat() if game.start_time else None,
            "end_time": game.end_time.isoformat() if game.end_time else None,
            "end_condition": game.end_condition,
            "score_to_win": game.score_to_win,
            "max_rounds": game.max_rounds,
            "time_limit": game.time_limit,
        },
        "matches": [
            {
                "round": match.round,
                "player_name": match.name,
                "winner_id": match.winner_id,
                "score": match.score,
                "details": json.loads(match.details),
                "created_at": match.created_at.isoformat(),
            }
            for match in matches
        ],
        "players": [
            {
                "player_id": player.GamePlayer.player_id,
                "name": player.name,
            }
            for player in players
        ],
        "winners": [
            {
                "player_id": winner.Winner.player_id,
                "name": winner.name,
            }
            for winner in winners
        ],
    }


@router.get("/recent")
def get_all_game_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user_group = "usergroup_" + str(user.id)

    games = (
        db.query(
            player_models.Game,
            func.count(player_models.GamePlayer.id).label("player_count"),
        )
        .filter(player_models.Game.player_group == user_group)
        .join(
            player_models.GamePlayer,
            player_models.Game.id == player_models.GamePlayer.game_id,
        )
        .group_by(player_models.Game.id)
        .order_by(player_models.Game.start_time.desc())
        .all()
    )

    print(games)

    if not games:
        raise HTTPException(status_code=404, detail=[{"msg": "No game history found"}])

    return {
        "games": [
            {
                "id": game.id,
                "name": game.name,
                "status": game.status,
                "start_time": game.start_time.isoformat() if game.start_time else None,
                "end_condition": game.end_condition,
                "score_to_win": game.score_to_win,
                "max_rounds": game.max_rounds,
                "time_limit": game.time_limit,
                "player_count": player_count,
                "end_time": game.end_time.isoformat() if game.end_time else None,
                "winner": [
                    {
                        "player_id": winner.player_id,
                        "player_name": winner.name,
                    }
                    for winner in db.query(
                        player_models.Winner,
                        player_models.Player.name,
                        player_models.Winner.player_id,
                    )
                    .filter(player_models.Winner.game_id == game.id)
                    .join(
                        player_models.Player,
                        player_models.Winner.player_id == player_models.Player.id,
                    )
                    .all()
                ],
            }
            for game, player_count in games
        ]
    }
