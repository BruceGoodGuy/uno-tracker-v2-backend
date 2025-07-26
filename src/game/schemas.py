from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


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


# class Game(BaseModel):
#     id: str = Field(..., description="Unique identifier for the game")
#     name: str = Field(..., min_length=3, max_length=50, description="Name of the game")
#     players: List[Player] = Field(..., description="List of players in the game")
#     created_at: Optional[str] = Field(None, description="Timestamp when the game was created")
#     updated_at: Optional[str] = Field(None, description="Timestamp when the game was last updated")
#     state: str = Field(..., description="Current state of the game (e.g., 'waiting', 'in_progress', 'finished')")
#     scoring_rules: int = Field(..., description="Scoring rules for the game (e.g., 0 winner takes all points)")

# class GameEndCondition(BaseModel):
#     id: str = Field(..., description="Unique identifier for the game end condition")
#     game_id: str = Field(..., description="ID of the game this condition belongs to")
#     condition: int = Field(..., description="Condition to be met for the game to end (e.g., number of rounds) 0 means player reaches target score, 1 maximum rounds reached and 2 means time limit reached")
#     score: Optional[int] = Field(None, description="Target score to be reached for the game to end, if applicable")
#     rounds: Optional[int] = Field(None, description="Maximum number of rounds to be played before the game ends, if applicable")
#     time: Optional[int] = Field(None, description="Time limit in seconds for the game to end, if applicable")

# class GameDetails(BaseModel):
#     game: Game = Field(..., description="Details of the game")
#     current_player: Player = Field(..., description="The player whose turn it is currently")
#     deck: List[str] = Field(..., description="List of cards in the deck")
#     discard_pile: List[str] = Field(..., description="List of cards in the discard pile")
