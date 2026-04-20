import secrets
from jose import jwt
from fastapi import HTTPException, status
from datetime import timezone, datetime, timedelta
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.services.email import send_email
from app.auth.schemas import ChangePasswordSchema
from app.core.security import hash_password, verify_password
from app.core.config import settings
from app.core.security import validate_password_complexity
from app.models.activation_tokens import ActivationToken
from app.models.refresh_tokens import RefreshToken
from app.models.users import User
from app.models.user_groups import UserGroup, UserGroupEnum
from app.models.password_reset_tokens import PasswordResetToken
from app.models.carts import Cart

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


def _get_user_by_email(db: Session, email: str) -> User:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def _send_email(to_email: str, subject: str, message: str) -> None:
    send_email(to_email, subject, message)


def _validate_token_expiration(token_obj, db: Session):
    expires_at = token_obj.expires_at

    if expires_at < datetime.now(timezone.utc):
        db.delete(token_obj)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )


def _delete_existing_token(model, user_id: int, db: Session) -> None:
    db.execute(delete(model).where(model.user_id == user_id))


def register(db: Session, email: str, password: str):
    if _get_user_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    validate_password_complexity(password)
    hashed_password = hash_password(password)

    group = db.execute(
        select(UserGroup).where(UserGroup.name == UserGroupEnum.USER)
    ).scalar_one()

    user = User(
        email=email,
        hashed_password=hashed_password,
        is_active=False,
        group_id=group.id,
    )
    db.add(user)
    db.flush()

    cart = Cart(user_id=user.id)
    db.add(cart)

    token = create_activation_token(db, user.id)

    db.commit()
    db.refresh(user)

    activation_link = f"{settings.BASE_URL}/auth/activate?token={token}"

    _send_email(
        user.email,
        "Account activation",
        f"Please activate your account by clicking on the following link: {activation_link}",
    )

    return user


def login(db: Session, email: str, password: str):
    user = _get_user_by_email(db, email)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    db.execute(delete(RefreshToken).where(RefreshToken.user_id == user.id))

    access_token_expires = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = jwt.encode(
        {"sub": str(user.id), "exp": access_token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    refresh_token_expires = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )
    refresh_token_str = jwt.encode(
        {"sub": str(user.id), "exp": refresh_token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    db.add(
        RefreshToken(
            user_id=user.id, token=refresh_token_str, expires_at=refresh_token_expires
        )
    )
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
    }


def logout(db: Session, refresh_token: str):
    token_obj = db.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    ).scalar_one_or_none()

    if token_obj:
        db.delete(token_obj)
        db.commit()

    return {"message": "Successfully logged out"}


def create_activation_token(db: Session, user_id: int):
    _delete_existing_token(ActivationToken, user_id, db)

    token_value = secrets.token_urlsafe(32)
    token = ActivationToken(
        user_id=user_id,
        token=token_value,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )

    db.add(token)

    return token_value


def activate_user(db: Session, token: str):
    activation = db.execute(
        select(ActivationToken).where(ActivationToken.token == token)
    ).scalar_one_or_none()

    if not activation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )

    _validate_token_expiration(activation, db)

    user = activation.user
    user.is_active = True

    db.delete(activation)
    db.commit()

    return user


def resend_activation(db: Session, email: str):
    user = _get_user_by_email(db, email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already activated"
        )

    token = create_activation_token(db, user.id)
    activation_link = f"{settings.BASE_URL}/auth/activate?token={token}"

    _send_email(
        user.email,
        "Resend account activation",
        f"Please activate your account by clicking on the following link: {activation_link}",
    )

    return token


def change_password(db: Session, current_user: User, data: ChangePasswordSchema):
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect"
        )

    try:
        validate_password_complexity(data.new_password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    current_user.hashed_password = hash_password(data.new_password)

    db.execute(delete(RefreshToken).where(RefreshToken.user_id == current_user.id))

    db.commit()

    return {"message": "Password changed successfully"}


def reset_password(db: Session, token: str, new_password: str):
    reset_token = db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token == token)
    ).scalar_one_or_none()

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )

    _validate_token_expiration(reset_token, db)

    user = reset_token.user
    validate_password_complexity(new_password)
    user.hashed_password = hash_password(new_password)

    db.execute(delete(RefreshToken).where(RefreshToken.user_id == user.id))

    db.delete(reset_token)
    db.commit()

    return {"message": "Password changed successfully"}


def forgot_password(db: Session, email: str):
    user = _get_user_by_email(db, email)

    if not user or not user.is_active:
        return {"message": "If the email exists, a reset link has been sent."}

    _delete_existing_token(PasswordResetToken, user.id, db)

    token_value = secrets.token_urlsafe(32)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token_value,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    db.add(reset_token)
    db.commit()

    reset_link = f"{settings.BASE_URL}/auth/reset-password?token={token_value}"

    _send_email(
        user.email,
        "Password Reset",
        f"Reset your password using this link: {reset_link}",
    )

    return {"message": "If the email exists, a reset link has been sent."}
