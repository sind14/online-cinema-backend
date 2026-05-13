from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.users import User
from app.auth.dependencies import get_current_user
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.database.session import get_db
from app.services.payment import PaymentService

router = APIRouter()


@router.get("/", response_model=list[PaymentResponse])
def get_my_payments(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return PaymentService.get_user_payments(db, user.id)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return PaymentService.get_payment(db, user.id, payment_id)


@router.post("/", response_model=PaymentResponse)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return PaymentService.create_payment(db, user, payment_data)
