"""create capabilities tables

Revision ID: 0001
Revises:
Create Date: 2026-06-03 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "capabilities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("practice_area", sa.String(), nullable=False),
        sa.Column("skill_levels", sa.JSON(), nullable=False),
        sa.Column("certifications", sa.JSON(), nullable=False),
        sa.Column("industry_verticals", sa.JSON(), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_capabilities_id"), "capabilities", ["id"], unique=False)
    op.create_index(op.f("ix_capabilities_name"), "capabilities", ["name"], unique=True)

    op.create_table(
        "capability_consultants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("capability_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["capability_id"], ["capabilities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("capability_id", "email", name="uq_capability_consultant"),
    )
    op.create_index(
        op.f("ix_capability_consultants_capability_id"),
        "capability_consultants",
        ["capability_id"],
        unique=False,
    )
    op.create_index(op.f("ix_capability_consultants_id"), "capability_consultants", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_capability_consultants_id"), table_name="capability_consultants")
    op.drop_index(op.f("ix_capability_consultants_capability_id"), table_name="capability_consultants")
    op.drop_table("capability_consultants")
    op.drop_index(op.f("ix_capabilities_name"), table_name="capabilities")
    op.drop_index(op.f("ix_capabilities_id"), table_name="capabilities")
    op.drop_table("capabilities")