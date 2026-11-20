"""Store borrowed_at without a timezone."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7f2c8a9d1e40"
down_revision: Union[str, Sequence[str], None] = "345ae3dc8c8e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "books",
        "borrowed_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(timezone=False),
        existing_nullable=True,
        postgresql_using="borrowed_at AT TIME ZONE 'UTC'",
    )


def downgrade() -> None:
    op.alter_column(
        "books",
        "borrowed_at",
        existing_type=sa.DateTime(timezone=False),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="borrowed_at AT TIME ZONE 'UTC'",
    )