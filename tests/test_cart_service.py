import pytest
from fastapi import HTTPException, status
from app.services.cart import CartService

def test_get_cart_returns_user_cart(db_session, active_user, cart):
    result = CartService.get_cart(db_session, active_user)

    assert result == cart
    assert result.user_id == active_user.id


def test_get_cart_returns_cart_with_items(db_session, active_user, cart, cart_item_factory, movie_factory):
    movie = movie_factory()
    cart_item = cart_item_factory(cart.id, movie.id)
    result = CartService.get_cart(db_session, active_user)

    assert len(result.items) == 1
    assert result.items[0] == cart_item
    assert result.items[0].movie_id == cart_item.movie_id


def test_get_cart_raises_for_no_cart(db_session, active_user):
    with pytest.raises(HTTPException) as exc_info:
        CartService.get_cart(db_session, active_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Cart not found"


def test_add_movie_to_cart(db_session, active_user, cart, movie_factory):
    movie = movie_factory()
    CartService.add_movie_to_cart(db_session, active_user, movie.id)
    result = CartService.get_cart(db_session, active_user)
    assert len(result.items) == 1
    assert result.items[0].movie_id == movie.id


def test_add_movie_to_cart_raises_for_existing_item(db_session, active_user, cart, movie_factory):
    movie = movie_factory()
    CartService.add_movie_to_cart(db_session, active_user, movie.id)

    with pytest.raises(HTTPException) as exc_info:
        CartService.add_movie_to_cart(db_session, active_user, movie.id)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Movie already in cart"


def test_add_movie_to_cart_raises_for_nonexistent_movie(db_session, active_user, cart):
    with pytest.raises(HTTPException) as exc_info:
        CartService.add_movie_to_cart(db_session, active_user, 999)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Movie with id 999 not found"


def test_remove_movie_from_cart(db_session, active_user, cart, movie_factory):
    movie = movie_factory()
    CartService.add_movie_to_cart(db_session, active_user, movie.id)
    CartService.remove_movie_from_cart(db_session, active_user, movie.id)
    result = CartService.get_cart(db_session, active_user)

    assert len(result.items) == 0
    assert result.items == []

def test_remove_movie_from_cart_raises_for_nonexistent_movie(db_session, active_user, cart):
    with pytest.raises(HTTPException) as exc_info:
        CartService.remove_movie_from_cart(db_session, active_user, 999)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Movie with id 999 not found in cart"


def test_clear_cart(db_session, active_user, cart, cart_item_factory, movie_factory):
    movie = movie_factory()
    cart_item_factory(cart.id, movie.id)
    CartService.clear_cart(db_session, active_user)
    result = CartService.get_cart(db_session, active_user)

    assert len(result.items) == 0
    assert result.user_id == active_user.id


def test_clear_cart_with_empty_cart(db_session, active_user, cart):
    CartService.clear_cart(db_session, active_user)
    result = CartService.get_cart(db_session, active_user)

    assert len(result.items) == 0
    assert result.user_id == active_user.id
