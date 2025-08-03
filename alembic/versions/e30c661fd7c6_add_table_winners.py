"""add table winners

Revision ID: e30c661fd7c6
Revises: 1d9d975ed397
Create Date: 2025-08-03 15:39:34.177245

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e30c661fd7c6"
down_revision: Union[str, Sequence[str], None] = "1d9d975ed397"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "winners",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("game_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("player_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
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
    op.drop_table("winners")
