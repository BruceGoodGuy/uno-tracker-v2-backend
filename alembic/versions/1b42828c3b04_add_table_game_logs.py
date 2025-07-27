"""Add table game_logs

Revision ID: 1b42828c3b04
Revises: 4c2dc8ba7002
Create Date: 2025-07-27 21:28:37.851951

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1b42828c3b04"
down_revision: Union[str, Sequence[str], None] = "4c2dc8ba7002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "game_logs",
        sa.Column(
            "id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            unique=True,
            index=True,
            default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("game_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("player_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(200), nullable=False),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("created_by", sa.UUID(as_uuid=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("game_logs")
