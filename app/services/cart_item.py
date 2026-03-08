from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.cart_items import CartItem
from app.services.base import BaseCRUDService


class CartItemService(BaseCRUDService):
    model = CartItem

    @classmethod
    def add_movie(cls, db: Session, cart_id: int, movie_id: int):
        existing = db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart_id,
                CartItem.movie_id == movie_id,
            )
        ).scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Movie already in cart",
            )

        return cls.create(db, cart_id=cart_id, movie_id=movie_id)


