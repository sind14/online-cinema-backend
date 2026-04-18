import enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, DECIMAL, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

class PaymentStatusEnum(str, enum.Enum):
    SUCCESSFUL = "successful"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(
        Enum(PaymentStatusEnum, name="payment_status_enum"),
        nullable=False,
        default=PaymentStatusEnum.SUCCESSFUL,
    )
    amount = Column(DECIMAL(10, 2), nullable=False)
    external_payment_id = Column(String, nullable=False)

    user = relationship("User", back_populates="payments")
    order = relationship("Order", back_populates="payment")
    payment_items = relationship("PaymentItem", back_populates="payment", cascade="all, delete-orphan")
