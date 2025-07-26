"""create players table

Revision ID: d135b6fc19d8
Revises: cf240b8501cd
Create Date: 2025-07-26 19:26:21.920164

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d135b6fc19d8"
down_revision: Union[str, Sequence[str], None] = "cf240b8501cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "players",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("player_group", sa.String(length=50), nullable=False),
        sa.Column("avatar", sa.Text(), nullable=False),  # Changed to sa.Text() for large strings
        sa.Column("win", sa.Integer(), nullable=False, default=0),
        sa.Column("loss", sa.Integer(), nullable=False, default=0),
        sa.Column("games_played", sa.Integer(), nullable=False, default=0),
        sa.Column("status", sa.String(length=20), nullable=False, default="active"),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
            onupdate=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("players")
