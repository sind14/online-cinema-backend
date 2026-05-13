import enum
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database.base import Base


class GenderEnum(str, enum.Enum):
    MAN = "MAN"
    WOMAN = "WOMAN"


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    avatar = Column(String(255))
    gender = Column(Enum(GenderEnum), nullable=True)
    date_of_birth = Column(Date)
    info = Column(Text)

    user = relationship("User", back_populates="profile")
