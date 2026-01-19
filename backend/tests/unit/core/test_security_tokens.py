import pytest

from app.core.security import hash_token, verify_token

TEST_SECRET = "test-secret"


@pytest.mark.parametrize(
    "token",
    [
        pytest.param("token123", id="normal_token"),
        pytest.param("", id="empty_token"),
        pytest.param("a", id="short_token"),
        pytest.param("pässwörd🔥", id="unicode_token"),
        pytest.param("x" * 10000, id="long_token"),
    ],
)
def test_hash_and_verify_token(token, mocker):
    """
    Test that hash_token and verify_token work correctly:
    - hash_token returns a hex string
    - verify_token returns True for correct token
    - verify_token returns False for wrong token
    """
    # Mock the secret
    mocker.patch(
        "app.core.security.settings.refresh_token_hmac_secret.get_secret_value",
        return_value=TEST_SECRET,
    )

    hashed = hash_token(token)

    # Hash is hex string
    assert isinstance(hashed, str)
    assert all(c in "0123456789abcdef" for c in hashed.lower())
    assert len(hashed) == 64  # SHA-256 HMAC hex length

    # Correct token verifies
    assert verify_token(token, hashed) is True

    # Wrong token fails
    assert verify_token(token + "wrong", hashed) is False


def test_hash_differs_with_different_secrets(mocker):
    """
    Ensure that changing the secret changes the hash.
    """
    token = "token123"

    mocker.patch(
        "app.core.security.settings.refresh_token_hmac_secret.get_secret_value",
        return_value="secretA",
    )
    hash1 = hash_token(token)

    mocker.patch(
        "app.core.security.settings.refresh_token_hmac_secret.get_secret_value",
        return_value="secretB",
    )
    hash2 = hash_token(token)

    assert hash1 != hash2
    # hash1 is no longer valid with secretB
    assert verify_token(token, hash1) is False
