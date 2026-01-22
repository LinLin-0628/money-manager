import logging
import math

from sqlalchemy.exc import IntegrityError

from app.api.deps.pagination import PaginationParams
from app.core.exceptions.category import CategoryNotFoundError, DuplicateCategoryError
from app.models import Category, User
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
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

    def create_category(
        self, current_user: User, category_create_data: CategoryCreate
    ) -> Category:
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

    def get_category_by_id(
        self, current_user: User, category_id: int
    ) -> Category | None:
        logger.info("Get category by id start", extra={"category_id": category_id})

        category = self.category_repo.get_category_by_id(current_user.id, category_id)

        logger.info(
            "Get category by id complete",
            extra={
                "category_id": category,
                "user_id": current_user.id,
                "found": category is not None,
            },
        )

        return category

    def update_category(
        self, current_user: User, category_id: int, category_update_data: CategoryUpdate
    ) -> Category:
        logger.info("Update category start", extra={"category_id": category_id})

        try:
            category = self.get_category_by_id(current_user, category_id)

            if not category:
                raise CategoryNotFoundError()

            for field, value in category_update_data.model_dump().items():
                setattr(category, field, value)

            self.category_repo.db.commit()
            self.category_repo.db.refresh(category)

            logger.info("Update category complete", extra={"category_id": category_id})

            return category
        except IntegrityError:
            self.category_repo.db.rollback()
            logger.exception("Update category field")
            raise

    def delete_category(self, current_user: User, category_id: int) -> None:
        logger.info("Delete category start", extra={"category_id": category_id})

        try:
            category = self.get_category_by_id(current_user, category_id)

            if not category:
                raise CategoryNotFoundError()

            self.category_repo.delete_category(category)
            self.category_repo.db.commit()

            logger.info("Delete category complete", extra={"category_id": category_id})

        except IntegrityError:
            self.category_repo.db.rollback()
            logger.exception("Delete category field")
            raise
