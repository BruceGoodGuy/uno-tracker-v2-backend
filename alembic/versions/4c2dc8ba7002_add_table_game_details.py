"""Add table game_details

Revision ID: 4c2dc8ba7002
Revises: a01f024de9cf
Create Date: 2025-07-27 21:26:33.582687

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4c2dc8ba7002"
down_revision: Union[str, Sequence[str], None] = "a01f024de9cf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "game_details",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, unique=True, index=True, nullable=False),
        sa.Column("game_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("winner_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("total_score", sa.Integer(), nullable=False, default=0),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("round_number", sa.Integer(), nullable=False, default=1),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"), onupdate=sa.text("CURRENT_TIMESTAMP")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("game_details")
