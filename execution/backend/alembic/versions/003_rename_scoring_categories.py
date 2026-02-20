"""Rename scoring categories to display labels

Revision ID: 003_rename_categories
Revises: 129ffb353b6b
Create Date: 2026-02-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_rename_categories'
down_revision: Union[str, None] = '129ffb353b6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename category values in the scores table
    op.execute("UPDATE scores SET category = 'LEADING' WHERE category = 'HIGH'")
    op.execute("UPDATE scores SET category = 'OPERATIONAL' WHERE category = 'MEDIUM_HIGH'")
    op.execute("UPDATE scores SET category = 'LAGGING' WHERE category = 'MEDIUM_LOW'")
    op.execute("UPDATE scores SET category = 'NO_SIGNAL' WHERE category = 'LOW'")


def downgrade() -> None:
    # Revert category names
    op.execute("UPDATE scores SET category = 'HIGH' WHERE category = 'LEADING'")
    op.execute("UPDATE scores SET category = 'MEDIUM_HIGH' WHERE category = 'OPERATIONAL'")
    op.execute("UPDATE scores SET category = 'MEDIUM_LOW' WHERE category = 'LAGGING'")
    # Note: NO_SIGNAL -> LOW is lossy (original NO_SIGNAL entries also become LOW)
    # This downgrade is best-effort
