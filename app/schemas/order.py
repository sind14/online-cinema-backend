from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.schemas.movie import MovieResponse
from app.models.orders import OrderStatusEnum


class OrderItemResponse(BaseModel):
    id: int
    movie: MovieResponse
    price_at_order: Decimal

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    status: OrderStatusEnum
    total_amount: Decimal
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = {"from_attributes": True}
