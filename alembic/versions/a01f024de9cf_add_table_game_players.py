"""Add table game_players

Revision ID: a01f024de9cf
Revises: 3c6739e0977c
Create Date: 2025-07-27 19:08:12.256365

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a01f024de9cf"
down_revision: Union[str, Sequence[str], None] = "3c6739e0977c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "game_players",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("game_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("player_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=20), default="active", nullable=False),
        sa.Column("total_win", sa.Integer(), default=0, nullable=True),
        sa.Column("score", sa.Integer(), default=0, nullable=True),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("game_players")
