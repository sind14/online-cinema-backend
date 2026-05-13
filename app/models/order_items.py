from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    __table_args__ = (UniqueConstraint("order_id", "movie_id", name="uq_order_movie"),)

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    price_at_order = Column(DECIMAL(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    movie = relationship("Movie", back_populates="order_items")
    payment_items = relationship("PaymentItem", back_populates="order_item")
