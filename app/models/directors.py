from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.associations import movie_directors


class Director(Base):
    __tablename__ = "directors"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)

    movies = relationship("Movie", secondary=movie_directors, back_populates="directors")
