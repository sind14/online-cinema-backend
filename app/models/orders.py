import enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class OrderStatusEnum(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    canceled = "canceled"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(Enum(OrderStatusEnum, name="order_status_enum"), nullable=False, default=OrderStatusEnum.pending)
    total_amount = Column(DECIMAL(10, 2), nullable=False)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
