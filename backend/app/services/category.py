import logging
import math

from sqlalchemy.exc import IntegrityError

from app.api.deps.pagination import PaginationParams
from app.core.exceptions.category import DuplicateCategoryError
from app.models import Category, User
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryRead
from app.schemas.pagination import PaginatedResponse

logger = logging.getLogger(__name__)


class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    def get_all_categories(
        self, current_user: User, pagination: PaginationParams
    ) -> PaginatedResponse[CategoryRead]:
        logger.info(
            "Fetch all categories start",
            extra={
                "page": pagination.page,
                "size": pagination.size,
            },
        )

        total = self.category_repo.get_total_count(current_user.id)
        categories = self.category_repo.get_all_categories(
            current_user.id, pagination.offset, pagination.size
        )
        total_pages = math.ceil(total / pagination.size) if total > 0 else 1
        items = [CategoryRead.model_validate(cat) for cat in categories]

        logger.info(
            "Fetch all categories complete",
            extra={
                "total": total,
                "page": pagination.page,
                "size": pagination.size,
                "total_pages": total_pages,
            },
        )

        return PaginatedResponse[CategoryRead](
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=total_pages,
            items=items,
        )

    def create_category(self, current_user: User, category_create_data: CategoryCreate):
        logger.info("Create category start")

        try:
            new_category = self.category_repo.create_category(
                Category(**category_create_data.model_dump(), user_id=current_user.id)
            )

            self.category_repo.db.commit()
            logger.info(
                "Create category complete", extra={"category_id": new_category.id}
            )
            return new_category

        except IntegrityError as e:
            self.category_repo.db.rollback()
            logger.warning("Create category failed")

            raise DuplicateCategoryError() from e
