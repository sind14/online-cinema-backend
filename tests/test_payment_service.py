import pytest
from fastapi import HTTPException, status
from app.services.payment import PaymentService
from app.services.order import OrderService
from app.schemas.payment import PaymentCreate
from app.models.orders import OrderStatusEnum


def test_create_payment(db_session, active_user, cart, movie_factory, cart_item_factory):
    movie = movie_factory()
    cart_item_factory(cart.id, movie.id)
    order = OrderService.create_order_from_cart(db_session, active_user)
    payment = PaymentService.create_payment(db_session, active_user, PaymentCreate(order_id=order.id))

    assert payment.user_id == active_user.id
    assert payment.order_id == order.id
    assert payment.amount == order.total_amount

    db_session.refresh(order)

    assert order.status == OrderStatusEnum.PAID
    assert len(payment.payment_items) == 1


def test_create_payment_raises_for_not_pending_order(db_session, active_user, order_factory):
    order = order_factory(user_id=active_user.id, status=OrderStatusEnum.PAID)
    with pytest.raises(HTTPException) as exc_info:
        PaymentService.create_payment(db_session, active_user, PaymentCreate(order_id=order.id))

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Order cannot be paid"


def test_create_payment_raises_for_nonexistent_order(db_session, active_user):
    with pytest.raises(HTTPException) as exc_info:
        PaymentService.create_payment(db_session, active_user, PaymentCreate(order_id=999))

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Order not found"


def test_get_payment(db_session, active_user, order_factory, payment_factory):
    order = order_factory(user_id=active_user.id)
    payment = payment_factory(user_id=active_user.id, order_id=order.id)
    result = PaymentService.get_payment(db_session, active_user.id, payment.id)

    assert result.id == payment.id



def test_get_payment_raises_for_nonexistent_payment(db_session, active_user):
    with pytest.raises(HTTPException) as exc_info:
        PaymentService.get_payment(db_session, active_user.id, 999)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Payment not found"


def test_get_payment_raises_for_other_user_payment(db_session, active_user, payment_factory, user_factory, order_factory):
    other_user = user_factory()
    order = order_factory(user_id=other_user.id)
    payment = payment_factory(user_id=other_user.id, order_id=order.id)

    with pytest.raises(HTTPException) as exc_info:
        PaymentService.get_payment(db_session, active_user.id, payment.id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Payment not found"


def test_get_user_payments(db_session, active_user, order_factory, payment_factory):
    order1 = order_factory(user_id=active_user.id)
    order2 = order_factory(user_id=active_user.id)
    payment1 = payment_factory(user_id=active_user.id, order_id=order1.id)
    payment2 = payment_factory(user_id=active_user.id, order_id=order2.id)
    payments = PaymentService.get_user_payments(db_session, active_user.id)

    assert len(payments) == 2
    assert payments[0].id == payment1.id
    assert payments[1].id == payment2.id
    assert all(payment.user_id == active_user.id for payment in payments)


def test_get_user_payments_returns_only_user_payments(
    db_session,
    active_user,
    payment_factory,
    order_factory,
    user_factory,
):
    other_user = user_factory()
    active_user_order = order_factory(user_id=active_user.id)
    other_user_order = order_factory(user_id=other_user.id)
    payment_factory(user_id=active_user.id, order_id=active_user_order.id)
    payment_factory(user_id=other_user.id, order_id=other_user_order.id)
    payments = PaymentService.get_user_payments(db_session, active_user.id)

    assert len(payments) == 1
    assert payments[0].user_id == active_user.id
