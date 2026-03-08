from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.users import User
from app.services.cart import CartService
from app.schemas.cart import CartResponse, CartItemCreate

router = APIRouter()


@router.get("/", response_model=CartResponse)
def get_cart(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return CartService.get_cart(db, current_user)


@router. post("/items", status_code=status.HTTP_201_CREATED)
def add_movie_to_cart(
        data: CartItemCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return CartService.add_movie_to_cart(db, current_user, data.movie_id)


@router.delete("/items/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_movie_from_cart(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    CartService.remove_movie_from_cart(db, current_user, movie_id)


@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    CartService.clear_cart(db, current_user)

