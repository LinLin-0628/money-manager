"""Create enum type 'transaction_type'

Revision ID: 9e04fe49d063
Revises: 9d652c3c857a
Create Date: 2026-01-22 17:45:10.076944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e04fe49d063'
down_revision: Union[str, Sequence[str], None] = '9d652c3c857a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add checkfirst=True inside the .create() method
    sa.Enum("INCOME", "EXPENSE", name="transaction_type").create(
        op.get_bind(), checkfirst=True
    )


def downgrade() -> None:
    # It's also safer to add checkfirst=True here
    sa.Enum("INCOME", "EXPENSE", name="transaction_type").drop(
        op.get_bind(), checkfirst=True
    )
