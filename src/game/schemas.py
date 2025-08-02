from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PlayerStatus(BaseModel):
    player_id: str = Field(description="ID of the player")
    game_id: str = Field(description="ID of the game")
    status: str = Field(
        "active",
        description="Status of the player (allowed: 'active', 'disabled', 'deleted')",
    )

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_status

    @staticmethod
    def validate_status(value):
        allowed = {"active", "disabled", "deleted"}
        if value not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return value


class PlayerWinner(BaseModel):
    player_id: str = Field(description="ID of the player")
    game_id: str = Field(description="ID of the game")


class Player(BaseModel):
    name: str = Field(min_length=3, max_length=20, description="Name of the player")
    avatar: str = Field(description="Avatar string for the player")
    win: int = Field(0, ge=0, description="Number of games won by the player")
    loss: int = Field(0, ge=0, description="Number of games lost by the player")
    games_played: int = Field(
        0, ge=0, description="Total number of games played by the player"
    )
    status: str = Field(
        "active",
        description="Status of the player (allowed: 'active', 'inactive', 'deleted')",
    )

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_status

    @staticmethod
    def validate_status(value):
        allowed = {"active", "inactive", "deleted"}
        if value not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return value


class Game(BaseModel):
    name: str = Field(min_length=3, max_length=200, description="Name of the game")
    player_group: Optional[str] = Field(
        None, max_length=50, description="Group of players for the game"
    )
    end_condition: str = Field(
        "score",
        description="Condition to end the game (allowed: 'score', 'rounds', 'time')",
    )
    score_to_win: Optional[int] = Field(
        500, ge=0, description="Score required to win the game"
    )
    max_rounds: Optional[int] = Field(
        10, ge=1, description="Maximum number of rounds in the game"
    )
    time_limit: Optional[int] = Field(
        120, ge=0, description="Time limit in seconds for the game"
    )
    game_players: List[str] = Field(
        min_items=2,
        description="List of player IDs participating in the game",
    )

class AddPlayerToGame(BaseModel):
    game_players: List[str] = Field(
        min_items=1,
        description="List of player IDs to be added to the game",
    )
    game_id: str = Field(description="ID of the game")
