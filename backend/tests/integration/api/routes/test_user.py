import pytest
from fastapi import status
from sqlalchemy import select

from app.models import User
from tests.factories.user import UserFactory

pytestmark = pytest.mark.integration


def test_register_user_success(client, db_session):
    payload = {"email": "test@example.com", "password": "pass1234", "name": "Alice"}

    response = client.post("/api/users/register", json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED

    assert data["email"] == payload["email"]
    assert data["name"] == payload["name"]
    assert data["id"] is not None

    stmt = select(User)
    users = db_session.execute(stmt).scalars().all()
    assert len(users) == 1


def test_register_user_return_409_when_email_duplicate(client, db_session):
    email = "existing@email.com"

    UserFactory.create(email=email)
    db_session.commit()

    payload = {"email": email, "password": "pass1234", "name": "Alice"}

    response = client.post("/api/users/register", json=payload)

    assert response.status_code == status.HTTP_409_CONFLICT

    stmt = select(User).where(User.email == email)
    users = db_session.execute(stmt).scalars().all()
    assert len(users) == 1
