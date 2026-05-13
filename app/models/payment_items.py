from sqlalchemy import Column, Integer, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from app.database.base import Base


class PaymentItem(Base):
    __tablename__ = "payment_items"

    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=False)
    price_at_payment = Column(DECIMAL(10, 2), nullable=False)

    payment = relationship("Payment", back_populates="payment_items")
    order_item = relationship("OrderItem", back_populates="payment_items")
