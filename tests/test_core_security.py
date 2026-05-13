import pytest
from app.core.security import hash_password, verify_password, validate_password_complexity


def test_hash_password_returns_hashed_value():
    password = "Password-123"
    hashed_password = hash_password(password)
    assert isinstance(hashed_password, str)
    assert hashed_password != password
    assert hashed_password != ""


def test_verify_password_returns_true_for_correct_password():
    password = "Password-123"
    hashed_password = hash_password(password)
    assert verify_password(password, hashed_password) is True


def test_verify_password_returns_false_for_wrong_password():
    password = "Password-123"
    wrong_password = "WrongPassword-123"
    hashed_password = hash_password(password)
    assert verify_password(wrong_password, hashed_password) is False


def test_validate_password_complexity_accepts_valid_password():
    password = "Password-123"
    validate_password_complexity(password)


def test_validate_password_complexity_rejects_short_password():
    password = "Pas-1"
    with pytest.raises(ValueError, match="Password must be at least 8 characters long."):
        validate_password_complexity(password)


def test_validate_password_complexity_rejects_long_password():
    password = "P" * 118 + "assword-123"
    with pytest.raises(ValueError, match="Password is too long."):
        validate_password_complexity(password)


def test_validate_password_complexity_rejects_no_uppercase_letter():
    password = "password-123"
    with pytest.raises(ValueError, match="Password must contain at least one uppercase letter."):
        validate_password_complexity(password)


def test_validate_password_complexity_rejects_no_lowercase_letter():
    password = "PASSWORD-123"
    with pytest.raises(ValueError, match="Password must contain at least one lowercase letter."):
        validate_password_complexity(password)


def test_validate_password_complexity_rejects_no_digit():
    password = "Password-abc"
    with pytest.raises(ValueError, match="Password must contain at least one digit."):
        validate_password_complexity(password)


def test_validate_password_complexity_rejects_no_special_character():
    password = "Password1123"
    with pytest.raises(ValueError, match="Password must contain at least one special character."):
        validate_password_complexity(password)
