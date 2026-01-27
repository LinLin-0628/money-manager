import pytest
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from app.core.security import hash_password, verify_password


@pytest.fixture(autouse=True)
def speed_up_password_hashing(mocker, monkeypatch):
    """
    Automatically simplifies Argon2 parameters for all tests.
    """
    fast_context = CryptContext(
        schemes=["argon2"],
        argon2__time_cost=1,  # Minimum time
        argon2__memory_cost=8,  # Minimum memory (8 KB)
        argon2__parallelism=1,  # Minimum CPU
    )

    # Patch the context inside the security module
    mocker.patch("app.core.security.pwd_context", fast_context)


def test_password_correctness_and_uniqueness():
    password = "supersecret123"

    # Hash the password
    hashed1 = hash_password(password)
    hashed2 = hash_password(password)

    # Test hash format
    assert hashed1 != password
    assert isinstance(hashed1, str)
    assert len(hashed1) > 0
    assert hashed1.startswith("$argon2id$")

    # Correct password matches
    assert verify_password(password, hashed1)
    assert verify_password(password, hashed2)

    # Hashes are unique because of salt
    assert hashed1 != hashed2

    # Incorrect password does not match
    assert not verify_password("wrongpassword", hashed1)


# ----------------------------
# 2. Edge Case Handling
# ----------------------------


@pytest.mark.parametrize(
    "password",
    [
        pytest.param("", id="empty_string"),
        pytest.param(" ", id="blank_space"),
        pytest.param("a", id="short_string"),
        pytest.param("a" * 4096, id="very_long_password"),
        pytest.param("p@$$w0rd🔥🚀", id="special_unicode"),
    ],
)
def test_password_edge_cases(password):
    hashed = hash_password(password)

    # Edge cases input should still be able to generate valid hash and verify correctly
    assert verify_password(password, hashed)


def test_password_none_input():
    # Passing None should raise TypeError
    with pytest.raises(TypeError):
        hash_password(None)

    with pytest.raises(TypeError):
        verify_password(None, hash_password("test"))


# ----------------------------
# 3. Security & Robustness
# ----------------------------


def test_password_hash_format_and_compatibility():
    password = "securepass"
    hashed = hash_password(password)

    # Re-verify multiple times to ensure compatibility
    for _ in range(5):
        assert verify_password(password, hashed)

    # Similar password should fail
    assert not verify_password(password + "1", hashed)


# ----------------------------
# 4. Negative / Failure Cases
# ----------------------------


@pytest.mark.parametrize(
    "hash_input, expected_exception",
    [
        pytest.param("not_a_hash", UnknownHashError, id="invalid_hash"),
        pytest.param("$argon2id$wrong$format", ValueError, id="wrong_format"),
    ],
)
def test_password_invalid_hash_input(hash_input, expected_exception):
    # Any invalid hash should fail verification
    with pytest.raises(expected_exception):
        verify_password("password", hash_input)


def test_password_corrupted_hash():
    password = "mypassword"
    hashed = hash_password(password)
    corrupted = hashed[:-5]  # remove last 5 chars

    with pytest.raises(ValueError):
        verify_password(password, corrupted)
