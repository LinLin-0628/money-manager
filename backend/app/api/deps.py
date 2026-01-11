from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.user import UserRepository
from app.services.user import UserService



def get_user_service(db: Session = Depends(get_db)) -> UserService:
    user_repo = UserRepository(db)
    return UserService(user_repo, request)
    return UserService(user_repo)


