"""create category table

Revision ID: bda56c36739d
Revises: 01a58dab941b
Create Date: 2026-01-25 00:53:57.125482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'bda56c36739d'
down_revision: Union[str, Sequence[str], None] = '01a58dab941b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

transaction_type_enum = postgresql.ENUM(
    "income",
    "expense",
    name="transaction_type",
    create_type=False
)



def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('type', transaction_type_enum, nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),

    sa.UniqueConstraint('user_id', 'name', name='uq_category_user_id_name')
    )

    op.create_index(op.f('ix_categories_user_id'), 'categories', ['user_id'], unique=False)

    op.execute("""
               CREATE TRIGGER update_categories_updated_at
                   BEFORE UPDATE
                   ON categories
                   FOR EACH ROW
                   EXECUTE FUNCTION update_updated_at_column();
   """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS update_categories_updated_at ON categories")
    op.drop_index(op.f('ix_categories_user_id'), table_name='categories')
    op.drop_table('categories')
