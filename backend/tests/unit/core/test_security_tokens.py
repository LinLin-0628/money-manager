import pytest

from app.core.security import hash_token, verify_token

TEST_SECRET = "test-secret"


@pytest.fixture(autouse=True)
def mock_hmac_secret(mocker):
    mocker.patch(
        "app.core.security.settings.refresh_token_hmac_secret.get_secret_value",
        return_value=TEST_SECRET,
    )


# ----------------------------
# 1. Functional Verification
# ----------------------------


def test_token_basic_functionality():
    token = "my_refresh_token"
    another_token = "other_token"

    # Hash the token
    hashed1 = hash_token(token)
    hashed2 = hash_token(token)

    # Hash consistency with same secret
    assert hashed1 == hashed2

    # Correct token verification
    assert verify_token(token, hashed1)
    assert verify_token(token, hashed2)

    # Incorrect token verification
    assert not verify_token(another_token, hashed1)


# ----------------------------
# 2. Edge Case Handling
# ----------------------------


@pytest.mark.parametrize(
    "token",
    [
        pytest.param("", id="empty_string"),
        pytest.param("a" * 10000, id="very_long_token"),
        pytest.param("tok🔥en123", id="special_unicode"),
    ],
)
def test_token_edge_cases(token):
    hashed = hash_token(token)
    assert verify_token(token, hashed)

    # Slightly different token should fail
    assert not verify_token(token + "x", hashed)


def test_token_none_input():
    # Passing None as token should raise TypeError
    with pytest.raises(AttributeError):
        hash_token(None)

    with pytest.raises(AttributeError):
        verify_token(None, "fakehash")

    with pytest.raises(TypeError):
        verify_token("token", None)


# ----------------------------
# 3. Security & Robustness
# ----------------------------


def test_token_secret_change_effect(mocker):
    token = "securetoken"

    # Hash with first secret
    mocker.patch(
        "app.core.security.settings.refresh_token_hmac_secret.get_secret_value",
        return_value="secret1",
    )
    hashed1 = hash_token(token)
    assert verify_token(token, hashed1)

    # Hash with second secret
    mocker.patch(
        "app.core.security.settings.refresh_token_hmac_secret.get_secret_value",
        return_value="secret2",
    )
    hashed2 = hash_token(token)
    assert verify_token(token, hashed2)

    # Old hash should fail with new secret
    assert not verify_token(token, hashed1)


def test_token_hash_format():
    token = "format_test_token"
    hashed = hash_token(token)
    # SHA256 HMAC produces 32 bytes = 64 hex characters
    assert isinstance(hashed, str)
    assert len(hashed) == 64
    # Ensure all characters are valid hex
    int(hashed, 16)


# ----------------------------
# 4. Negative / Failure Cases
# ----------------------------


def test_token_corrupted_hash():
    token = "token123"
    hashed = hash_token(token)
    corrupted = hashed[:-5]  # remove last 5 chars

    assert not verify_token(token, corrupted)


def test_token_mismatched_token_hash():
    token1 = "token_one"
    token2 = "token_two"

    hashed1 = hash_token(token1)
    hashed2 = hash_token(token2)

    # Tokens should only match their own hash
    assert verify_token(token1, hashed1)
    assert verify_token(token2, hashed2)
    assert not verify_token(token1, hashed2)
    assert not verify_token(token2, hashed1)


@pytest.mark.parametrize(
    "invalid_hash",
    [
        pytest.param("", id="empty_string"),
        pytest.param("not_a_hex_string_123", id="not_hex"),
        pytest.param("12345", id="too_short"),
    ],
)
def test_token_invalid_hash_input(invalid_hash):
    token = "token123"
    # Verification with invalid hash should fail
    assert not verify_token(token, invalid_hash)
