import pytest
from passlib.exc import UnknownHashError

from app.core.security import hash_password, verify_password


def test_hash_password_not_plaintext():
    """
    Ensure that hashing a password:
    - does not return the plaintext password
    - returns a string
    - returns a non-empty value
    """
    password = "secret_password"
    hashed = hash_password(password)

    assert hashed != password
    assert isinstance(hashed, str)
    assert len(hashed) > 0


@pytest.mark.parametrize(
    "password",
    [
        pytest.param("secret_password", id="normal_password"),
        pytest.param("pässwörd🔥", id="unicode_password"),
        pytest.param("a", id="short_password"),
        pytest.param("", id="empty_password"),
    ],
)
def test_password_hash_and_verify(password):
    """
    Test that various types of passwords:
    - Can be hashed
    - Can be successfully verified against the hash
    Covers normal, Unicode, short, and empty passwords.
    """
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_failure():
    """
    Ensure that an incorrect password does not verify
    against a valid hash.
    """
    password = "super-secret"
    hashed = hash_password(password)

    assert verify_password("wrong-password", hashed) is False


def test_same_password_produces_different_hashes():
    """
    Ensure that hashing the same password twice
    produces different hashes (due to salting).
    """
    password = "super-secret"

    hash1 = hash_password(password)
    hash2 = hash_password(password)

    assert hash1 != hash2


def test_verify_with_invalid_hash():
    """
    Ensure that verifying a password against an invalid
    or malformed hash raises UnknownHashError.
    """
    password = "password123"
    invalid_hash = "invalid-hash"

    with pytest.raises(UnknownHashError):
        verify_password(password, invalid_hash)
