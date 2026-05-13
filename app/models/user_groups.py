import enum
from sqlalchemy import Column, Integer, Enum
from sqlalchemy.orm import relationship
from app.database.base import Base


class UserGroupEnum(str, enum.Enum):
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class UserGroup(Base):
    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True)
    name = Column(
        Enum(UserGroupEnum, name="user_group_enum"), unique=True, nullable=False
    )
    users = relationship("User", back_populates="group")
