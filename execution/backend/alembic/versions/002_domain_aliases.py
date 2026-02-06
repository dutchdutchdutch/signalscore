"""Add company_domain_aliases table

Revision ID: 002_domain_aliases
Revises: b259375a2daf
Create Date: 2026-02-05

Story 4-8: Cross-Domain Alias Support
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "002_domain_aliases"
down_revision: Union[str, None] = "604b561c99c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "company_domain_aliases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("alias_domain", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_company_domain_aliases_id"), "company_domain_aliases", ["id"], unique=False)
    op.create_index(op.f("ix_company_domain_aliases_alias_domain"), "company_domain_aliases", ["alias_domain"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_company_domain_aliases_alias_domain"), table_name="company_domain_aliases")
    op.drop_index(op.f("ix_company_domain_aliases_id"), table_name="company_domain_aliases")
    op.drop_table("company_domain_aliases")
