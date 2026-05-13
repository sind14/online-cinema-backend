from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.models.payments import PaymentStatusEnum


class PaymentItemBase(BaseModel):
    order_item_id: int
    price_at_payment: Decimal


class PaymentItemCreate(PaymentItemBase):
    pass


class PaymentItemResponse(PaymentItemBase):
    id: int
    payment_id: int

    model_config = {"from_attributes": True}


class PaymentBase(BaseModel):
    order_id: int
    amount: Decimal


class PaymentCreate(BaseModel):
    order_id: int


class PaymentResponse(PaymentBase):
    id: int
    user_id: int
    status: PaymentStatusEnum
    external_payment_id: str
    payment_items: list[PaymentItemResponse]
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentDetailResponse(PaymentResponse):
    payment_items: list[PaymentItemResponse]
