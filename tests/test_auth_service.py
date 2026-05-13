import pytest
from fastapi import HTTPException, status
from sqlalchemy import select
from app.auth.schemas import ChangePasswordSchema
from app.auth.service import (
    _get_user_by_email,
    _validate_token_expiration,
    _delete_existing_token,
    logout,
    register,
    login,
    change_password,
    activate_user,
    resend_activation,
    reset_password,
    forgot_password,
)
from app.models.activation_tokens import ActivationToken
from app.models.refresh_tokens import RefreshToken
from app.models.carts import Cart
from app.models.users import User
from app.models.password_reset_tokens import PasswordResetToken
from app.core.security import verify_password


def test_get_user_by_email_returns_user_when_exists(db_session, active_user):
    result = _get_user_by_email(db_session, active_user.email)

    assert result.email == active_user.email
    assert result is not None


def test_get_user_by_email_returns_none_when_user_does_not_exist(db_session):
    result = _get_user_by_email(db_session, "missing@example.com")

    assert result is None


def test_validate_token_expiration_allows_valid_token(
    db_session, valid_activation_token
):
    _validate_token_expiration(valid_activation_token, db_session)


def test_validate_token_expiration_raises_for_expired_token(
    db_session, expired_activation_token
):
    with pytest.raises(HTTPException) as exc_info:
        _validate_token_expiration(expired_activation_token, db_session)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Invalid or expired token"


def test_delete_existing_token_removes_token_from_db(
    db_session, valid_activation_token
):
    _delete_existing_token(ActivationToken, valid_activation_token.user_id, db_session)

    db_session.commit()

    token_in_db = db_session.execute(
        select(ActivationToken).where(
            ActivationToken.user_id == valid_activation_token.user_id
        )
    ).scalar_one_or_none()

    assert token_in_db is None


def test_logout_deletes_existing_refresh_token(db_session, refresh_token):
    result = logout(db_session, refresh_token.token)

    token_in_db = db_session.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token.token)
    ).scalar_one_or_none()

    assert result == {"message": "Successfully logged out"}
    assert token_in_db is None


def test_logout_returns_success_when_token_does_not_exist(db_session):
    result = logout(db_session, "nonexistent-token")

    assert result == {"message": "Successfully logged out"}


def test_register_creates_user_cart_activation_token_and_sends_email(
    db_session, user_group, monkeypatch
):
    email = "newuser@example.com"
    password = "Password-123"
    sent_emails = []

    def mock_send_email(to_email, subject, message):
        sent_emails.append(
            {
                "to_email": to_email,
                "subject": subject,
                "message": message,
            }
        )

    monkeypatch.setattr("app.auth.service._send_email", mock_send_email)
    user = register(db_session, email, password)
    cart = db_session.execute(
        select(Cart).where(Cart.user_id == user.id)
    ).scalar_one_or_none()
    activation_token_stmt = select(ActivationToken).where(
        ActivationToken.user_id == user.id
    )
    activation_token = db_session.execute(activation_token_stmt).scalar_one_or_none()

    assert user.email == email
    assert user.is_active is False
    assert user.group_id == user_group.id
    assert len(sent_emails) == 1
    assert sent_emails[0]["to_email"] == email
    assert sent_emails[0]["subject"] == "Account activation"
    assert user.hashed_password != password
    assert cart is not None
    assert activation_token is not None


def test_register_raises_when_email_already_exists(
    db_session, active_user, monkeypatch
):
    sent_emails = []

    def mock_send_email(to_email, subject, message):
        sent_emails.append(
            {
                "to_email": to_email,
                "subject": subject,
                "message": message,
            }
        )

    monkeypatch.setattr("app.auth.service._send_email", mock_send_email)

    with pytest.raises(HTTPException) as exc_info:
        register(db_session, active_user.email, "Password-123")

    assert len(sent_emails) == 0
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Email already exists"


def test_register_raises_when_password_is_invalid(db_session):
    email = "newuser@example.com"
    invalid_password = "Pas-1"

    with pytest.raises(HTTPException) as exc_info:
        register(db_session, email, invalid_password)

    result = db_session.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Password must be at least 8 characters long."
    assert result is None


def test_login_raises_when_user_does_not_exist(db_session):
    email = "missing@example.com"
    password = "Password-123"

    with pytest.raises(HTTPException) as exc_info:
        login(db_session, email, password)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid credentials"


