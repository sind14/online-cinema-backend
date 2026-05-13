from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.payments import Payment
from app.models.payment_items import PaymentItem
from app.models.orders import Order, OrderStatusEnum
from app.models.users import User
from app.services.order import OrderService
from app.schemas.payment import PaymentCreate


class PaymentService:

    @staticmethod
    def _create_payment_items(db: Session, payment: Payment, order: Order) -> None:
        for item in order.items:
            payment_item = PaymentItem(
                payment_id=payment.id,
                order_item_id=item.id,
                price_at_payment=item.price_at_order,
            )

            db.add(payment_item)

    @staticmethod
    def create_payment(db: Session, user: User, payment_data: PaymentCreate) -> Payment:
        order = OrderService.get_order_by_id(db, user, payment_data.order_id)

        if order.status != OrderStatusEnum.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Order cannot be paid"
            )

        payment = Payment(
            user_id=user.id,
            order_id=order.id,
            amount=order.total_amount,
            external_payment_id="stripe_test_id",
        )

        db.add(payment)
        db.flush()

        PaymentService._create_payment_items(db, payment, order)

        order.status = OrderStatusEnum.PAID

        db.commit()
        db.refresh(payment)

        return payment

    @staticmethod
    def get_payment(db: Session, user_id: int, payment_id: int) -> Payment:
        stmt = select(Payment).where(
            Payment.id == payment_id, Payment.user_id == user_id
        )

        payment = db.scalar(stmt)

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
            )

        return payment

    @staticmethod
    def get_user_payments(db: Session, user_id: int) -> list[Payment]:
        stmt = select(Payment).where(Payment.user_id == user_id)
        return db.scalars(stmt).all()
