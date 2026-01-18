import uuid

import factory
from faker import Faker

from app.models.user import User

fake = Faker()


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = (
            "flush"  # keeps in session, does not auto-commit
        )

    # UUID primary key
    id = factory.LazyFunction(uuid.uuid4)

    # Fake realistic data
    email = factory.LazyAttribute(lambda _: fake.unique.email())
    name = factory.LazyAttribute(lambda _: fake.name())
    hashed_password = factory.LazyAttribute(lambda _: fake.password(length=12))

    # created_at and updated_at are handled by the database defaults
