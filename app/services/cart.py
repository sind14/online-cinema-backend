from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.carts import Cart
from app.models.cart_items import CartItem
from app.models.movies import Movie
from app.models.users import User
from app.services.cart_item import CartItemService


class CartService:

    @staticmethod
    def get_cart(db: Session, user: User):
        cart = db.execute(
            select(Cart).where(Cart.user_id == user.id)
        ).scalar_one_or_none()

        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found",
            )

        return cart

    @staticmethod
    def add_movie_to_cart(db: Session, user: User, movie_id: int):
        cart = CartService.get_cart(db, user)

        movie = db.get(Movie, movie_id)
        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Movie with id {movie_id} not found",
            )

        return CartItemService.add_movie(db, cart.id, movie_id)

    @staticmethod
    def remove_movie_from_cart(db: Session, user: User, movie_id: int):
        cart = CartService.get_cart(db, user)

        result = db.execute(
            delete(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.movie_id == movie_id,
            )
        )

        if result.rowcount  == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Movie with id {movie_id} not found in cart",
            )

        db.commit()

    @staticmethod
    def clear_cart(db: Session, user: User):
        cart = CartService.get_cart(db, user)
        db.execute(
            delete(CartItem).where(
                CartItem.cart_id == cart.id,
            )
        )
        db.commit()
