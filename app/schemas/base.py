from pydantic import BaseModel, Field
from typing import Optional


class NameBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class NameUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
