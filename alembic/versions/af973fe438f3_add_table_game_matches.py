"""Add table game_matches

Revision ID: af973fe438f3
Revises: 1b42828c3b04
Create Date: 2025-08-02 21:03:15.196015

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "af973fe438f3"
down_revision: Union[str, Sequence[str], None] = "1b42828c3b04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "game_matches",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("game_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("round", sa.Integer(), nullable=False),
        sa.Column("winner_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("score", sa.Integer(), default=0, nullable=True),
        sa.Column("details", sa.Text, nullable=True),
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
    op.drop_table("game_matches")
