from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.account import AccountRepository
from app.repositories.auth import AuthRepository
from app.repositories.category import CategoryRepository
from app.repositories.transaction import TransactionRepository
from app.repositories.user import UserRepository
from app.services.account import AccountService
from app.services.auth import AuthService
from app.services.category import CategoryService
from app.services.transaction import TransactionService
from app.services.user import UserService


def get_user_service(db: Annotated[Session, Depends(get_db)]) -> UserService:
    user_repo = UserRepository(db)
    return UserService(user_repo)


def get_auth_service(db: Annotated[Session, Depends(get_db)]) -> AuthService:
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)

    auth_repo = AuthRepository(db)
    return AuthService(
        auth_repo,
        user_service,
    )


def get_account_service(db: Annotated[Session, Depends(get_db)]) -> AccountService:
    account_repo = AccountRepository(db)
    return AccountService(account_repo)


def get_category_service(db: Annotated[Session, Depends(get_db)]) -> CategoryService:
    category_repo = CategoryRepository(db)
    return CategoryService(category_repo)


def get_transaction_service(
    db: Annotated[Session, Depends(get_db)],
) -> TransactionService:
    transaction_repo = TransactionRepository(db)
    account_repo = AccountRepository(db)
    category_repo = CategoryRepository(db)

    account_service = AccountService(account_repo)
    category_service = CategoryService(category_repo)

    return TransactionService(transaction_repo, account_service, category_service)
