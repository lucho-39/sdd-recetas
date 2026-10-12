"""make notifications.recipe_id nullable

Revision ID: 9c0bd638c4c7
Revises: 21978cca6cdc
Create Date: 2026-10-12 13:28:18.664150

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c0bd638c4c7'
down_revision: Union[str, None] = '21978cca6cdc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Written by hand: autogenerate produced an empty pass for this one.
    # A notification about an ingredient rejection (UC-ADMIN-016 AC3) has no
    # recipe behind it, so the column cannot stay NOT NULL.
    op.alter_column(
        'notifications',
        'recipe_id',
        existing_type=sa.UUID(),
        nullable=True,
    )


def downgrade() -> None:
    # Fails if any row already has a null recipe_id, which is the intended
    # guard: there is no way to re-attach those notifications to a recipe.
    op.alter_column(
        'notifications',
        'recipe_id',
        existing_type=sa.UUID(),
        nullable=False,
    )
