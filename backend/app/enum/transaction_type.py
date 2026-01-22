from enum import Enum

import sqlalchemy as sa


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


transaction_type_enum = sa.Enum(
    TransactionType,
    name="transaction_type",
    create_type=False,
)
