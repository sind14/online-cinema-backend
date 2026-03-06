from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.base import Base


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True, index=True)

    movies = relationship("Movie", back_populates="certification")