def test_login_raises_when_user_is_inactive(db_session, inactive_user):
    email = inactive_user.email
    password = "Password-123"

    with pytest.raises(HTTPException) as exc_info:
        login(db_session, email, password)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid credentials"


def test_login_raises_when_password_is_incorrect(db_session, active_user):
    email = active_user.email
    password = "incorrect-password"

    with pytest.raises(HTTPException) as exc_info:
        login(db_session, email, password)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid credentials"


def test_login_returns_tokens_for_valid_credentials(db_session, active_user):
    email = active_user.email
    password = "Password-123"

    result = login(db_session, email, password)
    stmt = select(RefreshToken).where(RefreshToken.user_id == active_user.id)
    refresh_token_in_db = db_session.execute(stmt).scalar_one_or_none()

    assert result["access_token"]
    assert result["refresh_token"]
    assert result["token_type"] == "bearer"
    assert refresh_token_in_db is not None
    assert refresh_token_in_db.token == result["refresh_token"]
    assert refresh_token_in_db.user_id == active_user.id


def test_login_replaces_existing_refresh_token(db_session, active_user, refresh_token):
    email = active_user.email
    password = "Password-123"
    old_refresh_token = refresh_token.token

    result = login(db_session, email, password)
    stmt = select(RefreshToken).where(RefreshToken.user_id == active_user.id)
    refresh_token_in_db = db_session.execute(stmt).scalar_one_or_none()

    assert refresh_token_in_db is not None
    assert refresh_token_in_db.token == result["refresh_token"]
    assert refresh_token_in_db.token != old_refresh_token


def test_change_password_raises_when_old_password_is_incorrect(db_session, active_user):
    new_password = "New-Password-123"
    old_password = "incorrect-password"

    with pytest.raises(HTTPException) as exc_info:
        change_password(
            db_session,
            active_user,
            ChangePasswordSchema(old_password=old_password, new_password=new_password),
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Old password is incorrect"


def test_change_password_raises_when_new_password_is_invalid(db_session, active_user):
    old_password = "Password-123"
    new_password = "short"

    with pytest.raises(HTTPException) as exc_info:
        change_password(
            db_session,
            active_user,
            ChangePasswordSchema(old_password=old_password, new_password=new_password),
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Password must be at least 8 characters long."


def test_change_password_updates_user_password_and_deletes_refresh_tokens(
    db_session, active_user
):
    new_password = "New-Password-123"
    old_password = "Password-123"
    result = change_password(
        db_session,
        active_user,
        ChangePasswordSchema(old_password=old_password, new_password=new_password),
    )
    stmt = select(RefreshToken).where(RefreshToken.user_id == active_user.id)
    refresh_token_in_db = db_session.execute(stmt).scalar_one_or_none()

    assert result["message"] == "Password changed successfully"
    assert verify_password(new_password, active_user.hashed_password)
    assert refresh_token_in_db is None


def test_activate_user_raises_when_token_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        activate_user(db_session, "nonexistent-token")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Invalid or expired token"


def test_activate_user_raises_when_token_is_expired(
    db_session, expired_activation_token
):
    with pytest.raises(HTTPException) as exc_info:
        activate_user(db_session, expired_activation_token.token)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Invalid or expired token"


def test_activate_user_activates_user_and_deletes_token(
    db_session, inactive_user, valid_activation_token
):
    returned_user = activate_user(db_session, valid_activation_token.token)

    user_in_db = db_session.execute(
        select(User).where(User.id == inactive_user.id)
    ).scalar_one_or_none()

    token_in_db = db_session.execute(
        select(ActivationToken).where(ActivationToken.user_id == inactive_user.id)
    ).scalar_one_or_none()

    assert returned_user.id == inactive_user.id
    assert user_in_db.is_active is True
    assert token_in_db is None


def test_resend_activation_raises_when_user_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        resend_activation(db_session, "missing@example.com")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "User not found"


def test_resend_activation_raises_when_user_already_activated(db_session, active_user):
    with pytest.raises(HTTPException) as exc_info:
        resend_activation(db_session, active_user.email)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "User already activated"


def test_resend_activation_creates_token_and_sends_email(
    db_session, inactive_user, monkeypatch
):
    email = inactive_user.email
    sent_emails = []

    def mock_send_email(to_email, subject, message):
        sent_emails.append(
            {
                "to_email": to_email,
                "subject": subject,
                "message": message,
            }
        )

    monkeypatch.setattr("app.auth.service._send_email", mock_send_email)
    returned_token = resend_activation(db_session, email)

    token_stmt = select(ActivationToken).where(
        ActivationToken.user_id == inactive_user.id
    )
    token = db_session.execute(token_stmt).scalar_one_or_none()

    assert returned_token == token.token
    assert len(sent_emails) == 1
    assert sent_emails[0]["to_email"] == email
    assert sent_emails[0]["subject"] == "Resend account activation"
    assert returned_token in sent_emails[0]["message"]
    assert token is not None


def test_reset_password_raises_when_token_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        reset_password(db_session, "nonexistent-token", "new-password")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Invalid or expired token"


def test_reset_password_raises_when_token_is_expired(db_session, expired_reset_token):
    with pytest.raises(HTTPException) as exc_info:
        reset_password(db_session, expired_reset_token.token, "new-password")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Invalid or expired token"


def test_reset_password_raises_when_password_is_invalid(db_session, valid_reset_token):
    with pytest.raises(HTTPException) as exc_info:
        reset_password(db_session, valid_reset_token.token, "short")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Password must be at least 8 characters long."


def test_reset_password_updates_password_deletes_refresh_tokens_and_token(
    db_session, valid_reset_token
):
    new_password = "New-Password-123"
    result = reset_password(db_session, valid_reset_token.token, new_password)
    user_id = valid_reset_token.user_id

    refresh_token_in_db = db_session.execute(
        select(RefreshToken).where(RefreshToken.user_id == user_id)
    ).scalar_one_or_none()

    token_in_db = db_session.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == valid_reset_token.token
        )
    ).scalar_one_or_none()

    user_in_db = db_session.execute(
        select(User).where(User.id == user_id)
    ).scalar_one_or_none()

    assert result["message"] == "Password changed successfully"
    assert verify_password(new_password, user_in_db.hashed_password)
    assert refresh_token_in_db is None
    assert token_in_db is None


