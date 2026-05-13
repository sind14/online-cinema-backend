import pytest
from fastapi import HTTPException, status
from app.services.order import OrderService
from app.models.orders import OrderStatusEnum


def test_create_order_from_cart(
    db_session, active_user, cart, movie_factory, cart_item_factory
):
    movie = movie_factory()
    cart_item_factory(cart.id, movie.id)
    order = OrderService.create_order_from_cart(db_session, active_user)

    assert order.user_id == active_user.id
    assert order.total_amount == movie.price
    assert len(order.items) == 1
    assert order.items[0].movie_id == movie.id
    assert order.items[0].price_at_order == movie.price

    db_session.refresh(cart)

    assert len(cart.items) == 0


def test_create_order_from_cart_raises_for_empty_cart(db_session, active_user, cart):
    with pytest.raises(HTTPException) as exc_info:
        OrderService.create_order_from_cart(db_session, active_user)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Cart is empty"


def test_create_order_from_cart_raises_when_movie_already_purchased(
    db_session, active_user, cart, movie_factory, cart_item_factory
):
    movie = movie_factory()
    cart_item_factory(cart.id, movie.id)
    order = OrderService.create_order_from_cart(db_session, active_user)
    order.status = OrderStatusEnum.PAID

    db_session.commit()

    cart_item_factory(cart.id, movie.id)

    with pytest.raises(HTTPException) as exc_info:
        OrderService.create_order_from_cart(db_session, active_user)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Some movies are already purchased"


def test_get_user_orders(db_session, active_user, order_factory):
    order1 = order_factory(user_id=active_user.id)
    order2 = order_factory(user_id=active_user.id)

    orders = OrderService.get_user_orders(db_session, active_user)

    assert len(orders) == 2
    assert orders[0].id == order1.id
    assert orders[1].id == order2.id
    assert all(order.user_id == active_user.id for order in orders)


def test_get_user_orders_returns_only_user_orders(
    db_session, active_user, order_factory, user_factory
):
    other_user = user_factory()
    order_factory(user_id=active_user.id)
    order_factory(user_id=other_user.id)

    orders = OrderService.get_user_orders(db_session, active_user)

    assert len(orders) == 1
    assert orders[0].user_id == active_user.id


def test_get_user_orders_returns_empty_list(db_session, active_user):
    orders = OrderService.get_user_orders(db_session, active_user)
    assert orders == []


def test_get_order_by_id(db_session, active_user, order_factory):
    order = order_factory(user_id=active_user.id)
    result = OrderService.get_order_by_id(db_session, active_user, order.id)
    assert result.id == order.id


def test_get_order_by_id_raises_for_nonexistent_order(db_session, active_user):
    with pytest.raises(HTTPException) as exc_info:
        OrderService.get_order_by_id(db_session, active_user, 999)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Order not found"


def test_get_order_by_id_raises_for_other_user_order(
    db_session, active_user, order_factory, user_factory
):
    other_user = user_factory()
    order = order_factory(user_id=other_user.id)

    with pytest.raises(HTTPException) as exc_info:
        OrderService.get_order_by_id(db_session, active_user, order.id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Order not found"


def test_cancel_order(db_session, active_user, order_factory):
    order = order_factory(user_id=active_user.id)
    result = OrderService.cancel_order(db_session, active_user, order.id)

    assert result.id == order.id
    assert result.status == OrderStatusEnum.CANCELED


def test_cancel_order_raises_for_not_pending_order(
    db_session, active_user, order_factory
):
    order = order_factory(user_id=active_user.id, status=OrderStatusEnum.PAID)
    with pytest.raises(HTTPException) as exc_info:
        OrderService.cancel_order(db_session, active_user, order.id)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Only pending orders can be canceled"


def test_cancel_order_raises_for_other_user_order(
    db_session, active_user, user_factory, order_factory
):
    other_user = user_factory()
    order = order_factory(user_id=other_user.id)
    with pytest.raises(HTTPException) as exc_info:
        OrderService.cancel_order(db_session, active_user, order.id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Order not found"
