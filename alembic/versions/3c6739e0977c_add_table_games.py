"""Add table games

Revision ID: 3c6739e0977c
Revises: d135b6fc19d8
Create Date: 2025-07-27 19:07:30.442459

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3c6739e0977c"
down_revision: Union[str, Sequence[str], None] = "d135b6fc19d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "games",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("player_group", sa.String(length=50), nullable=True),
        sa.Column("end_condition", sa.String(length=50), nullable=False),
        sa.Column("score_to_win", sa.Integer(), nullable=True),
        sa.Column("max_rounds", sa.Integer(), nullable=True),
        sa.Column("time_limit", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=True),
        sa.Column("end_time", sa.DateTime(), nullable=True),
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
    op.drop_table("games")
