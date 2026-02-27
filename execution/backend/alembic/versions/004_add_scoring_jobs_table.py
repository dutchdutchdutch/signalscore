"""Add scoring_jobs table for persistent job tracking

Revision ID: 004_scoring_jobs
Revises: 003_rename_categories
Create Date: 2026-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_scoring_jobs'
down_revision: Union[str, None] = '003_rename_categories'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'scoring_jobs',
        sa.Column('id', sa.String(12), primary_key=True),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='processing'),
        sa.Column('company_name', sa.String(255), nullable=True),
        sa.Column('error', sa.String(2000), nullable=True),
        sa.Column('is_new_company', sa.Boolean(), server_default=sa.text('true')),
        sa.Column('progress_phase', sa.String(50), nullable=True),
        sa.Column('progress_detail', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('scoring_jobs')
