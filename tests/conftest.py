import os
import sys
import pytest
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]

os.environ["ENV_FILE"] = str(PROJECT_ROOT / ".env.test")

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models.user_groups import UserGroup, UserGroupEnum
from app.models.password_reset_tokens import PasswordResetToken
from app.models.activation_tokens import ActivationToken
from app.models.refresh_tokens import RefreshToken
from app.models.genres import Genre
from app.models.directors import Director
from app.models.stars import Star
from app.models.certifications import Certification
from app.models.movies import Movie
from app.models.orders import Order, OrderStatusEnum
from app.models.users import User
from app.models.carts import Cart
from app.models.payments import Payment
from app.models.cart_items import CartItem
from app.core.security import hash_password
from app.schemas.movie import MovieCreate


@pytest.fixture
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def user_group(db_session):
    group = UserGroup(name=UserGroupEnum.USER)

    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)

    return group


@pytest.fixture
def inactive_user(db_session, user_group):
    user = User(
        email="inactive@example.com",
        hashed_password=hash_password("Password-123"),
        is_active=False,
        group_id=user_group.id,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def active_user(db_session, user_group):
    user = User(
        email="active@example.com",
        hashed_password=hash_password("Password-123"),
        is_active=True,
        group_id=user_group.id,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def valid_activation_token(db_session, inactive_user):
    token = ActivationToken(
        user_id=inactive_user.id,
        token="valid-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    db_session.add(token)
    db_session.commit()
    db_session.refresh(token)

    return token


@pytest.fixture
def expired_activation_token(db_session, active_user):
    token = ActivationToken(
        user_id=active_user.id,
        token="expired-token",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=10),
    )

    db_session.add(token)
    db_session.commit()
    db_session.refresh(token)

    return token


@pytest.fixture
def refresh_token(db_session, active_user):
    token = RefreshToken(
        user_id=active_user.id,
        token="refresh-token",
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
    )

    db_session.add(token)
    db_session.commit()
    db_session.refresh(token)

    return token


@pytest.fixture
def expired_reset_token(db_session, active_user):
    token = PasswordResetToken(
        user_id=active_user.id,
        token="expired-reset-token",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=10),
    )

    db_session.add(token)
    db_session.commit()
    db_session.refresh(token)

    return token


@pytest.fixture
def valid_reset_token(db_session, active_user):
    token = PasswordResetToken(
        user_id=active_user.id,
        token="valid-reset-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    db_session.add(token)
    db_session.commit()
    db_session.refresh(token)

    return token


@pytest.fixture
def certification(db_session):
    certification = Certification(name="Test Certification")

    db_session.add(certification)
    db_session.commit()
    db_session.refresh(certification)

    return certification

@pytest.fixture
def certification_factory(db_session):
    def create_certification(name="Test Certification"):
        certification = Certification(name=name)

        db_session.add(certification)
        db_session.commit()
        db_session.refresh(certification)

        return certification

    return create_certification


@pytest.fixture
def genre_factory(db_session):
    def create_genre(name="Test Genre"):
        genre = Genre(name=name)

        db_session.add(genre)
        db_session.commit()
        db_session.refresh(genre)

        return genre

    return create_genre


@pytest.fixture
def star_factory(db_session):
    def create_star(name="Test Star"):
        star = Star(name=name)

        db_session.add(star)
        db_session.commit()
        db_session.refresh(star)

        return star

    return create_star


@pytest.fixture
def director_factory(db_session):
    def create_director(name="Test Director"):
        director = Director(name=name)

        db_session.add(director)
        db_session.commit()
        db_session.refresh(director)

        return director

    return create_director


@pytest.fixture
def movie_create_data_factory(certification_factory, genre_factory, star_factory, director_factory):
    def create_data(**kwargs):
        genre = genre_factory()
        star = star_factory()
        director = director_factory()
        certification = certification_factory()

        return MovieCreate(
            name=kwargs.get("name", "Test Movie"),
            year=kwargs.get("year", 2023),
            time=kwargs.get("time", 120),
            imdb=kwargs.get("imdb", 7.5),
            votes=kwargs.get("votes", 1000),
            meta_score=kwargs.get("meta_score", 80),
            gross=kwargs.get("gross", 1000000),
            description=kwargs.get("description", "Test movie"),
            price=kwargs.get("price", 9.99),
            certification_id=kwargs.get("certification_id", certification.id),
            genre_ids=kwargs.get("genre_ids", [genre.id]),
            star_ids=kwargs.get("star_ids", [star.id]),
            director_ids=kwargs.get("director_ids", [director.id]),
        )

    return create_data


@pytest.fixture
def movie_factory(db_session, certification):
    def create_movie( **kwargs):
        movie = Movie(
            name=kwargs.get("name", "Test Movie"),
            year=kwargs.get("year", 2020),
            time=kwargs.get("time", 120),
            imdb=kwargs.get("imdb", 7.5),
            votes=kwargs.get("votes", 1000),
            meta_score=kwargs.get("meta_score", 80),
            gross=kwargs.get("gross", 1000000),
            description=kwargs.get("description", "Test movie"),
            price=kwargs.get("price", 9.99),
            certification_id=certification.id,
        )

        db_session.add(movie)
        db_session.commit()
        db_session.refresh(movie)

        return movie

    return create_movie


@pytest.fixture
def cart(db_session, active_user):
    cart = Cart(user_id=active_user.id)

    db_session.add(cart)
    db_session.commit()
    db_session.refresh(cart)

    return cart


@pytest.fixture
def cart_item_factory(db_session, movie_factory):
    def create_cart_item(cart_id, movie_id):
        cart_item = CartItem(cart_id=cart_id, movie_id=movie_id)

        db_session.add(cart_item)
        db_session.commit()
        db_session.refresh(cart_item)

        return cart_item

    return create_cart_item


@pytest.fixture
def order_factory(db_session):
    def create_order(**kwargs):
        order = Order(
            user_id=kwargs.get("user_id"),
            total_amount=kwargs.get("total_amount", Decimal("10.00")),
            status=kwargs.get("status", OrderStatusEnum.PENDING),
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        return order

    return create_order


@pytest.fixture
def user_factory(db_session):
    def create_user(**kwargs):
        user = User(
            email=kwargs.get("email", "test@example.com"),
            hashed_password=kwargs.get("hashed_password", "hashed_password"),
            is_active=kwargs.get("is_active", True),
            group_id=kwargs.get("group_id", 1),
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        return user

    return create_user


@pytest.fixture
def payment_factory(db_session):
    def create_payment(**kwargs):
        payment = Payment(
            user_id=kwargs.get("user_id"),
            order_id=kwargs.get("order_id"),
            amount=kwargs.get("amount", Decimal("10.00")),
            external_payment_id=kwargs.get("external_payment_id", "test_payment_id"),
        )

        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)

        return payment

    return create_payment


@pytest.fixture
def client():
    return TestClient(app)