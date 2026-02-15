"""create transaction_type enum

Revision ID: 01a58dab941b
Revises: 27221c576d96
Create Date: 2026-01-25 00:53:28.286234

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01a58dab941b'
down_revision: Union[str, Sequence[str], None] = '27221c576d96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


transaction_type_enum = sa.Enum(
    "income",
    "expense",
    name="transaction_type"
)


def upgrade() -> None:
    transaction_type_enum.create(op.get_bind(),checkfirst=True)



def downgrade() -> None:
    transaction_type_enum.drop(op.get_bind(), checkfirst=True)
