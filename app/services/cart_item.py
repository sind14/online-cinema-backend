from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.cart_items import CartItem
from app.services.base import BaseCRUDService


class CartItemService(BaseCRUDService):
    model = CartItem

    @classmethod
    def add_movie(cls, db: Session, cart_id: int, movie_id: int):
        stmt = select(cls.model).where(
            cls.model.cart_id == cart_id ,
            cls.model.movie_id == movie_id,
        )

        existing = db.scalar(stmt)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Movie already in cart",
            )

        return cls.create(db, cart_id=cart_id, movie_id=movie_id)
