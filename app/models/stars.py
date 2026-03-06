from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.associations import movie_stars


class Star(Base):
    __tablename__ = "stars"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True, index=True)

    movies = relationship("Movie", secondary=movie_stars, back_populates="stars")
