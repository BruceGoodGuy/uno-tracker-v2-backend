"""merge heads

Revision ID: 1d9d975ed397
Revises: a01f024de9cf, af973fe438f3
Create Date: 2025-08-03 15:26:07.902736

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d9d975ed397'
down_revision: Union[str, Sequence[str], None] = ('a01f024de9cf', 'af973fe438f3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
