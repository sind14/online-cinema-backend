from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.models.users import User
from app.auth.dependencies import get_current_user
from app.schemas.order import OrderResponse
from app.database.session import get_db
from app.services.order import OrderService


router = APIRouter()


@router.get("/", response_model=List[OrderResponse])
def get_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return OrderService.get_user_orders(db, current_user)


@router.get("/{order_id}", response_model= OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return OrderService.get_order_by_id(db, current_user, order_id)


@router.post("/", response_model=OrderResponse)
def create_order(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return OrderService.create_order_from_cart(db, current_user)

@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return OrderService.cancel_order(db, current_user, order_id)