def test_forgot_password_returns_success_when_user_not_found(db_session, monkeypatch):
    sent_emails = []

    def mock_send_email(to_email, subject, message):
        sent_emails.append(
            {
                "to_email": to_email,
                "subject": subject,
                "message": message,
            }
        )

    monkeypatch.setattr("app.auth.service._send_email", mock_send_email)

    result = forgot_password(db_session, "missing@example.com")
    token_in_db = db_session.execute(select(PasswordResetToken)).scalar_one_or_none()

    assert result == {"message": "If the email exists, a reset link has been sent."}
    assert len(sent_emails) == 0
    assert token_in_db is None


def test_forgot_password_returns_success_when_user_is_inactive(
    db_session, inactive_user, monkeypatch
):
    email = inactive_user.email
    sent_emails = []

    def mock_send_email(to_email, subject, message):
        sent_emails.append(
            {
                "to_email": to_email,
                "subject": subject,
                "message": message,
            }
        )

    monkeypatch.setattr("app.auth.service._send_email", mock_send_email)
    result = forgot_password(db_session, email)

    assert result == {"message": "If the email exists, a reset link has been sent."}
    assert len(sent_emails) == 0


def test_forgot_password_creates_reset_token_and_sends_email(
    db_session, active_user, monkeypatch
):
    email = active_user.email
    sent_emails = []

    def mock_send_email(to_email, subject, message):
        sent_emails.append(
            {
                "to_email": to_email,
                "subject": subject,
                "message": message,
            }
        )

    monkeypatch.setattr("app.auth.service._send_email", mock_send_email)
    result = forgot_password(db_session, email)
    token_in_db = db_session.execute(
        select(PasswordResetToken).where(PasswordResetToken.user_id == active_user.id)
    ).scalar_one_or_none()

    assert result == {"message": "If the email exists, a reset link has been sent."}
    assert len(sent_emails) == 1
    assert sent_emails[0]["to_email"] == email
    assert sent_emails[0]["subject"] == "Password Reset"
    assert token_in_db is not None
    assert token_in_db.token in sent_emails[0]["message"]
