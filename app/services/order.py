from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.orm import Session, selectinload
from app.models.users import User
from app.models.orders import Order, OrderStatusEnum
from app.models.order_items import OrderItem
from app.models.carts import Cart
from app.models.cart_items import CartItem


class OrderService:

    @staticmethod
    def create_order_from_cart(db: Session, user: User) -> Order:
        stmt = (
            select(Cart)
            .options(
                selectinload(Cart.items).selectinload(CartItem.movie)
            )
            .where(Cart.user_id == user.id)
        )

        cart = db.scalar(stmt)

        if not cart or not cart.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

        movie_ids = [item.movie_id for item in cart.items]

        purchased_stmt = (
            select(OrderItem.movie_id)
            .join(Order)
            .where(
                Order.user_id == user.id,
                Order.status == OrderStatusEnum.PAID,
                OrderItem.movie_id.in_(movie_ids),
            )
        )

        purchased_movies = db.scalars(purchased_stmt).all()

        if purchased_movies:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Some movies are already purchased")

        order = Order(user_id=user.id, total_amount=Decimal("0"))

        total = Decimal("0")

        db.add(order)
        db.flush()

        for item in cart.items:
            movie = item.movie

            order_item = OrderItem(
                order_id=order.id,
                movie_id=movie.id,
                price_at_order=movie.price,
            )

            total += movie.price
            db.add(order_item)

        order.total_amount = total

        db.execute(
            delete(CartItem).where(CartItem.cart_id == cart.id)
        )

        db.commit()
        db.refresh(order)

        return order

    @staticmethod
    def get_user_orders(db: Session, user: User) -> list[Order]:

        stmt = (
            select(Order)
            .options(
                selectinload(Order.items)
                .selectinload(OrderItem.movie)
            )
            .where(Order.user_id == user.id)
        )

        return list(db.scalars(stmt))

    @staticmethod
    def get_order_by_id(db: Session, user: User, order_id: int) -> Order:
        stmt = (
            select(Order)
            .options(
                selectinload(Order.items)
                .selectinload(OrderItem.movie)
            )
            .where(Order.id == order_id, Order.user_id == user.id)
        )

        order = db.scalar(stmt)

        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        return order

    @staticmethod
    def cancel_order(db: Session, user: User, order_id: int) -> Order:
        order = OrderService.get_order_by_id(db, user, order_id)

        if order.status != OrderStatusEnum.PENDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending orders can be canceled")

        order.status = OrderStatusEnum.CANCELED

        db.commit()
        db.refresh(order)

        return order
