from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth import service as auth_service
from app.auth.dependencies import get_current_user, require_role
from app.models.user_groups import UserGroupEnum
from app.auth.schemas import (
    UserCreateSchema,
    LogoutSchema,
    ChangePasswordSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
)


router = APIRouter()


@router.post("/register")
def register_user(data: UserCreateSchema, db: Session = Depends(get_db)):
    return auth_service.register(db, str(data.email), data.password)


@router.post("/reset-activation")
def resend_activation(email: str, db: Session = Depends(get_db)):
    auth_service.resend_activation(db, email)
    return {"message": f"Activation link sent to {email}."}


@router.post("/login")
def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return auth_service.login(db, str(data.username), data.password)


@router.post("/logout")
def logout(data: LogoutSchema, db: Session = Depends(get_db)):
    return auth_service.logout(db, data.refresh_token)


@router.post("/change-password")
def change_user_password(
        data: ChangePasswordSchema,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    return auth_service.change_password(db, current_user, data)


@router.post("/forgot-password")
def forgot_password_route(data: ForgotPasswordSchema, db: Session = Depends(get_db)):
    return auth_service.forgot_password(db, str(data.email))


@router.post("/reset-password")
def reset_password_route(data: ResetPasswordSchema, db: Session = Depends(get_db)):
    return auth_service.reset_password(db, data.token, data.new_password)


@router.get("/activate")
def activate_user(token: str, db: Session = Depends(get_db)):
    user = auth_service.activate_user(db, token)
    return {"message": f"User {user.email} activated successfully."}


@router.get("/admin-only")
def admin_only(current_user=Depends(require_role([UserGroupEnum.ADMIN]))):
    return {"message": f"Admin access granted for {current_user.email}"}


@router.get("/moderator-area")
def moderator_area(
    current_user = Depends(require_role([UserGroupEnum.ADMIN, UserGroupEnum.MODERATOR]))):
    return {"message": f"Moderator access granted for {current_user.email}"}
