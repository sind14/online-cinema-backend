import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, Float, String, Text, DECIMAL, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.associations import movie_directors, movie_genres, movie_stars


class Movie(Base):
    __tablename__ = "movies"

    __table_args__ = (UniqueConstraint("name", "year", "time", name="uq_movie_name_year_time"),)

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(250), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    time = Column(Integer, nullable=False)
    imdb = Column(Float, nullable=False)
    votes = Column(Integer, nullable=False)
    meta_score = Column(Float)
    gross = Column(Float)
    description = Column(Text, nullable=False)
    price = Column(DECIMAL(10, 2))
    certification_id = Column(Integer, ForeignKey("certifications.id"), nullable=False)

    certification = relationship("Certification", back_populates="movies")
    stars = relationship("Star", secondary=movie_stars, back_populates="movies")
    genres = relationship("Genre", secondary=movie_genres, back_populates="movies")
    directors = relationship("Director", secondary=movie_directors, back_populates="movies")
    cart_items = relationship("CartItem", back_populates="movie")
    order_items = relationship("OrderItem", back_populates="movie")
